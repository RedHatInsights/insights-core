from insights.core.dr import SkipComponent
from insights import rule
from insights.parsers.redhat_release import RedhatRelease
from insights.core.plugins import make_none


@rule(RedhatRelease)
def report_none(u):
    return


@rule(RedhatRelease)
def report_make_none(u):
    return make_none()


@rule(RedhatRelease)
def report_skip_exception(u):
    raise SkipComponent()


if __name__ == "__main__":
    from insights import run

    broker = run([report_none, report_make_none], print_summary=True)
