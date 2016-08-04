from falafel.core.plugins import mapper
from falafel.core import MapperOutput, computed


def parse(data):
    product, _, version_name = [v.strip() for v in data.partition("release")]
    version, code_name = [v.strip() for v in version_name.split(None, 1)]
    return {
        "product": product,
        "version": version,
        "code_name": code_name.strip("()")
    }


class RedhatRelease(MapperOutput):

    def __init__(self, data):
        self.parsed = parse(data)
        super(RedhatRelease, self).__init__(data)

    @computed
    def major(self):
        return int(self.parsed["version"].split(".")[0])

    @computed
    def minor(self):
        s = self.parsed["version"].split(".")
        if len(s) > 1:
            return int(s[1])

    @computed
    def version(self):
        return float(self.parsed["version"])

    @computed
    def is_rhel(self):
        return "Red Hat Enterprise Linux" in self.parsed["product"]

    @computed
    def product(self):
        return self.parsed["product"]


@mapper("redhat-release")
def redhat_release(context):
    if len(context.content) == 1 and len(context.content[0]) > 0:
        return RedhatRelease(context.content[0])
