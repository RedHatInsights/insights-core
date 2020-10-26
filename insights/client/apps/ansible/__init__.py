
__all__ = ("verify_playbook")


def verify_playbook(unverified_playbook: str) -> str:
    """
    Verify the signed playbook.

    Input: stringified "broken" unverified playbook
    Output: stringified "verified" playbook
    Error: exception
    """
    # Skeleton implementation ... "bless" the incoming playbook
    verified_playbook = unverified_playbook
    return verified_playbook

if __name__ == "__main__":
    # Read playbook from stdin
    # Pass playbook to verify_playbook method
    # Output verified playbook
    # On error...set return code to non-zero, output error message to stderr
    print("Verifying playbook")
