"""
NVIDIA Related Information
==========================

NvidiaSmiL - command ``/usr/bin/nvidia-smi -L``
-----------------------------------------------

NvidiaSmiActiveClocksEventReasons - command ``/usr/bin/nvidia-smi --query-gpu=name,clocks_event_reasons.active --format=csv,noheader``
--------------------------------------------------------------------------------------------------------------------------------------
"""

from insights.core import Parser
from insights.core.exceptions import ParseException, SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs

# Refer to the following doc for the detailed bitmask of active clock event reasons:
# - https://docs.nvidia.com/deploy/nvml-api/group__nvmlClocksEventReasons.html
BITMASK = {
    "none": 0x0000000000000000,
    "gpu_idle": 0x0000000000000001,
    "applications_clocks_setting": 0x0000000000000002,
    "sw_power_cap": 0x0000000000000004,
    "hw_slowdown": 0x0000000000000008,
    "sync_boost": 0x0000000000000010,
    "sw_thermal_slowdown": 0x0000000000000020,
    "hw_thermal_slowdown": 0x0000000000000040,
    "hw_power_brake_slowdown": 0x0000000000000080,
    "display_clock_setting": 0x0000000000000100,
}


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

                self.append(
                    {
                        "model": gpu_model,
                        "uuid": gpu_uuid,
                    }
                )

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


@parser(Specs.nvidia_smi_active_clocks_event_reasons)
class NvidiaSmiActiveClocksEventReasons(Parser, list):
    """
    Parser for the output of command `/usr/bin/nvidia-smi --query-gpu=name,clocks_event_reasons.active --format=csv,noheader`.
    This command lists each of the NVIDIA GPUs in the system, along with their names and bitmasks
    of active clock event reasons.

    Raises:
        ParseException: When run into an unparsable line
        SkipComponent: When content is empty

    Sample Content::
        NVIDIA L4, 0x0000000000000001
        NVIDIA A1, 0x0000000000000000
        NVIDIA H1, 0x0000000000000084

    Examples::
        >>> type(active_clocks_event_reasons)
        <class 'insights.parsers.nvidia.NvidiaSmiActiveClocksEventReasons'>
        >>> len(active_clocks_event_reasons)
        3
        >>> active_clocks_event_reasons[0]['applications_clocks_setting']
        False
        >>> active_clocks_event_reasons[2]['hw_power_brake_slowdown']
        True
        >>> active_clocks_event_reasons[2]['none']
        False
    """

    def parse_content(self, content):
        if not content:
            raise SkipComponent("Empty content.")

        for line in content:
            items = line.split(",")
            if len(items) != 2 or not items[1].strip().startswith("0x"):
                raise ParseException(
                    "Not an expected command output for active clocks event reasons: %s" % line
                )
            bitmask = int(items[1].strip().strip("LL"), 16)

            data = dict(gpu_name=items[0].strip())
            for key, bm in BITMASK.items():
                if key == "none":
                    data[key] = bm | bitmask == bm
                else:
                    data[key] = bm & bitmask == bm
            self.append(data)
