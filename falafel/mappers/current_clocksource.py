from falafel.core.plugins import mapper
from falafel.core import MapperOutput, computed

@mapper("current_clocksource")
class CurrentClockSource(MapperOutput):
    @classmethod
    def parse_context(cls, context):
        """
            Return the current clock source in string
        """
        clksrc = list(context.content)[0]

        return cls(clksrc, context.path)

    @computed
    def is_kvm(self):
        return 'kvm-clock' in self.data

    @computed
    def is_tsc(self):
        return 'tsc' in self.data

    @computed
    def is_vmi_timer(self):
        return 'vmi-timer' in self.data