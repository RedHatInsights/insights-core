# Change Log

## [insights-core-3.0.114-1078](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.114-1078) (2019-07-25)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.113-1062...insights-core-3.0.114-1078)

**Implemented enhancements:**

- Update the Mount parser and specs depends on '/proc/mounts' [\#2059](https://github.com/RedHatInsights/insights-core/issues/2059)

**Fixed bugs:**

- bash\_version example doesn't work with json format [\#2100](https://github.com/RedHatInsights/insights-core/issues/2100)
- CLI dumps tracebacks instead of simple message [\#2097](https://github.com/RedHatInsights/insights-core/issues/2097)
- Core doesn't detect chkconfig in services directory of sos archives [\#2087](https://github.com/RedHatInsights/insights-core/issues/2087)
- Dmesg combiner always succeeds [\#2084](https://github.com/RedHatInsights/insights-core/issues/2084)
- Modinfo Parser is Missing Insights Archive Spec [\#2053](https://github.com/RedHatInsights/insights-core/issues/2053)
- Systemctl cat needs to retain backward compatibility for archive specs [\#2038](https://github.com/RedHatInsights/insights-core/issues/2038)

**Closed issues:**

- insights.run does not run against sosreport directory if print\_summary=False [\#2107](https://github.com/RedHatInsights/insights-core/issues/2107)
- ProcMounts doesn't handle paths contain spaces, e.g."/run/media/VMware Tools" [\#2069](https://github.com/RedHatInsights/insights-core/issues/2069)
- Issue in installed\_rpms.redhat\_signed when run against sosreport [\#2066](https://github.com/RedHatInsights/insights-core/issues/2066)
- YAMLParser does not handle list-like YAML texts [\#2060](https://github.com/RedHatInsights/insights-core/issues/2060)
- JSONParser does not handle JSON texts consisting of an array [\#2056](https://github.com/RedHatInsights/insights-core/issues/2056)

## [insights-core-3.0.113-1062](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.113-1062) (2019-07-18)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.112-1...insights-core-3.0.113-1062)

**Implemented enhancements:**

- Refine the logic of parsers and combiners in "grub\_conf.py" [\#1983](https://github.com/RedHatInsights/insights-core/issues/1983)

**Closed issues:**

- Detect rules with possible duplicate response keys [\#2082](https://github.com/RedHatInsights/insights-core/issues/2082)
- 'grubenv' does not updated as per grubby [\#2041](https://github.com/RedHatInsights/insights-core/issues/2041)
- GRUB2 on RHEL8 - add support for blscfg [\#1650](https://github.com/RedHatInsights/insights-core/issues/1650)

## [3.0.112-1](https://github.com/RedHatInsights/insights-core/tree/3.0.112-1) (2019-07-17)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.111-1...3.0.112-1)

**Implemented enhancements:**

- Create make\_info response type for rules [\#2073](https://github.com/RedHatInsights/insights-core/issues/2073)
- Evolution of Rules to Share Code [\#1473](https://github.com/RedHatInsights/insights-core/issues/1473)

**Fixed bugs:**

- Fix command specs containing globs [\#1413](https://github.com/RedHatInsights/insights-core/issues/1413)

**Closed issues:**

- Incorrect insights.components.rhel\_version module doc [\#2048](https://github.com/RedHatInsights/insights-core/issues/2048)

## [3.0.111-1](https://github.com/RedHatInsights/insights-core/tree/3.0.111-1) (2019-07-17)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.110-1...3.0.111-1)

## [3.0.110-1](https://github.com/RedHatInsights/insights-core/tree/3.0.110-1) (2019-07-16)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.109-1047...3.0.110-1)

**Closed issues:**

- `modinfo` on all loaded modules [\#1793](https://github.com/RedHatInsights/insights-core/issues/1793)
- `DmesgLineList` parser cannot handle wrapped dmesg output [\#1792](https://github.com/RedHatInsights/insights-core/issues/1792)

**Merged pull requests:**

- Update changelog and bump version to 3.0.110 [\#2054](https://github.com/RedHatInsights/insights-core/pull/2054) ([wcmitchell](https://github.com/wcmitchell))

## [insights-core-3.0.109-1047](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.109-1047) (2019-07-11)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.108-1038...insights-core-3.0.109-1047)

**Implemented enhancements:**

- NmcliConnShow parser fails when there is warning in cmd output [\#2051](https://github.com/RedHatInsights/insights-core/issues/2051)

**Fixed bugs:**

- httpd\_V combiner doesn't treat httpd\_V parser arg as a list [\#1805](https://github.com/RedHatInsights/insights-core/issues/1805)

**Closed issues:**

- Need a parser for 'rabbitmqctl\_report' of containers [\#2049](https://github.com/RedHatInsights/insights-core/issues/2049)

## [insights-core-3.0.108-1038](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.108-1038) (2019-07-03)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.107-1033...insights-core-3.0.108-1038)

**Fixed bugs:**

- IfCFG parser do not add raw\_device\_value [\#2037](https://github.com/RedHatInsights/insights-core/issues/2037)
- incorrect default\_component\_enabled behavior [\#2034](https://github.com/RedHatInsights/insights-core/issues/2034)
- When em/en dash is mistakenly used for an arg to insights run exception is thrown [\#1832](https://github.com/RedHatInsights/insights-core/issues/1832)

**Closed issues:**

- Add regex support to add\_filter [\#2029](https://github.com/RedHatInsights/insights-core/issues/2029)
- Remove archive creation code [\#1642](https://github.com/RedHatInsights/insights-core/issues/1642)

## [insights-core-3.0.107-1033](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.107-1033) (2019-06-27)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.106-1020...insights-core-3.0.107-1033)

**Implemented enhancements:**

- Enhance parser qemu\_xml to parse new RHOSP specific attributes [\#1717](https://github.com/RedHatInsights/insights-core/issues/1717)

**Fixed bugs:**

- ModInfoVeth Parser needs spec for Insights Archives [\#2026](https://github.com/RedHatInsights/insights-core/issues/2026)

**Closed issues:**

- NoOptionError using smb.conf parser \(samba.py\) [\#2018](https://github.com/RedHatInsights/insights-core/issues/2018)
- The installed\_rpms spec does work on RHEL6 [\#2015](https://github.com/RedHatInsights/insights-core/issues/2015)
- Critical security issue in dependency pyyaml [\#2013](https://github.com/RedHatInsights/insights-core/issues/2013)
- ModuleNotFoundError: No module named 'insights.config' [\#2009](https://github.com/RedHatInsights/insights-core/issues/2009)
- Missing boilerplate notice in all the files of the project. [\#2003](https://github.com/RedHatInsights/insights-core/issues/2003)
- Markdown formatter needs to show plugin module in output [\#1700](https://github.com/RedHatInsights/insights-core/issues/1700)

## [insights-core-3.0.106-1020](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.106-1020) (2019-06-20)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.105-1009...insights-core-3.0.106-1020)

**Closed issues:**

- Change sequence of simple\_file for first\_of Spec for lspci in sos\_archive.py [\#1997](https://github.com/RedHatInsights/insights-core/issues/1997)
- Combiner CloudProvider appears in every "insights-info" [\#1994](https://github.com/RedHatInsights/insights-core/issues/1994)
- Current GrubConf parser cannot handle the "grub2/grub.cfg" of RHEL8 [\#1972](https://github.com/RedHatInsights/insights-core/issues/1972)
- Update is\_hypervisor check in InstalledRpms [\#1928](https://github.com/RedHatInsights/insights-core/issues/1928)
-  Specs.software\_collections\_list: Option `-l` is changed to 'list-collections' in RHEL8 [\#1870](https://github.com/RedHatInsights/insights-core/issues/1870)

## [insights-core-3.0.105-1009](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.105-1009) (2019-06-14)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.104-1004...insights-core-3.0.105-1009)

## [insights-core-3.0.104-1004](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.104-1004) (2019-06-13)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.103-995...insights-core-3.0.104-1004)

**Implemented enhancements:**

- Krb5Configuration do not list all the sections [\#1874](https://github.com/RedHatInsights/insights-core/issues/1874)
- Add "reponame" to the rpm query string for InstalledRpms [\#1854](https://github.com/RedHatInsights/insights-core/issues/1854)
- `CpuInfo` parser cannot handle ARM and PowerPC [\#1794](https://github.com/RedHatInsights/insights-core/issues/1794)
- Investigate collecting `/etc/dnf/modules.d` and other dnf related information [\#1648](https://github.com/RedHatInsights/insights-core/issues/1648)

**Fixed bugs:**

- There is a bug in parser "PassengerStatus" [\#1978](https://github.com/RedHatInsights/insights-core/issues/1978)
- Krb5Configuration do not list all the sections [\#1874](https://github.com/RedHatInsights/insights-core/issues/1874)
- FileListing could not check dir with sticky bit shown as 'T' in ls command [\#1121](https://github.com/RedHatInsights/insights-core/issues/1121)

**Closed issues:**

- ModInfo parser should parse octeon\_drv module. [\#1991](https://github.com/RedHatInsights/insights-core/issues/1991)
- setup\_env.sh does not check for the presence of 'virtualenv' [\#1988](https://github.com/RedHatInsights/insights-core/issues/1988)
- Need to enhance the keep\_scan and token\_scan of LogFileOutput [\#1969](https://github.com/RedHatInsights/insights-core/issues/1969)
- \[RFE\] Abrt DUPHASH integration for backtraces [\#1785](https://github.com/RedHatInsights/insights-core/issues/1785)
- Failed to get CephVersion from sosreport archives [\#1684](https://github.com/RedHatInsights/insights-core/issues/1684)

## [insights-core-3.0.103-995](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.103-995) (2019-06-05)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.102...insights-core-3.0.103-995)

**Closed issues:**

- issue on parsing line endswith "\*" in krb5.py [\#1911](https://github.com/RedHatInsights/insights-core/issues/1911)

## [3.0.102](https://github.com/RedHatInsights/insights-core/tree/3.0.102) (2019-06-04)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.101-986...3.0.102)

**Implemented enhancements:**

- Filter out wanted system logs according to the process name [\#1919](https://github.com/RedHatInsights/insights-core/issues/1919)
- Enhance @parser to allow additional dependencies [\#1888](https://github.com/RedHatInsights/insights-core/issues/1888)

**Closed issues:**

- Sync specs in sos\_archive.py [\#1950](https://github.com/RedHatInsights/insights-core/issues/1950)

## [insights-core-3.0.101-986](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.101-986) (2019-05-30)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.100-974...insights-core-3.0.101-986)

**Fixed bugs:**

- "CommandParser does skip the "No module named insights.tools" [\#1955](https://github.com/RedHatInsights/insights-core/issues/1955)
- wrong specs for heat api log  [\#1886](https://github.com/RedHatInsights/insights-core/issues/1886)

**Closed issues:**

- Invoking "insights-inspect" command without colorama installed results in a traceback [\#1956](https://github.com/RedHatInsights/insights-core/issues/1956)
- `SysconfigOptions` base parser does not parse unpaired quoted lines [\#1946](https://github.com/RedHatInsights/insights-core/issues/1946)
- Enhance parser RabbitMQReport  [\#1906](https://github.com/RedHatInsights/insights-core/issues/1906)
- Do we need ceph\_version parser? [\#1764](https://github.com/RedHatInsights/insights-core/issues/1764)
- nginx\_conf collection incomplete? [\#1472](https://github.com/RedHatInsights/insights-core/issues/1472)

## [insights-core-3.0.100-974](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.100-974) (2019-05-23)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.99-969...insights-core-3.0.100-974)

**Implemented enhancements:**

- New parser for PsAlxww [\#1833](https://github.com/RedHatInsights/insights-core/issues/1833)

**Fixed bugs:**

- Ps class incorrectly parses command name and forces position of "user" and "command" columns. [\#1915](https://github.com/RedHatInsights/insights-core/issues/1915)

## [insights-core-3.0.99-969](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.99-969) (2019-05-16)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.98-965...insights-core-3.0.99-969)

**Fixed bugs:**

- redhat\_release.RedHatRelease Combiner - Change `ParseException` to `SkipComponent`  [\#1924](https://github.com/RedHatInsights/insights-core/issues/1924)

**Closed issues:**

- get\_max\(package\_name\) returns TypeError for some package lists [\#1839](https://github.com/RedHatInsights/insights-core/issues/1839)
- The default comparison method of InstalledRpm should only for packages from "Red Hat" [\#1836](https://github.com/RedHatInsights/insights-core/issues/1836)

## [insights-core-3.0.98-965](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.98-965) (2019-05-14)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.97-1...insights-core-3.0.98-965)

**Implemented enhancements:**

- Local routes are filtered in the `RouteDevices` parser [\#1803](https://github.com/RedHatInsights/insights-core/issues/1803)

**Fixed bugs:**

- Directories of exploded archives not recognized as cluster [\#1900](https://github.com/RedHatInsights/insights-core/issues/1900)
- cluster rules execute during non-cluster analysis [\#1896](https://github.com/RedHatInsights/insights-core/issues/1896)

**Closed issues:**

- Collect insights client configuration with blacklist [\#588](https://github.com/RedHatInsights/insights-core/issues/588)
- Remove direct dependency on netstat [\#83](https://github.com/RedHatInsights/insights-core/issues/83)

## [3.0.97-1](https://github.com/RedHatInsights/insights-core/tree/3.0.97-1) (2019-05-06)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.96-1...3.0.97-1)

**Fixed bugs:**

- Timestamp without space in square brackets doesn't get parsed by dmesg parser [\#1909](https://github.com/RedHatInsights/insights-core/issues/1909)
- Ps aexww parser does not parser all environment vars correctly [\#1857](https://github.com/RedHatInsights/insights-core/issues/1857)
- SshDConfig parser doesn't support "=" key/value separator [\#1807](https://github.com/RedHatInsights/insights-core/issues/1807)

## [3.0.96-1](https://github.com/RedHatInsights/insights-core/tree/3.0.96-1) (2019-05-05)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.95-1...3.0.96-1)

## [3.0.95-1](https://github.com/RedHatInsights/insights-core/tree/3.0.95-1) (2019-05-05)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.94-1...3.0.95-1)

## [3.0.94-1](https://github.com/RedHatInsights/insights-core/tree/3.0.94-1) (2019-05-04)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.93-1...3.0.94-1)

## [3.0.93-1](https://github.com/RedHatInsights/insights-core/tree/3.0.93-1) (2019-05-03)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.92-937...3.0.93-1)

**Implemented enhancements:**

- Add "display\_name" spec to specs [\#1891](https://github.com/RedHatInsights/insights-core/issues/1891)

## [insights-core-3.0.92-937](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.92-937) (2019-05-02)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.91-930...insights-core-3.0.92-937)

**Closed issues:**

- Need to enhance parser "ls\_parser" to parse the output of  command 'ls -laRZ \<dir-name\>' in RHEL-8  [\#1825](https://github.com/RedHatInsights/insights-core/issues/1825)

## [insights-core-3.0.91-930](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.91-930) (2019-04-25)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.90-917...insights-core-3.0.91-930)

**Implemented enhancements:**

- No parser for /sos\_commands/ceph/ceph\_osd\_tree in sosreport  [\#1776](https://github.com/RedHatInsights/insights-core/issues/1776)

**Fixed bugs:**

- Insights Archive spec is Incorrect [\#1856](https://github.com/RedHatInsights/insights-core/issues/1856)

## [insights-core-3.0.90-917](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.90-917) (2019-04-18)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.89-899...insights-core-3.0.90-917)

**Closed issues:**

- Check of the IGNORE\_TYPES is not correct [\#1818](https://github.com/RedHatInsights/insights-core/issues/1818)

## [insights-core-3.0.89-899](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.89-899) (2019-04-11)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.88-889...insights-core-3.0.89-899)

**Implemented enhancements:**

- pcs\_config parser returns list instead of dict in "Cluster Properties" [\#1734](https://github.com/RedHatInsights/insights-core/issues/1734)

**Closed issues:**

- insights-run failed in Macbook\(Option --delay-directory-restore is not supported\) [\#1802](https://github.com/RedHatInsights/insights-core/issues/1802)
- python\_-m\_insights.tools.cat reports: "/bin/python: No module named tools" [\#1697](https://github.com/RedHatInsights/insights-core/issues/1697)

## [insights-core-3.0.88-889](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.88-889) (2019-04-04)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.87-1...insights-core-3.0.88-889)

**Implemented enhancements:**

- Allow different CONTENT for the same key [\#1767](https://github.com/RedHatInsights/insights-core/issues/1767)

**Closed issues:**

- Change spec for netstat parser in sos\_archive.py   [\#1783](https://github.com/RedHatInsights/insights-core/issues/1783)
- insights-client: WARNING: Unknown options: trace [\#1702](https://github.com/RedHatInsights/insights-core/issues/1702)

## [3.0.87-1](https://github.com/RedHatInsights/insights-core/tree/3.0.87-1) (2019-03-29)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.86-877...3.0.87-1)

**Closed issues:**

- Ceilometer Collector Log specs needs to be first\_file [\#1772](https://github.com/RedHatInsights/insights-core/issues/1772)

## [insights-core-3.0.86-877](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.86-877) (2019-03-27)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.85-868...insights-core-3.0.86-877)

## [insights-core-3.0.85-868](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.85-868) (2019-03-21)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.84-864...insights-core-3.0.85-868)

**Fixed bugs:**

- FileListing parser does not correctly handle directory path with dot [\#1748](https://github.com/RedHatInsights/insights-core/issues/1748)

## [insights-core-3.0.84-864](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.84-864) (2019-03-18)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.83-1...insights-core-3.0.84-864)

## [3.0.83-1](https://github.com/RedHatInsights/insights-core/tree/3.0.83-1) (2019-03-14)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.82-858...3.0.83-1)

**Fixed bugs:**

- Enhance multipath conf parser to parse multiple entries [\#1722](https://github.com/RedHatInsights/insights-core/issues/1722)

## [insights-core-3.0.82-858](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.82-858) (2019-03-14)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.81-848...insights-core-3.0.82-858)

**Implemented enhancements:**

- Set LC\_ALL=C for all commands [\#1623](https://github.com/RedHatInsights/insights-core/issues/1623)

**Fixed bugs:**

- parse\_fixed\_table header prefix bug [\#1737](https://github.com/RedHatInsights/insights-core/issues/1737)

**Closed issues:**

- SMDA\* is not business SAP instances [\#1740](https://github.com/RedHatInsights/insights-core/issues/1740)

## [insights-core-3.0.81-848](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.81-848) (2019-03-07)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.80-833...insights-core-3.0.81-848)

**Implemented enhancements:**

- Add filterable option to IronicInspectorLog [\#1718](https://github.com/RedHatInsights/insights-core/issues/1718)

**Fixed bugs:**

- exceptions logged at warn level when calling get\_canonical\_facts [\#1726](https://github.com/RedHatInsights/insights-core/issues/1726)
- subscription manager identity datasource raises exception [\#1674](https://github.com/RedHatInsights/insights-core/issues/1674)

**Closed issues:**

- Enhance the "Examples" of LogFileOutput and Syslog [\#1724](https://github.com/RedHatInsights/insights-core/issues/1724)
- Add filtering to the result of insights-run [\#1687](https://github.com/RedHatInsights/insights-core/issues/1687)
- Output of "insights-info" is not so accurate [\#1645](https://github.com/RedHatInsights/insights-core/issues/1645)
- A utility interface to `redhat\_release` to check/get RHEL version [\#1644](https://github.com/RedHatInsights/insights-core/issues/1644)

## [insights-core-3.0.80-833](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.80-833) (2019-02-28)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.79-822...insights-core-3.0.80-833)

**Closed issues:**

- insights/util/subproc.py", line 100: An unexpected keyword argument 'STDOUT' [\#1712](https://github.com/RedHatInsights/insights-core/issues/1712)

## [insights-core-3.0.79-822](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.79-822) (2019-02-21)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.78-807...insights-core-3.0.79-822)

**Closed issues:**

- LogFileOutput.token\_scan does not support `list` [\#1688](https://github.com/RedHatInsights/insights-core/issues/1688)
- TarExtractor doesn’t work on macOS [\#1686](https://github.com/RedHatInsights/insights-core/issues/1686)

## [insights-core-3.0.78-807](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.78-807) (2019-02-08)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.77-804...insights-core-3.0.78-807)

## [insights-core-3.0.77-804](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.77-804) (2019-02-07)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.76-795...insights-core-3.0.77-804)

**Closed issues:**

- password blanking broken on RHEL8 [\#1670](https://github.com/RedHatInsights/insights-core/issues/1670)

## [insights-core-3.0.76-795](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.76-795) (2019-01-31)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.75-1...insights-core-3.0.76-795)

## [3.0.75-1](https://github.com/RedHatInsights/insights-core/tree/3.0.75-1) (2019-01-30)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.74-778...3.0.75-1)

**Fixed bugs:**

- streaming bug with python3.7 [\#1652](https://github.com/RedHatInsights/insights-core/issues/1652)

**Closed issues:**

- Modinfo Parser class should be in Parsers instead of the Package spec [\#1659](https://github.com/RedHatInsights/insights-core/issues/1659)

## [insights-core-3.0.74-778](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.74-778) (2019-01-24)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.73-767...insights-core-3.0.74-778)

**Fixed bugs:**

- RedhatRelease parser failed to parse minor release version in some scenarios [\#1590](https://github.com/RedHatInsights/insights-core/issues/1590)
- Exceptions on the command line with invalid arguments in the archive position [\#1486](https://github.com/RedHatInsights/insights-core/issues/1486)

**Closed issues:**

- Parse\_error TOP1: mysqladmin.py: Empty or wrong content in table [\#1637](https://github.com/RedHatInsights/insights-core/issues/1637)
- Typo in quickstart documentation [\#1635](https://github.com/RedHatInsights/insights-core/issues/1635)

## [insights-core-3.0.73-767](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.73-767) (2019-01-17)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.72-1...insights-core-3.0.73-767)

**Closed issues:**

- ifcfg parser to support for MASTER and TEAM\_MASTER keys slave type [\#1626](https://github.com/RedHatInsights/insights-core/issues/1626)

## [3.0.72-1](https://github.com/RedHatInsights/insights-core/tree/3.0.72-1) (2019-01-09)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.71-1...3.0.72-1)

## [3.0.71-1](https://github.com/RedHatInsights/insights-core/tree/3.0.71-1) (2019-01-07)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.70-754...3.0.71-1)

## [insights-core-3.0.70-754](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.70-754) (2018-12-24)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.69-744...insights-core-3.0.70-754)

## [insights-core-3.0.69-744](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.69-744) (2018-12-13)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.68-1...insights-core-3.0.69-744)

**Closed issues:**

- DeprecationWarning from qemu\_xml [\#1594](https://github.com/RedHatInsights/insights-core/issues/1594)

## [3.0.68-1](https://github.com/RedHatInsights/insights-core/tree/3.0.68-1) (2018-12-11)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.67-732...3.0.68-1)

## [insights-core-3.0.67-732](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.67-732) (2018-12-06)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.66-1...insights-core-3.0.67-732)

## [3.0.66-1](https://github.com/RedHatInsights/insights-core/tree/3.0.66-1) (2018-12-05)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.64-717...3.0.66-1)

## [insights-core-3.0.64-717](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.64-717) (2018-11-30)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.63-708...insights-core-3.0.64-717)

## [insights-core-3.0.63-708](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.63-708) (2018-11-29)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.62-686...insights-core-3.0.63-708)

**Implemented enhancements:**

- Unnecessary Exception raised [\#1564](https://github.com/RedHatInsights/insights-core/issues/1564)

**Fixed bugs:**

- Invalid datasource for ceph\_conf [\#1570](https://github.com/RedHatInsights/insights-core/issues/1570)

**Closed issues:**

- bond object do not have \_active\_slave attribute exception issue [\#1563](https://github.com/RedHatInsights/insights-core/issues/1563)
- Unsuitable parse error in `Lssap` [\#1559](https://github.com/RedHatInsights/insights-core/issues/1559)

## [insights-core-3.0.62-686](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.62-686) (2018-11-20)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.61-682...insights-core-3.0.62-686)

**Closed issues:**

- Mention unsupported docs building on Python 2.6 [\#1391](https://github.com/RedHatInsights/insights-core/issues/1391)

## [insights-core-3.0.61-682](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.61-682) (2018-11-15)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.60-680...insights-core-3.0.61-682)

## [insights-core-3.0.60-680](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.60-680) (2018-11-15)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.59-1...insights-core-3.0.60-680)

## [3.0.59-1](https://github.com/RedHatInsights/insights-core/tree/3.0.59-1) (2018-11-14)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.58-1...3.0.59-1)

**Fixed bugs:**

- Add xfs\_info datasource to default.py [\#1303](https://github.com/RedHatInsights/insights-core/issues/1303)

**Closed issues:**

- InstalledRpm.from\_package doesn't support 'epoch' correctly [\#1544](https://github.com/RedHatInsights/insights-core/issues/1544)

## [3.0.58-1](https://github.com/RedHatInsights/insights-core/tree/3.0.58-1) (2018-11-12)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.57-663...3.0.58-1)

**Closed issues:**

- Working without parsers [\#1518](https://github.com/RedHatInsights/insights-core/issues/1518)

## [insights-core-3.0.57-663](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.57-663) (2018-11-08)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.56-653...insights-core-3.0.57-663)

**Implemented enhancements:**

- Some sos reports include JBoss Diagnostic Report contents [\#1511](https://github.com/RedHatInsights/insights-core/issues/1511)

**Fixed bugs:**

- FileListing parser does not handle filenames with newlines in the name [\#1527](https://github.com/RedHatInsights/insights-core/issues/1527)
- FileListing class has selinux arg that is not used [\#1492](https://github.com/RedHatInsights/insights-core/issues/1492)
- render is called even when rule has missing requirements [\#1489](https://github.com/RedHatInsights/insights-core/issues/1489)

**Closed issues:**

- Ensure current working directory is on the python path with insights-run [\#1523](https://github.com/RedHatInsights/insights-core/issues/1523)
- \[RFE\] Results to include positive NACK - CVEs to which a system is NOT vulnerable [\#1510](https://github.com/RedHatInsights/insights-core/issues/1510)
- `list.sort\(\)` doesn't work as expected in python3 [\#1496](https://github.com/RedHatInsights/insights-core/issues/1496)

## [insights-core-3.0.56-653](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.56-653) (2018-11-01)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.55-1...insights-core-3.0.56-653)

**Implemented enhancements:**

- rules without CONTENT produce hard to interpret reports [\#1480](https://github.com/RedHatInsights/insights-core/issues/1480)

**Fixed bugs:**

- The human readable rule report includes rules with missing requirements [\#1479](https://github.com/RedHatInsights/insights-core/issues/1479)

## [3.0.55-1](https://github.com/RedHatInsights/insights-core/tree/3.0.55-1) (2018-10-31)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.54-643...3.0.55-1)

**Closed issues:**

- fix wrong passenger\_status part in insights/specs/insights\_archive.py  [\#1508](https://github.com/RedHatInsights/insights-core/issues/1508)
- \[python3\] `unordered\_compare` does support comparing list with dictionaries [\#1494](https://github.com/RedHatInsights/insights-core/issues/1494)

## [insights-core-3.0.54-643](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.54-643) (2018-10-25)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.52-1...insights-core-3.0.54-643)

**Fixed bugs:**

- configtree include directives only work from top level [\#1477](https://github.com/RedHatInsights/insights-core/issues/1477)

**Closed issues:**

- installed\_rpms missing EPOCH [\#1431](https://github.com/RedHatInsights/insights-core/issues/1431)

## [3.0.52-1](https://github.com/RedHatInsights/insights-core/tree/3.0.52-1) (2018-10-18)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.51-623...3.0.52-1)

**Fixed bugs:**

- Issue to collect insights-archive in RHEL6 [\#1461](https://github.com/RedHatInsights/insights-core/issues/1461)

**Closed issues:**

- Add 'to\_serializable\(\)' function to 'InputData' object [\#1421](https://github.com/RedHatInsights/insights-core/issues/1421)

## [insights-core-3.0.51-623](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.51-623) (2018-10-11)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.50-1...insights-core-3.0.51-623)

## [3.0.50-1](https://github.com/RedHatInsights/insights-core/tree/3.0.50-1) (2018-10-10)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.49-615...3.0.50-1)

**Fixed bugs:**

- Mistake to recognize collected files as missing requirements [\#1466](https://github.com/RedHatInsights/insights-core/issues/1466)

## [insights-core-3.0.49-615](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.49-615) (2018-10-03)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.48-1...insights-core-3.0.49-615)

**Closed issues:**

- Run Flake8 lint on RHEL6 [\#1262](https://github.com/RedHatInsights/insights-core/issues/1262)

## [3.0.48-1](https://github.com/RedHatInsights/insights-core/tree/3.0.48-1) (2018-10-01)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.47-1...3.0.48-1)

**Fixed bugs:**

- Tar files aren't handled [\#1457](https://github.com/RedHatInsights/insights-core/issues/1457)

**Closed issues:**

- Incorrect configuration file paths for specs related to OpenStack [\#1441](https://github.com/RedHatInsights/insights-core/issues/1441)

## [3.0.47-1](https://github.com/RedHatInsights/insights-core/tree/3.0.47-1) (2018-09-27)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.46-605...3.0.47-1)

## [insights-core-3.0.46-605](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.46-605) (2018-09-27)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.45-594...insights-core-3.0.46-605)

## [insights-core-3.0.45-594](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.45-594) (2018-09-20)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.44-586...insights-core-3.0.45-594)

**Closed issues:**

- utf-8 UnicodeDecodeError in 'var/log/messages' parsing [\#1432](https://github.com/RedHatInsights/insights-core/issues/1432)

## [insights-core-3.0.44-586](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.44-586) (2018-09-13)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.43-576...insights-core-3.0.44-586)

**Closed issues:**

- No parser for getting number of cpu cores [\#1422](https://github.com/RedHatInsights/insights-core/issues/1422)

## [insights-core-3.0.43-576](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.43-576) (2018-09-05)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.42-564...insights-core-3.0.43-576)

## [insights-core-3.0.42-564](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.42-564) (2018-08-30)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.41-1...insights-core-3.0.42-564)

**Fixed bugs:**

- getsebool parser "need more than 1 value to unpack" [\#1394](https://github.com/RedHatInsights/insights-core/issues/1394)
- Unicode Warning in Python 2.7 for unitfiles module [\#1366](https://github.com/RedHatInsights/insights-core/issues/1366)

**Closed issues:**

- Need to patch machine-id in the test\_set\_display\_name [\#1407](https://github.com/RedHatInsights/insights-core/issues/1407)
- Split setuptools develop extras bundle [\#1261](https://github.com/RedHatInsights/insights-core/issues/1261)

## [3.0.41-1](https://github.com/RedHatInsights/insights-core/tree/3.0.41-1) (2018-08-29)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.40-1...3.0.41-1)

## [3.0.40-1](https://github.com/RedHatInsights/insights-core/tree/3.0.40-1) (2018-08-29)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.39-545...3.0.40-1)

**Fixed bugs:**

- Initialize release in evaluators.py [\#1383](https://github.com/RedHatInsights/insights-core/issues/1383)
- The rule component type overrides invoke but should override process [\#1376](https://github.com/RedHatInsights/insights-core/issues/1376)

**Closed issues:**

- Client Test Attempts to  Removes non-user Insights App File [\#1380](https://github.com/RedHatInsights/insights-core/issues/1380)

## [insights-core-3.0.39-545](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.39-545) (2018-08-22)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.38-534...insights-core-3.0.39-545)

**Closed issues:**

- Do not install docs tools on Python 2.6 [\#1387](https://github.com/RedHatInsights/insights-core/issues/1387)
- Limit Sphinx version to 1.6.7 [\#1385](https://github.com/RedHatInsights/insights-core/issues/1385)

## [insights-core-3.0.38-534](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.38-534) (2018-08-16)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.37-525...insights-core-3.0.38-534)

**Closed issues:**

- Spec for docker\_ps [\#1347](https://github.com/RedHatInsights/insights-core/issues/1347)

## [insights-core-3.0.37-525](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.37-525) (2018-08-13)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.36-512...insights-core-3.0.37-525)

**Implemented enhancements:**

- Add threshold for grep vs in-process filtering [\#1099](https://github.com/RedHatInsights/insights-core/issues/1099)
- Insights core tests should use Insights Demo Plugins repository as a test bed [\#1009](https://github.com/RedHatInsights/insights-core/issues/1009)
- Evaluate including psutil with Insights [\#689](https://github.com/RedHatInsights/insights-core/issues/689)
- Parser tests should be able to pass files by path rather than context\_wrap [\#413](https://github.com/RedHatInsights/insights-core/issues/413)

**Fixed bugs:**

- Specs with precommands that are not at the end don't work [\#664](https://github.com/RedHatInsights/insights-core/issues/664)
- Specs may work differently when extracting from an archive vs in the Insights client. [\#594](https://github.com/RedHatInsights/insights-core/issues/594)

**Closed issues:**

- Python 3 Issue in Client  [\#1322](https://github.com/RedHatInsights/insights-core/issues/1322)
- Research options around customer notifications for updated uploader.json/egg [\#774](https://github.com/RedHatInsights/insights-core/issues/774)
- Need to document how Specs work and how to test them [\#662](https://github.com/RedHatInsights/insights-core/issues/662)
- Content for Custom Rules [\#293](https://github.com/RedHatInsights/insights-core/issues/293)
- include and run custom rules during data collection on individual hosts [\#289](https://github.com/RedHatInsights/insights-core/issues/289)
- Improve the examples in lvm.py [\#287](https://github.com/RedHatInsights/insights-core/issues/287)
- SysctlConfInitramfs should be a Scannable, not a LogFileOutput [\#210](https://github.com/RedHatInsights/insights-core/issues/210)

## [insights-core-3.0.36-512](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.36-512) (2018-08-09)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.36-511...insights-core-3.0.36-512)

## [insights-core-3.0.36-511](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.36-511) (2018-08-09)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.35-1...insights-core-3.0.36-511)

## [3.0.35-1](https://github.com/RedHatInsights/insights-core/tree/3.0.35-1) (2018-08-08)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.34-1...3.0.35-1)

**Closed issues:**

- Consistent size constraints on make\_metadata\_key cause a plugin to fail [\#1329](https://github.com/RedHatInsights/insights-core/issues/1329)
- `add\_filter` is completely undocumented [\#927](https://github.com/RedHatInsights/insights-core/issues/927)

## [3.0.34-1](https://github.com/RedHatInsights/insights-core/tree/3.0.34-1) (2018-08-06)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.33-1...3.0.34-1)

**Closed issues:**

- Check if a archive is from container or host [\#1291](https://github.com/RedHatInsights/insights-core/issues/1291)

## [3.0.33-1](https://github.com/RedHatInsights/insights-core/tree/3.0.33-1) (2018-08-03)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.32-494...3.0.33-1)

## [insights-core-3.0.32-494](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.32-494) (2018-08-02)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.31-466...insights-core-3.0.32-494)

**Implemented enhancements:**

- No JSON object could be decoded [\#996](https://github.com/RedHatInsights/insights-core/issues/996)
- Filter only when collecting on host? [\#981](https://github.com/RedHatInsights/insights-core/issues/981)
- Enable filtering and copying of large files outside the python process [\#949](https://github.com/RedHatInsights/insights-core/issues/949)

**Fixed bugs:**

- FileListing Parser does not return total for a single directory listing [\#1306](https://github.com/RedHatInsights/insights-core/issues/1306)
- Quotes and doublequotes break configtree parser [\#1300](https://github.com/RedHatInsights/insights-core/issues/1300)
- Add xfs\_info spec to default and sos\_archive [\#1117](https://github.com/RedHatInsights/insights-core/issues/1117)
- Better handling of files containing failed command output [\#1076](https://github.com/RedHatInsights/insights-core/issues/1076)
- parse\_systemd\_ini relies on implementation details of ConfigParser [\#324](https://github.com/RedHatInsights/insights-core/issues/324)

**Closed issues:**

- About the parser 'pcs\_status', the spec of it does include the full correct file path [\#1315](https://github.com/RedHatInsights/insights-core/issues/1315)
- Key error in spec.httpd\_conf [\#1308](https://github.com/RedHatInsights/insights-core/issues/1308)
- InstalledRpm parser not working [\#1299](https://github.com/RedHatInsights/insights-core/issues/1299)
- httpd\_conf parser creating list of objects [\#1288](https://github.com/RedHatInsights/insights-core/issues/1288)
- dirsrv\_access and dirsrv\_errors will never collect [\#891](https://github.com/RedHatInsights/insights-core/issues/891)

## [insights-core-3.0.31-466](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.31-466) (2018-07-26)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.30-462...insights-core-3.0.31-466)

## [insights-core-3.0.30-462](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.30-462) (2018-07-24)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.29-455...insights-core-3.0.30-462)

**Fixed bugs:**

- Wrong comparison method is used in get\_localport and get\_peerport of SsTULPN parser   [\#1281](https://github.com/RedHatInsights/insights-core/issues/1281)
- insights hang when extract jdr archive [\#1272](https://github.com/RedHatInsights/insights-core/issues/1272)
- Dead loop in Mount.get\_dir\(\) when no '/' in mount output [\#1245](https://github.com/RedHatInsights/insights-core/issues/1245)
- Commands return bytes instead of unicode [\#1181](https://github.com/RedHatInsights/insights-core/issues/1181)
- Hostname parser doesn't raise exception on invalid data [\#1113](https://github.com/RedHatInsights/insights-core/issues/1113)

**Closed issues:**

- Enhance parser mysqladmin [\#1242](https://github.com/RedHatInsights/insights-core/issues/1242)
- Failing tests in master [\#1231](https://github.com/RedHatInsights/insights-core/issues/1231)
- Issue with simple\_command data source in spec\_factory [\#1228](https://github.com/RedHatInsights/insights-core/issues/1228)
- No spec for docker\_image\_inspect and docker\_container\_inspect [\#1197](https://github.com/RedHatInsights/insights-core/issues/1197)
- There are unnecessary secondary specs in DefaultSpecs [\#1186](https://github.com/RedHatInsights/insights-core/issues/1186)
- Missing dependencies in README [\#1164](https://github.com/RedHatInsights/insights-core/issues/1164)

## [insights-core-3.0.29-455](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.29-455) (2018-07-18)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.28...insights-core-3.0.29-455)

## [insights-core-3.0.28](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.28) (2018-07-18)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.27-441...insights-core-3.0.28)

## [insights-core-3.0.27-441](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.27-441) (2018-07-11)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.26-436...insights-core-3.0.27-441)

## [insights-core-3.0.26-436](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.26-436) (2018-07-02)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.25-430...insights-core-3.0.26-436)

**Closed issues:**

- insights.utils.fs.ensure\_path is not setting requested mode on dirs [\#1238](https://github.com/RedHatInsights/insights-core/issues/1238)

## [insights-core-3.0.25-430](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.25-430) (2018-06-28)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.24-426...insights-core-3.0.25-430)

## [insights-core-3.0.24-426](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.24-426) (2018-06-26)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.22-410...insights-core-3.0.24-426)

**Closed issues:**

- path of ls\_osroot need to be fix [\#1221](https://github.com/RedHatInsights/insights-core/issues/1221)

## [insights-core-3.0.22-410](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.22-410) (2018-06-20)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.21-398...insights-core-3.0.22-410)

**Implemented enhancements:**

- Performance Degradation Processing Archives [\#1098](https://github.com/RedHatInsights/insights-core/issues/1098)

**Fixed bugs:**

- HttpdV combiner with 1.x interface [\#1206](https://github.com/RedHatInsights/insights-core/issues/1206)
- Performance Degradation Processing Archives [\#1098](https://github.com/RedHatInsights/insights-core/issues/1098)

**Closed issues:**

- FileListing cannot get the `first\_path` of `ls\_osroot` [\#1203](https://github.com/RedHatInsights/insights-core/issues/1203)
- FIX wrong command in parser systemctl\_show\_qdrouterd [\#1198](https://github.com/RedHatInsights/insights-core/issues/1198)

## [insights-core-3.0.21-398](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.21-398) (2018-06-14)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.20-390...insights-core-3.0.21-398)

**Fixed bugs:**

- ps parser depends on implementation details of cpython [\#959](https://github.com/RedHatInsights/insights-core/issues/959)
- ip parser depends on implementation specific details of cpython [\#958](https://github.com/RedHatInsights/insights-core/issues/958)
- netstat combiner depends on implementation details of cpython [\#957](https://github.com/RedHatInsights/insights-core/issues/957)
- httpd\_conf combiner depends on implementation details of python2 [\#956](https://github.com/RedHatInsights/insights-core/issues/956)
- RPM Comparisons via `InstalledRPM` rely on naive `LooseVersion` comparisons [\#952](https://github.com/RedHatInsights/insights-core/issues/952)

## [insights-core-3.0.20-390](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.20-390) (2018-06-07)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.19-380...insights-core-3.0.20-390)

**Merged pull requests:**

- httpd conf combiner new test [\#1191](https://github.com/RedHatInsights/insights-core/pull/1191) ([jsvob](https://github.com/jsvob))

## [insights-core-3.0.19-380](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.19-380) (2018-05-31)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.18-371...insights-core-3.0.19-380)

**Closed issues:**

- Make GrubConf combiner to get the valid grub. [\#987](https://github.com/RedHatInsights/insights-core/issues/987)

## [insights-core-3.0.18-371](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.18-371) (2018-05-24)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.17-362...insights-core-3.0.18-371)

**Fixed bugs:**

- httpd\_conf parser and combiner cannot handle directives in nest and parallel sections correct [\#1175](https://github.com/RedHatInsights/insights-core/issues/1175)

## [insights-core-3.0.17-362](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.17-362) (2018-05-21)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.16-355...insights-core-3.0.17-362)

**Closed issues:**

- Test of prodsec rules \(NFS\) are broken [\#1104](https://github.com/RedHatInsights/insights-core/issues/1104)

## [insights-core-3.0.16-355](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.16-355) (2018-05-16)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.15-350...insights-core-3.0.16-355)

## [insights-core-3.0.15-350](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.15-350) (2018-05-11)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.14-345...insights-core-3.0.15-350)

## [insights-core-3.0.14-345](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.14-345) (2018-05-10)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.13-338...insights-core-3.0.14-345)

**Implemented enhancements:**

- Use consistent heading and class style for parser catalogue [\#132](https://github.com/RedHatInsights/insights-core/issues/132)
- Create log transaction-id for log messages associated with a single transaction. [\#126](https://github.com/RedHatInsights/insights-core/issues/126)

**Fixed bugs:**

- A bug caused by typo in parser meminfo [\#1151](https://github.com/RedHatInsights/insights-core/issues/1151)
- fstab parser: parsing broken with ValueError [\#1126](https://github.com/RedHatInsights/insights-core/issues/1126)

**Closed issues:**

- Remove reminder comments after fixed mount-point-space issue from fstab's test [\#1157](https://github.com/RedHatInsights/insights-core/issues/1157)
- Add sos\_commands path entry into sos\_archive.py specs file. [\#1141](https://github.com/RedHatInsights/insights-core/issues/1141)
- LsPci needs to be anything but a LogFileOutput class [\#176](https://github.com/RedHatInsights/insights-core/issues/176)
- Asserts should be try/except in Prod [\#113](https://github.com/RedHatInsights/insights-core/issues/113)

## [insights-core-3.0.13-338](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.13-338) (2018-05-04)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.12-335...insights-core-3.0.13-338)

## [insights-core-3.0.12-335](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.12-335) (2018-05-03)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.11-322...insights-core-3.0.12-335)

## [insights-core-3.0.11-322](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.11-322) (2018-04-27)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.10-317...insights-core-3.0.11-322)

## [insights-core-3.0.10-317](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.10-317) (2018-04-26)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.9-309...insights-core-3.0.10-317)

**Fixed bugs:**

- Archives are wrong, extraneous top level files \(BZ1561015\) [\#1042](https://github.com/RedHatInsights/insights-core/issues/1042)

**Closed issues:**

- `obfuscate\_hostname` should require `obfuscate` \(BZ1554999\) [\#1016](https://github.com/RedHatInsights/insights-core/issues/1016)

## [insights-core-3.0.9-309](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.9-309) (2018-04-18)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.8-295...insights-core-3.0.9-309)

**Fixed bugs:**

- Add pcs\_status to sos\_archive.py [\#1082](https://github.com/RedHatInsights/insights-core/issues/1082)
- foreman production log needed for sos archives [\#1060](https://github.com/RedHatInsights/insights-core/issues/1060)
- hostname parser doesn't handle sos\_commands/general/hostname [\#1055](https://github.com/RedHatInsights/insights-core/issues/1055)

## [insights-core-3.0.8-295](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.8-295) (2018-04-12)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.4-3...insights-core-3.0.8-295)

**Fixed bugs:**

- ssh.py: ValueError: need more than 1 value to unpack  [\#1034](https://github.com/RedHatInsights/insights-core/issues/1034)

**Closed issues:**

- \[ls\_etc\] Test can be merged into docstring [\#1079](https://github.com/RedHatInsights/insights-core/issues/1079)

## [insights-core-3.0.4-3](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.4-3) (2018-04-06)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.7-270...insights-core-3.0.4-3)

**Fixed bugs:**

- SubscriptionManagerListInstalled should depend on Specs.subscription\_manager\_list\_installed [\#1047](https://github.com/RedHatInsights/insights-core/issues/1047)

**Closed issues:**

- Shippable fails with nbsphinx version 0.3.2 [\#1054](https://github.com/RedHatInsights/insights-core/issues/1054)

## [insights-core-3.0.7-270](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.7-270) (2018-03-28)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.6-261...insights-core-3.0.7-270)

**Closed issues:**

- . [\#1044](https://github.com/RedHatInsights/insights-core/issues/1044)

## [insights-core-3.0.6-261](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.6-261) (2018-03-20)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.6-257...insights-core-3.0.6-261)

## [insights-core-3.0.6-257](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.6-257) (2018-03-16)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.75.0-245...insights-core-3.0.6-257)

**Fixed bugs:**

- WARNING:insights.tests:Replacing ps\_auxcww in --appdebug output [\#1007](https://github.com/RedHatInsights/insights-core/issues/1007)
- Parser error in lsblk.py [\#790](https://github.com/RedHatInsights/insights-core/issues/790)
- Parser error in scsi.py [\#789](https://github.com/RedHatInsights/insights-core/issues/789)
- Parser error in fstab.py [\#788](https://github.com/RedHatInsights/insights-core/issues/788)
- Parser error in lssap.py [\#787](https://github.com/RedHatInsights/insights-core/issues/787)
- Parser error in lvm.py [\#784](https://github.com/RedHatInsights/insights-core/issues/784)
- Parser error in ntp\_sources.py [\#783](https://github.com/RedHatInsights/insights-core/issues/783)
- Parser error in dockerinfo.py [\#782](https://github.com/RedHatInsights/insights-core/issues/782)
- Parser error in ssh.py [\#781](https://github.com/RedHatInsights/insights-core/issues/781)
- Parser error in LsPci in lspci.py [\#780](https://github.com/RedHatInsights/insights-core/issues/780)
- Parser error in iptables.py [\#779](https://github.com/RedHatInsights/insights-core/issues/779)
- Parser error in netstat.py [\#778](https://github.com/RedHatInsights/insights-core/issues/778)
- Error in parser `fstab.py` [\#682](https://github.com/RedHatInsights/insights-core/issues/682)
- Error in combiner `lvm.py` [\#681](https://github.com/RedHatInsights/insights-core/issues/681)
- Possible parser error in `rabbitmq.py` [\#680](https://github.com/RedHatInsights/insights-core/issues/680)
- Another parser error in `iptables.py` [\#678](https://github.com/RedHatInsights/insights-core/issues/678)
- Parser error in `ntp\_sources.py` [\#677](https://github.com/RedHatInsights/insights-core/issues/677)
- Parser error in `ssh.py` [\#676](https://github.com/RedHatInsights/insights-core/issues/676)
- Error in parser `iptables.py` [\#675](https://github.com/RedHatInsights/insights-core/issues/675)
- Parser error in `blkid.py` [\#674](https://github.com/RedHatInsights/insights-core/issues/674)
- Parser error in `netstat.py` [\#673](https://github.com/RedHatInsights/insights-core/issues/673)

**Closed issues:**

- Should Docker Commands run in HostContext? [\#997](https://github.com/RedHatInsights/insights-core/issues/997)
- Collect specs that aren't used by a rule [\#654](https://github.com/RedHatInsights/insights-core/issues/654)
- Sync new style specs with old specs [\#598](https://github.com/RedHatInsights/insights-core/issues/598)

## [insights-core-1.75.0-245](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.75.0-245) (2018-03-12)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.74.0-241...insights-core-1.75.0-245)

**Implemented enhancements:**

- Cache Graph Run Order [\#974](https://github.com/RedHatInsights/insights-core/issues/974)
- Ability to enable and disable arbitrary components [\#969](https://github.com/RedHatInsights/insights-core/issues/969)
- Command parsers to be based on a CommandParser class [\#898](https://github.com/RedHatInsights/insights-core/issues/898)

**Fixed bugs:**

- Engine should parse all specs associated with an All SpecGroup [\#807](https://github.com/RedHatInsights/insights-core/issues/807)

**Closed issues:**

- Design and develop client runtime API [\#9](https://github.com/RedHatInsights/insights-core/issues/9)

## [insights-core-1.74.0-241](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.74.0-241) (2018-03-08)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.73.0-236...insights-core-1.74.0-241)

**Fixed bugs:**

- Invalid Subscription Manager specs [\#972](https://github.com/RedHatInsights/insights-core/issues/972)

**Closed issues:**

- Add check for brctl "No such file or directory" [\#988](https://github.com/RedHatInsights/insights-core/issues/988)
- Add parsers LvsAll, PvsAll, VgsAll and combiner LvmAll for getting LVM information for all accepted and rejected devices. \#908 [\#980](https://github.com/RedHatInsights/insights-core/issues/980)
- Install instructions do not work on RHEL 7 [\#911](https://github.com/RedHatInsights/insights-core/issues/911)
- Spec for command `modinfo` : remove OR enhance ? [\#730](https://github.com/RedHatInsights/insights-core/issues/730)

## [insights-core-1.73.0-236](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.73.0-236) (2018-02-27)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.72.0-224...insights-core-1.73.0-236)

**Implemented enhancements:**

- Refactor insights/specs\_\*.py files into a specs package [\#948](https://github.com/RedHatInsights/insights-core/issues/948)
- `FileListing` ignores `ls` listings that don't contain the name of the directory. [\#827](https://github.com/RedHatInsights/insights-core/issues/827)
- Update 3.x specs to handle 1.x archives [\#809](https://github.com/RedHatInsights/insights-core/issues/809)
- Insights test connection cleanup [\#708](https://github.com/RedHatInsights/insights-core/issues/708)
- Stacked Decorators are Bad [\#14](https://github.com/RedHatInsights/insights-core/issues/14)

**Fixed bugs:**

- Parser error in cluster\_conf.py [\#785](https://github.com/RedHatInsights/insights-core/issues/785)
- Parser error in `cluster\_conf.py` [\#679](https://github.com/RedHatInsights/insights-core/issues/679)
- Parser error in `check\_iptableds\_pid` [\#671](https://github.com/RedHatInsights/insights-core/issues/671)

**Closed issues:**

- Parser nmcli dev show 3.x [\#973](https://github.com/RedHatInsights/insights-core/issues/973)
- Separate specs required for Insights from those required for other archives [\#815](https://github.com/RedHatInsights/insights-core/issues/815)
- Remove 1.x spec handling from 3.x [\#808](https://github.com/RedHatInsights/insights-core/issues/808)
- Documentation referring to old parser requirement syntax [\#791](https://github.com/RedHatInsights/insights-core/issues/791)
- Get rpm signature from InstalledRpms parser [\#688](https://github.com/RedHatInsights/insights-core/issues/688)
- "runnable rules" [\#292](https://github.com/RedHatInsights/insights-core/issues/292)
- For Fava, alter the doc for each Parser and Combiner [\#291](https://github.com/RedHatInsights/insights-core/issues/291)
- run parsers and combiners \(and rules\) during collection [\#290](https://github.com/RedHatInsights/insights-core/issues/290)

## [insights-core-1.72.0-224](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.72.0-224) (2018-02-08)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0rc1...insights-core-1.72.0-224)

**Closed issues:**

- run\_phase: explicit handling of process.returncode values [\#931](https://github.com/RedHatInsights/insights-core/issues/931)
- Keep .registered, .unregistered in /etc/redhat-access-insights [\#915](https://github.com/RedHatInsights/insights-core/issues/915)
- PSAuxcww need to skip warning line [\#912](https://github.com/RedHatInsights/insights-core/issues/912)

## [3.0rc1](https://github.com/RedHatInsights/insights-core/tree/3.0rc1) (2018-01-30)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.4-2...3.0rc1)

## [insights-core-3.0.4-2](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.4-2) (2018-01-26)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.71.0-217...insights-core-3.0.4-2)

## [insights-core-1.71.0-217](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.71.0-217) (2018-01-26)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.70.0-214...insights-core-1.71.0-217)

**Fixed bugs:**

- Update --force-reregister messaging [\#703](https://github.com/RedHatInsights/insights-core/issues/703)

## [insights-core-1.70.0-214](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.70.0-214) (2018-01-23)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.69.0-211...insights-core-1.70.0-214)

## [insights-core-1.69.0-211](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.69.0-211) (2018-01-19)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.68.0-203...insights-core-1.69.0-211)

**Fixed bugs:**

- Client log file rotation issues [\#710](https://github.com/RedHatInsights/insights-core/issues/710)
- Client Crashes on Fedora 26 [\#706](https://github.com/RedHatInsights/insights-core/issues/706)
- Fix fallback in 1.x and 3.x version of the client [\#695](https://github.com/RedHatInsights/insights-core/issues/695)

## [insights-core-1.68.0-203](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.68.0-203) (2018-01-11)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.67.0-188...insights-core-1.68.0-203)

**Closed issues:**

- Parser for command output ip -s link \#859 [\#864](https://github.com/RedHatInsights/insights-core/issues/864)
- Add CPU flags to cpuinfo parser \#816 [\#837](https://github.com/RedHatInsights/insights-core/issues/837)

## [insights-core-1.67.0-188](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.67.0-188) (2018-01-02)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.66.0-177...insights-core-1.67.0-188)

## [insights-core-1.66.0-177](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.66.0-177) (2017-12-18)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.65.0-166...insights-core-1.66.0-177)

**Implemented enhancements:**

- De-duplicate `ps` parsers [\#382](https://github.com/RedHatInsights/insights-core/issues/382)

**Fixed bugs:**

- Parser error in rabbitmq.py [\#786](https://github.com/RedHatInsights/insights-core/issues/786)

**Closed issues:**

- Nova\_log parser has no tests [\#797](https://github.com/RedHatInsights/insights-core/issues/797)
- ClusterConf should be an XML parser rather than based on LogFileOutput [\#177](https://github.com/RedHatInsights/insights-core/issues/177)

## [insights-core-1.65.0-166](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.65.0-166) (2017-12-12)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.64.0-154...insights-core-1.65.0-166)

**Implemented enhancements:**

- Make remove.conf smarter [\#801](https://github.com/RedHatInsights/insights-core/issues/801)
- Ps parsers update for master branch \(\#744\) [\#793](https://github.com/RedHatInsights/insights-core/issues/793)
- Implement ACLs properly [\#712](https://github.com/RedHatInsights/insights-core/issues/712)

**Fixed bugs:**

- bug in Pvs parser and Lvm combiner [\#736](https://github.com/RedHatInsights/insights-core/issues/736)

**Closed issues:**

- Also parse the grub v1 config file for UEFI machine. \#794 [\#811](https://github.com/RedHatInsights/insights-core/issues/811)
- Added new parsers for two options under /sys/kernel/mm/transparent\_hugepage/. \#767 [\#769](https://github.com/RedHatInsights/insights-core/issues/769)
- Update Insights man pages [\#707](https://github.com/RedHatInsights/insights-core/issues/707)

## [insights-core-1.64.0-154](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.64.0-154) (2017-11-30)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.3-2...insights-core-1.64.0-154)

**Implemented enhancements:**

- SkipComponent/SkipException Handling and Extension to Combiners [\#720](https://github.com/RedHatInsights/insights-core/issues/720)

**Fixed bugs:**

- Parse Error in `ntp\_sources.py` [\#727](https://github.com/RedHatInsights/insights-core/issues/727)
- Parser error in `ntp\_sources.py` [\#672](https://github.com/RedHatInsights/insights-core/issues/672)
- SysconfigKdump parser missing from master branch [\#670](https://github.com/RedHatInsights/insights-core/issues/670)
- satellite\_version combiner should not return None [\#658](https://github.com/RedHatInsights/insights-core/issues/658)

**Closed issues:**

- Add parser audit\_log.py to 3.x [\#685](https://github.com/RedHatInsights/insights-core/issues/685)

## [insights-core-3.0.3-2](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.3-2) (2017-11-21)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.63.0-140...insights-core-3.0.3-2)

## [insights-core-1.63.0-140](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.63.0-140) (2017-11-21)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.62.0-129...insights-core-1.63.0-140)

**Fixed bugs:**

- jaylin test [\#719](https://github.com/RedHatInsights/insights-core/issues/719)
- .cache.json is not updated correctly [\#715](https://github.com/RedHatInsights/insights-core/issues/715)

**Closed issues:**

- test [\#718](https://github.com/RedHatInsights/insights-core/issues/718)

## [insights-core-1.62.0-129](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.62.0-129) (2017-11-13)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.61.0-127...insights-core-1.62.0-129)

## [insights-core-1.61.0-127](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.61.0-127) (2017-11-10)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.60.0-117...insights-core-1.61.0-127)

**Fixed bugs:**

- Incorrect use of optional dependencies in combiners [\#647](https://github.com/RedHatInsights/insights-core/issues/647)

**Closed issues:**

- Update docs and create PR for master branch for libkeyutils parser [\#643](https://github.com/RedHatInsights/insights-core/issues/643)

## [insights-core-1.60.0-117](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.60.0-117) (2017-11-01)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.59.0-113...insights-core-1.60.0-117)

**Closed issues:**

- Port Scaffold Script to Master Branch [\#254](https://github.com/RedHatInsights/insights-core/issues/254)

## [insights-core-1.59.0-113](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.59.0-113) (2017-10-27)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.58.0-107...insights-core-1.59.0-113)

## [insights-core-1.58.0-107](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.58.0-107) (2017-10-19)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.3-1...insights-core-1.58.0-107)

## [insights-core-3.0.3-1](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.3-1) (2017-10-18)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.57.0-102...insights-core-3.0.3-1)

## [insights-core-1.57.0-102](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.57.0-102) (2017-10-18)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.56.0-95...insights-core-1.57.0-102)

**Implemented enhancements:**

- De-duplicate util/parse\_table and parsers/parse\_fixed\_table [\#344](https://github.com/RedHatInsights/insights-core/issues/344)

**Closed issues:**

- Update yaml.load to yaml.safe\_load [\#316](https://github.com/RedHatInsights/insights-core/issues/316)

## [insights-core-1.56.0-95](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.56.0-95) (2017-10-12)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.55.0-90...insights-core-1.56.0-95)

**Fixed bugs:**

- limits\_conf "unlimitied" error [\#447](https://github.com/RedHatInsights/insights-core/issues/447)

## [insights-core-1.55.0-90](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.55.0-90) (2017-10-11)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.54.0-87...insights-core-1.55.0-90)

## [insights-core-1.54.0-87](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.54.0-87) (2017-10-11)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.53.0-81...insights-core-1.54.0-87)

## [insights-core-1.53.0-81](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.53.0-81) (2017-10-10)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.52.0-71...insights-core-1.53.0-81)

## [insights-core-1.52.0-71](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.52.0-71) (2017-10-06)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.2-6...insights-core-1.52.0-71)

## [insights-core-3.0.2-6](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.2-6) (2017-10-04)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.1-1...insights-core-3.0.2-6)

## [insights-core-3.0.1-1](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.1-1) (2017-10-03)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.0-5...insights-core-3.0.1-1)

## [insights-core-3.0.0-5](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.0-5) (2017-10-03)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.51.0-65...insights-core-3.0.0-5)

## [insights-core-1.51.0-65](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.51.0-65) (2017-09-29)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.50.0-56...insights-core-1.51.0-65)

## [insights-core-1.50.0-56](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.50.0-56) (2017-09-26)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.49.0-38...insights-core-1.50.0-56)

**Implemented enhancements:**

- Rework core runtime to be like vulcan [\#11](https://github.com/RedHatInsights/insights-core/issues/11)
- Support Python Version 2.6.x [\#10](https://github.com/RedHatInsights/insights-core/issues/10)

**Closed issues:**

- Should probably rename hand\_map\_error and handle\_reduce\_error in evaluators.py [\#66](https://github.com/RedHatInsights/insights-core/issues/66)
- Drop support for local mappers [\#7](https://github.com/RedHatInsights/insights-core/issues/7)

## [insights-core-1.49.0-38](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.49.0-38) (2017-09-15)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.49.0-37...insights-core-1.49.0-38)

**Fixed bugs:**

- chkconfig.py can not parsed RHEL 7.3 'chkconfig --list' [\#112](https://github.com/RedHatInsights/insights-core/issues/112)
- Vgdisplay spec does not match sos report or rule [\#13](https://github.com/RedHatInsights/insights-core/issues/13)

**Closed issues:**

- Get 100% test coverage of insights/core/\_\_init\_\_.py [\#139](https://github.com/RedHatInsights/insights-core/issues/139)

## [insights-core-1.49.0-37](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.49.0-37) (2017-09-13)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.48.0-34...insights-core-1.49.0-37)

## [insights-core-1.48.0-34](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.48.0-34) (2017-09-12)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.47.0-17...insights-core-1.48.0-34)

**Closed issues:**

- Sync the master branch with 1.x branch [\#121](https://github.com/RedHatInsights/insights-core/issues/121)

## [insights-core-1.47.0-17](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.47.0-17) (2017-08-31)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.46.0-15...insights-core-1.47.0-17)

## [insights-core-1.46.0-15](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.46.0-15) (2017-08-30)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.46.0-12...insights-core-1.46.0-15)

## [insights-core-1.46.0-12](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.46.0-12) (2017-08-28)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.44.0-105...insights-core-1.46.0-12)

**Closed issues:**

- CertificatesEnddate fails to parse filenames [\#300](https://github.com/RedHatInsights/insights-core/issues/300)

## [insights-core-1.44.0-105](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.44.0-105) (2017-08-02)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.44.0-103...insights-core-1.44.0-105)

## [insights-core-1.44.0-103](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.44.0-103) (2017-07-28)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.43.0-93...insights-core-1.44.0-103)

**Fixed bugs:**

- Lvs mapper fails on lists with log and image LVs [\#288](https://github.com/RedHatInsights/insights-core/issues/288)

**Closed issues:**

- Move AlternativesOutput class and associated parsers into single file. [\#140](https://github.com/RedHatInsights/insights-core/issues/140)

## [insights-core-1.43.0-93](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.43.0-93) (2017-07-18)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.42.0-63...insights-core-1.43.0-93)

**Implemented enhancements:**

- Support python 2.6 [\#180](https://github.com/RedHatInsights/insights-core/issues/180)

**Closed issues:**

- Add new shared parser irqbalance\_conf.py \#213 [\#223](https://github.com/RedHatInsights/insights-core/issues/223)
- Should we convert this multinode parser \(metadata.json\) to class type ? [\#221](https://github.com/RedHatInsights/insights-core/issues/221)
- NTPConfParser class is missing from the documentation [\#167](https://github.com/RedHatInsights/insights-core/issues/167)
- Neutron server log documentation for 1.x branch \#146 [\#152](https://github.com/RedHatInsights/insights-core/issues/152)
- Neutron plugin documentation for 1.x branch \#145 [\#151](https://github.com/RedHatInsights/insights-core/issues/151)
- Test scannable parser class for 1.x branch \#144 [\#150](https://github.com/RedHatInsights/insights-core/issues/150)
- Remove the deprecated `.data` from LsBoot \#103 [\#104](https://github.com/RedHatInsights/insights-core/issues/104)
- Limits conf combiner \#70 [\#85](https://github.com/RedHatInsights/insights-core/issues/85)

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

## [insights-core-1.41.0-43](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.41.0-43) (2017-06-20)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/falafel-1.40.0-23...insights-core-1.41.0-43)

**Closed issues:**

- Update ceph\_version to add version 2.2 \#105 [\#106](https://github.com/RedHatInsights/insights-core/issues/106)
- Removing previously used but abandoned test functions \#98 [\#99](https://github.com/RedHatInsights/insights-core/issues/99)
- Expose associated satellite information in system metadata \#65 [\#87](https://github.com/RedHatInsights/insights-core/issues/87)
- Added keyword\_search function \#69 [\#86](https://github.com/RedHatInsights/insights-core/issues/86)
- Rename from falafel to insights-core [\#8](https://github.com/RedHatInsights/insights-core/issues/8)

## [falafel-1.40.0-23](https://github.com/RedHatInsights/insights-core/tree/falafel-1.40.0-23) (2017-06-07)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/falafel-1.39.0-11...falafel-1.40.0-23)

**Fixed bugs:**

- Transaction check error w/python-requests on falafel-1.38.0-25 installation [\#12](https://github.com/RedHatInsights/insights-core/issues/12)

**Closed issues:**

- uname parser fails for kernel 2.6.32-504.8.2.bgq.el6 [\#52](https://github.com/RedHatInsights/insights-core/issues/52)

## [falafel-1.39.0-11](https://github.com/RedHatInsights/insights-core/tree/falafel-1.39.0-11) (2017-05-31)


\* *This Change Log was automatically generated by [github_changelog_generator](https://github.com/skywinder/Github-Changelog-Generator)*