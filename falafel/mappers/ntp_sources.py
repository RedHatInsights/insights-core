from .. import Mapper, mapper


@mapper('chronyc_sources')
class ChronycSources(Mapper):

    def parse_content(self, content):
        """
        Get source, mode and state for chrony
        """
        self.data = []
        for row in content[3:]:
            if row.strip():
                values = row.split(" ", 2)
                self.data.append({"source": values[1], "mode": values[0][0], "state": values[0][1]})


@mapper('ntpq_leap')
class NtpqLeap(Mapper):

    def parse_content(self, content):
        """
        Sample Input:
            leap=00

        Sample Output:
            {"leap": "00"}
        """
        line = content[0].strip()
        if "=" in line:
            k, v = line.split("=")
            self.data = {k: v}


@mapper('ntpq_pn')
class NtpqPn(Mapper):

    def parse_content(self, content):
        """
        Get source, flag for ntp
        """
        self.data = []
        for row in content[2:]:
            if row.strip():
                values = row.split(" ", 2)
                self.data.append({"source": values[0][1:], "flag": values[0][0]})
