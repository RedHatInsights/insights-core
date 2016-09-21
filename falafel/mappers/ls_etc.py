from .. import mapper


@mapper("ls_etc")
def parse_ls_etc(context):
    """
    Parse "ls -lanR /etc" and return all the regular and link files in a list.

    Input Example:

    /etc/sysconfig:
    total 96
    drwxr-xr-x.  7 0 0 4096 Jul  6 23:41 .
    drwxr-xr-x. 77 0 0 8192 Jul 13 03:55 ..
    drwxr-xr-x.  2 0 0   41 Jul  6 23:32 cbq
    drwxr-xr-x.  2 0 0    6 Sep 16  2015 console
    -rw-------.  1 0 0 1390 Mar  4  2014 ebtables-config
    -rw-r--r--.  1 0 0   72 Sep 15  2015 firewalld
    lrwxrwxrwx.  1 0 0   17 Jul  6 23:32 grub -> /etc/default/grub

    /etc/rc.d/rc3.d:
    total 4
    drwxr-xr-x.  2 0 0   58 Jul  6 23:32 .
    drwxr-xr-x. 10 0 0 4096 Sep 16  2015 ..
    lrwxrwxrwx.  1 0 0   20 Jul  6 23:32 K50netconsole -> ../init.d/netconsole
    lrwxrwxrwx.  1 0 0   17 Jul  6 23:32 S10network -> ../init.d/network
    lrwxrwxrwx.  1 0 0   15 Jul  6 23:32 S97rhnsd -> ../init.d/rhnsd

    Output Example:

    {
        "/etc/sysconfig":
            {
                "files": ['ebtables-config', 'firewalld', 'grub'],
                "directories": ['cbq', 'console']
            },
        "/etc/rc.d/rc3.d":
            {
                "files": ['K50netconsole', 'S10network', 'S97rhnsd'],
                "directories": []
            }
    }
    """
    dicts = {}
    files = []
    directories = []
    dir_ = ""
    for line in context.content:
        if not line:
            dicts[dir_] = {"files": files, "directories": directories}
            files = []
            directories = []
        elif line.strip().endswith(":"):
            dir_ = line.split(":")[0]
        elif line.startswith('-'):
            files.append(line.split()[-1])
        elif line.startswith('l'):
            files.append(line.split()[-3])
        elif line.startswith('d') and not line.endswith('.'):
            directories.append(line.split()[-1])
    dicts[dir_] = {"files": files, "directories": directories}
    return dicts
