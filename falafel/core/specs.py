import re
import os
import logging
from collections import defaultdict
from falafel.config.static import get_config
from falafel.config import AnalysisTarget, META_FILE_LIST, CommandSpec

logger = logging.getLogger(__name__)
logger.setLevel(logging.FATAL)


class SpecMapper(object):
    """
    This class wraps a tarfile-like object with spec mapping of names.
    """

    def __init__(self, tf_object, data_spec_config=None):
        self.tf = tf_object
        self.all_names = [f for f in self.tf.getnames() if not self.tf.isdir(f)]
        self.root = os.path.commonprefix(self.all_names)
        logger.debug("SpecMapper.root: %s", self.root)
        self.data_spec_config = data_spec_config if data_spec_config else get_config()
        self.symbolic_files = defaultdict(list)
        self.analysis_target = self._determine_analysis_target()
        self.create_symbolic_file_list()

    def _get_first_matching(self, pattern):
        for match in filter(
                re.compile(self.root + "?" + pattern + "$").match,
                self.all_names):
            return match

    def _determine_analysis_target(self):
        path = self._get_first_matching(META_FILE_LIST["analysis_target"])
        if path:
            section = self.get_content(path, symbolic=False)[0].strip()
            return AnalysisTarget.get(section)

    def _extend_symbolic_files(self, symbolic_name, matches):
        if matches:
            self.symbolic_files[symbolic_name].extend(matches)

    def filter_commands(self, files):
        for f in files:
            if "sos_commands" in f or "insights_commands" in f or "commands/" in f:
                yield f

    def add_files(self, file_map):
        logger.debug("ROOT: %s", self.root)
        unrooted_map = {
            f.split(self.root)[1]: f
            for f in self.all_names
            if f != self.root
        }
        unrooted_files = set(unrooted_map)
        commands = set(self.filter_commands(unrooted_files))
        non_commands = unrooted_files - commands
        if logger.level == logging.DEBUG:
            logger.debug("\n".join(uf for uf in sorted(unrooted_files)))

        for symbolic_name, spec_group in file_map.iteritems():
            for spec in spec_group.get_all_specs():  # Usually just one item in paths
                is_command = isinstance(spec, CommandSpec)

                # foreman-debug archives contain flat structures of commands
                # that can be confused with other command outputs easily so
                # we'll add a ^ to the beginning of the pattern if it is not an
                # insights archive
                if '/' in spec.get_path() or self.analysis_target is not None:
                    prefix = ''
                else:
                    prefix = '^'

                r = spec.get_regex(prefix=prefix, analysis_target=self.analysis_target)
                if is_command or "_commands/" in r.pattern:
                    filter_set = commands
                else:
                    filter_set = non_commands
                logger.debug("Pattern: %s", r.pattern)
                matches = filter(r.search, filter_set)
                if matches:
                    matches = [unrooted_map[m] for m in matches]

                    # In order to prevent matching *dumb* symlinks in some
                    # archive formats, we are going to filter out symlinks when
                    # calculating matches for CommandSpecs
                    if is_command:
                        matches = filter(lambda n: not self.tf.issym(n), matches)

                    # filter out directories that match
                    matches = [m for m in matches if not self.tf.isdir(m)]

                    if not matches:
                        continue
                    # In order to prevent accidental duplication when matching
                    # files, we only allow the first matched file to be added
                    # to the working set for non-pattern file specs.
                    if not spec.is_multi_output() and len(matches) > 1:
                        logger.debug("Non multi-output file had multiple matches: %s", matches)
                        self._extend_symbolic_files(symbolic_name, [matches[0]])
                    else:
                        self._extend_symbolic_files(symbolic_name, matches)
                    break  # only add the first matching pattern

    def _add_meta_files(self):
        for symbolic_name, suffix in META_FILE_LIST.items():
            self._extend_symbolic_files(symbolic_name, [self._get_first_matching(suffix)])

    def create_symbolic_file_list(self):
        self.add_files(self.data_spec_config.get_spec_lists())
        if not self.analysis_target:
            self.add_files(self.data_spec_config.get_meta_specs())
        else:
            self._add_meta_files()

    def get_content(self, path, split=True, symbolic=True, default=""):
        """Returns file content from path, where path is the full pathname inside
        the archive"""
        if symbolic:
            path = self.symbolic_files.get(path, [""])[0]
        content = self.tf.extractfile(path) if path in self.all_names else default
        return list(content.splitlines()) if split else content

    def exists(self, path, symbolic=True):
        return path in self.symbolic_files if symbolic else path in self.all_names
