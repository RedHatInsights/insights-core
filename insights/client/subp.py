#!/usr/bin/python
import subprocess


def call(cmd, keep_rc=True, env=None):
    """
    Run a command as a subprocess.
    Return a triple of return code, standard out, standard err.
    """
    cmd = shlex.split(cmd)
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            env=env)
    stdout, stderr = proc.communicate()
    if keep_rc:
        return (proc.returncode, stdout.decode('utf-8', 'ignore'))
    else:
        return stdout.decode('utf-8', 'ignore')
