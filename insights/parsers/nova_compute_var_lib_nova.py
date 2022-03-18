"""
NovaComputeLsVarLibNova - command ``docker exec nova_compute /bin/ls -larn /var/lib/nova``
==========================================================================================

The parser class in this module uses the base parsers ``CommandParser`` and ``FileListing``
to list the files & directories under ``/var/lib/nova`` in the ``nova_compute`` container.
"""
from insights.components.openstack import IsOpenStackCompute
from insights import CommandParser, FileListing, parser
from insights.specs import Specs


@parser(Specs.nova_compute_ls_var_lib_nova, IsOpenStackCompute)
class NovaComputeLsVarLibNova(CommandParser, FileListing):
    """
    This class parses the output of ``docker exec nova_compute /bin/ls -larn /var/lib/nova``
    to output the file listing.

    This parser depends on ``insights.components.openstack.IsOpenStackCompute``
    and will be fired only if the dependency is met.

    Typical output is::

        total 4
        drwxr-xr-x. 2 42436 42436   6 Jun 21  2018 tmp
        drwxr-xr-x. 2 42436 42436   6 Jun 21  2018 networks
        drwxr-xr-x. 2 42436 42436   6 Jun 21  2018 keys
        drwxr-xr-x. 5 42436 42436  97 May 23 10:42 instances
        drwxr-xr-x. 2 42436 42436   6 Jun 21  2018 buckets
        drwx------. 2 42436 42436  20 May 28 09:34 .ssh
        -rw-------. 1 42436 42436 682 May 27 11:12 .bash_history
        drwxr-xr-x. 1     0     0  19 Jul 14  2018 ..
        drwxr-xr-x. 8 42436 42436 110 Jun 21  2018 .

    Examples:

        >>> ls.listing_of("/var/lib/nova")[".ssh"]["links"]
        2
        >>> ls.listings["/var/lib/nova"]["entries"]["tmp"]["perms"]
        'rwxr-xr-x.'
        >>> len(ls.listings["/var/lib/nova"])
        6
    """
    pass
