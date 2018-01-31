# Change Log

## [3.0rc1](https://github.com/RedHatInsights/insights-core/tree/3.0rc1) (2018-01-30)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.71.0-217...3.0rc1)

## [insights-core-1.71.0-217](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.71.0-217) (2018-01-26)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.70.0-214...insights-core-1.71.0-217)

**Implemented enhancements:**

- Add parsers LvsAll, PvsAll, VgsAll and combiner LvmAll for getting LVM information for all accepted and rejected devices. [\#908](https://github.com/RedHatInsights/insights-core/pull/908) ([lonicerae](https://github.com/lonicerae))

**Fixed bugs:**

- Update --force-reregister messaging [\#703](https://github.com/RedHatInsights/insights-core/issues/703)

## [insights-core-1.70.0-214](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.70.0-214) (2018-01-23)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.69.0-211...insights-core-1.70.0-214)

**Merged pull requests:**

- Added combiner NetworkStats [\#903](https://github.com/RedHatInsights/insights-core/pull/903) ([vishwanathjadhav](https://github.com/vishwanathjadhav))

## [insights-core-1.69.0-211](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.69.0-211) (2018-01-19)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.68.0-203...insights-core-1.69.0-211)

**Implemented enhancements:**

- Rabbitmq improvements 1.x [\#829](https://github.com/RedHatInsights/insights-core/pull/829) ([PaulWay](https://github.com/PaulWay))
- Hammer task list parser for 1.x branch [\#826](https://github.com/RedHatInsights/insights-core/pull/826) ([PaulWay](https://github.com/PaulWay))

**Fixed bugs:**

- Client log file rotation issues [\#710](https://github.com/RedHatInsights/insights-core/issues/710)
- Client Crashes on Fedora 26 [\#706](https://github.com/RedHatInsights/insights-core/issues/706)
- Fix fallback in 1.x and 3.x version of the client [\#695](https://github.com/RedHatInsights/insights-core/issues/695)

**Merged pull requests:**

- take into account rotated logs of directory server [\#901](https://github.com/RedHatInsights/insights-core/pull/901) ([germanparente](https://github.com/germanparente))
- Add ovs other config parser 1.x [\#899](https://github.com/RedHatInsights/insights-core/pull/899) ([chenlizhong](https://github.com/chenlizhong))
- Add 3 new parsers SystemctlShowPulp\* [\#887](https://github.com/RedHatInsights/insights-core/pull/887) ([TripleJQK](https://github.com/TripleJQK))
- Updating documentation with current doctest usage code and discussion [\#845](https://github.com/RedHatInsights/insights-core/pull/845) ([PaulWay](https://github.com/PaulWay))

## [insights-core-1.68.0-203](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.68.0-203) (2018-01-11)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.67.0-188...insights-core-1.68.0-203)

**Closed issues:**

- Parser for command output ip -s link \#859 [\#864](https://github.com/RedHatInsights/insights-core/issues/864)
- Add CPU flags to cpuinfo parser \#816 [\#837](https://github.com/RedHatInsights/insights-core/issues/837)

**Merged pull requests:**

- Parser net snmp ipv6 [\#883](https://github.com/RedHatInsights/insights-core/pull/883) ([vishwanathjadhav](https://github.com/vishwanathjadhav))
- Add debug files to detect Spectre/Meltdown mitigation [\#882](https://github.com/RedHatInsights/insights-core/pull/882) ([kgrant-rh](https://github.com/kgrant-rh))
- \[docs\_example\_1.x\] Fixed same 'ListenAddress' in assertion [\#877](https://github.com/RedHatInsights/insights-core/pull/877) ([psachin](https://github.com/psachin))
- Modify \_parse\_dom\(\) method to public [\#873](https://github.com/RedHatInsights/insights-core/pull/873) ([zhangyi733](https://github.com/zhangyi733))
- \[doc\] Fixed missing 'self' as parameter in parse\_content\(\) [\#871](https://github.com/RedHatInsights/insights-core/pull/871) ([psachin](https://github.com/psachin))
- Update the init of XMLParser to get xmlns before parseing dom [\#870](https://github.com/RedHatInsights/insights-core/pull/870) ([xiangce](https://github.com/xiangce))
- Parser net snmp [\#868](https://github.com/RedHatInsights/insights-core/pull/868) ([vishwanathjadhav](https://github.com/vishwanathjadhav))
- Update nginx\_conf spec for different nginx.conf paths [\#866](https://github.com/RedHatInsights/insights-core/pull/866) ([wushiqinlou](https://github.com/wushiqinlou))
- Delete the decorator on GrubConf that already fixed in plugins [\#861](https://github.com/RedHatInsights/insights-core/pull/861) ([xiangce](https://github.com/xiangce))
- Move code from upstream to insights/contrib [\#860](https://github.com/RedHatInsights/insights-core/pull/860) ([wushiqinlou](https://github.com/wushiqinlou))
- Parser for command output ip -s link [\#859](https://github.com/RedHatInsights/insights-core/pull/859) ([vishwanathjadhav](https://github.com/vishwanathjadhav))
- Update TomcatWebXml for 1.x [\#856](https://github.com/RedHatInsights/insights-core/pull/856) ([xiangce](https://github.com/xiangce))
- Add xml file base class [\#855](https://github.com/RedHatInsights/insights-core/pull/855) ([zhangyi733](https://github.com/zhangyi733))
- Add parser - foreman-ssl\_access\_ssl.log [\#846](https://github.com/RedHatInsights/insights-core/pull/846) ([sagaraivale](https://github.com/sagaraivale))

## [insights-core-1.67.0-188](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.67.0-188) (2018-01-02)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.66.0-177...insights-core-1.67.0-188)

**Implemented enhancements:**

- Backporting cmd\_names property to 1.x for compatiblity with master [\#848](https://github.com/RedHatInsights/insights-core/pull/848) ([PaulWay](https://github.com/PaulWay))

**Merged pull requests:**

- Enhance parser nginx\_conf 1x [\#857](https://github.com/RedHatInsights/insights-core/pull/857) ([wushiqinlou](https://github.com/wushiqinlou))
- Merge CatalinaOut and CatalinaServerLog to catalina\_log [\#853](https://github.com/RedHatInsights/insights-core/pull/853) ([xiangce](https://github.com/xiangce))
- Enhance parser nginx\_conf\_1x [\#852](https://github.com/RedHatInsights/insights-core/pull/852) ([wushiqinlou](https://github.com/wushiqinlou))
- Update tuned-adm path for both RHEL6 and RHEL7 for 1.x [\#844](https://github.com/RedHatInsights/insights-core/pull/844) ([mhuth](https://github.com/mhuth))
- CPU feature flags for 1.x [\#843](https://github.com/RedHatInsights/insights-core/pull/843) ([kgrant-rh](https://github.com/kgrant-rh))
- Added non-recursive spec for /var/www. [\#835](https://github.com/RedHatInsights/insights-core/pull/835) ([jsvob](https://github.com/jsvob))
- Add parser for nginx.conf 1x [\#820](https://github.com/RedHatInsights/insights-core/pull/820) ([wushiqinlou](https://github.com/wushiqinlou))
- Doctest example code - part A - for 1.x branch [\#817](https://github.com/RedHatInsights/insights-core/pull/817) ([PaulWay](https://github.com/PaulWay))

## [insights-core-1.66.0-177](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.66.0-177) (2017-12-18)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.65.0-166...insights-core-1.66.0-177)

**Implemented enhancements:**

- De-duplicate `ps` parsers [\#382](https://github.com/RedHatInsights/insights-core/issues/382)
- DeprecationWarnings are now non-fatal and are the only type of deprecation - for 1.x branch [\#819](https://github.com/RedHatInsights/insights-core/pull/819) ([PaulWay](https://github.com/PaulWay))
- Adding 'get\_param' and 'get\_last' methods to NTP\_conf for 1.x branch [\#742](https://github.com/RedHatInsights/insights-core/pull/742) ([PaulWay](https://github.com/PaulWay))

**Fixed bugs:**

- Parser error in rabbitmq.py [\#786](https://github.com/RedHatInsights/insights-core/issues/786)

**Closed issues:**

- Nova\_log parser has no tests [\#797](https://github.com/RedHatInsights/insights-core/issues/797)
- ClusterConf should be an XML parser rather than based on LogFileOutput [\#177](https://github.com/RedHatInsights/insights-core/issues/177)

**Merged pull requests:**

- Deprecating OracleConfig parser - redone after \#819 - for 1.x branch [\#823](https://github.com/RedHatInsights/insights-core/pull/823) ([PaulWay](https://github.com/PaulWay))
- Revert "Marked OracleConfig as deprecated, removed tests" [\#821](https://github.com/RedHatInsights/insights-core/pull/821) ([xiangce](https://github.com/xiangce))
- Nfnetlink queue documentation for 1.x branch [\#814](https://github.com/RedHatInsights/insights-core/pull/814) ([PaulWay](https://github.com/PaulWay))
- Change mongod related specs to allow multi files parsing [\#773](https://github.com/RedHatInsights/insights-core/pull/773) ([JoySnow](https://github.com/JoySnow))
- Deprecating other Sysconfig parsers in favour of those in sysconfig module [\#737](https://github.com/RedHatInsights/insights-core/pull/737) ([PaulWay](https://github.com/PaulWay))
- Marked LimitsConf and NprocConf as deprecated, use limits\_conf instead [\#734](https://github.com/RedHatInsights/insights-core/pull/734) ([PaulWay](https://github.com/PaulWay))
- Marked OracleConfig as deprecated, removed tests [\#733](https://github.com/RedHatInsights/insights-core/pull/733) ([PaulWay](https://github.com/PaulWay))
- Marked cpuinfo\_max\_freq as deprecated, removed tests [\#732](https://github.com/RedHatInsights/insights-core/pull/732) ([PaulWay](https://github.com/PaulWay))

## [insights-core-1.65.0-166](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.65.0-166) (2017-12-12)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.64.0-154...insights-core-1.65.0-166)

**Implemented enhancements:**

- Make remove.conf smarter [\#801](https://github.com/RedHatInsights/insights-core/issues/801)
- Ps parsers update for master branch \(\#744\) [\#793](https://github.com/RedHatInsights/insights-core/issues/793)
- Implement ACLs properly [\#712](https://github.com/RedHatInsights/insights-core/issues/712)
- Also parse the grub v1 config file for UEFI machine. [\#794](https://github.com/RedHatInsights/insights-core/pull/794) ([lonicerae](https://github.com/lonicerae))
- No bashisms in command for 1.x branch [\#764](https://github.com/RedHatInsights/insights-core/pull/764) ([PaulWay](https://github.com/PaulWay))
- Ps parsers update for 1.x branch [\#744](https://github.com/RedHatInsights/insights-core/pull/744) ([PaulWay](https://github.com/PaulWay))
- Document and tidy the ClusterConf parser for 1.x branch [\#743](https://github.com/RedHatInsights/insights-core/pull/743) ([PaulWay](https://github.com/PaulWay))

**Fixed bugs:**

- bug in Pvs parser and Lvm combiner [\#736](https://github.com/RedHatInsights/insights-core/issues/736)
- Fix bug in Pvs parser for duplicate devices [\#795](https://github.com/RedHatInsights/insights-core/pull/795) ([bfahr](https://github.com/bfahr))

**Closed issues:**

- Also parse the grub v1 config file for UEFI machine. \#794 [\#811](https://github.com/RedHatInsights/insights-core/issues/811)
- Added new parsers for two options under /sys/kernel/mm/transparent\_hugepage/. \#767 [\#769](https://github.com/RedHatInsights/insights-core/issues/769)
- Update Insights man pages [\#707](https://github.com/RedHatInsights/insights-core/issues/707)

**Merged pull requests:**

- Parser bond xmit hash policy [\#806](https://github.com/RedHatInsights/insights-core/pull/806) ([vishwanathjadhav](https://github.com/vishwanathjadhav))
- Add combiner HttpdV for RHEL6 for 1.x branch [\#800](https://github.com/RedHatInsights/insights-core/pull/800) ([xiangce](https://github.com/xiangce))
- Update openshift get to include the command oc get bc [\#776](https://github.com/RedHatInsights/insights-core/pull/776) ([shzhou12](https://github.com/shzhou12))
- Add parser for swift object-expirer.conf [\#772](https://github.com/RedHatInsights/insights-core/pull/772) ([chenlizhong](https://github.com/chenlizhong))
- SSH parser has a new method for detecting the "+" syntax [\#753](https://github.com/RedHatInsights/insights-core/pull/753) ([jsvob](https://github.com/jsvob))
- Deprecated get\_limits function, use LimitsConf class instead [\#735](https://github.com/RedHatInsights/insights-core/pull/735) ([PaulWay](https://github.com/PaulWay))

## [insights-core-1.64.0-154](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.64.0-154) (2017-11-30)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.3-2...insights-core-1.64.0-154)

**Implemented enhancements:**

- SkipComponent/SkipException Handling and Extension to Combiners [\#720](https://github.com/RedHatInsights/insights-core/issues/720)

**Fixed bugs:**

- Parse Error in `ntp\_sources.py` [\#727](https://github.com/RedHatInsights/insights-core/issues/727)
- Parser error in `ntp\_sources.py` [\#672](https://github.com/RedHatInsights/insights-core/issues/672)
- SysconfigKdump parser missing from master branch [\#670](https://github.com/RedHatInsights/insights-core/issues/670)
- satellite\_version combiner should not return None [\#658](https://github.com/RedHatInsights/insights-core/issues/658)
- Raise SkipComponent if unable to determine Satellite version [\#751](https://github.com/RedHatInsights/insights-core/pull/751) ([PaulWay](https://github.com/PaulWay))

**Closed issues:**

- Add parser audit\_log.py to 3.x [\#685](https://github.com/RedHatInsights/insights-core/issues/685)

**Merged pull requests:**

- Modify fc-match to make it only run on RHEL7 [\#768](https://github.com/RedHatInsights/insights-core/pull/768) ([zhangyi733](https://github.com/zhangyi733))
- Added new parsers for two options under /sys/kernel/mm/transparent\_hugepage/. [\#767](https://github.com/RedHatInsights/insights-core/pull/767) ([jsvob](https://github.com/jsvob))
- Revert "Modify fc-match command to make it work only on RHEL7" [\#763](https://github.com/RedHatInsights/insights-core/pull/763) ([xiangce](https://github.com/xiangce))
- Update exception\_model docs to include SkipComponent. [\#762](https://github.com/RedHatInsights/insights-core/pull/762) ([csams](https://github.com/csams))
- Add parser catalina\_server\_log to parser default catalina log file [\#761](https://github.com/RedHatInsights/insights-core/pull/761) ([zhangyi733](https://github.com/zhangyi733))
- Ignore new errors in flake8 3.5.0 [\#758](https://github.com/RedHatInsights/insights-core/pull/758) ([bfahr](https://github.com/bfahr))
- Modify fc-match command to make it work only on RHEL7 [\#757](https://github.com/RedHatInsights/insights-core/pull/757) ([zhangyi733](https://github.com/zhangyi733))
- Add SkipComponent and correctly ignore it for all component types [\#755](https://github.com/RedHatInsights/insights-core/pull/755) ([csams](https://github.com/csams))
- Remove --type option from docker inspect specs items [\#749](https://github.com/RedHatInsights/insights-core/pull/749) ([wushiqinlou](https://github.com/wushiqinlou))
- Fix bug for "NtpqLeap has no attribute 'data'" [\#728](https://github.com/RedHatInsights/insights-core/pull/728) ([xiangce](https://github.com/xiangce))

## [insights-core-3.0.3-2](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.3-2) (2017-11-21)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.63.0-140...insights-core-3.0.3-2)

## [insights-core-1.63.0-140](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.63.0-140) (2017-11-21)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.62.0-129...insights-core-1.63.0-140)

**Implemented enhancements:**

- Completely test ethtool parsers for 1.x branch [\#645](https://github.com/RedHatInsights/insights-core/pull/645) ([PaulWay](https://github.com/PaulWay))
- LVM: Improved tests and code for near 100% test coverage for 1.x branch [\#639](https://github.com/RedHatInsights/insights-core/pull/639) ([PaulWay](https://github.com/PaulWay))
- Add 'deprecated' decorator to log use of deprecated parsers [\#361](https://github.com/RedHatInsights/insights-core/pull/361) ([PaulWay](https://github.com/PaulWay))

**Fixed bugs:**

- jaylin test [\#719](https://github.com/RedHatInsights/insights-core/issues/719)
- .cache.json is not updated correctly [\#715](https://github.com/RedHatInsights/insights-core/issues/715)
- xinetd.conf spec needs to match PatternSpec with xinetd.d for 1.x branch [\#638](https://github.com/RedHatInsights/insights-core/pull/638) ([PaulWay](https://github.com/PaulWay))

**Closed issues:**

- test [\#718](https://github.com/RedHatInsights/insights-core/issues/718)

**Merged pull requests:**

- Fixed a bug when parsing the status code in ntptime. [\#721](https://github.com/RedHatInsights/insights-core/pull/721) ([lonicerae](https://github.com/lonicerae))
- changes to tmpfilesd combiner for 1x to work properly [\#716](https://github.com/RedHatInsights/insights-core/pull/716) ([SteveHNH](https://github.com/SteveHNH))
- Unpack list of parsers in the TomcatVirtualDirContextCombined combiner [\#713](https://github.com/RedHatInsights/insights-core/pull/713) ([skontar](https://github.com/skontar))
- Keyword search in Netstat parser for 1.x branch [\#625](https://github.com/RedHatInsights/insights-core/pull/625) ([PaulWay](https://github.com/PaulWay))

## [insights-core-1.62.0-129](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.62.0-129) (2017-11-13)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.61.0-127...insights-core-1.62.0-129)

**Fixed bugs:**

- Raise Exception instead of return None for satellite\_version [\#693](https://github.com/RedHatInsights/insights-core/pull/693) ([xiangce](https://github.com/xiangce))

## [insights-core-1.61.0-127](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.61.0-127) (2017-11-10)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.60.0-117...insights-core-1.61.0-127)

**Fixed bugs:**

- Incorrect use of optional dependencies in combiners [\#647](https://github.com/RedHatInsights/insights-core/issues/647)

**Closed issues:**

- Update docs and create PR for master branch for libkeyutils parser [\#643](https://github.com/RedHatInsights/insights-core/issues/643)

**Merged pull requests:**

- Fix manila configuration file path [\#691](https://github.com/RedHatInsights/insights-core/pull/691) ([pratikgadiya12](https://github.com/pratikgadiya12))
- Add manila config parser [\#687](https://github.com/RedHatInsights/insights-core/pull/687) ([pratikgadiya12](https://github.com/pratikgadiya12))
- add spec, parser, and combiner for tmpfilesd [\#684](https://github.com/RedHatInsights/insights-core/pull/684) ([SteveHNH](https://github.com/SteveHNH))
- Changes to support pypi releases [\#668](https://github.com/RedHatInsights/insights-core/pull/668) ([kylape](https://github.com/kylape))
- Fix the spec of installed\_rpm [\#665](https://github.com/RedHatInsights/insights-core/pull/665) ([shzhou12](https://github.com/shzhou12))
- Fix documentation and parsing algorithm for libkeyutils parser [\#661](https://github.com/RedHatInsights/insights-core/pull/661) ([skontar](https://github.com/skontar))
- Fix spec command for tomcat\_virtual\_dir\_context [\#651](https://github.com/RedHatInsights/insights-core/pull/651) ([skontar](https://github.com/skontar))
- Add parser for file /var/log/audit/audit.log [\#646](https://github.com/RedHatInsights/insights-core/pull/646) ([JoySnow](https://github.com/JoySnow))

## [insights-core-1.60.0-117](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.60.0-117) (2017-11-01)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.59.0-113...insights-core-1.60.0-117)

**Closed issues:**

- Port Scaffold Script to Master Branch [\#254](https://github.com/RedHatInsights/insights-core/issues/254)

**Merged pull requests:**

- Modify blkid item in specs.py to make it work both in rhel 6 and 7 [\#648](https://github.com/RedHatInsights/insights-core/pull/648) ([zhangyi733](https://github.com/zhangyi733))
- Add new path in candlepin\_error\_log spec file [\#606](https://github.com/RedHatInsights/insights-core/pull/606) ([sagaraivale](https://github.com/sagaraivale))

## [insights-core-1.59.0-113](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.59.0-113) (2017-10-27)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.58.0-107...insights-core-1.59.0-113)

**Implemented enhancements:**

- Make parser catalogue heading lines consistent for 1.x branch [\#627](https://github.com/RedHatInsights/insights-core/pull/627) ([PaulWay](https://github.com/PaulWay))
- SelinuxConfig parser docs and enhancements for 1.x branch [\#624](https://github.com/RedHatInsights/insights-core/pull/624) ([PaulWay](https://github.com/PaulWay))

**Merged pull requests:**

- New specs and parsers for libkeyutils [\#642](https://github.com/RedHatInsights/insights-core/pull/642) ([skontar](https://github.com/skontar))
- Support Mac OS X [\#637](https://github.com/RedHatInsights/insights-core/pull/637) ([kylape](https://github.com/kylape))
- Add more `dig` commands for DNSSEC analysis [\#634](https://github.com/RedHatInsights/insights-core/pull/634) ([skontar](https://github.com/skontar))

## [insights-core-1.58.0-107](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.58.0-107) (2017-10-19)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.57.0-102...insights-core-1.58.0-107)

**Implemented enhancements:**

- Vsftpd parsers documentation for 1.x branch [\#619](https://github.com/RedHatInsights/insights-core/pull/619) ([PaulWay](https://github.com/PaulWay))

**Merged pull requests:**

- Remove the backslash for dots in the path of PatternSpecs [\#612](https://github.com/RedHatInsights/insights-core/pull/612) ([xiangce](https://github.com/xiangce))
- Add Parser for sysconfig\_mongod in branch 1.x [\#595](https://github.com/RedHatInsights/insights-core/pull/595) ([JoySnow](https://github.com/JoySnow))
- Add parser MongodConf at mongod\_conf.py [\#459](https://github.com/RedHatInsights/insights-core/pull/459) ([JoySnow](https://github.com/JoySnow))

## [insights-core-1.57.0-102](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.57.0-102) (2017-10-18)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.56.0-95...insights-core-1.57.0-102)

**Implemented enhancements:**

- De-duplicate util/parse\_table and parsers/parse\_fixed\_table [\#344](https://github.com/RedHatInsights/insights-core/issues/344)
- RcLocal parser documentation for 1.x branch [\#605](https://github.com/RedHatInsights/insights-core/pull/605) ([PaulWay](https://github.com/PaulWay))
- Resolv\_conf class documentation for 1.x branch [\#604](https://github.com/RedHatInsights/insights-core/pull/604) ([PaulWay](https://github.com/PaulWay))
- Use \_\_str\_\_ instead of \_\_repr\_\_ for informal object depictions for 1.x branch [\#601](https://github.com/RedHatInsights/insights-core/pull/601) ([PaulWay](https://github.com/PaulWay))
- Adding \_\_str\_\_ method to hostname for debugging purposes for 1.x branch [\#599](https://github.com/RedHatInsights/insights-core/pull/599) ([PaulWay](https://github.com/PaulWay))

**Closed issues:**

- Update yaml.load to yaml.safe\_load [\#316](https://github.com/RedHatInsights/insights-core/issues/316)

**Merged pull requests:**

- gen\_api supports multiple rule packages [\#597](https://github.com/RedHatInsights/insights-core/pull/597) ([jhjaggars](https://github.com/jhjaggars))
- InitScript parser and unit tests branch 1.x [\#580](https://github.com/RedHatInsights/insights-core/pull/580) ([rmetrich](https://github.com/rmetrich))

## [insights-core-1.56.0-95](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.56.0-95) (2017-10-12)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.55.0-90...insights-core-1.56.0-95)

**Implemented enhancements:**

- Catch unparseable lines in `bad\_lines` property for 1.x branch [\#589](https://github.com/RedHatInsights/insights-core/pull/589) ([PaulWay](https://github.com/PaulWay))
- Xfs\_info parser doc and code enhancements for 1.x branch [\#575](https://github.com/RedHatInsights/insights-core/pull/575) ([PaulWay](https://github.com/PaulWay))
- Fstab keyword search for 1.x branch [\#568](https://github.com/RedHatInsights/insights-core/pull/568) ([PaulWay](https://github.com/PaulWay))

**Fixed bugs:**

- limits\_conf "unlimitied" error [\#447](https://github.com/RedHatInsights/insights-core/issues/447)

## [insights-core-1.55.0-90](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.55.0-90) (2017-10-11)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.54.0-87...insights-core-1.55.0-90)

**Merged pull requests:**

- add total archive timing checks and handle error cases [\#584](https://github.com/RedHatInsights/insights-core/pull/584) ([jhjaggars](https://github.com/jhjaggars))
- add lssap spec and parser for 1x [\#583](https://github.com/RedHatInsights/insights-core/pull/583) ([SteveHNH](https://github.com/SteveHNH))

## [insights-core-1.54.0-87](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.54.0-87) (2017-10-11)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.53.0-81...insights-core-1.54.0-87)

**Merged pull requests:**

- Add parser ipaupgrade 1x [\#576](https://github.com/RedHatInsights/insights-core/pull/576) ([wushiqinlou](https://github.com/wushiqinlou))
- Add the missed `rqm -qf` to pre\_command `java\_command\_package` [\#574](https://github.com/RedHatInsights/insights-core/pull/574) ([xiangce](https://github.com/xiangce))
- Enhance parser and package\_provides\_java.py [\#572](https://github.com/RedHatInsights/insights-core/pull/572) ([zhangyi733](https://github.com/zhangyi733))
- making the slow threshold configurable [\#567](https://github.com/RedHatInsights/insights-core/pull/567) ([jhjaggars](https://github.com/jhjaggars))
- add more detail to error messages [\#566](https://github.com/RedHatInsights/insights-core/pull/566) ([jhjaggars](https://github.com/jhjaggars))

## [insights-core-1.53.0-81](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.53.0-81) (2017-10-10)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.52.0-71...insights-core-1.53.0-81)

**Implemented enhancements:**

- Rename parse\_table to parse\_delimited\_table and move to parsers for 1.x branch [\#445](https://github.com/RedHatInsights/insights-core/pull/445) ([PaulWay](https://github.com/PaulWay))
- Modprobe combiner for 1.x branch [\#430](https://github.com/RedHatInsights/insights-core/pull/430) ([PaulWay](https://github.com/PaulWay))

**Merged pull requests:**

- adding time measurements for parsers and reducers [\#563](https://github.com/RedHatInsights/insights-core/pull/563) ([jhjaggars](https://github.com/jhjaggars))
- Add TomcatVirtualDirContext [\#562](https://github.com/RedHatInsights/insights-core/pull/562) ([skontar](https://github.com/skontar))
- Add parser package\_provides\_java.py in 1.x branch [\#558](https://github.com/RedHatInsights/insights-core/pull/558) ([zhangyi733](https://github.com/zhangyi733))
- Add tomcat to `ps\_aux` filter [\#554](https://github.com/RedHatInsights/insights-core/pull/554) ([skontar](https://github.com/skontar))
- Enhance combiner krb5 1x [\#553](https://github.com/RedHatInsights/insights-core/pull/553) ([wushiqinlou](https://github.com/wushiqinlou))
- Add case\_variant utility function [\#550](https://github.com/RedHatInsights/insights-core/pull/550) ([kylape](https://github.com/kylape))

## [insights-core-1.52.0-71](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.52.0-71) (2017-10-06)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.2-6...insights-core-1.52.0-71)

**Implemented enhancements:**

- Improvements to the LSBlock and LSBlockPairs parsers for 1.x branch [\#498](https://github.com/RedHatInsights/insights-core/pull/498) ([PaulWay](https://github.com/PaulWay))

**Merged pull requests:**

- Handle missing option in /etc/sysconfig/selinux [\#547](https://github.com/RedHatInsights/insights-core/pull/547) ([skontar](https://github.com/skontar))
- add parse\_table functionality to 1.x [\#539](https://github.com/RedHatInsights/insights-core/pull/539) ([SteveHNH](https://github.com/SteveHNH))

## [insights-core-3.0.2-6](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.2-6) (2017-10-04)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.1-1...insights-core-3.0.2-6)

## [insights-core-3.0.1-1](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.1-1) (2017-10-03)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.0-5...insights-core-3.0.1-1)

## [insights-core-3.0.0-5](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.0-5) (2017-10-03)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.51.0-65...insights-core-3.0.0-5)

## [insights-core-1.51.0-65](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.51.0-65) (2017-09-29)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.50.0-56...insights-core-1.51.0-65)

**Implemented enhancements:**

- Mount keyword search for 1.x branch [\#493](https://github.com/RedHatInsights/insights-core/pull/493) ([PaulWay](https://github.com/PaulWay))
- Add `get\_dir` method to find mount point for given directory [\#492](https://github.com/RedHatInsights/insights-core/pull/492) ([PaulWay](https://github.com/PaulWay))

**Merged pull requests:**

- Put the new NovaComputeLog to nova\_log.py [\#532](https://github.com/RedHatInsights/insights-core/pull/532) ([xiangce](https://github.com/xiangce))
- Add nova\_compute\_log parser [\#531](https://github.com/RedHatInsights/insights-core/pull/531) ([chenlizhong](https://github.com/chenlizhong))
- Enhance the `limits` parser for `httpd` [\#526](https://github.com/RedHatInsights/insights-core/pull/526) ([xiangce](https://github.com/xiangce))
- New parser httpd\_limits [\#520](https://github.com/RedHatInsights/insights-core/pull/520) ([xiangce](https://github.com/xiangce))
- Add QemuConf class to parse /etc/libvirt/qemu.conf [\#519](https://github.com/RedHatInsights/insights-core/pull/519) ([chenlizhong](https://github.com/chenlizhong))
- Add parser smbstatus 1x [\#501](https://github.com/RedHatInsights/insights-core/pull/501) ([wushiqinlou](https://github.com/wushiqinlou))

## [insights-core-1.50.0-56](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.50.0-56) (2017-09-26)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.49.0-38...insights-core-1.50.0-56)

**Implemented enhancements:**

- Rework core runtime to be like vulcan [\#11](https://github.com/RedHatInsights/insights-core/issues/11)
- Support Python Version 2.6.x [\#10](https://github.com/RedHatInsights/insights-core/issues/10)

**Closed issues:**

- Should probably rename hand\_map\_error and handle\_reduce\_error in evaluators.py [\#66](https://github.com/RedHatInsights/insights-core/issues/66)
- Drop support for local mappers [\#7](https://github.com/RedHatInsights/insights-core/issues/7)

**Merged pull requests:**

- Unescape dots in PatternSpec files [\#488](https://github.com/RedHatInsights/insights-core/pull/488) ([kylape](https://github.com/kylape))
- Re-structure the parsers for file under `/etc/sysconfig/` [\#486](https://github.com/RedHatInsights/insights-core/pull/486) ([xiangce](https://github.com/xiangce))
- Document rhn schema version - 1.x [\#484](https://github.com/RedHatInsights/insights-core/pull/484) ([xiangce](https://github.com/xiangce))
- Add parser fc match 1 x [\#483](https://github.com/RedHatInsights/insights-core/pull/483) ([zhangyi733](https://github.com/zhangyi733))
- Add parser for 'candlepin/error.log' [\#476](https://github.com/RedHatInsights/insights-core/pull/476) ([sagaraivale](https://github.com/sagaraivale))
- New parser and combiner for virt-who configuration [\#474](https://github.com/RedHatInsights/insights-core/pull/474) ([xiangce](https://github.com/xiangce))
- Added Filters column to Report to list filters [\#464](https://github.com/RedHatInsights/insights-core/pull/464) ([lhuett](https://github.com/lhuett))
- Add nova crontab parser [\#458](https://github.com/RedHatInsights/insights-core/pull/458) ([chenlizhong](https://github.com/chenlizhong))
- Add md5 check for configuration file /etc/fonts/fonts.conf [\#455](https://github.com/RedHatInsights/insights-core/pull/455) ([zhangyi733](https://github.com/zhangyi733))
- Add attributes' docstring for krb5 parser [\#453](https://github.com/RedHatInsights/insights-core/pull/453) ([xiangce](https://github.com/xiangce))
- Refine the docstring in test/\_init\_.py [\#452](https://github.com/RedHatInsights/insights-core/pull/452) ([xiangce](https://github.com/xiangce))
- New parser for 'journal\_since\_boot' \('sos\_commands/logs/journalctl\_…'\) [\#446](https://github.com/RedHatInsights/insights-core/pull/446) ([rmetrich](https://github.com/rmetrich))
- changed local addr parsing to account for ipv6 addrs [\#443](https://github.com/RedHatInsights/insights-core/pull/443) ([jeudy100](https://github.com/jeudy100))
- Net stat parser [\#437](https://github.com/RedHatInsights/insights-core/pull/437) ([vishwanathjadhav](https://github.com/vishwanathjadhav))
- Fix bug when parsing parameters which presented in both solo format and key-value format. [\#422](https://github.com/RedHatInsights/insights-core/pull/422) ([lonicerae](https://github.com/lonicerae))
- Add combiner krb5 1x [\#417](https://github.com/RedHatInsights/insights-core/pull/417) ([wushiqinlou](https://github.com/wushiqinlou))

## [insights-core-1.49.0-38](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.49.0-38) (2017-09-15)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.49.0-37...insights-core-1.49.0-38)

**Fixed bugs:**

- chkconfig.py can not parsed RHEL 7.3 'chkconfig --list' [\#112](https://github.com/RedHatInsights/insights-core/issues/112)
- Vgdisplay spec does not match sos report or rule [\#13](https://github.com/RedHatInsights/insights-core/issues/13)

**Closed issues:**

- Get 100% test coverage of insights/core/\_\_init\_\_.py [\#139](https://github.com/RedHatInsights/insights-core/issues/139)

**Merged pull requests:**

- Fix `lvs\_noheadings` missed the "vg\_name" error [\#435](https://github.com/RedHatInsights/insights-core/pull/435) ([xiangce](https://github.com/xiangce))

## [insights-core-1.49.0-37](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.49.0-37) (2017-09-13)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.48.0-34...insights-core-1.49.0-37)

**Merged pull requests:**

- Remove the debug `print` and one more test for empty assignment - 1.x [\#426](https://github.com/RedHatInsights/insights-core/pull/426) ([xiangce](https://github.com/xiangce))

## [insights-core-1.48.0-34](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.48.0-34) (2017-09-12)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.47.0-17...insights-core-1.48.0-34)

**Implemented enhancements:**

- Crontab minor improvements back to 1.x branch [\#421](https://github.com/RedHatInsights/insights-core/pull/421) ([PaulWay](https://github.com/PaulWay))
- Fix path of Directory Server access and error logs for 1.x branch [\#408](https://github.com/RedHatInsights/insights-core/pull/408) ([PaulWay](https://github.com/PaulWay))
- Make raw options string available for 1.x branch [\#390](https://github.com/RedHatInsights/insights-core/pull/390) ([PaulWay](https://github.com/PaulWay))
- More debugging on run\_parsers for 1.x branch [\#375](https://github.com/RedHatInsights/insights-core/pull/375) ([PaulWay](https://github.com/PaulWay))
- Added `strip\_quotes` option to optlist\_to\_dict for 1.x branch [\#374](https://github.com/RedHatInsights/insights-core/pull/374) ([PaulWay](https://github.com/PaulWay))

**Closed issues:**

- Sync the master branch with 1.x branch [\#121](https://github.com/RedHatInsights/insights-core/issues/121)

**Merged pull requests:**

- add swift\_conf parser module [\#416](https://github.com/RedHatInsights/insights-core/pull/416) ([chenlizhong](https://github.com/chenlizhong))
- Enhance parser scsi [\#405](https://github.com/RedHatInsights/insights-core/pull/405) ([JoySnow](https://github.com/JoySnow))
- Enhance class Ethtool with two more ParseExceptions cases [\#403](https://github.com/RedHatInsights/insights-core/pull/403) ([JoySnow](https://github.com/JoySnow))
- RHEL 7.4 is released, update Uname correspondingly [\#400](https://github.com/RedHatInsights/insights-core/pull/400) ([xiangce](https://github.com/xiangce))
- handle multiple lines of output with the mlx4 parser [\#396](https://github.com/RedHatInsights/insights-core/pull/396) ([jhjaggars](https://github.com/jhjaggars))
- Refine the satellite\_version as per the latest version map - 1.x [\#395](https://github.com/RedHatInsights/insights-core/pull/395) ([xiangce](https://github.com/xiangce))
- Updating pcs\_status class to show bad nodes, aka nodes that for 1.x [\#394](https://github.com/RedHatInsights/insights-core/pull/394) ([xiangce](https://github.com/xiangce))
- Add parser krb5 1.x [\#388](https://github.com/RedHatInsights/insights-core/pull/388) ([wushiqinlou](https://github.com/wushiqinlou))
- Standard Import Hooks for Fava [\#323](https://github.com/RedHatInsights/insights-core/pull/323) ([csams](https://github.com/csams))

## [insights-core-1.47.0-17](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.47.0-17) (2017-08-31)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.46.0-15...insights-core-1.47.0-17)

## [insights-core-1.46.0-15](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.46.0-15) (2017-08-30)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.46.0-12...insights-core-1.46.0-15)

**Merged pull requests:**

- New parser to get info whether there are numeric user or group names. [\#331](https://github.com/RedHatInsights/insights-core/pull/331) ([jsvob](https://github.com/jsvob))

## [insights-core-1.46.0-12](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.46.0-12) (2017-08-28)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.44.0-105...insights-core-1.46.0-12)

**Implemented enhancements:**

- Added keyword search to PAM configuration parser [\#358](https://github.com/RedHatInsights/insights-core/pull/358) ([PaulWay](https://github.com/PaulWay))
- Add specs for pam.conf and oc\_get\_pvc for 1.x branch [\#357](https://github.com/RedHatInsights/insights-core/pull/357) ([PaulWay](https://github.com/PaulWay))
- Crontab parser improvements for 1.x branch [\#355](https://github.com/RedHatInsights/insights-core/pull/355) ([PaulWay](https://github.com/PaulWay))
- Simplify rhn.conf parsing using new unsplit\_lines keep\_cont\_char option [\#354](https://github.com/RedHatInsights/insights-core/pull/354) ([PaulWay](https://github.com/PaulWay))
- Enhance unsplit\_lines to allow keeping continuation character for 1.x branch [\#348](https://github.com/RedHatInsights/insights-core/pull/348) ([PaulWay](https://github.com/PaulWay))
- RHNConf documentation for 1.x branch [\#347](https://github.com/RedHatInsights/insights-core/pull/347) ([PaulWay](https://github.com/PaulWay))
- Add SkipException for dirty parsers [\#336](https://github.com/RedHatInsights/insights-core/pull/336) ([bfahr](https://github.com/bfahr))
- Parser for `getcert list` for 1.x branch [\#328](https://github.com/RedHatInsights/insights-core/pull/328) ([PaulWay](https://github.com/PaulWay))
- More features added to keyword\_search [\#326](https://github.com/RedHatInsights/insights-core/pull/326) ([PaulWay](https://github.com/PaulWay))
- SMARTctl documentation and improved functionality for 1.x branch [\#299](https://github.com/RedHatInsights/insights-core/pull/299) ([PaulWay](https://github.com/PaulWay))

**Fixed bugs:**

- Enhance specs docker inspect 1x [\#368](https://github.com/RedHatInsights/insights-core/pull/368) ([wushiqinlou](https://github.com/wushiqinlou))

**Closed issues:**

- CertificatesEnddate fails to parse filenames [\#300](https://github.com/RedHatInsights/insights-core/issues/300)

**Merged pull requests:**

- cleaned up the fava related integration tests [\#372](https://github.com/RedHatInsights/insights-core/pull/372) ([gavin-romig-koch](https://github.com/gavin-romig-koch))
- Remove filter in nfs\_exports.py [\#350](https://github.com/RedHatInsights/insights-core/pull/350) ([zhangyi733](https://github.com/zhangyi733))
- convert unittest to pytest in test\_fava [\#342](https://github.com/RedHatInsights/insights-core/pull/342) ([gavin-romig-koch](https://github.com/gavin-romig-koch))
- Escape literal dots in pattern specs [\#339](https://github.com/RedHatInsights/insights-core/pull/339) ([kylape](https://github.com/kylape))
- Fix broken spec cmd of certificates\_enddate.py [\#335](https://github.com/RedHatInsights/insights-core/pull/335) ([JoySnow](https://github.com/JoySnow))
- Enhance config systemd 1x [\#333](https://github.com/RedHatInsights/insights-core/pull/333) ([wushiqinlou](https://github.com/wushiqinlou))
- bugfix: make jinja2 a runtime dep rather than a develop dep. [\#332](https://github.com/RedHatInsights/insights-core/pull/332) ([gavin-romig-koch](https://github.com/gavin-romig-koch))
- Fava - add when with a list [\#322](https://github.com/RedHatInsights/insights-core/pull/322) ([gavin-romig-koch](https://github.com/gavin-romig-koch))
- Move and translate Fava\*.md files to docs/fava.rst [\#321](https://github.com/RedHatInsights/insights-core/pull/321) ([gavin-romig-koch](https://github.com/gavin-romig-koch))
- All parsers are now automatically available for use in Fava [\#320](https://github.com/RedHatInsights/insights-core/pull/320) ([gavin-romig-koch](https://github.com/gavin-romig-koch))
- Update specs file to change lvs\_noheadings [\#318](https://github.com/RedHatInsights/insights-core/pull/318) ([shzhou12](https://github.com/shzhou12))
- Make smb.conf parser evaluate the ini file the same as samba. [\#314](https://github.com/RedHatInsights/insights-core/pull/314) ([jsvob](https://github.com/jsvob))
- Enhance specs semid 1x [\#309](https://github.com/RedHatInsights/insights-core/pull/309) ([wushiqinlou](https://github.com/wushiqinlou))
- Add parser for /var/log/rhn/rhn\_server\_satellite.log [\#305](https://github.com/RedHatInsights/insights-core/pull/305) ([sagaraivale](https://github.com/sagaraivale))
- Fix list index error in ps exception - 1x [\#303](https://github.com/RedHatInsights/insights-core/pull/303) ([xiangce](https://github.com/xiangce))
- New parser katello\_service\_status for 1.x [\#301](https://github.com/RedHatInsights/insights-core/pull/301) ([xiangce](https://github.com/xiangce))
- Enhance hammer\_ping for 1.x [\#294](https://github.com/RedHatInsights/insights-core/pull/294) ([xiangce](https://github.com/xiangce))
- Document the ``nproc`` and ``get\_limits`` as deprecated [\#277](https://github.com/RedHatInsights/insights-core/pull/277) ([xiangce](https://github.com/xiangce))
- Fava - an alternative, ansible like, way to write rule plugins [\#227](https://github.com/RedHatInsights/insights-core/pull/227) ([gavin-romig-koch](https://github.com/gavin-romig-koch))

## [insights-core-1.44.0-105](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.44.0-105) (2017-08-02)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.44.0-103...insights-core-1.44.0-105)

**Merged pull requests:**

- handle unicode characters in RPM name in InstalledRpm property [\#297](https://github.com/RedHatInsights/insights-core/pull/297) ([bobcallaway](https://github.com/bobcallaway))

## [insights-core-1.44.0-103](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.44.0-103) (2017-07-28)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.43.0-93...insights-core-1.44.0-103)

**Implemented enhancements:**

- NSSwitch\_Conf parser for /etc/nsswitch.conf for 1.x branch [\#281](https://github.com/RedHatInsights/insights-core/pull/281) ([PaulWay](https://github.com/PaulWay))
- Handle RHEL 7.3 `chkconfig` output [\#275](https://github.com/RedHatInsights/insights-core/pull/275) ([PaulWay](https://github.com/PaulWay))
- Improvements to VgDisplay for `vgdisplay -vv` command handling for 1.x branch [\#272](https://github.com/RedHatInsights/insights-core/pull/272) ([PaulWay](https://github.com/PaulWay))
- Add get\_dir\(\) method for the mount point associated with a path for 1.x branch [\#261](https://github.com/RedHatInsights/insights-core/pull/261) ([PaulWay](https://github.com/PaulWay))
- Improve testing and logic of `parted` parser for 1.x branch [\#217](https://github.com/RedHatInsights/insights-core/pull/217) ([PaulWay](https://github.com/PaulWay))
- Dmesg\_log parser add get\_after for 1.x branch [\#198](https://github.com/RedHatInsights/insights-core/pull/198) ([PaulWay](https://github.com/PaulWay))

**Fixed bugs:**

- Lvs mapper fails on lists with log and image LVs [\#288](https://github.com/RedHatInsights/insights-core/issues/288)
- Improvements to VgDisplay for `vgdisplay -vv` command handling for 1.x branch [\#272](https://github.com/RedHatInsights/insights-core/pull/272) ([PaulWay](https://github.com/PaulWay))

**Closed issues:**

- Move AlternativesOutput class and associated parsers into single file. [\#140](https://github.com/RedHatInsights/insights-core/issues/140)

**Merged pull requests:**

- Add crontab files from sosreport [\#278](https://github.com/RedHatInsights/insights-core/pull/278) ([abhaykadam](https://github.com/abhaykadam))
- Documentation restructure and cleanup for 1.x branch [\#271](https://github.com/RedHatInsights/insights-core/pull/271) ([bfahr](https://github.com/bfahr))
- remote branch and leaf should be numbers not strings [\#268](https://github.com/RedHatInsights/insights-core/pull/268) ([jhjaggars](https://github.com/jhjaggars))
- Enhance virt-what [\#262](https://github.com/RedHatInsights/insights-core/pull/262) ([xiangce](https://github.com/xiangce))

## [insights-core-1.43.0-93](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.43.0-93) (2017-07-18)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.42.0-63...insights-core-1.43.0-93)

**Implemented enhancements:**

- Support python 2.6 [\#180](https://github.com/RedHatInsights/insights-core/issues/180)
- Get \(basic\) config items from rsyslog configuration for 1.x branch [\#224](https://github.com/RedHatInsights/insights-core/pull/224) ([PaulWay](https://github.com/PaulWay))
- Test scannner functionality in LogFileOutput for 1.x branch [\#219](https://github.com/RedHatInsights/insights-core/pull/219) ([PaulWay](https://github.com/PaulWay))
- Catalina\_out parser add get\_after\(\) method for 1.x branch - This Time For Sure [\#216](https://github.com/RedHatInsights/insights-core/pull/216) ([PaulWay](https://github.com/PaulWay))
- Adding NTPConfParser base class to documentation for 1.x branch [\#215](https://github.com/RedHatInsights/insights-core/pull/215) ([PaulWay](https://github.com/PaulWay))
- Vdsm\_log parser gets full documentation and get\_after\(\) method for 1.x branch [\#214](https://github.com/RedHatInsights/insights-core/pull/214) ([PaulWay](https://github.com/PaulWay))
- Sssd\_logs parser add get\_after for 1.x branch [\#211](https://github.com/RedHatInsights/insights-core/pull/211) ([PaulWay](https://github.com/PaulWay))
- Libvirtd\_log parser add get\_after for 1.x branch [\#209](https://github.com/RedHatInsights/insights-core/pull/209) ([PaulWay](https://github.com/PaulWay))
- Keystone\_log parser add get\_after for 1.x branch [\#207](https://github.com/RedHatInsights/insights-core/pull/207) ([PaulWay](https://github.com/PaulWay))
- Httpd\_log parsers add get\_after for 1.x branch [\#206](https://github.com/RedHatInsights/insights-core/pull/206) ([PaulWay](https://github.com/PaulWay))
- Heat\_log parser add get\_after for 1.x branch [\#205](https://github.com/RedHatInsights/insights-core/pull/205) ([PaulWay](https://github.com/PaulWay))
- RHN\_logs parser add get\_after for 1.x branch [\#204](https://github.com/RedHatInsights/insights-core/pull/204) ([PaulWay](https://github.com/PaulWay))
- Rabbitmq\_log parser add get\_after for 1.x branch [\#203](https://github.com/RedHatInsights/insights-core/pull/203) ([PaulWay](https://github.com/PaulWay))
- Openvswitch\_logs parser add get\_after for 1.x branch [\#202](https://github.com/RedHatInsights/insights-core/pull/202) ([PaulWay](https://github.com/PaulWay))
- Neutron\_ovs\_agent\_log parser add get\_after for 1.x branch [\#201](https://github.com/RedHatInsights/insights-core/pull/201) ([PaulWay](https://github.com/PaulWay))
- Mariadb\_log parser add get\_after for 1.x branch [\#200](https://github.com/RedHatInsights/insights-core/pull/200) ([PaulWay](https://github.com/PaulWay))
- Cinder\_log parser add get\_after for 1.x branch [\#199](https://github.com/RedHatInsights/insights-core/pull/199) ([PaulWay](https://github.com/PaulWay))
- Engine\_log parser add get\_after for 1.x branch [\#197](https://github.com/RedHatInsights/insights-core/pull/197) ([PaulWay](https://github.com/PaulWay))
- Foreman\_log parser add get\_after for 1.x branch [\#196](https://github.com/RedHatInsights/insights-core/pull/196) ([PaulWay](https://github.com/PaulWay))
- Glance\_log parser add get\_after for 1.x branch [\#195](https://github.com/RedHatInsights/insights-core/pull/195) ([PaulWay](https://github.com/PaulWay))
- Secure log parser add get\_after for 1.x branch [\#194](https://github.com/RedHatInsights/insights-core/pull/194) ([PaulWay](https://github.com/PaulWay))
- Documentation for Postgresql\_log parser [\#193](https://github.com/RedHatInsights/insights-core/pull/193) ([PaulWay](https://github.com/PaulWay))
- Pacemaker\_log parser add get\_after for 1.x branch [\#192](https://github.com/RedHatInsights/insights-core/pull/192) ([PaulWay](https://github.com/PaulWay))
- Osa\_dispatcher\_log parser add get\_after for 1.x branch [\#191](https://github.com/RedHatInsights/insights-core/pull/191) ([PaulWay](https://github.com/PaulWay))
- Ceph\_osd\_log parser add get\_after for 1.x branch [\#190](https://github.com/RedHatInsights/insights-core/pull/190) ([PaulWay](https://github.com/PaulWay))
- Ceilometer\_log parser add get\_after for 1.x branch [\#189](https://github.com/RedHatInsights/insights-core/pull/189) ([PaulWay](https://github.com/PaulWay))
- Nova\_api\_log parser add get\_after for 1.x branch [\#188](https://github.com/RedHatInsights/insights-core/pull/188) ([PaulWay](https://github.com/PaulWay))
- Log file output get after improvements for 1.x branch [\#186](https://github.com/RedHatInsights/insights-core/pull/186) ([PaulWay](https://github.com/PaulWay))

**Closed issues:**

- Add new shared parser irqbalance\_conf.py \#213 [\#223](https://github.com/RedHatInsights/insights-core/issues/223)
- Should we convert this multinode parser \(metadata.json\) to class type ? [\#221](https://github.com/RedHatInsights/insights-core/issues/221)
- NTPConfParser class is missing from the documentation [\#167](https://github.com/RedHatInsights/insights-core/issues/167)
- Neutron server log documentation for 1.x branch \#146 [\#152](https://github.com/RedHatInsights/insights-core/issues/152)
- Neutron plugin documentation for 1.x branch \#145 [\#151](https://github.com/RedHatInsights/insights-core/issues/151)
- Test scannable parser class for 1.x branch \#144 [\#150](https://github.com/RedHatInsights/insights-core/issues/150)
- Remove the deprecated `.data` from LsBoot \#103 [\#104](https://github.com/RedHatInsights/insights-core/issues/104)
- Limits conf combiner \#70 [\#85](https://github.com/RedHatInsights/insights-core/issues/85)

**Merged pull requests:**

- Alternatives output into parser module 1.x [\#255](https://github.com/RedHatInsights/insights-core/pull/255) ([PaulWay](https://github.com/PaulWay))
- INSIGHTS\_OSP: Added parser for systemctl list-units [\#220](https://github.com/RedHatInsights/insights-core/pull/220) ([vishwanathjadhav](https://github.com/vishwanathjadhav))
- Add new shared parser irqbalance\_conf.py [\#213](https://github.com/RedHatInsights/insights-core/pull/213) ([lonicerae](https://github.com/lonicerae))
- Change the wildcard \* to pre\_command for sysctl.conf\_initramfs spec [\#184](https://github.com/RedHatInsights/insights-core/pull/184) ([xiangce](https://github.com/xiangce))
- Add pre-command for shared-mapper dumpe2fs-h [\#181](https://github.com/RedHatInsights/insights-core/pull/181) ([zhangyi733](https://github.com/zhangyi733))
- Update the parser 'ceph\_version' to add version2.3 [\#178](https://github.com/RedHatInsights/insights-core/pull/178) ([shzhou12](https://github.com/shzhou12))
- 389 Directory server spec fix [\#173](https://github.com/RedHatInsights/insights-core/pull/173) ([PaulWay](https://github.com/PaulWay))
- update the shared parser "teamdctl\_state\_dump.py" [\#170](https://github.com/RedHatInsights/insights-core/pull/170) ([xiaoyu74](https://github.com/xiaoyu74))
- Add 'macpools' field into RHEV metadata [\#161](https://github.com/RedHatInsights/insights-core/pull/161) ([JoySnow](https://github.com/JoySnow))
- Neutron server log documentation for 1.x branch [\#146](https://github.com/RedHatInsights/insights-core/pull/146) ([PaulWay](https://github.com/PaulWay))
- Neutron plugin documentation for 1.x branch [\#145](https://github.com/RedHatInsights/insights-core/pull/145) ([PaulWay](https://github.com/PaulWay))
- Test scannable parser class for 1.x branch [\#144](https://github.com/RedHatInsights/insights-core/pull/144) ([PaulWay](https://github.com/PaulWay))
- Remove the deprecated `.data` from LsBoot [\#103](https://github.com/RedHatInsights/insights-core/pull/103) ([xiangce](https://github.com/xiangce))
- Limits\_conf combiner for 1.x branch [\#95](https://github.com/RedHatInsights/insights-core/pull/95) ([PaulWay](https://github.com/PaulWay))

## [insights-core-1.42.0-63](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.42.0-63) (2017-07-03)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.41.0-43...insights-core-1.42.0-63)

**Closed issues:**

- Parser module test coverage at 100% \#148 [\#154](https://github.com/RedHatInsights/insights-core/issues/154)
- Kerberos KDC log parser for 2.x branch [\#153](https://github.com/RedHatInsights/insights-core/issues/153)
- Add new shared parser iscsiadm\_mode\_session.py \#136 [\#137](https://github.com/RedHatInsights/insights-core/issues/137)
- Enhance httpd\_conf to support nested sections \#84 [\#120](https://github.com/RedHatInsights/insights-core/issues/120)
- Simplify Policy booleans handling \#96 [\#97](https://github.com/RedHatInsights/insights-core/issues/97)
- Uname not properly parsed for RHEL 6.3 sosreports [\#90](https://github.com/RedHatInsights/insights-core/issues/90)
- Falafel reference in image [\#23](https://github.com/RedHatInsights/insights-core/issues/23)

**Merged pull requests:**

- Enhance2 parser openshift\_get 1x [\#168](https://github.com/RedHatInsights/insights-core/pull/168) ([wushiqinlou](https://github.com/wushiqinlou))
- Parsers for the 389 Directory Server access and errors log files - 1.x branch [\#165](https://github.com/RedHatInsights/insights-core/pull/165) ([PaulWay](https://github.com/PaulWay))
- minor doc fix: ordering of 'git remote' command [\#163](https://github.com/RedHatInsights/insights-core/pull/163) ([bobcallaway](https://github.com/bobcallaway))
- Add mitigation for CVE-2017-2636 to demo base archives [\#156](https://github.com/RedHatInsights/insights-core/pull/156) ([wcmitchell](https://github.com/wcmitchell))
- Parser module test coverage at 100% [\#148](https://github.com/RedHatInsights/insights-core/pull/148) ([PaulWay](https://github.com/PaulWay))
- Kerberos KDC log parser for 1.x branch [\#147](https://github.com/RedHatInsights/insights-core/pull/147) ([PaulWay](https://github.com/PaulWay))
- Removing no longer used ErrorCollector class - 1.x branch [\#142](https://github.com/RedHatInsights/insights-core/pull/142) ([PaulWay](https://github.com/PaulWay))
- Add new shared parser iscsiadm\_mode\_session.py [\#136](https://github.com/RedHatInsights/insights-core/pull/136) ([xiaoyu74](https://github.com/xiaoyu74))
- Enhance2 parser uname 1x [\#134](https://github.com/RedHatInsights/insights-core/pull/134) ([wushiqinlou](https://github.com/wushiqinlou))
- Enhance httpd\_conf to support nested sections [\#133](https://github.com/RedHatInsights/insights-core/pull/133) ([xiangce](https://github.com/xiangce))
- Add new shared parser teamdctl\_state\_dump.py [\#128](https://github.com/RedHatInsights/insights-core/pull/128) ([xiaoyu74](https://github.com/xiaoyu74))
- LogFileOutput parser class `get\_after\(\)` method - 1.x branch [\#119](https://github.com/RedHatInsights/insights-core/pull/119) ([PaulWay](https://github.com/PaulWay))
- Unitfiles parser enhanced to deal with all unit states. [\#115](https://github.com/RedHatInsights/insights-core/pull/115) ([jsvob](https://github.com/jsvob))
- Simplify 'Policy booleans' handling [\#111](https://github.com/RedHatInsights/insights-core/pull/111) ([PaulWay](https://github.com/PaulWay))
- Improve docs, test coverage and parsing of the system\_time parser for the 1.x branch [\#109](https://github.com/RedHatInsights/insights-core/pull/109) ([PaulWay](https://github.com/PaulWay))

## [insights-core-1.41.0-43](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.41.0-43) (2017-06-20)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/falafel-1.40.0-23...insights-core-1.41.0-43)

**Closed issues:**

- Update ceph\_version to add version 2.2 \#105 [\#106](https://github.com/RedHatInsights/insights-core/issues/106)
- Removing previously used but abandoned test functions \#98 [\#99](https://github.com/RedHatInsights/insights-core/issues/99)
- Expose associated satellite information in system metadata \#65 [\#87](https://github.com/RedHatInsights/insights-core/issues/87)
- Added keyword\_search function \#69 [\#86](https://github.com/RedHatInsights/insights-core/issues/86)
- Rename from falafel to insights-core [\#8](https://github.com/RedHatInsights/insights-core/issues/8)

**Merged pull requests:**

- Removing previously used but abandoned test functions - 1.x branch [\#110](https://github.com/RedHatInsights/insights-core/pull/110) ([PaulWay](https://github.com/PaulWay))
- Update ceph\_version to add version 2.2 [\#105](https://github.com/RedHatInsights/insights-core/pull/105) ([shzhou12](https://github.com/shzhou12))
- Enhance parser openshift\_get 1.x [\#101](https://github.com/RedHatInsights/insights-core/pull/101) ([wushiqinlou](https://github.com/wushiqinlou))
- Keyword search helper function for parsers [\#93](https://github.com/RedHatInsights/insights-core/pull/93) ([PaulWay](https://github.com/PaulWay))
- Remove private URL from uname's docstring [\#92](https://github.com/RedHatInsights/insights-core/pull/92) ([xiangce](https://github.com/xiangce))
- Remove the deprecated method: get\_expiration\_date\(\) [\#91](https://github.com/RedHatInsights/insights-core/pull/91) ([JoySnow](https://github.com/JoySnow))
- Enhance httpd\_conf mapper and shared reducer \(\#36\) [\#82](https://github.com/RedHatInsights/insights-core/pull/82) ([xiangce](https://github.com/xiangce))
- Un-renaming some combiner stuff [\#80](https://github.com/RedHatInsights/insights-core/pull/80) ([kylape](https://github.com/kylape))
- Update docs and consolidate tests for parsers module [\#79](https://github.com/RedHatInsights/insights-core/pull/79) ([bfahr](https://github.com/bfahr))
- Rename forgotten mapper to parser in \*.md [\#77](https://github.com/RedHatInsights/insights-core/pull/77) ([xiangce](https://github.com/xiangce))
- Correct the path in MAINFEST.in [\#75](https://github.com/RedHatInsights/insights-core/pull/75) ([xiangce](https://github.com/xiangce))
- Forget to rename the REDUCER in insight.tests [\#74](https://github.com/RedHatInsights/insights-core/pull/74) ([xiangce](https://github.com/xiangce))
- Rename 1.x [\#72](https://github.com/RedHatInsights/insights-core/pull/72) ([xiangce](https://github.com/xiangce))
- Component results get stored in shared if not None. [\#67](https://github.com/RedHatInsights/insights-core/pull/67) ([csams](https://github.com/csams))
- Expose associated satellite information in system metadata [\#65](https://github.com/RedHatInsights/insights-core/pull/65) ([jeudy100](https://github.com/jeudy100))

## [falafel-1.40.0-23](https://github.com/RedHatInsights/insights-core/tree/falafel-1.40.0-23) (2017-06-07)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/falafel-1.39.0-11...falafel-1.40.0-23)

**Fixed bugs:**

- Transaction check error w/python-requests on falafel-1.38.0-25 installation [\#12](https://github.com/RedHatInsights/insights-core/issues/12)

**Closed issues:**

- uname parser fails for kernel 2.6.32-504.8.2.bgq.el6 [\#52](https://github.com/RedHatInsights/insights-core/issues/52)

**Merged pull requests:**

- Skip newline for rhel63 \(1.x\) [\#63](https://github.com/RedHatInsights/insights-core/pull/63) ([chenlizhong](https://github.com/chenlizhong))
- Enhance grub\_conf.py \(1.x\) [\#61](https://github.com/RedHatInsights/insights-core/pull/61) ([xiangce](https://github.com/xiangce))
- Fix uname to accept 5 sections in release string. \(1.x\) [\#53](https://github.com/RedHatInsights/insights-core/pull/53) ([jsvob](https://github.com/jsvob))
- Version bump to 1.40 [\#45](https://github.com/RedHatInsights/insights-core/pull/45) ([kylape](https://github.com/kylape))
- Don't process blank lines from blkid [\#43](https://github.com/RedHatInsights/insights-core/pull/43) ([kylape](https://github.com/kylape))
- Modify 1.x for rule analysis [\#42](https://github.com/RedHatInsights/insights-core/pull/42) ([songuyen](https://github.com/songuyen))
- \[backport\] using the correct rhel6.x version for the test archive [\#40](https://github.com/RedHatInsights/insights-core/pull/40) ([jhjaggars](https://github.com/jhjaggars))
- Mapper for osp mariadb plugin 1.x [\#37](https://github.com/RedHatInsights/insights-core/pull/37) ([vishwanathjadhav](https://github.com/vishwanathjadhav))
- Enhance mapper certificates\_enddate.py [\#33](https://github.com/RedHatInsights/insights-core/pull/33) ([JoySnow](https://github.com/JoySnow))

## [falafel-1.39.0-11](https://github.com/RedHatInsights/insights-core/tree/falafel-1.39.0-11) (2017-05-31)
**Merged pull requests:**

- Adding changelog [\#32](https://github.com/RedHatInsights/insights-core/pull/32) ([kylape](https://github.com/kylape))
- Modify packaging to include archive tool data files [\#31](https://github.com/RedHatInsights/insights-core/pull/31) ([kylape](https://github.com/kylape))
- Adding back archive tool [\#28](https://github.com/RedHatInsights/insights-core/pull/28) ([kylape](https://github.com/kylape))



\* *This Change Log was automatically generated by [github_changelog_generator](https://github.com/skywinder/Github-Changelog-Generator)*