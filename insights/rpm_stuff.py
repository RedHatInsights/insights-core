"""
For Testing Only
"""


def rpm_commands(num):
    try:
        import rpm
        success = True
        version = rpm.__version__
        print("Successfully imported rpm module")
    except ImportError:
        print("Unable to import rpm module")
        success = False
        version = ""

    return num + num, success, version
