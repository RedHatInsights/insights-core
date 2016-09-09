import yaml
from falafel.core.plugins import mapper
from falafel.core import MapperOutput


@mapper('cobbler_settings')
class CobblerSettings(MapperOutput):

    @staticmethod
    def parse_content(content):
        """
        Return a dict that is parsed from the YAML settings
        - keys are the row header
        - values are the option after the ":".
        ---Result---
        {'kernel_options':
            {'ksdevice':'bootif', 'lang': ' ', 'text':'~'}
        }
        ---Sample---
        # kernel options that should be present in every cobbler installation.
        # kernel options can also be applied at the distro/profile/system
        # level.
        kernel_options:
            ksdevice: bootif
            lang: ' '
            text: ~
        """

        # Revert the list to a stream string
        cob_set_dict = yaml.load('\n'.join(content))
        return cob_set_dict
