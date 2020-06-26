from __future__ import absolute_import
import pkgutil
import insights
import json
import six
import logging

from .constants import InsightsConstants as constants
from insights.specs.default import DefaultSpecs

APP_NAME = constants.app_name
logger = logging.getLogger(__name__)


def map_rm_conf_to_components(rm_conf):
    '''
    In order to maximize compatibility between "classic" remove.conf
    configurations and core collection, do the following mapping
    strategy:
    1. If remove.conf entry matches a symbolic name, disable the
        corresponding core component.
    2. If remove.conf entry is a raw command or file, do a reverse
        lookup on the symbolic name based on stored uploader.json data,
        then continue as in step 1.
    3. If neither conditions 1 or 2 are matched it is either
        a) a mistyped command/file, or
        b) an arbitrary file.
        For (a), classic remove.conf configs require an exact match to
            uploader.json. We can carry that condition into our
            compatibility with core.
        For (b), classic collection had the ability to skip arbitrary
            files based on filepaths in uploader.json post-expansion
            (i.e. a specific repo file in /etc/yum.repos.d).
            Core checks all files collected against the file
            blacklist filters, so these files will be omitted
            just by the nature of core collection.
    '''
    updated_commands = []
    updated_files = []
    updated_components = []

    uploader_json_file = pkgutil.get_data(insights.__name__, "uploader_json_map.json")
    uploader_json = json.loads(uploader_json_file)

    if not rm_conf:
        return

    logger.warning("If possible, commands and files specified in the blacklist configuration will be converted to Insights component specs that will be disabled as needed.")

    # save matches to a dict for informative logging
    conversion_map = {}
    longest_key = 0

    # loop
    #   match command/symbol with symbolic name
    #   get component from symbolic name
    #   add component to components blacklist (with prefix)
    #   add command and result (without prefix) to map for logging at the end

    # this is a little confusing after being refactored, so:
    #   uploader_json - the loaded uploader.json data, as a dict
    #   rm_conf_key   - one of the section names in remove.conf (commands and files)
    #   search_keys   - the keys to look for in uploader.json depending on rm_conf_key.
    #                   for "commands" it's just "commands" but for "files" we're
    #                   looking in both "files" and "globs"
    #   singular      - search_key with the trailing "s" removed to peek into the
    #                   uploader.json dicts
    #   c             - one of the values of our current rm_conf_key
    #   matched       - whether or not a match to a component has been found in the list
    #   s             - one of the search_keys
    #   spec          - one of the individual dicts of uploader.json
    #   sname         - the symbolic name of a matching record
    #   component     - the component matching to a symbolic name

    #   updated_components - the list of matching components
    #   updated_commands   - leftover commands that could not be matched
    #   updated_files      - leftover files that could not be matched
    #   conversion_map     - dict of rm_conf entries and the matching component for logging
    #   longest_key        - keep track of longest entry for logging

    for rm_conf_key in ['commands', 'files']:
        # iterate over the two keys we are interested in
        search_keys = [rm_conf_key]
        if rm_conf_key == 'files':
            search_keys = ['files', 'globs']
        for c in rm_conf.get(rm_conf_key, []):
            # iterate over each value in commands/files
            matched = False
            for s in search_keys:
                # will only be 1 or 2 iterations - [commands] or [files, globs]
                singular = s.rstrip('s')
                for spec in uploader_json[s]:
                    if c == spec['symbolic_name'] or (c == spec[singular] and s != 'globs'):
                        # matches to a symbolic name or raw command, cache the symbolic name
                        # only match symbolic name for globs
                        sname = spec['symbolic_name']
                        if not six.PY3:
                            sname = sname.encode('utf-8')
                        component = _get_component_by_symbolic_name(sname)
                        if component is None:
                            # the spec is not collected by core
                            continue
                        conversion_map[c] = component
                        if len(c) > longest_key:
                            longest_key = len(c)
                        updated_components.append(component)
                        matched = True
                        break
            if not matched:
                # could not match the command to anything, keep in config as-is
                if rm_conf_key == 'commands':
                    updated_commands.append(c)
                if rm_conf_key == 'files':
                    updated_files.append(c)

    for n in conversion_map:
        spec_name_no_prefix = conversion_map[n].rsplit('.', 1)[-1]
        logger.warning('{0:{1}}\t=> {2}'.format(n, longest_key, spec_name_no_prefix))

    updated_components = list(dict.fromkeys(updated_components))

    rm_conf['commands'] = updated_commands
    rm_conf['files'] = updated_files
    rm_conf['components'] = updated_components

    return rm_conf


def _get_component_by_symbolic_name(sname):
    # match a component to a symbolic name
    # some symbolic names need to be renamed to fit specs
    spec_prefix = "insights.specs.default.DefaultSpecs."
    spec_conversion = {
        'getconf_pagesize': 'getconf_page_size',
        'lspci_kernel': 'lspci',
        'netstat__agn': 'netstat_agn',
        'rpm__V_packages': 'rpm_V_packages',
        'ss_tupna': 'ss',

        'machine_id1': 'machine_id',
        'machine_id2': 'machine_id',
        'machine_id3': 'machine_id',
        'grub2_efi_grubenv': None,
        'grub2_grubenv': None,
        'limits_d': 'limits_conf',
        'modprobe_conf': 'modprobe',
        'modprobe_d': 'modprobe',
        'ps_auxwww': 'insights.specs.sos_archive.SosSpecs.ps_auxww',  # special case
        'rh_mongodb26_conf': 'mongod_conf',
        'sysconfig_rh_mongodb26': 'sysconfig_mongod',
        'redhat_access_proactive_log': None,

        'krb5_conf_d': 'krb5'
    }

    if sname in spec_conversion:
        if spec_conversion[sname] is None:
            return None
        if sname == 'ps_auxwww':
            return spec_conversion[sname]
        return spec_prefix + spec_conversion[sname]
    return spec_prefix + sname
