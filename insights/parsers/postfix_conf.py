"""
PostfixMaster - file ``/etc/postfix/master.cf``
===============================================

"""
from insights.core import Parser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.postfix_master)
class PostfixMaster(Parser, list):
    """
    Class to parses the content of postfix configuration files ``/etc/postfix/master.cf``

    Typical content looks like::

        # ==========================================================================
        # service type  private unpriv  chroot  wakeup  maxproc command + args
        #               (yes)   (yes)   (no)    (never) (100)
        # ==========================================================================
        smtp      inet  n       -       n       -       -       smtpd
        pickup    unix  n       -       n       60      1       pickup
        cleanup   unix  n       -       n       -       0       cleanup
        qmgr      unix  n       -       n       300     1       qmgr
        #qmgr     unix  n       -       n       300     1       oqmgr
        tlsmgr    unix  -       -       n       1000?   1       tlsmgr
        rewrite   unix  -       -       n       -       -       trivial-rewrite
        bounce    unix  -       -       n       -       0       bounce
        defer     unix  -       -       n       -       0       bounce
        trace     unix  -       -       n       -       0       bounce
        verify    unix  -       -       n       -       1       verify
        flush     unix  n       -       n       1000?   0       flush
        proxymap  unix  -       -       n       -       -       proxymap
        proxywrite unix -       -       n       -       1       proxymap
        smtp      unix  -       -       n       -       -       smtp
        relay     unix  -       -       n       -       -       smtp
                -o syslog_name=postfix/$service_name
        #       -o smtp_helo_timeout=5 -o smtp_connect_timeout=5
        showq     unix  n       -       n       -       -       showq
        error     unix  -       -       n       -       -       error
        retry     unix  -       -       n       -       -       error
        discard   unix  -       -       n       -       -       discard
        local     unix  -       n       n       -       -       local
        virtual   unix  -       n       n       -       -       virtual
        lmtp      unix  -       -       n       -       -       lmtp
        anvil     unix  -       -       n       -       1       anvil
        scache    unix  -       -       n       -       1       scache

    Examples:
        >>> type(postfix_master)
        <class 'insights.parsers.postfix_conf.PostfixMaster'>
        >>> len(postfix_master)
        24
        >>> postfix_master[-1] == {'service': 'scache', 'type': 'unix', 'private': '-', 'unpriv': '-', 'chroot': 'n', 'wakeup': '-', 'maxproc': '1', 'command': 'scache'}
        True

    Raises:
        insights.core.exceptions.SkipComponent: if the ``/etc/postfix/master.cf`` is empty.
    """

    def parse_content(self, content):
        service_info = None
        heading = ['service', 'type', 'private', 'unpriv', 'chroot', 'wakeup', 'maxproc', 'command']
        for line in content:
            if not line.strip() or line.startswith('#'):
                continue

            if ('=' in line or '$' in line) and service_info:
                service_info['args'] = service_info.get('args', [])
                service_info['args'].append(line.strip())

            elif len(line.split()) == 8:
                line_sp = line.split()
                service_info = dict(zip(heading, line_sp))
                self.append(service_info)

        if not self:
            raise SkipComponent("Empty result")
