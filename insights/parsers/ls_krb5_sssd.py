"""
Lskrb5Sssd - command ``ls -lan /var/lib/sss/pubconf/krb5.include.d``
====================================================================

The ``ls -lan /var/lib/sss/pubconf/krb5.include.d`` command provides information for the listing of the
``/var/lib/sss/pubconf/krb5.include.d`` directory. See the ``FileListing`` class for a more complete description
of the available features of the class.

Sample ``ls -lan /var/lib/sss/pubconf/krb5.include.d`` output::

    /var/lib/sss/pubconf/krb5.include.d:
    total 24
    drwxr-xr-x@ 6 501  20  192 Jul  1 23:46 .
    drwxr-xr-x@ 3 501  20   96 Jul  1 23:48 ..
    -rw-r--r--@ 1 501  20  674 Jul  1 23:46 domain_realm_rhidm_gwl_bz
    -rw-r--r--@ 1 501  20   35 Jul  1 23:46 krb5_libdefaults
    -rw-r--r--@ 1 501  20   98 Jul  1 23:46 localauth_plugin
    -rw-------@ 1 501  20    0 Oct  1  2021 localauth_pluginolsIe3

Examples:
    >>> '/var/lib/sss/pubconf/krb5.include.d' in ls_krb5_sssd
    True
    >>> ls_krb5_sssd.files_of('/var/lib/sss/pubconf/krb5.include.d') == ['domain_realm_rhidm_gwl_bz', 'krb5_libdefaults', 'localauth_plugin', 'localauth_pluginolsIe3']
    True
"""

from insights.specs import Specs
from .. import parser, CommandParser, FileListing
from insights.util import deprecated


@parser(Specs.ls_krb5_sssd)
class LsKrb5SSSD(CommandParser, FileListing):
    """
    .. warning::
        This class is deprecated and will be removed from 3.5.0.
        Please use the :class:`insights.parsers.ls.LSlan` instead.

    Parse the /var/lib/sss/pubconf/krb5.include.d directory listing using a standard FileListing parser.
    """
    def __init__(self, *args, **kwargs):
        deprecated(LsKrb5SSSD, "Please use the :class:`insights.parsers.ls.LSlan` instead.", "3.5.0")
        super(LsKrb5SSSD, self).__init__(*args, **kwargs)
