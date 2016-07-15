from falafel.core.plugins import mapper
import os


@mapper("limits.conf")
@mapper("nproc.conf")
def get_nproc(context):
    """
    - Get nproc lines from limits.conf and *.-nproc.conf
    - Returns any nproc lines from the contents of the passed in mapper file. Given the
      'etc/security/limits.conf' as an example:
      --- INPUT ---
      #oracle       hard    nproc   1024
       #oracle       hard    nproc   2024
      *             -       nproc   2048
      oracle        soft    nproc   4096# this is soft
      oracle        hard    nproc   65536
      user          -       nproc   12345

      --- OUTPUT ---
      {'limits.conf':
          [
              ['*', '-', 'nproc', '2048'],
              ['oracle', 'soft', 'nproc', '4096'],
              ['oracle', 'hard', 'nproc', '65536'],
              ['user', '-', 'nproc', '12345']
          ]
      }
    """
    result = {}
    cfg_file = os.path.basename(context.path)
    if cfg_file.strip():
        nproc_lines = []
        for line in context.content:
            line = line.strip()
            if line.startswith('#'):
                continue
            if line and 'nproc' in line:
                line = line.split('#')[0].split()
                nproc_lines.append(line)
        result[cfg_file] = nproc_lines
    return result
