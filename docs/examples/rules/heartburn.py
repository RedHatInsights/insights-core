from insights.parsers.installed_rpms import InstalledRpms
from insights.parsers.lsof import Lsof
from insights.parsers.netstat import Netstat
from insights import condition, rule, make_response


@condition(InstalledRpms)
def is_library_installed(installed_rpms):
    # If not installed, returns False. Therefore not applicable
    return 'shared-library-1.0.0' in installed_rpms

Lsof.collect_keys('libshared_procs', NAME='usr/lib64/libshared.so.1')


@condition(Lsof)
def in_use_processes(lsof):
    pids = []
    for p in lsof.libshared_procs:
        pids.append(p['PID'])
    return pids


@condition(Netstat)
def listening_processes(netstat):
    return netstat.listening_pid.keys()


@rule(is_library_installed, in_use_processes, listening_processes)
def heartburn(pkg, in_use, listening):
    if pkg and in_use and listening:
        # get the set of processes that are using the library and listening
        vulnerable_processes = set(in_use) & set(listening)

        if vulnerable_processes:
            return make_response("YOU_HAVE_HEARTBURN",
                                 listening_pids=vulnerable_processes)
