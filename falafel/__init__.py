import os
from .core import LogFileOutput, MapperOutput, computed  # noqa: F401
from .core.plugins import mapper, reducer, make_response, make_metadata  # noqa: F401
from .mappers import get_active_lines  # noqa: F401
from .util import defaults, parse_table  # noqa: F401

__here__ = os.path.dirname(os.path.abspath(__file__))
VERSION = "1.9.0"
NAME = "falafel"

with open(os.path.join(__here__, "RELEASE")) as f:
    RELEASE = f.read().strip()

with open(os.path.join(__here__, "COMMIT")) as f:
    COMMIT = f.read().strip()


def get_nvr():
    return "{0}-{1}-{2}".format(NAME, VERSION, RELEASE)
