import os

__all__ = ("verify", "PlaybookValidationError")


class PlaybookValidationError(Exception):
    """
    Exception raised when playbook validation fails

    Attributes:
        playbook -- stringified playbook yaml from stdin
        message -- explanation of why validation failed
    """

    def __init__(self, message="PLAYBOOK VALIDATION FAILED"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


def verify(unverified_playbook):
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
