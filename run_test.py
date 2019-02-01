from insights import run
from insights.parsers.rhev_data_center import RhevDataCenter
from insights import make_fail, rule


@rule(RhevDataCenter)
def report(rhev):
    return make_fail("ERROR", files=rhev.data)


if __name__ == "__main__":
    broker = run(report, print_summary=True)
    print('finished')
