from collections import namedtuple
from .. import Mapper, get_active_lines, mapper
from ..mappers import unsplit_lines


class PamConfEntry(object):
    """Contains information from one pam conf line."""

    ControlFlag = namedtuple('ControlFlag', 'flag, value')

    def __init__(self, line, pamd_conf=False, service=None):
        self.data = {}
        self.raw_line = line
        # If not pam.d file then service is first column in
        # line for pam.conf file. Otherwise service must be parameter.
        if not pamd_conf:
            service, rest = line.split(None, 1)
            line = rest
        elif service is None:
            raise ValueError('Service name must be provided for pam.d conf file')

        mod_if, rest = line.split(None, 1)
        mod_if = mod_if.lower()
        if not rest[0] == '[':
            ctrl_flag, mod_info = rest.split(None, 1)
            ctrl_flags = [self.ControlFlag(ctrl_flag, None)]
        else:
            ctrl_flag, mod_info = rest[1:].split(']', 1)
            ctrl_flags = []
            for flag_val in ctrl_flag.split():
                flag, _, val = flag_val.partition('=')
                ctrl_flags.append(self.ControlFlag(flag, val))

        mod_info = mod_info.split(None, 1)
        if len(mod_info) == 1:
            mod_name = mod_info[0]
            mod_args = None
        elif len(mod_info) > 1:
            mod_name = mod_info[0]
            mod_args = mod_info[1]
        else:
            raise ValueError('Missing module name from pam conf line: {}'.format(line))

        self.data['service'] = service
        self.data['interface'] = mod_if
        self.data['flags'] = ctrl_flags
        self.data['mod_name'] = mod_name
        self.data['mod_args'] = mod_args

    def __getitem__(self, key):
        return self.data[key]

    @property
    def service(self):
        return self.data['service']

    @property
    def interface(self):
        return self.data['interface']

    @property
    def control_flags(self):
        return self.data['flags']

    @property
    def module_name(self):
        return self.data['mod_name']

    @property
    def module_args(self):
        return self.data['mod_args']


@mapper('pam.conf')
class PamConf(Mapper):
    """Base class for parsing pam config file `/etc/pam.conf`

    Derive from this class for mappers of files in
    the `/etc/pam.d` directory.

    Configuration file format is::

        service_name    module_interface    control_flag    module_name module_arguments

    Sample input::

        # Comment line
        vsftpd      auth        required    pam_securetty.so
        vsftpd      auth        required    pam_unix.so nullok
        vsftpd      auth        required    pam_nologin.so
        vsftpd      account     required    pam_unix.so
        other       password    required    pam_cracklib.so retry=3
        other       password    required    pam_unix.so shadow nullok use_authtok
        servicex    session     required    pam_unix.so

    Reference:
        https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux/6/html/Managing_Smart_Cards/PAM_Configuration_Files.html
        http://www.linux-pam.org/Linux-PAM-html/Linux-PAM_SAG.html
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
    """Base class for parsing files in `/etc/pam.d`

    Derive from this class for mappers of files in
    the `/etc/pam.d` directory.

    Configuration file format is::

        module_interface    control_flag    module_name module_arguments

    Sample input for an example file named `/etc/pam.d/some_application`::

        #%PAM-1.0
        auth        required    pam_securetty.so
        auth        required    pam_unix.so nullok
        auth        required    pam_nologin.so
        account     required    pam_unix.so
        password    required    pam_cracklib.so retry=3
        password    required    pam_unix.so shadow nullok use_authtok
        session     required    pam_unix.so

    Reference:
        https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux/6/html/Managing_Smart_Cards/PAM_Configuration_Files.html
        http://www.linux-pam.org/Linux-PAM-html/Linux-PAM_SAG.html
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
