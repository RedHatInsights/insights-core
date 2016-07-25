from falafel.core.plugins import mapper
from falafel.core import MapperOutput, computed

eus = [
    '5.0.z',
    '5.1.z',
    '5.2.z',
    '5.3.ll',
    '5.3.z',
    '5.4.z',
    '5.6.ll',
    '5.6.z',
    '5.9.ll',
    '5.9.z'
    '6.0.z',
    '6.1.z',
    '6.2.aus',
    '6.2.z',
    '6.3.z',
    '6.4.aus',
    '6.4.z',
    '6.5.aus',
    '6.5.z',
    '6.6.aus',
    '6.6.z',
    '6.7.z'
]


def _parse(lines):
    found_start = False
    for line in lines:

        if line.startswith("repolist:"):
            return

        if found_start:
            id_, right = line.split(None, 1)
            try:
                name, status = right.rsplit(None, 1)
            except ValueError:
                status = right
                name = ""

            yield {"id": id_.strip(), "name": name.strip(), "status": status.strip()}

        if not found_start:
            found_start = line.startswith("repo id")


@mapper("yum-repolist")
def repo_list(context):
    return YumRepoList(list(_parse(context.content)))


class YumRepoList(MapperOutput):

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        if isinstance(idx, int):
            return self.data[idx]
        else:
            return super(YumRepoList, self).__getitem__(idx)

    @computed
    def eus(self):
        euses = []
        for repo in [r["id"] for r in self.data]:
            if repo.startswith("rhel-") and "server-" in repo:
                _, eus_version = repo.split("server-", 1)
                if eus_version in eus:
                    euses.append(eus_version)
        return euses
