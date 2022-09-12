from insights.tests import context_wrap
from insights.parsers.sysconfig import OracleasmSysconfig

ORACLEASM_SYSCONFIG = """
#
# This is a configuration file for automatic loading of the Oracle
# Automatic Storage Management library kernel driver.  It is generated
# By running /etc/init.d/oracleasm configure.  Please use that method
# to modify this file
#

# ORACLEASM_ENABELED: 'true' means to load the driver on boot.
ORACLEASM_ENABLED=true

# ORACLEASM_UID: Default user owning the /dev/oracleasm mount point.
ORACLEASM_UID=oracle

# ORACLEASM_GID: Default group owning the /dev/oracleasm mount point.
ORACLEASM_GID=oinstall

# ORACLEASM_SCANBOOT: 'true' means scan for ASM disks on boot.
ORACLEASM_SCANBOOT=true

# ORACLEASM_SCANORDER: Matching patterns to order disk scanning
ORACLEASM_SCANORDER="dm"

# ORACLEASM_SCANEXCLUDE: Matching patterns to exclude disks from scan
ORACLEASM_SCANEXCLUDE="sd"
""".strip()


def test_sysconfig_oracleasm():
    result = OracleasmSysconfig(context_wrap(ORACLEASM_SYSCONFIG))
    assert result["ORACLEASM_SCANORDER"] == 'dm'
    assert result.get("ORACLEASM_SCANBOOT") == 'true'
    assert result.get("NONEXISTENT_VAR") is None
    assert "NONEXISTENT_VAR" not in result
    assert "ORACLEASM_SCANEXCLUDE" in result
