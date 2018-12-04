from insights.core.plugins import make_response, rule, condition
from insights.parsers.installed_rpms import InstalledRpms

ERROR_KEY = 'RPMDB_CORRUPT'


@rule(InstalledRpms)
def report(rpms):
    if rpms.corrupt:
        for line in rpms.errors:
            if 'rpmdbNextIterator:' in line.split():
                return make_response(ERROR_KEY, rpmdb_error=line)
