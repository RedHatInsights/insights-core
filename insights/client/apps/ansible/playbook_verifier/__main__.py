import os
import sys
from insights.client.constants import InsightsConstants as constants
from insights.client.apps.ansible.playbook_verifier import verify, load_playbook_yaml, PlaybookVerificationError


def read_playbook():
    """Read in the playbook from stdin."""
    unverified_playbook = ""
    for line in sys.stdin:
        unverified_playbook += line
    return unverified_playbook


try:
    raw_playbook = read_playbook()
    if os.environ.get("SKIP_VERIFY"):
        print(raw_playbook)
        exit(0)

    playbook = load_playbook_yaml(raw_playbook)[0]  # type: dict
    verified_playbook = verify(playbook)  # type: dict
except PlaybookVerificationError as err:
    sys.stderr.write(err.message)
    sys.exit(constants.sig_kill_bad)

print(raw_playbook)
