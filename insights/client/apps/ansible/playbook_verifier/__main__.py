import os
import sys
from insights.client.constants import InsightsConstants as constants
from insights.client.apps.ansible.playbook_verifier import verify, loadPlaybookYaml


def read_playbook():
    """
    Read in the stringified playbook yaml from stdin
    """
    unverified_playbook = ''
    for line in sys.stdin:
        unverified_playbook += line

    return unverified_playbook


playbook = read_playbook()
playbook_yaml = loadPlaybookYaml(playbook)
skipVerify = False

if (os.environ.get('SKIP_VERIFY')):
    skipVerify = True

try:
    verified_playbook = verify(playbook_yaml, skipVerify)
except Exception as e:
    sys.stderr.write(e.message)
    sys.exit(constants.sig_kill_bad)

print(playbook)
