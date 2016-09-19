import os

__here__ = os.path.dirname(os.path.abspath(__file__))
VERSION = "1.9.0"
NAME = "falafel"

with open(os.path.join(__here__, "RELEASE")) as f:
    RELEASE = f.read().strip()

with open(os.path.join(__here__, "COMMIT")) as f:
    COMMIT = f.read().strip()


def get_nvr():
    return "{0}-{1}-{2}".format(NAME, VERSION, RELEASE)
