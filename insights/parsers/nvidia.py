"""
NVIDIA Related Information
==========================

NvidiaSmiL - command ``/usr/bin/nvidia-smi -L``
------------------------------------------------
"""

from insights.core import Parser
from insights.core.exceptions import ParseException, SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.nvidia_smi_l)
class NvidiaSmiL(Parser, list):
    """
    Prase for output of command `/usr/bin/nvidia-smi -L`. This command lists
    each of the NVIDIA GPUs in the system, along with their UUIDs.

    The GPU info shown in each line will be parsed as follows::

        model (string):   The gpu model
        uuid (string):    The gpu uuid

    Raises:
        ParseException: When run into unparsable gpu line
        SkipComponent: When content is empty or no parsable content

    Sample Content::

        GPU 0: NVIDIA A100-PCIE-40GB (UUID: GPU-63110aaa-3561-c8f5-e125-4ab40bbcf838)
        GPU 1: NVIDIA A100-PCIE-40GB (UUID: GPU-c9bd25dc-c0c4-3ab6-8f7f-3ad16d6bde4a)

    Examples::
        >>> gpus.gpu_count
        2
        >>> "NVIDIA A100-PCIE-40GB" in gpus.gpu_models
        True
        >>> gpus[0]
        {'model': 'NVIDIA A100-PCIE-40GB', 'uuid': 'GPU-63110aaa-3561-c8f5-e125-4ab40bbcf838'}
    """

    def parse_content(self, content):
        if not content:
            raise SkipComponent("Empty content")

        _gpu_index_validator = 0

        for line in content:
            if line.startswith("GPU ") and "(UUID: " in line and line.endswith(')'):
                spl_line = line.split("(UUID: ")
                spl_left = spl_line[0].split(': ')
                if not len(spl_left) == 2:
                    raise ParseException("Unparsable GPU model: %s" % line)

                gpu_id = spl_left[0].split()[-1]
                if not (gpu_id.isdigit() and int(gpu_id) == _gpu_index_validator):
                    raise ParseException("Unparsable GPU id: %s" % line)
                _gpu_index_validator += 1

                gpu_model = spl_left[-1].strip()
                gpu_uuid = spl_line[-1].strip(') ')
                if not (gpu_model and gpu_uuid):
                    raise ParseException("Unparsable GPU line: %s" % line)

                self.append({
                    "model": gpu_model,
                    "uuid": gpu_uuid,
                })

        if len(self) < 1:
            raise ParseException("Empty GPU info after parse: %s" % content)

    @property
    def gpu_count(self):
        """
        str: Returns the GPU count
        """
        return len(self)

    @property
    def gpu_models(self):
        """
        str: Returns the GPUs model set
        """
        return set([gpu["model"] for gpu in self])
