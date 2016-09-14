from falafel.mappers.installed_rpms import InstalledRpms
from falafel.tests import context_wrap

RPMS = """
COMMAND> rpm xxxxx
BESAgent-9.2.5.130-rhe5.x86_64                              Wed Jan 27 09:18:52 2016	1453904332	IBM Corp.	rhel5x64bs	(none)	(none)
ConsoleKit-0.4.1-3.el6.x86_64                               Wed Sep 17 11:34:25 2014
kernel-2.6.32-573.el6.x86_64                                Wed May 18 14:17:17 2016
zisofs-tools-1.0.6-3.2.2.x86_64                             Wed May 18 14:15:26 2016
tftp-server-5.2-12.el7.x86_64
yum-3.2.29-69.el6.noarch                                    Wed May 18 14:16:21 2016	1410968065	Red Hat, Inc.	hs20-bc2-4.build.redhat.com	8902150305004c6955c9199e2f91fd431d51010853c80ffb05f6916ea5f2980314b1766656aeb544777db76296173ffc16708d725e7b691e4ad9aef3dbe9c544a5d33264c9b4bf36464bec32ae6960be72c0175d710333f7aa52e24fc774d1c8809c2730d381593214b51abf7a455354e56993eac5a536fbdda1f1530ca8a9b5816bb47f0a5cf60081462aef48c8a68c761cd15d01f53eabc10aa4b90f47fac18ee8094d1613195277120a85efc6a0c9e2dbbb619f520c59ee74a7be84b2ae4177ece2e10f18617bfb926eade8537993f16fbd28e4a95e3bf7acf381b847171e0a03c241c5c20b5cfb021f69903b9afa4ce40d2bf17b5b439b1014bb974becca815b268f209833dce8cdd4052020aee680a56d1eff7214fb36bbcd35a0674374df2a64e3c3f13c10f23c7d33d035f3a7c7525e7037868ef86681ce0f41d9376f0ac4b1176a939752e1b63cb5a49e9004ee6b9d797ee16dd7b5b97496b3c1f5c0fd792e28117887af78026eb8422077e27d32fb0dba7025d870e8db7fa4e6abfb221abe9b1997ab808c07220329e0ec7863dfcf0c1c1931c4f0061015b902a6d65e59ca8a9252dcf4eeeac3cdfbbf4664a356d6f05e031bcd9cc3223d10425a03bacbe2f49d3f54bd2288f64c9812a5c255e6c11a4dd46255c3a9f2bed34b61bbd849bcf1f007d5f4e3f6e60064b372e0ac6ab301163393adb10d9aa47fe6be211b3576ff37da7e12e2285358267495ac48a437d4eefb3213	RSA/8, Mon Aug 16 11:14:17 2010, Key ID 199e2f91fd431d51
""".strip()

ERROR_DB = '''
error: rpmdbNextIterator: skipping h#     753 Header V3 DSA signature: BAD, key ID db42a6
yum-security-1.1.16-21.el5.noarch
'''.strip()


def test_installed_rpms():
    rpms = InstalledRpms.parse_context(context_wrap(RPMS))
    assert rpms.get_max("ConsoleKit")["arch"] == 'x86_64'
    assert rpms.get_max("kernel")["version"] == '2.6.32'
    assert rpms.get_max("yum")["release"] == '69.el6'
    assert rpms.get_max("tftp-server")["version"] == '5.2'
    assert rpms.get_max("yum").package == "yum-3.2.29-69.el6"
    assert rpms.corrupt is False


def test_corrupt_db():
    rpms = InstalledRpms.parse_context(context_wrap(ERROR_DB))
    assert "yum-security" in rpms
    assert rpms.corrupt is True
