"""
Pluggable Authentication Module configuration
=============================================

This module provides parsing for PAM configuration files.
``PamConf`` is a parser for ``/etc/pam.conf`` files. Sample input is provided
in the examples.

PamConf - file ``/etc/pam.conf``
--------------------------------

Sample file data::

    #%PAM-1.0
    vsftpd      auth        required    pam_securetty.so
    vsftpd      auth        requisite   pam_unix.so nullok
    vsftpd      auth        sufficient  pam_nologin.so
    vsftpd      account     optional    pam_unix.so
    other       password    include     pam_cracklib.so retry=3 logging=verbose
    other       password    required    pam_unix.so shadow nullok use_authtok
    other       session     required    pam_unix.so


Examples:
    >>> type(pam_conf)
    <class 'insights.parsers.pam.PamConf'>
    >>> len(pam_conf)
    7
    >>> pam_conf[0].service
    'vsftpd'
    >>> pam_conf[0].interface
    'auth'
    >>> pam_conf[0].control_flags
    [ControlFlag(flag='required', value=None)]
    >>> pam_conf[0].module_name
    'pam_securetty.so'
    >>> pam_conf[0].module_args is None
    True
    >>> pam_conf.file_path
    '/etc/pam.conf'

PamDConf - used for specific PAM configuration files
----------------------------------------------------

``PamDConf`` is a base class for the creation of parsers for ``/etc/pam.d``
service specific configuration files.

Sample file from ``/etc/pam.d/sshd``::

    #%PAM-1.0
    auth       required     pam_sepermit.so
    auth       substack     password-auth
    auth       include      postlogin
    # Used with polkit to reauthorize users in remote sessions
    -auth      optional     pam_reauthorize.so prepare
    account    required     pam_nologin.so
    account    include      password-auth
    password   include      password-auth
    # pam_selinux.so close should be the first session rule
    session    required     pam_selinux.so close
    session    required     pam_loginuid.so
    # pam_selinux.so open should only be followed by sessions to be executed in the user context
    session    required     pam_selinux.so open env_params
    session    required     pam_namespace.so
    session    optional     pam_keyinit.so force revoke
    session    include      password-auth
    session    include      postlogin
    # Used with polkit to reauthorize users in remote sessions
    -session   optional     pam_reauthorize.so prepare

Examples:

    >>> type(pamd_conf)
    <class 'insights.parsers.pam.PamDConf'>
    >>> len(pamd_conf)
    15
    >>> pamd_conf[0]._errors == [] # No errors in parsing
    True
    >>> pamd_conf[0].service
    'sshd'
    >>> pamd_conf[0].interface
    'auth'
    >>> pamd_conf[0].control_flags
    [ControlFlag(flag='required', value=None)]
    >>> pamd_conf[0].module_name
    'pam_sepermit.so'
    >>> pamd_conf[0].module_args is None
    True
    >>> pamd_conf.file_path
    '/etc/pam.d/sshd'
    >>> pamd_conf[3].module_name
    'pam_reauthorize.so'
    >>> pamd_conf[3].ignored_if_module_not_found
    True

Normal use of the ``PamDConf`` class is to subclass it for a parser.  In
``insights/specs/default.py``::

    pam_sshd = simple_file("etc/pam.d/sshd")

In the parser module (e.g. ``insights/parsers/pam_sshd.py``)::

    from insights import parser
    from insights.parsers.pam import PamDConf
    from insights.specs import Specs

    @parser(Specs.pam_sshd)
    class PamSSHD(PamDConf):
        pass

References:
    http://www.linux-pam.org/Linux-PAM-html/Linux-PAM_SAG.html
"""

from collections import namedtuple
from .. import Parser, get_active_lines, parser
from ..parsers import unsplit_lines, keyword_search, optlist_to_dict

import re
from insights.specs import Specs


class PamConfEntry(object):
    """Contains information from one PAM configuration line.

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

    Attributes:
        service (str): The service name (taken from the line or from the
            file name if not parsing ``pam.conf``)
        interface (str): The *type* clause - should be one of ``'account'``,
            ``'auth'``, ``'password'`` or ``'session'.  If the line was
            invalid this is set to ``None``.
        ignored_if_module_not_found (bool): If the *type* clause is preceded
            by ``'-'``, then this is set to True and it indicates that PAM
            would skip this line rather than reporting an error if the given
            module is not found.
        control_flags (list): A list of ControlFlag named tuples.  If the
            control flag was one of ``'required'``, ``'requisite'``,
            ``'sufficient'``, ``'optional'``, ``'include'``, or
            ``'substack'``, then this is the only flag in the list and its
            value is set to ``True``.  If the control flag started with ``[``,
            then the list inside the square brackets is interpreted as a list
            of key=value tuples.
        _control_raw (str): the raw control flag string before parsing, for
            reference.
        module_name (str): the PAM module name (including the '.so')
        module_args (str): the PAM module arguments, if any.  This is not
            parsed.
        _full_line (str): The original line in the PAM configuration.
        _errors (list): A list of parsing errors detected in this line.

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
        [ControlFlag(flag='success', value='2'), ControlFlag(flag='default', value='ok')]
        >>> entry.module_args
        'auth=perm_denied cred=success'

    Raises:
        ValueError: If `pamd_conf` is True and `service` name is not provided,
            or if the line doesn't contain any module information.

    .. describe:: ControlFlag

        A named tuple with the 'flag' and 'value' properties, used to store
        information about the control flags in a PAM configuration line.
    """

    ControlFlag = namedtuple('ControlFlag', 'flag, value')

    type_re = r'(?P<type>-?(?:account|auth|password|session))'
    control_re = r'(?P<control>required|requisite|sufficient|optional|' +\
        r'include|substack|\[\w+=\w+(?:\s+\w+=\w+)*\])'
    mod_path_re = r'(?P<module>[\w.-]+)'
    mod_args_re = r'(?P<mod_args>\S.*)'
    line_re = r'\s+'.join([type_re, control_re, mod_path_re]) + \
        r'(?:\s+' + mod_args_re + r')?'
    line_rex = re.compile(line_re)
    _keys = ('service', 'interface', 'control_flags', 'module_name', 'module_args')

    def __init__(self, line, pamd_conf=False, service=None):
        # If not pam.d file then service is first column in
        # line for pam.conf file. Otherwise service must be parameter.
        # print "PamConfEntry(line='{l}', pamd_conf={p}, service={s})".format(l=line, p=pamd_conf, s=service)
        self._full_line = line
        self._errors = []
        self.service = service
        self.interface = None
        self.ignored_if_module_not_found = None
        self._control_raw = ''
        self.control_flags = []
        self.module_name = None
        self.module_args = None
        if not pamd_conf:
            # Because this is called using get_active_lines() and
            # line_unsplit(), we cannot get a line that does not at least have
            # one token on it.
            self.service, line = line.split(None, 1)
        elif service is None:
            # The only valid situation to raise an error - the implementation
            # has called us with pamd_conf = true so we expect a service to
            # be given as a parameter.
            raise ValueError('Service name must be provided for pam.d conf file')

        match = self.line_rex.search(line)
        if match:
            # Type can have a '-' in front, if so line is ignored if module
            # cannot be found.
            self._type_raw = match.group('type')
            self.ignored_if_module_not_found = self._type_raw[0] == '-'
            self.interface = self._type_raw[1:] if self.ignored_if_module_not_found else self._type_raw
            # Parse control token, either regular word or [key=val...]
            self._control_raw = match.group('control')
            if self._control_raw.startswith('['):
                self.control_flags = []
                # Regex assures that it ends with ]
                for group in self._control_raw[1:-1].split(None):
                    # We could do a match: val is constrained to a list and
                    # action is 'ignore', 'bad', 'die', 'ok', done', 'reset'
                    # or N where N is an unsigned integer.  But keep it simple
                    # for now.
                    # Regex makes sure that each group contains an '=' though.
                    val, action = group.split('=', 1)
                    self.control_flags.append(self.ControlFlag(val, action))
            else:
                self.control_flags = [self.ControlFlag(self._control_raw, None)]
            self.module_name = match.group('module')
            self.module_args = match.group('mod_args') if 'mod_args' in match.groupdict() else None
            self.module_args_dict = (
                optlist_to_dict(self.module_args, opt_sep=' ')
                if self.module_args is not None
                else {}
            )
        else:
            # Line not valid - report error
            self._errors.append("Cannot parse line '{l}' as a valid pam.d entry".format(l=self._full_line))

    def __contains__(self, key):
        return key in self._keys

    def __getitem__(self, key):
        if key == 'control_flags':
            return dict(
                (f.flag, f.value)
                for f in self.control_flags
            )
        return getattr(self, key) or ''

    def items(self):
        for key in self._keys:
            yield (key, self[key])

    def keys(self):
        return self._keys

    def __repr__(self):
        return "<PamConfEntry for {svc}: {typ} {ctl} {name}{args}>".format(
            svc=self.service, typ=self._type_raw, ctl=self._control_raw,
            name=self.module_name, args=(
                ' ' + self.module_args if self.module_args else ''
            )
        )


class PamDConf(Parser):
    """Base class for parsing files in ``/etc/pam.d``

    Derive from this class for parsers of files in
    the ``/etc/pam.d`` directory.  Parses each line of the conf
    file into a list of PamConfEntry.  Configuration file format is::

        module_interface    control_flag    module_name module_arguments

    Sample input::
        >>> pam_sshd = '''
        ... auth        required    pam_securetty.so
        ... auth        requisite   pam_unix.so nullok
        ... auth        sufficient  pam_nologin.so
        ... auth        [success=2 default=ok]  pam_debug.so auth=perm_denied cred=success
        ... account     optional    pam_unix.so
        ... password    include     pam_cracklib.so retry=3 logging=verbose
        ... password    required    pam_unix.so shadow nullok use_authtok
        ... '''
        >>> from insights.tests import context_wrap
        >>> class YourPamDConf(PamDConf):  # A trivial example
        ...     pass
        >>> conf = YourPamDConf(context_wrap(pam_sshd, path='/etc/pam.d/sshd'))

    The `service` property of each PamConfEntry is set to the complete path
    name of the PAM config file.

    Attributes:
        data (list): List containing a PamConfEntry object for each line of
            the conf file in the same order as lines appear in the file.

    Examples:
        >>> conf[0].module_name  # Can be used like a list of objects
        'pam_securetty.so'
        >>> account_rows = list(conf.search(interface='account'))
        >>> len(account_rows)
        1
        >>> account_rows[0].interface
        'account'
        >>> account_rows[0].module_name
        'pam_unix.so'
        >>> account_rows[0].control_flags
        [ControlFlag(flag='optional', value=None)]
    """
    def parse_content(self, content):
        self.data = []
        # Need unsplit_lines for handling \ line continuations
        for line in get_active_lines(unsplit_lines(content)):
            self.data.append(PamConfEntry(line, pamd_conf=True, service=self.file_name))

    def __iter__(self):
        """(iterable): Iterate through the list of rules in the file"""
        for entry in self.data:
            yield entry

    def __getitem__(self, ndx):
        """(PamConfEntry): Return the entry data for the given line number"""
        return self.data[ndx]

    def __len__(self):
        """(int): Return the number of entries read from the file"""
        return len(self.data)

    def search(self, **kwargs):
        """
        Search the pam.d configuration file by keyword.  This is provided by
        the :func:`insights.parsers.keyword_search` function - see its
        documentation for more information.

        Searching on the list of PAM configuration entries is exactly like
        they were dictionaries instead of objects with properties.  In
        addition, the 'control_flags' property becomes a dictionary of
        keywords and values, so that 'control_flags__contains' allows
        searching for a particular control flag.

        Returns:
            (list): A list of PamConfEntry objects that match the given
            search criteria.
        """
        return keyword_search(self, **kwargs)


@parser(Specs.pam_conf)
class PamConf(PamDConf):
    """Base class for parsing pam config file ``/etc/pam.conf``.

    Based on the PamDConf parser class, but the service must be given as
    the first element of the line, rather than assumed from the file name.
    """
    def parse_content(self, content):
        self.data = []
        for line in get_active_lines(content):
            self.data.append(PamConfEntry(line))
