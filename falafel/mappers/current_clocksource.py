from falafel.core.plugins import mapper
from falafel.core import MapperOutput, computed


@mapper("current_clocksource")
class CurrentClockSource(MapperOutput):

    @staticmethod
    def parse_content(content):
        return list(content)[0]

    @computed
    def is_kvm(self):
        return 'kvm-clock' in self.data

    @computed
    def is_tsc(self):
        return 'tsc' in self.data

    @computed
    def is_vmi_timer(self):
        return 'vmi-timer' in self.data
