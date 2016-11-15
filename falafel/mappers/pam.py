"""
pam - Files pam conf
====================

This module provides parsing for PAM configuration files.
``PamConf`` is a mapper for ``/etc/pam.conf`` files. Sample input is provided
in the examples.

Examples:
    >>> pam_input_data = '''
    ... # Comment line
    ... vsftpd      auth        required    pam_securetty.so
    ... vsftpd      auth        required    pam_unix.so nullok
    ... vsftpd      auth        required    pam_nologin.so
    ... vsftpd      account     required    pam_unix.so
    ... other       password    required    pam_cracklib.so retry=3
    ... other       password    required    pam_unix.so shadow nullok use_authtok
    ... servicex    session     required    pam_unix.so
    ... '''.strip()
    >>> from falafel.tests import context_wrap
    >>> pam_conf = PamConf(context_wrap(pam_input_data, path='/etc/pam.conf'))
    >>> len(pam_conf)
    7
    >>> pam_conf[0].service
    'vsftpd'
    >>> pam_conf[0].interface
    'auth'
    >>> pam_conf[0].control_flags
    [(flag='required', value=None)]
    >>> pam_conf[0].module_name
    'pam_security.so'
    >>> pam_conf[0].module_args
    None
    >>> pam_conf.file_path
    '/etc/pam.conf'

``PamDConf`` is a base class for the creation of mappers for ``/etc/pam.d``
service specific configuration files. Sample input is provided in the examples.

Examples:
    >>> pam_input_data = '''
    ... # Comment line
    ... vsftpd      auth        required    pam_securetty.so
    ... vsftpd      auth        required    pam_unix.so nullok
    ... vsftpd      auth        required    pam_nologin.so
    ... vsftpd      account     required    pam_unix.so
    ... other       password    required    pam_cracklib.so retry=3
    ... other       password    required    pam_unix.so shadow nullok use_authtok
    ... servicex    session     required    pam_unix.so
    ... '''.strip()
    >>> from falafel.tests import context_wrap
    >>> pam_conf = PamConf(context_wrap(pam_input_data, path='/etc/pam.conf'))
    >>> len(pam_conf)
    7
    >>> pam_conf[0].service
    'vsftpd'
    >>> pam_conf[0].interface
    'auth'
    >>> pam_conf[0].control_flags
    [(flag='required', value=None)]
    >>> pam_conf[0].module_name
    'pam_security.so'
    >>> pam_conf[0].module_args
    None
    >>> pam_conf.file_path
    '/etc/pam.conf'

References:
    http://www.linux-pam.org/Linux-PAM-html/Linux-PAM_SAG.html
"""

from collections import namedtuple
from .. import Mapper, get_active_lines, mapper
from ..mappers import unsplit_lines


class PamConfEntry(object):
    """Contains information from one pam conf line.

    Parses a single line of either a ``/etc/pam.conf`` file or
    a service specific ``/etc/pam.d`` conf file. The difference
    is that for ``/etc/pam.conf``, the service name is the first
    column of the input line. If a service specific conf file
    then the service name is not present in the line and must
    be provided as the ``service`` parameter as well as setting
    the ``pamd_conf`` to True.

    Parameters:
        line (str): One line of the pam conf info.
        pamd_config (boolean): If this is set to False then
            ``line`` will be parsed as a line from the ``etc/pam.conf`` file,
            if ``True`` then the line will be parsed as a line from a service
            specific ``etc/pam.d/`` conf file. Default is ``True``.
        service (str): If ``pamd_conf`` is ``True`` then the name of the service file
            must be provided since it is not present in `line`.

    Examples:
        >>> pam_conf_line = 'vsftpd      auth        requisite   pam_unix.so nullok'
        >>> entry = PamConfEntry(pam_conf_line)
        >>> entry.service
        'vsftpd'
        >>> entry.control_flags[0].flag
        'requisite'
        >>> entry.module_args
        'nullok'
        >>> pamd_conf_line = '''
        ... auth        [success=2 default=ok]  pam_debug.so auth=perm_denied cred=success
        ... '''.strip()
        >>> entry = PamConfEntry(pamd_conf_line, pamd_conf=True, service='vsftpd')
        >>> entry.service
        'vsftpd'
        >>> entry.control_flags
        [(flag='success', value='2'), (flag='default', value='ok')]
        >>> entry.module_args
        'auth=perm_denied cred=success'

    Raises:
        ValueError: If `pamd_conf` is True and `service` name is not provided,
            or if the line doesn't contain any module information.
    """

    ControlFlag = namedtuple('ControlFlag', 'flag, value')

    def __init__(self, line, pamd_conf=False, service=None):
        # If not pam.d file then service is first column in
        # line for pam.conf file. Otherwise service must be parameter.
        self._service = service
        if not pamd_conf:
            self._service, rest = line.split(None, 1)
            line = rest
        elif service is None:
            raise ValueError('Service name must be provided for pam.d conf file')

        self._mod_if, rest = line.split(None, 1)
        self._mod_if = self._mod_if.lower()
        if not rest[0] == '[':
            ctrl_flag, mod_info = rest.split(None, 1)
            self._ctrl_flags = [self.ControlFlag(ctrl_flag, None)]
        else:
            ctrl_flag, mod_info = rest[1:].split(']', 1)
            self._ctrl_flags = []
            for flag_val in ctrl_flag.split():
                flag, _, val = flag_val.partition('=')
                self._ctrl_flags.append(self.ControlFlag(flag, val))

        mod_info = mod_info.split(None, 1)
        if len(mod_info) >= 1:
            self._mod_name = mod_info[0]
            self._mod_args = mod_info[1] if len(mod_info) > 1 else None
        else:
            raise ValueError('Missing module name from pam conf line: {}'.format(line))

    @property
    def service(self):
        """str: name of the service."""
        return self._service

    @property
    def interface(self):
        """str: name of the module interface."""
        return self._mod_if

    @property
    def control_flags(self):
        """list: List of ControlFlag(flag, value) tuples."""
        return self._ctrl_flags

    @property
    def module_name(self):
        """str: Name of the module."""
        return self._mod_name

    @property
    def module_args(self):
        """str: Module arguments."""
        return self._mod_args


@mapper('pam.conf')
class PamConf(Mapper):
    """Base class for parsing pam config file ``/etc/pam.conf``.

    This class provides parsing for the ``pam.conf`` configuration
    file. Each line of the file is parsed into ``PamConfEntry`` class
    object containing the columns of the configuration file.  Each
    parsed entry is stored in a list in the order it appears in the
    ``pam.conf`` file. The format of the input data is::

        service_name    module_interface    control_flag    module_name module_arguments

    Sample input data is provided in the examples above.

    Attributes:
        data (list): List of PamConfEntry objects for each line in the conf file.
    """
    def parse_content(self, content):
        self.data = []
        for line in get_active_lines(unsplit_lines(content)):
            self.data.append(PamConfEntry(line))

    def __iter__(self):
        for entry in self.data:
            yield entry
        return

    def __getitem__(self, ndx):
        return self.data[ndx]

    def __len__(self):
        return len(self.data)


class PamDConf(Mapper):
    """Base class for parsing files in ``/etc/pam.d``

    Derive from this class for mappers of files in
    the ``/etc/pam.d`` directory.  Parses each line of the conf
    file into a list of PamConfEntry.  Configuration file format is::

        module_interface    control_flag    module_name module_arguments

    Sample input is provided in the examples above.

    Attributes:
        data (list): List containing a PamConfEntry object for each line of
            the conf file in the same order as lines appear in the file.
    """
    def parse_content(self, content):
        self.data = []
        for line in get_active_lines(unsplit_lines(content)):
            self.data.append(PamConfEntry(line, pamd_conf=True, service=self.file_name))

    def __iter__(self):
        for entry in self.data:
            yield entry
        return

    def __getitem__(self, ndx):
        return self.data[ndx]

    def __len__(self):
        return len(self.data)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
