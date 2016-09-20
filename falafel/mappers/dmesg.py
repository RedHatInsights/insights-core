from .. import LogFileOutput, mapper


class DmesgLineList(LogFileOutput):
    def has_startswith(self, prefix):
        """
        Returns a boolean array which is `True` where there is one line in
        dmesg starts with `prefix`, otherwise `False`.
        """
        return any(line.startswith(prefix) for line in self.lines)


@mapper('dmesg')
def dmesg(context):
    """
    Returns an object of DmesgLineList
    """
    return DmesgLineList(context.content, path=context.path)


@mapper('vmcore-dmesg')
def vmcore_dmesg(context):
    """
    Returns an object of DmesgLineList
    """
    return DmesgLineList(context.content, path=context.path)
