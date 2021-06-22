"""
Custom datasources for cloud initialization information
"""
import json
import yaml

from insights.core.context import HostContext
from insights.core.dr import SkipComponent
from insights.core.plugins import datasource
from insights.core.spec_factory import DatasourceProvider, simple_file
from insights.specs import Specs


class LocalSpecs(Specs):
    """ Local specs used only by cloud_init datasources """

    cloud_cfg_input = simple_file("/etc/cloud/cloud.cfg")
    """ Returns the contents of the file ``/etc/cloud/cloud.cfg`` """


@datasource(LocalSpecs.cloud_cfg_input, HostContext)
def cloud_cfg(broker):
    """
    This datasource provides the network configuration information collected
    from ``/etc/cloud/cloud.cfg``.

    Typical content of ``/etc/cloud/cloud.cfg`` file is::

        #cloud-config
        users:
          - name: demo
            ssh-authorized-keys:
              - key_one
              - key_two
            passwd: $6$j212wezy$7H/1LT4f9/N3wpgNunhsIqtMj62OKiS3nyNwuizouQc3u7MbYCarYeAHWYPYb2FT.lbioDm2RrkJPb9BZMN1O/

        network:
            version: 1
            config:
            - type: physical
                name: eth0
                subnets:
                  - type: dhcp
                  - type: dhcp6

        system_info:
            default_user:
            name: user2
            plain_text_passwd: 'someP@assword'
            home: /home/user2

        debug:
            output: /var/log/cloud-init-debug.log
            verbose: true

    Note:
        This datasource may be executed using the following command:

        ``insights cat --no-header cloud_cfg``

    Sample data returned includes only the ``network`` portion of the input file in JSON format::

        {
            "version": 1,
            "config": [
                {
                    "type": "physical",
                    "name": "eth0",
                    "subnets": [
                        {"type": "dhcp"},
                        {"type": "dhcp6"}
                    ]
                }
            ]
        }

    Returns:
        str: JSON string when the ``network`` parameter includes content, else `None` is returned.

    Raises:
        SkipComponent: When the path does not exist or any exception occurs.
    """
    relative_path = '/etc/cloud/cloud.cfg'
    try:
        content = broker[LocalSpecs.cloud_cfg_input].content
        if content:
            content = yaml.load('\n'.join(content), Loader=yaml.SafeLoader)
            network_config = content.get('network', None)
            if network_config:
                return DatasourceProvider(content=json.dumps(network_config), relative_path=relative_path)
    except Exception as e:
        raise SkipComponent("Unexpected exception:{e}".format(e=str(e)))

    raise SkipComponent('No network section in yaml')
