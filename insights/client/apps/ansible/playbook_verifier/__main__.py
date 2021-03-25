import sys
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

try:
    verified_playbook = verify(playbook_yaml, checkVersion=False)
except Exception as e:
    sys.stderr.write(e.message)
    sys.exit(1)

print(playbook)
