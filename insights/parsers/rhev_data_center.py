"""
rhev_data_center - datasource ``rhev_data_center``
==================================================
"""
import json
from insights import Parser, parser
from insights.specs import Specs


@parser(Specs.rhev_data_center)
class RhevDataCenter(Parser):
    """Walk through the `/rhev/data-center` directory of RHEV host and return the
    full path of files not having correct file ownership i.e vdsm:kvm. See the
    `rhev_data_center` Datasource for more info.

    Attributes:
        data(list): A list of the parsed output returned by `rhev_data_center` Datasource.

    The following are available in ``data``:

        * ``name``  - file owner
        * ``group`` - file group
        * ``path``  - full path of a file

    Examples:
        >>> assert len(rhev_dc.data) == 3
        >>> assert len(rhev_dc.bad_image_ownership) == 1
        >>> assert rhev_dc.bad_image_ownership[0]['path'] == '/rhev/data-center/mnt/host1.example.com:_nfsshare_data/a384bf5d-db92-421e-926d-bfb99a6b4b28/images/b7d6cc07-d1f1-44b3-b3c0-7067ec7056a3/4d6e5dea-995f-4a4e-b487-0f70361f6137'
        >>> assert rhev_dc.bad_image_ownership[0]['name'] == 'root'
        >>> assert rhev_dc.bad_image_ownership[0]['group'] == 'root'
    """
    def parse_content(self, content):
        self.data = json.loads(''.join(content))

    @property
    def bad_image_ownership(self):
        """Returns full path of RHEV VM images in the Data Center not having correct file ownership.

        Returns:
            (list): [{'name': 'root', 'group': 'root', 'path': '/rhev/data-center/mnt/example.com:_nfsshare_data/a384bf5d/images/b7d6cc07/4d6e5dea'}]
        """
        bad_ownership = []
        for each in self.data:
            if '/images/' in each['path']:
                bad_ownership.append(each)
        return bad_ownership
