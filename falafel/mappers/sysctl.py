from .. import Mapper, mapper


@mapper('sysctl')
class Sysctl(Mapper):

    def parse_content(self, content):
        r = {}
        for line in content:
            if "=" not in line:
                continue

            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip()
            r[k] = v
        self.data = r


@mapper('sysctl')
def runtime(context):
    """Deprecated, do not use."""
    return Sysctl(context).data
