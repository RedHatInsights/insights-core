"""
dmsetup commands - Command ``dmsetup``
======================================

Parsers for parsing and extracting data from output of commands related to
``dmsetup``.
Parsers contained in this module are:

DmsetupInfo - command ``dmsetup info -C``
-----------------------------------------

DmsetupStatus - command ``dmsetup status``
------------------------------------------

"""
from collections import namedtuple
from insights import parser, CommandParser
from insights.parsers import parse_delimited_table
from insights.parsers import ParseException
from insights.specs import Specs


SetupInfo = namedtuple('SetupInfo', [
    'name', 'major', 'minor', 'open', 'segments', 'events',
    'live_table', 'inactive_table', 'suspended', 'readonly', 'uuid']
)
""" Data structure to represent dmsetup information """

SetupStatus = namedtuple('SetupStatus', [
    'device_name', 'start_sector', 'num_sectors', 'target_type',
    'target_args', 'parsed_args']
)
""" Data structure to represent dmsetup status """


@parser(Specs.dmsetup_info)
class DmsetupInfo(CommandParser):
    """
    ``dmsetup info -C`` command output

    Example input::

        Name               Maj Min Stat Open Targ Event  UUID
        VG00-tmp           253   8 L--w    1    1      0 LVM-gy9uAwD7LuTIApplr2sogbOx5iS0FTax6lLmBji2ueSbX49gxcV76M29cmukQiw4
        VG00-home          253   3 L--w    1    1      0 LVM-gy9uAwD7LuTIApplr2sogbOx5iS0FTaxCqXOnbGe2zjhX923dFiIdl1oi7mO9tXp
        VG00-var           253   6 L--w    1    2      0 LVM-gy9uAwD7LuTIApplr2sogbOx5iS0FTaxicvyvt67113nTb8vMlGfgdEjDx0LKT2O
        VG00-swap          253   1 L--w    2    1      0 LVM-gy9uAwD7LuTIApplr2sogbOx5iS0FTax3Ll2XhOYZkylx1CjOQi7G4yHgrIOsyqG
        VG00-root          253   0 L--w    1    1      0 LVM-gy9uAwD7LuTIApplr2sogbOx5iS0FTaxKpnAKYhrYMYMNMwjegkW965bUgtJFTRY
        VG00-var_log_audit 253   5 L--w    1    1      0 LVM-gy9uAwD7LuTIApplr2sogbOx5iS0FTaxwQ8R0XWJRm86QX3befq1cHRy47Von6ZW

    Example data structure produced::

        data = [
          {
            'Stat': 'L--w',
            'Name': 'VG00-tmp',
            'Min': '8',
            'Targ': '1',
            'Maj': '253',
            'Open': '1',
            'Event': '0',
            'UUID': 'LVM-gy9uAwD7LuTIApplr2sogbOx5iS0FTax6lLmBji2ueSbX49gxcV76M29cmukQiw4'
          },...
        ]

    Attributes:
        data (list): List of devices found, in order
        names (list): Device names, in order found
        uuids (list): UUID
        by_name (dict): Access to each device by devicename
        by_uuid (dict): Access to each device by uuid
        info (list): List of devices found, in order using SetupInfo structure

    Example:
        >>> len(setup_info)
        6
        >>> setup_info.names[0]
        'VG00-tmp'
        >>> setup_info[1]['Maj']
        '253'
        >>> setup_info[1]['Stat']
        'L--w'
        >>> setup_info.info[-1].name
        'VG00-var_log_audit'
        >>> setup_info.info[-1].major
        253
        >>> setup_info.info[-1].live_table
        True
        >>> setup_info.info[-1].readonly
        False
    """

    def parse_content(self, content):
        self.data = parse_delimited_table(content)

        self.names = [dm['Name'] for dm in self.data if 'Name' in dm]
        self.by_name = dict((dm['Name'], dm) for dm in self.data if 'Name' in dm)
        self.uuids = [dm['UUID'] for dm in self.data if 'UUID' in dm]
        self.by_uuid = dict((dm['UUID'], dm) for dm in self.data if 'UUID' in dm)
        self.info = []
        for dm in self.data:
            self.info.append(SetupInfo(
                name=dm.get('Name'),
                major=int(dm.get('Maj')) if 'Maj' in dm and dm.get('Maj').isdigit() else None,
                minor=int(dm.get('Min')) if 'Min' in dm and dm.get('Min').isdigit() else None,
                open=int(dm.get('Open')) if 'Open' in dm and dm.get('Open').isdigit() else None,
                segments=int(dm.get('Targ')) if 'Targ' in dm and dm.get('Targ').isdigit() else None,
                events=int(dm.get('Event')) if 'Event' in dm and dm.get('Event').isdigit() else None,
                live_table=dm.get('Stat', '----')[0] == 'L',
                inactive_table=dm.get('Stat', '----')[1] == 'I',
                suspended=dm.get('Stat', '----')[2] == 's',
                readonly=dm.get('Stat', '----')[3] == 'r',
                uuid=dm.get('UUID')
            ))

    def __len__(self):
        """
        The length of the devices list
        """
        return len(self.data)

    def __iter__(self):
        """
        Iterate through the devices list
        """
        for dm in self.data:
            yield dm

    def __getitem__(self, idx):
        """
        Fetch a device by index in devices list
        """
        return self.data[idx]


@parser(Specs.dmsetup_status)
class DmsetupStatus(CommandParser, list):
    """
    ``dmsetup status -C`` command output

    Example input::

        rootvg-tanlv: 0 6291456 linear
        rootvg-ssnap: 0 16384000 snapshot 1560768/5120000 6088
        rootvg-optvolapp: 0 8192000 snapshot-origin
        docker-253:10-1234567-0df13579: 0 20971520 thin 1922048 20971519
        docker-253:10-4254621-0496628a: 0 20971520 thin 1951744 20971519
        docker-253:10-4254621-d392682f: 0 20971520 thin 7106560 20971519
        rootvg-docker--pool: 0 129548288 thin-pool 1 20/49152 38/126512 - rw no_discard_passdown queue_if_no_space -
        rootvg-tmpvol: 0 2048000 linear
        rootvg-varvol: 0 18874368 snapshot Invalid
        rootvg-optvol: 0 8192000 snapshot 616408/5120000 2408
        rootvg-varvol-cow: 0 5120000 linear
        appsvg-lvapps_docker: 0 104857600 thin-pool 441 697/2048 20663/102400 - rw no_discard_passdown queue_if_no_space -

    Example data structure produced::

        [
            SetupStatus(
                device_name='rootvg-tanlv', start_sector='0',
                num_sectors='6291456', target_type='linear',
                target_args=None, parsed_args=None,
            ), ...
        ]

    Attributes:
        names (list): Device names, in order found
        by_name (dict): Access to each device by devicename
        unparseable_lines (list): Unparseable raw lines

    Example:
        >>> len(dmsetup_status)
        12
        >>> dmsetup_status.names[0]
        'rootvg-tanlv'
        >>> dmsetup_status[1].target_type
        'snapshot'
        >>> dmsetup_status[1].start_sector
        '0'
        >>> len(dmsetup_status.by_name)
        12
        >>> dmsetup_status[-1].parsed_args['used_metadata_blocks']
        '697'
        >>> dmsetup_status[-1].parsed_args['total_metadata_blocks']
        '2048'
        >>> dmsetup_status[-1].parsed_args['opts']
        ['rw', 'no_discard_passdown', 'queue_if_no_space', '-']
    """

    def parse_content(self, content):
        self.unparseable_lines = []
        if content[0].lower() == "no devices found":
            return

        for line in content:
            _device_name, _device_info_str = line.rsplit(':', 1)
            device_name = _device_name.strip()
            device_info_spl = _device_info_str.strip().split(' ', 3)
            if len(device_info_spl) < 3:
                self.unparseable_lines.append(line)
                continue
            target_type = device_info_spl[2]
            target_args = device_info_spl[3] if len(device_info_spl) == 4 else None
            parsed_args = None
            if target_args:
                try:
                    parsed_args = self._parse_target_args(target_type, target_args)
                except ParseException:
                    self.unparseable_lines.append(line)
            self.append(SetupStatus(
                device_name=device_name,
                start_sector=device_info_spl[0],
                num_sectors=device_info_spl[1],
                target_type=target_type,
                target_args=target_args,
                parsed_args=parsed_args,
            ))

    @property
    def names(self):
        return [dm[0] for dm in self]

    @property
    def by_name(self):
        return dict((dm[0], dm) for dm in self)

    def _parse_target_args(self, target_type, target_args):
        pars_func_name = '_parse_target_args_' + target_type.replace('-', '_')
        pars_func = getattr(self, pars_func_name, None)
        return pars_func(target_args) if pars_func else None

    def _parse_target_args_thin_pool(self, target_args):
        """
        Format:
            <transaction_id> <used_metadata_blocks>/<total_metadata_blocks>
            <used_data_blocks>/<total_data_blocks> <held_metadata_root>
            ro|rw|out_of_data_space [no_]discard_passdown [error|queue]_if_no_space
            needs_check|- metadata_low_watermark
        Refer to https://www.kernel.org/doc/Documentation/device-mapper/thin-provisioning.txt .
        """
        args = target_args.split()
        if len(args) < 8 or '/' not in args[1] or '/' not in args[2]:
            raise ParseException("Invalid thin_pool target_args: {0}".format(target_args))
        parsed_args = {}
        parsed_args['transaction_id'] = args[0]
        parsed_args['used_metadata_blocks'], parsed_args['total_metadata_blocks'] = args[1].split('/', 1)
        parsed_args['used_data_blocks'], parsed_args['total_data_blocks'] = args[2].split('/', 1)
        parsed_args['held_metadata_root'] = args[3]
        parsed_args['opts'] = args[4:8]
        parsed_args['metadata_low_watermark'] = args[8] if len(args) > 8 else None
        return parsed_args

    def _parse_target_args_thin(self, target_args):
        """
        Format:
            <nr_mapped_sectors> <highest_mapped_sector>
        Refer to https://www.kernel.org/doc/Documentation/device-mapper/thin-provisioning.txt .
        """
        args = target_args.split()
        if len(args) < 2:
            raise ParseException("Invalid thin target_args: {0}".format(target_args))
        parsed_args = {}
        parsed_args['nr_mapped_sectors'] = args[0]
        parsed_args['highest_mapped_sector'] = args[1]
        return parsed_args

    def _parse_target_args_snapshot(self, target_args):
        """
        Format:
            <sectors_allocated>/<total_sectors> <metadata_sectors>
        Refer to https://www.kernel.org/doc/Documentation/device-mapper/snapshot.txt .
        """
        args = target_args.split()
        if len(args) < 2 or '/' not in args[0]:
            raise ParseException("Invalid snapshot target_args: {0}".format(target_args))
        parsed_args = {}
        parsed_args['sectors_allocated'], parsed_args['total_sectors'] = args[0].split('/', 1)
        parsed_args['metadata_sectors'] = args[1]
        return parsed_args
