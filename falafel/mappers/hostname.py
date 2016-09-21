from .. import MapperOutput, mapper, computed


class Hostname(MapperOutput):

    @computed
    def fqdn(self):
        return self.data

    @computed
    def hostname(self):
        return self.data.split(".")[0]

    @computed
    def domain(self):
        return ".".join(self.data.split(".")[1:])


@mapper("hostname")
def hostname(context):
    if len(context.content) == 1:
        hostname = context.content[0].strip()
        return Hostname(hostname) if hostname else None
