"""
Interrupts
==========

Provides parsing for contents of ``/proc/interrupts``.
"""
from .. import Mapper, mapper
from ..mappers import ParseException


@mapper("interrupts")
class Interrupts(Mapper):
    """Parse contents of ``/proc/interrupts``.

    The contents of a typical ``interrupts`` file looks like::

                 CPU0       CPU1       CPU2       CPU3
        0:         37          0          0          0  IR-IO-APIC   2-edge      timer
        1:          3          2          1          0  IR-IO-APIC   1-edge      i8042
        8:          0          1          0          0  IR-IO-APIC   8-edge      rtc0
        9:      11107       2316       4040       1356  IR-IO-APIC   9-fasteoi   acpi
      NMI:        210         92        179         96   Non-maskable interrupts
      LOC:    7561411    2488524    6527767    2448192   Local timer interrupts
      ERR:          0
      MIS:          0

    Parameters
    ----------

    content : list
        Lines in list represent content of ``/proc/interrupts``.

    Returns
    -------

    dict
        A list of dictionaries containing information for each row of the
        content.  Blank values in content will not be present in the
        dictionary.

    .. code-block:: python

        [
            { 'irq': '0',
              'num_cpus': 4,
              'counts': [37, 0, 0, 0],
              'type_device': 'IR-IO-APIC   2-edge      timer'},
            # Other rows present in output
            { 'irq': 'MIS',
              'num_cpus': 4,
              'counts': [0, ]}
        ]

    """

    def get(self, filter):
        """Returns list of records containing ``filter`` in the type/device field."""
        return [i for i in self.data if 'type_device' in i and filter in i['type_device']]

    def __iter__(self):
        return iter(self.data)

    @property
    def num_cpus(self):
        """Total number of CPUs."""
        return int(self.data[0]['num_cpus'])

    def parse_content(self, content):
        self.data = []
        try:
            cpu_names = content[0].split()
        except:
            raise ParseException("Invalid first line of content for /proc/interrupts")
        if len(cpu_names) < 1 or not cpu_names[0].startswith("CPU"):
            raise ParseException("Unable to determine number of CPUs in /proc/interrupts")
        for line in content[1:]:
            parts = line.split(None, len(cpu_names) + 1)
            one_int = {'irq': parts[0].replace(":", "")}
            one_int['num_cpus'] = len(cpu_names)
            one_int['counts'] = []
            if len(parts) == len(cpu_names) + 2:
                one_int['type_device'] = parts[-1]
                for part, cpu in zip(parts[1:-1], cpu_names):
                    one_int['counts'].append(int(part))
            else:
                for part, cpu in zip(parts[1:], cpu_names):
                    one_int['counts'].append(int(part))
            self.data.append(one_int)
        if len(self.data) < 1:
            raise ParseException("No information in /proc/interrupts")
