import sys
import oyaml as yaml

from insights.client.apps.ansible.playbook_verifier import verify


def read_playbook():
    """
    Read in the stringified playbook yaml from stdin
    """
    unverified_playbook = ''
    for line in sys.stdin:
        unverified_playbook += line

    return unverified_playbook


unverified_playbook = read_playbook()
unverified_playbook = yaml.load(unverified_playbook)

try:
    verified_playbook = verify(unverified_playbook, checkVersion=False)
except Exception as e:
    sys.stderr.write(e.message)
    sys.exit(1)

print(verified_playbook)
