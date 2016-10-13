from .. import Mapper, mapper


@mapper("redhat-release")
class RedhatRelease(Mapper):

    def parse_content(self, content):
        assert len(content) == 1
        self.raw = content[0]
        product, _, version_name = [v.strip() for v in content[0].partition("release")]
        version, code_name = [v.strip() for v in version_name.split(None, 1)]
        self.parsed = {
            "product": product,
            "version": version,
            "code_name": code_name.strip("()")
        }

    @property
    def major(self):
        return int(self.parsed["version"].split(".")[0])

    @property
    def minor(self):
        s = self.parsed["version"].split(".")
        if len(s) > 1:
            return int(s[1])

    @property
    def version(self):
        return self.parsed["version"]

    @property
    def is_rhel(self):
        return "Red Hat Enterprise Linux" in self.parsed["product"]

    @property
    def product(self):
        return self.parsed["product"]

    @property
    def is_hypervisor(self):
        return "Hypervisor" in self.parsed["product"]
