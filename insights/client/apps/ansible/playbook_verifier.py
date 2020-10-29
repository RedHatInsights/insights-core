import os
import sys
__all__ = ("verify_playbook")

####  PLAYBOOK VALIDATION ERROR MESSAGE ####
class PlaybookValidationError(Exception):
    """
    Exception raised when playbook validation fails

    Attributes:
        playbook -- stringified playbook yaml from stdin
        message -- explanation of why validation failed
    """

    def __init__(self, message = "PLAYBOOK VALIDATION FAILED"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'

def verify(unverified_playbook: str) -> str:
    """
    Verify the signed playbook.

    Input: stringified "broken" unverified playbook
    Output: stringified "verified" playbook
    Error: exception
    """
    # Skeleton implementation ... "bless" the incoming playbook 
    ERROR = os.getenv('ANSIBLE_PLAYBOOK_VERIFIER_THROW_ERROR')
    if ERROR:
        raise PlaybookValidationError()

    verified_playbook = unverified_playbook
    return verified_playbook

def read_playbook() -> str:
    """
    Read in the stringified playbook yaml from stdin
    """
    unverified_playbook = ''
    for line in sys.stdin:
        unverified_playbook += line.rstrip()

    return unverified_playbook

if __name__ == "__main__":
    # Read playbook from stdin
    unverified_playbook = read_playbook()

    # Pass playbook to verify_playbook method
    try:
        verified_playbook = verify(unverified_playbook)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)

    # Output verified playbook
    # On error...set return code to non-zero, output error message to stderr
    print(verified_playbook)
