from falafel.core.plugins import mapper
from falafel.core import MapperOutput, computed
from falafel.mappers import get_active_lines


def get_modprobe_items(content, action):
    items = dict()
    for line in get_active_lines(content, "#"):
        if line.strip().startswith(action):
            items[line.split()[1]] = line.split()[2:]
    return items


class ModProbe(MapperOutput):
    """
    Since there are some other COMMANDS that could be set in
    modprobe.d/\*,conf such as:

    1. blacklist modulename
    3. remove modulename command...

    however, they are not common used in current plugins.
    So I just defined 2 APIs to get "options and "install"
    related items first
    """

    @computed
    def options_dict(self):
        """
        Return a dict which use "module name" as key and "options" as value.

        Example data in /etc/modprobe.d/\*.conf:
        ----------------------------------------
        options modulename option ...

        options ipv6 disable=1
        options mlx4_core debug_level=1 log_num_mgm_entry_size=-1
        ----------------------------------------
        """
        return get_modprobe_items(self.data, 'options')

    @computed
    def install_dict(self):
        """
        Return a dict which use "module name" as key and "commands" as value.

        Example data in /etc/modprobe.d/\*.conf:
        ----------------------------------------
        install modulename command ...

        install ipv6 /bin/true
        ----------------------------------------
        """
        return get_modprobe_items(self.data, 'install')


@mapper('modprobe.d')
def modprobe(context):
    """
    Returns an object of ModProbe.
    """
    return ModProbe(context.content)
