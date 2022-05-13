import doctest
from insights.parsers import proc_stat
from insights.parsers.proc_stat import ProcStat
from insights.tests import context_wrap

PROC_STAT = """
cpu  32270961 89036 23647730 1073132344 1140756 0 1522035 18738206 0 0
cpu0 3547155 11248 2563031 135342787 113432 0 199615 2199379 0 0
cpu1 4660934 10954 3248126 132271933 120282 0 279870 2660186 0 0
cpu2 4421035 10729 3306081 132914999 126705 0 194141 2505565 0 0
cpu3 4224551 10633 3139695 133634676 121035 0 181213 2380738 0 0
cpu4 3985452 11151 2946570 134064686 205568 0 165839 2478471 0 0
cpu5 3914912 11396 2896447 134635676 117341 0 164794 2260011 0 0
cpu6 3802544 11418 2817453 134878674 222855 0 182738 2150276 0 0
cpu7 3714375 11503 2730323 135388911 113534 0 153821 2103576 0 0
intr 21359029 22 106 0 0 0 0 3 0 1 0 16 155 357 0 0 671261 0 0 0 0 0 0 0 0 0 0 0 32223 0 4699385 2 0 8 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
ctxt 17852681
btime 1542179825
processes 19212
procs_running 1
procs_blocked 0
softirq 11867930 1 3501158 6 4705528 368244 0 79 2021509 0 1271405
""".strip()


def test_proc_stat():
    proc_stat = ProcStat(context_wrap(PROC_STAT))
    assert proc_stat.btime == '1542179825'
    assert proc_stat.softirq_total == 11867930
    assert proc_stat.cpu_percentage == '6.73%'
    assert proc_stat.btime == '1542179825'
    assert proc_stat.ctxt == 17852681
    assert proc_stat.intr_total == 21359029
    assert proc_stat.processes == 19212
    assert proc_stat.procs_running == 1
    assert proc_stat.procs_blocked == 0


def test_proc_stat_doc_examples():
    env = {
        'proc_stat': ProcStat(
            context_wrap(PROC_STAT))
    }
    failed, total = doctest.testmod(proc_stat, globs=env)
    assert failed == 0
