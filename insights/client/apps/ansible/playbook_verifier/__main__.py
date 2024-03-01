import os
import sys
from insights.client.constants import InsightsConstants as constants
from insights.client.apps.ansible.playbook_verifier import verify, load_playbook_yaml, PlaybookVerificationError

skipVerify = False


def read_playbook():
    """
    Read in the stringified playbook yaml from stdin
    """
    unverified_playbook = ''
    for line in sys.stdin:
        unverified_playbook += line

    return unverified_playbook


if os.environ.get('SKIP_VERIFY'):
    skipVerify = True

try:
    playbook = read_playbook()
    playbook_yaml = load_playbook_yaml(playbook)
    verified_playbook = verify(playbook_yaml, skipVerify)
except PlaybookVerificationError as err:
    sys.stderr.write(err.message)
    sys.exit(constants.sig_kill_bad)

print(playbook)
