import json

from insights.core.spec_factory import DatasourceProvider
from insights.specs.datasources import yum_updates
from mock.mock import MagicMock, patch


# Verify that the yum_updates broker correctly executes.
def test_yum_updates_runs_correctly():
    expected_json = json.dumps({
            "releasever": "8",
            "basearch": "x86_64",
            "update_list": {
                "NetworkManager-1:1.22.8-4.el8.x86_64": {
                    "available_updates": [
                        {
                            "package": "NetworkManager-1:1.22.8-5.el8_2.x86_64",
                            "repository": "rhel-8-for-x86_64-baseos-rpms",
                            "basearch": "x86_64",
                            "releasever": "8",
                            "erratum": "RHSA-2020:3011"
                        }
                    ]
                }
            },
            "metadata_time": "2021-01-01T09:39:45Z"
    })
    # setup dnf mock
    with patch("insights.specs.datasources.yum_updates.UpdatesManager", yum_updates.DnfManager):
        yum_updates.dnf = MagicMock()
        yum_updates.hawkey = MagicMock()
        yum_updates.dnf.VERSION = "4.7.0"
        yum_updates.dnf.rpm.detect_releasever.return_value = "8"
        yum_updates.dnf.rpm.basearch.return_value = "x86_64"
        repo = MagicMock()
        repo._repo.getTimestamp.return_value = 1609493985
        yum_updates.dnf.base.Base().repos.iter_enabled.return_value = [repo]
        pkg = MagicMock(epoch=1, version="1.22.8", release="4.el8", arch="x86_64")
        pkg.name = "NetworkManager"
        yum_updates.dnf.base.Base().sack.query().installed().run.return_value = [pkg]
        update = MagicMock(epoch=1, version="1.22.8", release="5.el8_2", arch="x86_64",
                    reponame="rhel-8-for-x86_64-baseos-rpms", basearch="x86_64", releasever="8")
        update.name = "NetworkManager"
        update.get_advisories.return_value = [MagicMock(id="RHSA-2020:3011")]
        yum_updates.dnf.base.Base().sack.query().filter.return_value = [update]

        result = yum_updates.yum_updates({})
        assert result is not None
        assert isinstance(result, DatasourceProvider)
        assert expected_json == ''.join(result.content)
