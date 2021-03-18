from insights.parsers.cpuinfo import CpuInfo
from insights.parsr.query import from_dict, Result

from . import queryview


@queryview(CpuInfo)
def cpuinfo(cpus):
    res = (from_dict(cpus.data, src=cpus),)
    return Result(children=res)
