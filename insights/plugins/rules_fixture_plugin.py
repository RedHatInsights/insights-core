from insights.core.plugins import rule, make_fail, make_pass
from insights.parsers import installed_rpms, uname as uname_mod


@rule(optional=[installed_rpms.InstalledRpms, uname_mod.Uname])
def report(rpms, uname):
    if rpms is not None:
        bash_ver = rpms.get_max('bash')
        if uname is not None:
            return make_pass('PASS', bash_ver=bash_ver.nvr, uname_ver=uname.version)
        else:
            return make_fail('FAIL', bash_ver=bash_ver.nvr, path=rpms.file_path)

    # implicit return None
