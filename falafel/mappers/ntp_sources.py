from .. import MapperOutput, mapper


@mapper('chronyc_sources')
class ChronycSources(MapperOutput):

    @staticmethod
    def parse_content(content):
        """
        Get source, mode and state for chrony
        """
        source_list = []
        for row in content[3:]:
            if row.strip():
                values = row.split(" ", 2)
                source_list.append({"source": values[1], "mode": values[0][0], "state": values[0][1]})
        return source_list if source_list else None


@mapper('ntpq_pn')
class NtpqPn(MapperOutput):

    @staticmethod
    def parse_content(content):
        """
        Get source, flag for ntp
        """
        source_list = []
        for row in content[2:]:
            if row.strip():
                values = row.split(" ", 2)
                source_list.append({"source": values[0][1:], "flag": values[0][0]})
        return source_list if source_list else None
