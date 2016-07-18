from falafel.core.plugins import mapper


@mapper("ls_boot")
def parse_ls_boot(context):
    """
    parsing ls_boot and return all the regular and link files in a list.
    Input Example:
        /boot:
        total 187380
        dr-xr-xr-x.  3 0 0     4096 Mar  4 16:19 .
        dr-xr-xr-x. 19 0 0     4096 Jul 14 09:10 ..
        -rw-r--r--.  1 0 0   123891 Aug 25  2015 config-3.10.0-229.14.1.el7.x86_64

        /boot/grub2:
        total 36
        drwxr-xr-x. 6 0 0  104 Mar  4 16:16 .
        dr-xr-xr-x. 3 0 0 4096 Mar  4 16:19 ..
        lrwxrwxrwx. 1 0 0     11 Aug  4  2014 menu.lst -> ./grub.conf
        -rw-r--r--. 1 0 0   64 Sep 18  2015 device.map

    Output Example:
        ['config-3.10.0-229.14.1.el7.x86_64', 'menu.lst', 'device.map']
    """

    files = []
    for line in context.content:
        if line.startswith('-'):
            files.append(line.split()[-1])
        elif line.startswith('l'):
            files.append(line.split()[-3])

    return files
