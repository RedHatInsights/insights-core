from falafel.core.plugins import mapper


@mapper("ls_dev")
def parse_ls_dev(context):
    """
    parsing ls -lanR /dev and return all the regular and link files in a list.
    Input Example:
      /dev/fedora:
      total 0
      drwxr-xr-x.  2 0 0  100 Jul 25 10:00 .
      drwxr-xr-x. 23 0 0 3720 Jul 25 12:43 ..
      lrwxrwxrwx.  1 0 0    7 Jul 25 10:00 home -> ../dm-2
      lrwxrwxrwx.  1 0 0    7 Jul 25 10:00 root -> ../dm-0
      lrwxrwxrwx.  1 0 0    7 Jul 25 10:00 swap -> ../dm-

      /dev/mapper:
      total 0
      drwxr-xr-x.  2 0 0     140 Jul 25 10:00 .
      drwxr-xr-x. 23 0 0    3720 Jul 25 12:43 ..
      crw-------.  1 0 0 10, 236 Jul 25 10:00 control
      lrwxrwxrwx.  1 0 0       7 Jul 25 10:00 docker-253:0-1443032-pool -> ../dm-3
      lrwxrwxrwx.  1 0 0       7 Jul 25 10:00 fedora-home -> ../dm-2
      lrwxrwxrwx.  1 0 0       7 Jul 25 10:00 fedora-root -> ../dm-0
      lrwxrwxrwx.  1 0 0       7 Jul 25 10:00 fedora-swap -> ../dm-1

    Output Example:
        {"/dev/fedora":["home", "root", "swap"], "/dev/mapper": ["fedora-home", "fedora-root", "fedora-swap"]}
    """
    dicts = dict()
    files = list()
    dir = ""
    for line in context.content:
        if not line:
            dicts[dir] = files
            files = list()
        elif line.strip().endswith(":"):
            dir = line.split(":")[0]
        elif line.startswith('-'):
            files.append(line.split()[-1])
        elif line.startswith('l'):
            files.append(line.split()[-3])
    dicts[dir] = files
    return dicts
