import re
import types
import os

from falafel.util.command import retarget_command_for_mountpoint

COMMANDS_ARCHIVE_DIR = "/insights_commands"
DATA_ARCHIVE_DIR = "/insights_data"

META_FILE_LIST = {
    "analysis_target": DATA_ARCHIVE_DIR + "/analysis_target",
    "machine-id": DATA_ARCHIVE_DIR + "/machine-id",
    "branch_info": "/branch_info",
    "uploader_log": DATA_ARCHIVE_DIR + "/insights_logs/insights.log"
}


class SpecPathError(Exception):
    """
        Errors in the path to a ___Spec call - e.g. a SimpleFileSpec starting
        with a /, or a CommandSpec not starting with one.
    """
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message


def get_meta_specs():
    result = {}
    for symbolic_name, location in META_FILE_LIST.items():
        result[symbolic_name] = {
            "archive_file_name": location
        }
    return result


class AnalysisTarget:

    ALL_DERIVED_CLASSES = []
    section_name = "unset"

    def __str__(self):
        return self.section_name

    @classmethod
    def add_section(cls, json, section):
        if cls.instance not in cls.ALL_DERIVED_CLASSES:
            raise ValueError("in AnalysisTarget:add_section: class %s not in ALL_DERIVED_CLASSES" % cls)

        if not section:
            return json

        if not json:
            json = {}

        if cls.section_name in json:
            json[cls.section_name].extend(section)
        else:
            json[cls.section_name] = section

        return json

    @classmethod
    def get(cls, section_name):
        for each_class in cls.ALL_DERIVED_CLASSES:
            if section_name == each_class.section_name:
                return each_class
        return None

    def _calc_dirs(self, name):
        self.archive_dir = os.path.join(DATA_ARCHIVE_DIR, name)
        self.rootfs_archive_dir = os.path.join(self.archive_dir, "rootfs")
        self.commands_archive_dir = os.path.join(self.archive_dir, "commands")
        self.host_rootfs_archive_dir = os.path.join(self.archive_dir, "dockerhost", "rootfs")
        self.host_commands_archive_dir = os.path.join(self.archive_dir, "dockerhost", "commands")


class HostTarget(AnalysisTarget):

    section_name = "host"

    def place_in_archive_command(self, mangled_command):
        return os.path.join(COMMANDS_ARCHIVE_DIR, mangled_command)

    def place_in_archive_file(self, path):
        if path.startswith("/"):
            return path
        else:
            return "/" + path

    def place_in_archive_docker_host_command(self, mangled_command):
        # This case should never happen, that is get_for_uploader should never
        #  call this case, and so one of these should never appear in uploader.json,
        #  so this case will never appear in the archive, and TarProcessor shouldn't
        #  ever see on of these.
        # But, TarProcessor which calls get_regex doesn't filter specs on
        # analysis_target, it just tries to collect all specs from somewhere
        # in the archive, even if they are never there, and shouldn't be there.
        # Maybe we should change TarProcessor to filter..., but until then
        # we just return valid, but never used data.
        return os.path.join(DATA_ARCHIVE_DIR + "/dockerhost/commands", mangled_command)

    def place_in_archive_docker_host_file(self, path):
        # This case should never happen, that is get_for_uploader should never
        #  call this case, and so one of these should never appear in uploader.json,
        #  so this case will never appear in the archive, and TarProcessor shouldn't
        #  ever see on of these.
        # But, TarProcessor which calls get_regex doesn't filter specs on
        # analysis_target, it just tries to collect all specs from somewhere
        # in the archive, even if they are never there, and shouldn't be there.
        # Maybe we should change TarProcessor to filter..., but until then
        # we just return valid, but never used data.
        return os.path.join(DATA_ARCHIVE_DIR + "/dockerhost/rootfs", path)

    def add_command_section(self, json, spec, output_filters):
        doc = {
            "command": spec.get_for_uploader(),
            "pattern": output_filters,
            "archive_file_name": spec.get_archive_file_name(self)}
        if spec.get_pre_command_key():
            doc["pre_command"] = spec.get_pre_command_key()

        return self.add_section(json, [doc])

    def add_file_section(self, json, spec, output_filters):
        section = [{
            "file": spec.get_for_uploader(),
            "pattern": output_filters,
            "archive_file_name": spec.get_archive_file_name(self)}]

        return self.add_section(json, section)

    def retarget_command(self, command):
        # if a command, written to collect data from a host,
        # can be applied to this target,
        #   return a rewritten command to do so
        #   otherwise return None

        # For HostTarget, obviously this function does nothing
        #   we implement all commands, and we don't need to alter the command
        return command

    def retarget_file(self, path):
        # if a path, written to collect data from a host,
        # can be applied to this target,
        #   return a rewritten path to do so
        #   otherwise return None

        # For HostTarget, obviously this function does nothing
        #   we collect from all paths, and we don't need to alter the file to do so
        return path


VIRTUAL_FILE_MOUNT_POINTS = ["/proc", "/sys"]


class DockerTarget(AnalysisTarget):

    def place_in_archive_command(self, mangled_command):
        return os.path.join(self.commands_archive_dir, mangled_command)

    def place_in_archive_file(self, path):
        return os.path.join(self.rootfs_archive_dir, path)

    def place_in_archive_docker_host_command(self, mangled_command):
        return os.path.join(self.host_commands_archive_dir, mangled_command)

    def place_in_archive_docker_host_file(self, path):
        return os.path.join(self.host_rootfs_archive_dir, path)

    def add_command_section(self, json, spec, output_filters):
        command = spec.get_for_uploader(self)

        if command is None:
            return json

        section = [{
            "command": command,
            "pattern": output_filters,
            "archive_file_name": spec.get_archive_file_name(self)}]

        return self.add_section(json, section)

    def add_file_section(self, json, spec, output_filters):
        path = spec.get_for_uploader(self)

        if path is None:
            return json

        section = [{
            "file": path,
            "pattern": output_filters,
            "archive_file_name": spec.get_archive_file_name(self)}]

        return self.add_section(json, section)

    def retarget_command(self, command):
        # if a command, written to collect data from a host,
        # can be applied to this target,
        #   return a rewritten command to do so
        #   otherwise return None

        return retarget_command_for_mountpoint(command)


class DockerImageTarget(DockerTarget):

    section_name = "docker_image"

    def __init__(self):
        self._calc_dirs("image")

    def retarget_file(self, path):
        # if a path, written to collect data from a host,
        # can be applied to this target,
        #   return a rewritten path to do so
        #   otherwise return None

        # For DockerImageTarget, we collect from any path that isn't in
        # a virtual file system

        if any(path.startswith(pt) for pt in VIRTUAL_FILE_MOUNT_POINTS):
            return None
        else:
            return '{CONTAINER_MOUNT_POINT}' + path


class DockerContainerTarget(DockerTarget):

    section_name = "docker_container"

    def __init__(self):
        self._calc_dirs("container")

    def retarget_file(self, path):
        # if a path, written to collect data from a host,
        # can be applied to this target,
        #   return a rewritten path to do so
        #   otherwise return None

        # For DockerContainerTarget, we collect from all paths

        return '{CONTAINER_MOUNT_POINT}' + path


AnalysisTarget.ALL_DERIVED_CLASSES = DefaultAnalysisTargets = [
    HostTarget(), DockerImageTarget(), DockerContainerTarget()
]

HostTarget.instance, DockerImageTarget.instance, DockerContainerTarget.instance = DefaultAnalysisTargets


def check_consistency(name, specs):
    """Function that ensures all specs in a SpecGroup have the same configuration."""
    try:
        it = iter(specs)
        first = next(it)
        lrg = first.is_large()
        mo = first.is_multi_output()
        if not all(lrg == i.is_large() and mo == i.is_multi_output() for i in it):
            raise Exception('{n} does not have consistent spec definitions.'.format(n=name))
    except StopIteration:
        pass


def group_wrap(spec_map):
    """Convenience method for ensuring that every spec is a member of a group."""

    out_map = {}
    for name, specs in spec_map.iteritems():
        out_map[name] = specs if isinstance(specs, SpecGroup) else First([specs])
        check_consistency(name, out_map[name].get_specs())
    return out_map


class SpecGroup(object):
    """BaseClass for groups of specs
    that provides no behavior and
    is intended to be subclassed.
    """

    def __init__(self, specs):
        self.specs = specs

    def __len__(self):
        return len(self.specs)

    def get_all_specs(self):
        return self.specs

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, str(self.specs))


class First(SpecGroup):
    """Indicates the uploader should collect the first spec
    (InsightsDataSpecBase) in the list.  Other items in the list
    are available for backwards compatibility in the processing
    of archives.  That is, rules will be given results from either
    spec, but only the first will be collected going forward."""

    def get_specs(self):
        return (self.specs[0],)


class All(SpecGroup):
    """Indicates the uploader should attempt to collect the all specs
    (InsightsDataSpecBase) in the list.  This SpecGroup is used to cover
    use cases such as a command that lives in ``/usr/sbin/`` on one
    version of RHEL and ``/sbin`` on another version."""

    def get_specs(self):
        return self.specs


class NoneGroup(SpecGroup):
    """Indicates the uploader should not attempt to collect anything from this
    spec.  This is to provide separate definitions for different formats of the
    same command.  This generally happens when one format is collected by
    SoSReport, but Insights collects a different version (usually to get more
    or more easily parseable information)."""

    def get_specs(self):
        return []


class InsightsDataSpecConfig(object):

    def __init__(self, specs, meta_specs, pre_commands=None, maximum_line_size=1024 * 32):
        self.specs = group_wrap(specs)
        self.pre_commands = pre_commands if pre_commands else {}
        self.meta_specs = group_wrap(meta_specs)
        self.maximum_line_size = maximum_line_size

    def _get_group_and_specs(self, specs, other_specs):
        s_g = specs.__class__
        s_s = specs.get_all_specs()

        o_g = other_specs.__class__
        o_s = other_specs.get_all_specs()

        if s_g != o_g:
            raise Exception("Spec Groups are not allowed to differ")

        return s_g(s_s + o_s)

    def merge(self, others):
        out = {}
        all_keys = set(self.specs.keys() + others.keys())
        for key in all_keys:
            s = self.specs.get(key)
            o = others.get(key)
            if s and o:
                out[key] = self._get_group_and_specs(s, o)
            else:
                out[key] = s or o
        self.specs = out

    def compose(self, other):
        self.specs.update(other.specs)
        self.meta_specs.update(other.meta_specs)
        return self

    def iteritems(self):
        return self.specs.iteritems()

    def get_spec_lists(self):
        return self.specs

    def get_meta_specs(self):
        return self.meta_specs

    def get_spec_list(self, symbolic_name, default=First([])):
        return self.specs.get(symbolic_name, default).get_all_specs()

    def get_specs(self, symbolic_name, default=All([])):
        return self.specs.get(symbolic_name, default).get_specs()

    def get_meta_spec_list(self, symbolic_name, default=All([])):
        return self.meta_specs.get(symbolic_name, default).get_all_specs()

    def is_large(self, symbolic_name):
        specs = self.get_spec_list(symbolic_name)
        return any(spec.is_large() for spec in specs)

    def is_multi_output(self, symbolic_name):
        spec_list = self.get_spec_list(symbolic_name)
        return any(spec.is_multi_output() for spec in spec_list)

    def max_line_size(self):
        return self.maximum_line_size

    def __contains__(self, key):
        return key in self.specs or key in self.meta_specs

# The original three primary spec classes, SimpleFileSpec, PatternSpec,
# and CommandSpec, have been generalized so that when collecting from
# DockerImage or DockerContainer, those specs will collect from those
# things if it is appropriate to do so.
#
# But we also need a way, when collecting from a DockerImage or DockerContainer
# to collect data from the host those things are on.  DockerHostSimpleFileSpec,
# DockerHostPatternSpec, and DockerHostCommand (below) are for that case.


class InsightsDataSpecBase(object):

    def __init__(self, multi_output=False, large_content=False):
        self.multi_output = multi_output
        self.large_content = large_content
        self.regex_cache = {}

    def get_path(self, analysis_target=None, for_archive_file_name=False):
        # this method, and it's overrides in derived classes
        # provides the significant sub-string of get_regex and get_archive_file_name
        # as well as determining what gets collected for file specs
        # With the addition of multiple analysis_targets we would like the option
        # of placing the archive file in different locations for different targets
        # If analysis_target is None and for_archive_file_name, then get_path must
        #   implement it's original behavor
        raise NotImplementedError()

    def get_regex(self, prefix='', suffix='$', analysis_target=None):
        # this method, and it's overrides in derived classes
        # is what the engine uses to find files in archives
        regex = prefix + self.get_path(analysis_target) + suffix
        if regex in self.regex_cache:
            r = self.regex_cache[regex]
        else:
            r = re.compile(regex.strip("/").replace("//", "/"))
            self.regex_cache[regex] = r
        return r

    def get_archive_file_name(self, analysis_target):
        # this method, and it's overrides in derived classes
        # returns the archive_file_name that should go in uploader.json
        # see get_regex
        # therefore this method must do what get_regex does, except for
        # the re.compile and the prefix and suffix
        return self.get_path(analysis_target=analysis_target, for_archive_file_name=True)

    def matches(self, f, prefix='', suffix=''):
        return self.get_regex(prefix, suffix).search(f)

    def get_preferred_path(self):
        raise NotImplementedError()

    def is_multi_output(self):
        return self.multi_output

    def get_pre_command_key(self):
        return None

    def is_large(self):
        return self.large_content

    def get_dynamic_args(self):
        ''' CommandSpec instances should return match groups for their paths
            if any exist.
            Other subclasses shouldn't bother implementing.
        '''
        return []

    def add_uploader_spec(self, json, output_filters):
        raise NotImplementedError()

    def __unicode__(self):
        return self.get_path()

    def __str__(self):
        return self.get_path()

    def __repr__(self):
        return "<%s '%s'>" % (self.__class__.__name__, str(self))


class SimpleFileSpec(InsightsDataSpecBase):

    def __init__(self, path, multi_output=False, large_content=False):
        if path[0] == '/':
            raise SpecPathError(path, "SimpleFileSpec path must not start with '/'")
        super(SimpleFileSpec, self).__init__(multi_output=multi_output, large_content=large_content)
        if not isinstance(path, types.StringTypes):
            raise ValueError("Path must be a string")
        self.path = path
        self.multi_output = multi_output

    def get_for_uploader(self, analysis_target=None):
        # this provides the path that goes into the 'file' field of uploader.json
        #    since 'retarget_file' can potentially return None
        #    if this method is called with a non-null analysis_target
        #       it may return None, and any caller must be prepared for that
        #    if called with no analysis_target, it always returns a valid path
        path = os.path.join("/", self.path)
        if analysis_target:
            path = analysis_target.retarget_file(path)
        return path

    def get_path(self, analysis_target=None, for_archive_file_name=False):
        # this provides the bases of get_regex, get_archive_file_name, and
        # for the 'file' field in uploader.json
        # if for_archive_file_name then this is for get_archive_file_name
        # if analysis_target=None and for_archive_file_name=False
        #   we need to return self.path unaltered
        path = self.path

        if for_archive_file_name:
            if self.multi_output:
                path = "{EXPANDED_FILE_NAME}"

        # where it is in the archive needs to be known for both regex's
        #  and for_archive_file_name
        if analysis_target:
            path = self.place_in_archive(path, analysis_target)

        return path

    def get_archive_file_name(self, analysis_target):
        return self.get_path(analysis_target=analysis_target, for_archive_file_name=True)

    def place_in_archive(self, path, analysis_target):
        return analysis_target.place_in_archive_file(path)

    def add_uploader_spec(self, json, output_filters):
        for each in DefaultAnalysisTargets:
            json = each.add_file_section(json, self, output_filters)
        return json


class PatternSpec(SimpleFileSpec):

    def __init__(self, path, large_content=False):
        super(PatternSpec, self).__init__(path, multi_output=True, large_content=large_content)

    def get_for_uploader(self, analysis_target=None):
        path = super(PatternSpec, self).get_for_uploader(analysis_target)
        if path:
            dir_path, filename = os.path.split(path)
            return os.path.join(dir_path, "()*" + filename)


class DockerHostSimpleFileSpec(SimpleFileSpec):
    #  If you are collecting data for a DockerContainer or DockerImage
    #  but you want to collect data from it's host, use this spec
    #  instead of SimpleFileSpec.
    #  We implement this by altering the 'file' field in uploader.json
    #   and where in the archive the output goes

    def place_in_archive(self, path, analysis_target):
        return analysis_target.place_in_archive_docker_host_file(path)

    def get_for_uploader(self, analysis_target=None):
        # ignore analysis target for the purposes of generating the file field
        #   so it collects from the host rather than the container or image
        return super(DockerHostSimpleFileSpec, self).get_for_uploader()


class DockerHostPatternSpec(SimpleFileSpec):
    #  If you are collecting data for a DockerContainer or DockerImage
    #  but you want to collect data from it's host, use this spec
    #  instead of PatternFileSpec.
    #  We implement this by altering the 'file' field in uploader.json
    #   and where in the archive the output goes

    def place_in_archive(self, path, analysis_target):
        return analysis_target.place_in_archive_docker_host_file(path)

    def get_for_uploader(self, analysis_target=None):
        # ignore analysis target for the purposes of generating the file field
        #   so it collects from the host rather than the container or image
        return super(DockerHostPatternSpec, self).get_for_uploader()


class CommandSpec(InsightsDataSpecBase):

    # this is the list of variables that are expanded by the client,
    # and so should not be expanded here, in the server
    CLIENT_SIDE_VARIABLES = ['DOCKER_IMAGE_NAME', 'DOCKER_CONTAINER_NAME',
                             'EXPANDED_FILE_NAME', 'CONTAINER_MOUNT_POINT']

    def __str__(self):
        return '<Command "{0}">'.format(self.command)

    def __init__(self, command, multi_output=True, large_content=False, **kwargs):
        if command[0] != '/':
            raise SpecPathError(command, "CommandSpec command must start with '/'")
        super(CommandSpec, self).__init__(multi_output=multi_output and len(kwargs) > 0, large_content=large_content)
        self.command = command
        self.path_groups = kwargs
        for k, v in self.path_groups.items():
            self.path_groups[k] = r"(?P<{0}>{1})".format(k, v)
        self.has_client_side_variables = self._contains_client_side_variables(self.command)

    @staticmethod
    def _contains_client_side_variables(command):
        # if any client side variables are within command
        for k in CommandSpec.CLIENT_SIDE_VARIABLES:
            if command.find("{%s}" % k) >= 0:
                return True
        return False

    @staticmethod
    def mangle_command(command, name_max=255, has_variables=False):
        """
        Mangle a command line string into something suitable for use as the basename of a filename.
        At minimum this function must remove slashes, but it also does other things to clean up
        the basename: removing directory names from the command name, replacing many non-typical
        characters with undersores, in addition to replacing slashes with dots.

        By default, curly braces, '{' and '}', are replaced with underscore, set 'has_variables'
        to leave curly braces alone.

        This function was copied from the function that insights-client uses to create the name it uses
        to capture the output of the command.

        Here, server side, it is used to figure out what file in the archive contains the output of
        a command.  Server side, the command may contain references to variables (names within
        matching curly braces) that will be expanded before the name is actually used as a file name.

        To completly mimic the insights-client behavior, curly braces need to be replaced with
        underscores.  If the command has variable references, the curly braces must be left alone.
        Set has_variables, to leave curly braces alone.

        This implementation of 'has_variables' assumes that variable names only contain characters
        that are not replaced by mangle_command.
        """
        if has_variables:
            pattern = r"[^\w\-\.\/{}]+"
        else:
            pattern = r"[^\w\-\.\/]+"

        mangledname = re.sub(r"^/(usr/|)(bin|sbin)/", "", command)
        mangledname = re.sub(pattern, "_", mangledname)
        mangledname = re.sub(r"/", ".", mangledname).strip(" ._-")
        mangledname = mangledname[:name_max]
        return mangledname

    # special situation that will go away when uploader
    # handles fancy {} sub syntax
    def get_for_uploader(self, analysis_target=None):
        # this provides the command that goes into the 'command' field of uploader.json
        #    since 'retarget_command' can potentially return None
        #    if this method is called with a non-null analysis_target
        #       it may return None, and any caller must be prepared for that
        #    if called with no analysis_target, it always returns a valid path
        command = self.command
        if self.multi_output or self.has_client_side_variables:
            command = self.replace_variables_for_uploader(self.command, self.path_groups)
        if analysis_target:
            command = analysis_target.retarget_command(command)
        return command

    def get_path(self, analysis_target=None, for_archive_file_name=False):

        if self.multi_output or self.has_client_side_variables:
            mangled = self.mangle_command(self.command, has_variables=True)
            if for_archive_file_name:
                formatted = self.replace_variables_for_archive_file_name(mangled, self.path_groups)
            else:
                formatted = self.replace_variables_for_regex(mangled, self.path_groups)

        else:
            formatted = self.mangle_command(self.command)

        # where it is in the archive needs to be known for both regex's
        #  and for_archive_file_name
        if analysis_target:
            return self.place_in_archive(formatted, analysis_target)
        else:
            return formatted

    def place_in_archive(self, mangled_command, analysis_target):
        return analysis_target.place_in_archive_command(mangled_command)

    def get_pre_command_key(self):
        # we only support one for now...
        if self.multi_output:
            return self.path_groups.keys()[0]

    def get_regex(self, prefix="", suffix="$", analysis_target=None):
        directory_prefix = "" if analysis_target else ".*/"
        return super(CommandSpec, self).get_regex(prefix + directory_prefix, suffix, analysis_target)

    def get_archive_file_name(self, analysis_target):
        return self.get_path(analysis_target=analysis_target, for_archive_file_name=True)

    def get_preferred_path(self):
        return self.get_regex()

    def add_uploader_spec(self, json, output_filters):
        for target in DefaultAnalysisTargets:
            json = target.add_command_section(json, self, output_filters)
        return json

    def replace_variables(self, command, mapping):
        return command.format(**mapping).strip()

    def replace_variables_for_uploader(self, command, path_groups):
        # for the uploader (for the 'command' field in uploader.json)
        #  we want to simply remove the server side
        #  variables, and leave the client side variables as is,
        #  that is map them from {NAME} to {NAME}
        mapping = dict((k, "") for k in path_groups)
        mapping.update(dict((k, "{%s}" % k) for k in self.CLIENT_SIDE_VARIABLES))
        return self.replace_variables(command, mapping)

    def replace_variables_for_archive_file_name(self, command, path_groups):
        # for archive file names we want to simply remove the server side
        #  variables, and leave the client side variables as is,
        #  that is map them from {NAME} to {NAME}
        mapping = dict((k, "") for k in path_groups)
        mapping.update(dict((k, "{%s}" % k) for k in self.CLIENT_SIDE_VARIABLES))
        return self.replace_variables(command, mapping)

    def replace_variables_for_regex(self, command, path_groups):
        # for the regex we want to replace server side variables with the
        #  regex patterns that are already in path_groups
        #  replace the client side variables with the pattern r'\S+'
        mapping = path_groups.copy()
        mapping.update(dict((k, r'\S+') for k in self.CLIENT_SIDE_VARIABLES))
        return self.replace_variables(command, mapping)


class DockerHostCommandSpec(CommandSpec):
    #  If you are collecting data for a DockerContainer or DockerImage
    #  but you want to collect data from it's host, use this spec
    #  instead of CommandSpec.
    #  We implement this by altering the 'command' field
    #   and where in the archive the output goes

    def place_in_archive(self, mangled_command, analysis_target):
        return analysis_target.place_in_archive_docker_host_command(mangled_command)

    def get_for_uploader(self, analysis_target=None):
        # ignore analysis target for the purposes of generating the command
        #   so it collects from the host rather than the container or image
        return super(DockerHostCommandSpec, self).get_for_uploader()


def _make_rpm_formatter(fmt=None):
    if fmt is None:
        fmt = [
            "%{NAME}-%{VERSION}-%{RELEASE}.%{ARCH}",
            "%{INSTALLTIME:date}",
            "%{BUILDTIME}",
            "%{RSAHEADER:pgpsig}",
            "%{DSAHEADER:pgpsig}"
        ]

    def inner(idx=None):
        if idx:
            return "\t".join(fmt[:idx]) + "\n"
        else:
            return "\t".join(fmt) + "\n"
    return inner


def json_format(fmt=None):
    if fmt is None:
        fmt = [
            ("name", "NAME"),
            ("version", "VERSION"),
            ("epoch", "EPOCH"),
            ("release", "RELEASE"),
            ("arch", "ARCH"),
            ("installtime", "INSTALLTIME:date"),
            ("buildtime", "BUILDTIME"),
            ("rsaheader", "RSAHEADER:pgpsig"),
            ("dsaheader", "DSAHEADER:pgpsig"),
            ("srpm", "SOURCERPM")
        ]

    def inner(idx=None):
        if idx:
            fields = ['"%s": "%%{%s}"' % (k, v) for k, v in fmt[:idx]]
        else:
            fields = ['"%s": "%%{%s}"' % (k, v) for k, v in fmt]
        return "\\{" + ",".join(fields) + "\\}\\n"
    return inner


format_rpm = _make_rpm_formatter()
