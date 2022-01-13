"""
Custom datasources for cloud initialization information
"""
import json
import yaml

from insights.core.context import HostContext
from insights.core.dr import SkipComponent
from insights.core.plugins import datasource
from insights.core.filters import get_filters
from insights.core.spec_factory import DatasourceProvider, simple_file
from insights.specs import Specs


class LocalSpecs(Specs):
    """ Local specs used only by cloud_init datasources """

    cloud_cfg_input = simple_file("/etc/cloud/cloud.cfg")
    """ Returns the contents of the file ``/etc/cloud/cloud.cfg`` """


@datasource(LocalSpecs.cloud_cfg_input, HostContext)
def cloud_cfg(broker):
    """
    This datasource provides configuration collected from ``/etc/cloud/cloud.cfg``.

    Typical content of ``/etc/cloud/cloud.cfg`` file is::

        #cloud-config
        users:
          - name: demo
            ssh-authorized-keys:
              - key_one
              - key_two
            passwd: $6$j212wezy$7H/1LT4f9/N3wpgNunhsIqtMj62OKiS3nyNwuizouQc3u7MbYCarYeAHWYPYb2FT.lbioDm2RrkJPb9BZMN1O/

        ssh_deletekeys: 1

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

    Sample output in JSON format::

        {
          "ssh_deletekeys": 1,
          "network": {
            "version": 1,
            "config": [
              {
                "type": "physical",
                "name": "eth0",
                "subnets": [
                  {
                    "type": "dhcp"
                  },
                  {
                    "type": "dhcp6"
                  }
                ]
              }
            ]
          },
          "debug": {
            "output": "/var/log/cloud-init-debug.log",
            "verbose": true
          }
        }

    Returns:
        str: JSON string after removing the sensitive information.

    Raises:
        SkipComponent: When the path does not exist or any exception occurs.
    """
    relative_path = '/etc/cloud/cloud.cfg'
    try:
        filters = get_filters(Specs.cloud_cfg)
        content = broker[LocalSpecs.cloud_cfg_input].content
        if content and filters:
            result = dict()
            content = yaml.load('\n'.join(content), Loader=yaml.SafeLoader)
            if isinstance(content, dict):
                # remove sensitive data
                content.pop('users', None)
                content.pop('system_info', None)
                # apply filters
                for item in filters:
                    if item in content:
                        result[item] = content[item]

                if result:
                    result = dict(sorted(result.items(), key=lambda x: x[0]))
                    return DatasourceProvider(content=json.dumps(result), relative_path=relative_path)
            raise SkipComponent("Invalid YAML format")
    except Exception as e:
        raise SkipComponent("Unexpected exception:{e}".format(e=str(e)))
    raise SkipComponent
