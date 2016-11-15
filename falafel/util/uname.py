from falafel.mappers import uname

import logging

logger = logging.getLogger(__name__)


class Uname(uname.Uname):
    pass


UnameError = uname.UnameError
pad_release = uname.pad_release
parse_uname = uname.parse_uname
rhel_release_map = uname.rhel_release_map
release_to_kernel_map = uname.release_to_kernel_map
