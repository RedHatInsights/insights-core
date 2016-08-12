from falafel.core.plugins import mapper
from falafel.core import MapperOutput
from falafel.mappers import get_active_lines


class ResolvConf(MapperOutput):
    pass


@mapper('resolv.conf')
def resolv_conf(context):
    '''
    Return a object contains a dict.
    The file content looks like:
    -------------------
    # This file is being maintained by Puppet.
    # DO NOT EDIT
    search a.b.com b.c.com
    options timeout:2 attempts:2
    nameserver 10.160.224.51
    nameserver 10.160.225.51
    nameserver 10.61.193.11
    -------------------
    The return output:
    {
        "active": "search",
        "nameserver": [
            "10.160.224.51",
            "10.160.225.51",
            "10.61.193.11"
        ],
        "search": [
            "a.b.com",
            "b.c.com"
        ],
        "options": [
            "timeout:2",
            "attempts:2"
        ]
    }
    '''
    resolv_info = {}
    name_info = []
    domain = False
    search = False

    # According to the man page, the 'domain' and 'search' keywords are mutually
    # exclusive.If more than one instance of these keywords is present, the
    # last instance wins. So, add a key "active" into resolve_info pointing out
    # which keywords is effective.
    for line in get_active_lines(context.content):
        if line.startswith('nameserver'):
            name_info.append(line.split()[1])
        else:
            temp = line.split()
            if temp[0] == 'domain':
                domain = True
                search = False
            if temp[0] == 'search':
                search = True
                domain = False
            resolv_info[temp[0]] = temp[1:]
    resolv_info['nameserver'] = name_info

    if domain and not search:
        resolv_info['active'] = 'domain'
    elif search and not domain:
        resolv_info['active'] = 'search'
    else:
        resolv_info['active'] = ''

    return ResolvConf(resolv_info)
