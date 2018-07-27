"""VirshListAll - command ``virsh --readonly list --all``
=========================================================

This module provides VM status using output of command ``virsh --readonly list --all``.
"""
from collections import namedtuple

from insights.specs import Specs
from .. import CommandParser, parser
from . import parse_fixed_table, keyword_search


@parser(Specs.virsh_list_all)
class VirshListAll(CommandParser):
    """Parsing output of ``virsh --readonly list --all``.

    Typical output of ``virsh --readonly list --all`` command is::

        Id    Name                           State
        ----------------------------------------------------
        2     rhel7.4                        running
        4     rhel7.0                        paused
        -     centos6.8-router               shut off
        -     cfme-5.7.13                    shut off
        -     cfme-rhos-5.9.0.15             shut off
        -     fedora-24-kernel               shut off
        -     fedora-saio_fedoraSaio         shut off
        -     fedora24-misc                  shut off
        -     freebsd11.0                    shut off
        -     guixSD                         shut off
        -     miq-gap-1                      shut off
        -     rhel7.2                        shut off
        -     RHOSP10                        shut off


    Examples:

        >>> len(output.search(state='shut off')) == 11
        True
        >>> len(output.search(id=None)) == 11
        True
        >>> len(output.search(id=2)) == 1
        True
        >>> output.search(name='rhel7.4') == [{'state': 'running', 'id': 2, 'name': 'rhel7.4'}]
        True
        >>> output.get_vm_state('rhel7.0') == 'paused'
        True
        >>> output.get_vm_state('rhel9.0') is None
        True
        >>> 'cfme' in output
        False
        >>> 'cfme-5.7.13' in output
        True

    Attributes:
        fields (list): List of ``KeyValue`` namedtupules for each line
                       in the command.

        cols (list): List id key value pair derived from the command.

        keywords (list): keywords present in the command, each
                        keyword is converted to lowercase.

    """
    keyvalue = namedtuple('KeyValue',
                          ['name', 'state', 'id', 'name_lower'])
    """namedtuple: Represent name value pair as a namedtuple with case."""
    def _cleanup(self):
        for col in self.cols:
            if col['id'] == '-':
                col['id'] = None
            else:
                col['id'] = (lambda x: int(x) if x.isdigit() else x)(col['id'])

    def parse_content(self, content):
        self.fields = []
        self.cols = []
        self.keywords = []
        if not content:
            return

        self.cols = parse_fixed_table(content,
                                      heading_ignore=['Id', 'Name', 'State'],
                                      header_substitute=[('Id', 'id'), ('Name', 'name'), ('State', 'state')])[1:]  # noqa
        self._cleanup()

        for item in self.cols:
            self.fields.append(self.keyvalue(item['name'], item['state'], item['id'], item['name'].lower()))  # noqa
        self.keywords = [name.name_lower for name in self.fields]

    def __contains__(self, keyword):
        return keyword.lower() in self.keywords

    def __iter__(self):
        return iter(self.fields)

    def search(self, **kw):
        '''Search item based on key value pair.

        Example:

            >>> len(output.search(state='shut off')) == 11
            True
            >>> len(output.search(id=None)) == 11
            True
            >>> len(output.search(id=2)) == 1
            True
        '''
        return keyword_search(self.cols, **kw)

    def get_vm_state(self, vmname):
        '''Get VM state associated with vmname

        Typical output is ``virsh --readonly list --all`` command::

             Id    Name                           State
            ----------------------------------------------------
             2     rhel7.4                        running
             4     rhel7.0                        paused


        Example:

            >>> output.get_vm_state('rhel7.0')
            'paused'

        Args:

            vmname (str): A key. For ex. ``rhel7.0``.

        Returns:

            str: State of VM. Returns None if, ``vmname`` does not exist.
        '''
        vmname = vmname.lower()
        if vmname in self.keywords:
            return self.search(name=vmname)[0]['state']
        return None
