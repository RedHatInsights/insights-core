from .. import Mapper, mapper


@mapper("current_clocksource")
class CurrentClockSource(Mapper):

    def parse_content(self, content):
        self.data = list(content)[0]

    @property
    def is_kvm(self):
        return 'kvm-clock' in self.data

    @property
    def is_tsc(self):
        return 'tsc' in self.data

    @property
    def is_vmi_timer(self):
        return 'vmi-timer' in self.data
