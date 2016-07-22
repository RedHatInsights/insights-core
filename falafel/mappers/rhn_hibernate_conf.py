from falafel.mappers import get_active_lines
from falafel.core.plugins import mapper


@mapper("rhn_hibernate.conf")
def rhn_hibernate_conf(context):
    """
    Parses rhn_hibernate.conf and returns a dict.
    - {
        "hibernate.c3p0.min_size": '5'
        "hibernate.c3p0.preferredTestQuery": "select 'c3p0 ping' from dual"
      }
    """
    hb_dict = {}
    for line in get_active_lines(context.content):
        if '=' in line:
            key, _, value = line.partition('=')
            hb_dict[key.strip()] = value.strip()
    return hb_dict
