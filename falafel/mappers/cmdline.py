from falafel.core.plugins import mapper
from falafel.core import MapperOutput


@mapper('cmdline')
class CmdLine(MapperOutput):

    @staticmethod
    def parse_content(content):
        """
        Content format is like "ro root=/dev/mapper/vg_rootvg-lv_root"

        If a property doesn't have "=" as spliter, set itself as key and its corresponding value is None.
        If a property contains "=", the corresponding values are stored in a list.
        For special cmdlines that include two "=", just like: root=LABEL=/1
        "root" will be the key and "LABEL=/1" will be the value in the returned list.
        Note: Some parameters(the returned keys) might be still effective even if there is '#' before it. For example: '#rhgb'.
            Add necessary checking conditions when using this shared mapper in reducer.
        """
        cmdline_properties = {}
        line = content[0]
        for el in line.strip().split():
            if not el:
                continue
            elif "=" not in el:
                cmdline_properties[el] = None
            else:
                (key, value) = el.split("=", 1)
                cmdline_properties.setdefault(key, []).append(value)
        return cmdline_properties
