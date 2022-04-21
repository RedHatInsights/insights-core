"""
For Testing Only
"""


def rpm_commands(num):
    try:
        import rpm
        success = True
        print("Successfully imported rpm module")
    except ImportError:
        print("Unable to import rpm module")
        success = False

    return num + num, success
