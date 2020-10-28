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

    def __init__(self, playbook, message = " #### PLAYBOOK VALIDATION FAILED ####: ", code = -1):
        self.playbook = playbook
        self.message = message
        self.code = code
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message} {self.playbook}, error code: {self.code}'

def verify_playbook(unverified_playbook: str) -> str:
    """
    Verify the signed playbook.

    Input: stringified "broken" unverified playbook
    Output: stringified "verified" playbook
    Error: exception
    """
    # Skeleton implementation ... "bless" the incoming playbook 
    ERROR = os.getenv('THROW_ERROR')
    if ERROR:
        raise PlaybookValidationError(unverified_playbook)

    verified_playbook = unverified_playbook
    return verified_playbook

def read_playbook() -> str:
    """
    Read in the stringified playbook yaml from stdin
    """
    unverified_playbook = sys.stdin.readline()
    return unverified_playbook

if __name__ == "__main__":
    # Read playbook from stdin
    unverified_playbook = read_playbook()

    # Pass playbook to verify_playbook method
    try:
        verified_playbook = verify_playbook(unverified_playbook)
    except PlaybookValidationError as e:
        raise e

    # Output verified playbook
    # On error...set return code to non-zero, output error message to stderr
    print("Verified Playbook: ", verified_playbook)
