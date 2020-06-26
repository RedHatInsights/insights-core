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

uploader_json_file = pkgutil.get_data(insights.__name__, "uploader_json_map.json")
uploader_json = json.loads(uploader_json_file)


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

    if not rm_conf:
        return

    logger.warning("If possible, commands and files specified in the blacklist configuration will be converted to Insights component specs that will be disabled as needed.")

    # save matches to a dict for informative logging
    conversion_map = {}
    longest_key_len = 0

    for section in ['commands', 'files']:
        if section not in rm_conf:
            continue
        for key in rm_conf[section]:
            if section == 'commands':
                symbolic_name = _search_uploader_json(['commands'], key)
            elif section == 'files':
                # match both files and globs to rm_conf files
                symbolic_name = _search_uploader_json(['files', 'globs'], key)

            component = _get_component_by_symbolic_name(symbolic_name)
            if component:
                conversion_map[key] = component
                if len(key) > longest_key_len:
                    longest_key_len = len(key)
                updated_components.append(component)
            else:
                if section == 'commands':
                    updated_commands.append(key)
                elif section == 'files':
                    updated_files.append(key)

    for n in conversion_map:
        spec_name_no_prefix = conversion_map[n].rsplit('.', 1)[-1]
        logger.warning('{0:{1}}\t=> {2}'.format(n, longest_key_len, spec_name_no_prefix))

    updated_components = list(dict.fromkeys(updated_components))

    rm_conf['commands'] = updated_commands
    rm_conf['files'] = updated_files
    rm_conf['components'] = updated_components

    return rm_conf


def _search_uploader_json(headings, key):
    '''
    Search an uploader.json block for a command/file from "name"
    and return the symbolic name if it exists

    headings        - list of headings to search inside uploader.json
    key             - raw command/file or symbolic name to search
    conversion_map  - list of names to found components for logging
    longest_key_len - length of longest name for logging
    '''
    for heading in headings:
        # keys inside the dicts are the heading, but singular
        singular = heading.rstrip('s')

        for spec in uploader_json[heading]:
            if key == spec['symbolic_name'] or (key == spec[singular] and heading != 'globs'):
                # matches to a symbolic name or raw command, cache the symbolic name
                # only match symbolic name for globs
                sname = spec['symbolic_name']
                if not six.PY3:
                    sname = sname.encode('utf-8')
                return sname


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
