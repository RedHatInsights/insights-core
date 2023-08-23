from __future__ import absolute_import

import logging
import textwrap

from insights.client.constants import InsightsConstants as constants

APP_NAME = constants.app_name
logger = logging.getLogger(__name__)


def map_rm_conf_to_components(rm_conf):
    '''
    Convert the "files" and "commands" configured in the "classic" remove.conf
    and file-redaction.yaml to insights components.
    '''
    updated_commands = []
    updated_files = []
    updated_components = []

    if not rm_conf:
        return rm_conf

    logger.warning("If possible, commands and files specified in the blacklist configuration will be converted to Insights component specs that will be disabled as needed.")

    # save matches to a dict for informative logging
    conversion_map = {}
    longest_key_len = 0

    for section in ['commands', 'files']:
        for key in rm_conf.get(section, []):
            components = _search_specs(key)
            if components:
                for comp in components:
                    conversion_map[key] = comp
                    if len(key) > longest_key_len:
                        longest_key_len = len(key)
                    updated_components.append(comp)
            else:
                if section == 'commands':
                    updated_commands.append(key)
                elif section == 'files':
                    updated_files.append(key)

    _log_conversion_table(conversion_map, longest_key_len)

    if 'components' in rm_conf:
        # update components list if there already is one
        original_comp_set = set(rm_conf['components'])
        updated_comp_set = set(dict.fromkeys(updated_components))
        # avoid duplicates
        rm_conf['components'] += list(updated_comp_set - original_comp_set)
    else:
        # otherwise create it
        rm_conf['components'] = list(dict.fromkeys(updated_components))

    rm_conf['commands'] = updated_commands
    rm_conf['files'] = updated_files

    return rm_conf


def _search_specs(key):
    '''
    Search the `:class:insights.specs.default.DefaultSpecs` for a command/file
    from "name" and return the full spec module name if it exists
    '''
    def _all_patterns(s_mod):
        patterns = []
        patterns.append(s_mod.cmd) if hasattr(s_mod, 'cmd') else None
        patterns.append(s_mod.path) if hasattr(s_mod, 'path') else None
        patterns.extend(s_mod.paths) if hasattr(s_mod, 'paths') else None
        patterns.extend(s_mod.patterns) if hasattr(s_mod, 'patterns') else None
        if hasattr(s_mod, 'dep'):  # head
            patterns.extend(_all_patterns(s_mod.dep))
        if hasattr(s_mod, 'deps'):
            for dp in s_mod.deps:  # first_of
                patterns.extend(_all_patterns(dp))
        return patterns

    specs = []
    from insights.specs.default import DefaultSpecs
    for spec in filter(lambda x: not x.startswith('__'), dir(DefaultSpecs)):
        spec_module = getattr(DefaultSpecs, spec)
        if not hasattr(spec_module, 'multi_output'):
            # It's NOT a spec
            continue
        spec_mod_name = "insights.specs.default.DefaultSpecs.{0}".format(spec)
        if key == spec:
            return [spec_mod_name]
        patterns = _all_patterns(spec_module)
        if any(pat == key for pat in patterns if pat):
            specs.append(spec_mod_name)
    return specs


def _log_conversion_table(conversion_map, longest_key_len):
    '''
    Handle wrapping & logging the conversions
    '''
    max_log_len = 48

    for n in conversion_map:
        spec_name_no_prefix = conversion_map[n].rsplit('.', 1)[-1]

        # for specs exceeding a max length, wrap them past the first line
        if longest_key_len > max_log_len:
            log_len = max_log_len
        else:
            log_len = longest_key_len

        wrapped_spec = textwrap.wrap(n, max_log_len)
        # log the conversion on the first line of the "wrap"
        wrapped_spec[0] = '- {0:{1}} => {2}'.format(wrapped_spec[0], log_len, spec_name_no_prefix)
        logger.warning('\n  '.join(wrapped_spec))
