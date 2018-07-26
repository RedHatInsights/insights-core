from insights.parsers.dmsetup import DmsetupInfo
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
