import doctest
from insights.parsers import dmsetup
from insights.parsers.dmsetup import DmsetupInfo, SetupInfo
from insights.parsers.dmsetup import DmsetupStatus, SetupStatus
from insights.tests import context_wrap

DMSETUP_INFO_1 = """
Name               Maj Min Stat Open Targ Event  UUID
VG00-tmp           253   8 L--w    1    1      0 LVM-gy9uAwD7LuTIApplr2sogbOx5iS0FTax6lLmBji2ueSbX49gxcV76M29cmukQiw4
VG00-var_tmp       253   4 L--w    1    1      0 LVM-gy9uAwD7LuTIApplr2sogbOx5iS0FTaxXOT2ZNHpEmJy2g2FpmXfAH1chG4Utm4Q
VG00-home          253   3 L--w    1    1      0 LVM-gy9uAwD7LuTIApplr2sogbOx5iS0FTaxCqXOnbGe2zjhX923dFiIdl1oi7mO9tXp
VG00-var_log       253   9 L--w    1    1      0 LVM-gy9uAwD7LuTIApplr2sogbOx5iS0FTaxlycWK5qprImfYnbkZLNiFZ5Lc6rJq04Z
VG00-usr           253   2 L--w    1    1      0 LVM-gy9uAwD7LuTIApplr2sogbOx5iS0FTaxJqQ6DLofdR0uWkTnlpkRnFShO3PgqhCT
VG00-var           253   6 L--w    1    2      0 LVM-gy9uAwD7LuTIApplr2sogbOx5iS0FTaxicvyvt67113nTb8vMlGfgdEjDx0LKT2O
VG00-swap          253   1 L--w    2    1      0 LVM-gy9uAwD7LuTIApplr2sogbOx5iS0FTax3Ll2XhOYZkylx1CjOQi7G4yHgrIOsyqG
VG00-root          253   0 L--w    1    1      0 LVM-gy9uAwD7LuTIApplr2sogbOx5iS0FTaxKpnAKYhrYMYMNMwjegkW965bUgtJFTRY
VG00-var_log_audit 253   5 L--w    1    1      0 LVM-gy9uAwD7LuTIApplr2sogbOx5iS0FTaxwQ8R0XWJRm86QX3befq1cHRy47Von6ZW
VG_DB-vol01        253  10 L--w    1    2      0 LVM-dgoBx4rat9aLu3sg1k95D7YwUT7YnFddgcZSaU2sjHZMVBlwcNwDjmmGGtfXeIZs
VG00-opt           253   7 L--w    1    4      0 LVM-gy9uAwD7LuTIApplr2sogbOx5iS0FTaxIiCYm5hcvgQdXynPGBfHQLrtE3sqUKT2
""".strip()

DMSETUP_INFO_2 = """
Name               Maj Min Stat Open Targ Event  UUID
VG00-tmp           253   8 xIsr    1    1      a LVM-gy9uAwD7LuTIApplr2sogbOx5iS0FTax6lLmBji2ueSbX49gxcV76M29cmukQiw4
""".strip()


def test_dmsetup_info():
    r = DmsetupInfo(context_wrap(DMSETUP_INFO_1))
    assert len(r) == 11
    assert len(r[0]) == 8
    assert r[0]['UUID'] == 'LVM-gy9uAwD7LuTIApplr2sogbOx5iS0FTax6lLmBji2ueSbX49gxcV76M29cmukQiw4'
    assert r[-1]['Stat'] == 'L--w'
    assert r.names == ['VG00-tmp', 'VG00-var_tmp', 'VG00-home', 'VG00-var_log',
                       'VG00-usr', 'VG00-var', 'VG00-swap', 'VG00-root',
                       'VG00-var_log_audit', 'VG_DB-vol01', 'VG00-opt']
    assert r.names == [dm['Name'] for dm in r]
    assert len(r.by_uuid) == 11
    assert r.info[0] == SetupInfo(
        name='VG00-tmp',
        major=253,
        minor=8,
        open=1,
        segments=1,
        events=0,
        live_table=True,
        inactive_table=False,
        suspended=False,
        readonly=False,
        uuid='LVM-gy9uAwD7LuTIApplr2sogbOx5iS0FTax6lLmBji2ueSbX49gxcV76M29cmukQiw4'
    )
    assert r.info[-1] == SetupInfo(
        name='VG00-opt',
        major=253,
        minor=7,
        open=1,
        segments=4,
        events=0,
        live_table=True,
        inactive_table=False,
        suspended=False,
        readonly=False,
        uuid='LVM-gy9uAwD7LuTIApplr2sogbOx5iS0FTaxIiCYm5hcvgQdXynPGBfHQLrtE3sqUKT2'
    )


def test_dmsetup_setupinfo():
    r = DmsetupInfo(context_wrap(DMSETUP_INFO_2))
    assert r.info[0] == SetupInfo(
        name='VG00-tmp',
        major=253,
        minor=8,
        open=1,
        segments=1,
        events=None,
        live_table=False,
        inactive_table=True,
        suspended=True,
        readonly=True,
        uuid='LVM-gy9uAwD7LuTIApplr2sogbOx5iS0FTax6lLmBji2ueSbX49gxcV76M29cmukQiw4'
    )


DMSETUP_STATUS_1 = """
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
""".strip()

DMSETUP_STATUS_2 = """
rootvg-tanlv: 0 6291456
rootvg-ssnap: 0 16384000 unknown-type
rootvg-docker--pool: 0 129548288 thin-pool 1 20/49152 38/126512 - rw no_discard_passdown queue_if_no_space
rootvg-optvol: 0 8192000 snapshot-origin
docker-253:10-4254621-d392682f: 0 20971520 thin 7106560 20971519
docker-253:10-1234567-0df13579: 0 20971520 thin 1922048
""".strip()

DMSETUP_STATUS_3 = """
No devices found
""".strip()


def test_dmsetup_status():
    r = DmsetupStatus(context_wrap(DMSETUP_STATUS_1))
    assert len(r) == 12
    assert len(r[0]) == 6
    assert r[0].device_name == 'rootvg-tanlv'
    assert r[0].start_sector == '0'
    assert r[0].num_sectors == '6291456'
    assert r[0].target_type == 'linear'
    assert r[0].target_args is None
    assert r[0].parsed_args is None
    assert r.names == ['rootvg-tanlv', 'rootvg-ssnap', 'rootvg-optvolapp',
            'docker-253:10-1234567-0df13579', 'docker-253:10-4254621-0496628a',
            'docker-253:10-4254621-d392682f', 'rootvg-docker--pool',
            'rootvg-tmpvol', 'rootvg-varvol', 'rootvg-optvol',
            'rootvg-varvol-cow', 'appsvg-lvapps_docker']

    assert len(r.by_name) == len([dev.device_name for dev in r])
    assert r[0] == SetupStatus(
            device_name='rootvg-tanlv', start_sector='0',
            num_sectors='6291456', target_type='linear',
            target_args=None, parsed_args=None,
    )
    assert r[-1] == SetupStatus(
            device_name='appsvg-lvapps_docker', start_sector='0',
            num_sectors='104857600', target_type='thin-pool',
            target_args='441 697/2048 20663/102400 - rw no_discard_passdown queue_if_no_space -',
            parsed_args={
                'transaction_id': '441',
                'used_metadata_blocks': '697',
                'total_metadata_blocks': '2048',
                'used_data_blocks': '20663',
                'total_data_blocks': '102400',
                'held_metadata_root': '-',
                'opts': ['rw', 'no_discard_passdown', 'queue_if_no_space', '-'],
                'metadata_low_watermark': None
            })
    assert r[3] == SetupStatus(
            device_name='docker-253:10-1234567-0df13579', start_sector='0',
            num_sectors='20971520', target_type='thin', target_args='1922048 20971519',
            parsed_args={'nr_mapped_sectors': '1922048', 'highest_mapped_sector': '20971519'}
    )
    assert r[-3] == SetupStatus(
            device_name='rootvg-optvol', start_sector='0', num_sectors='8192000',
            target_type='snapshot', target_args='616408/5120000 2408',
            parsed_args={'sectors_allocated': '616408', 'total_sectors': '5120000', 'metadata_sectors': '2408'}
    )
    assert r[-4] == SetupStatus(
            device_name='rootvg-varvol', start_sector='0', num_sectors='18874368',
            target_type='snapshot', target_args='Invalid', parsed_args=None
    )
    assert r.unparseable_lines == ['rootvg-varvol: 0 18874368 snapshot Invalid']

    r = DmsetupStatus(context_wrap(DMSETUP_STATUS_2))
    assert len(r) == 5
    assert r.unparseable_lines == [
            'rootvg-tanlv: 0 6291456',
            'rootvg-docker--pool: 0 129548288 thin-pool 1 20/49152 38/126512 - rw no_discard_passdown queue_if_no_space',
            'docker-253:10-1234567-0df13579: 0 20971520 thin 1922048']

    r = DmsetupStatus(context_wrap(DMSETUP_STATUS_3))
    assert len(r) == 0
    assert r.unparseable_lines == []


DMSETUP_EXAMPLES = """
Name               Maj Min Stat Open Targ Event  UUID
VG00-tmp           253   8 L--w    1    1      0 LVM-gy9uAwD7LuTIApplr2sogbOx5iS0FTax6lLmBji2ueSbX49gxcV76M29cmukQiw4
VG00-home          253   3 L--w    1    1      0 LVM-gy9uAwD7LuTIApplr2sogbOx5iS0FTaxCqXOnbGe2zjhX923dFiIdl1oi7mO9tXp
VG00-var           253   6 L--w    1    2      0 LVM-gy9uAwD7LuTIApplr2sogbOx5iS0FTaxicvyvt67113nTb8vMlGfgdEjDx0LKT2O
VG00-swap          253   1 L--w    2    1      0 LVM-gy9uAwD7LuTIApplr2sogbOx5iS0FTax3Ll2XhOYZkylx1CjOQi7G4yHgrIOsyqG
VG00-root          253   0 L--w    1    1      0 LVM-gy9uAwD7LuTIApplr2sogbOx5iS0FTaxKpnAKYhrYMYMNMwjegkW965bUgtJFTRY
VG00-var_log_audit 253   5 L--w    1    1      0 LVM-gy9uAwD7LuTIApplr2sogbOx5iS0FTaxwQ8R0XWJRm86QX3befq1cHRy47Von6ZW
""".strip()


def test_examples():
    env = {
        'setup_info': DmsetupInfo(context_wrap(DMSETUP_EXAMPLES)),
        'dmsetup_status': DmsetupStatus(context_wrap(DMSETUP_STATUS_1))
    }
    failed, total = doctest.testmod(dmsetup, globs=env)
    assert failed == 0
