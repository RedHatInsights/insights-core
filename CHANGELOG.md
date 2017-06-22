# Change Log

## [Unreleased](https://github.com/RedHatInsights/insights-core/tree/HEAD)

[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.41.0-43...HEAD)

**Closed issues:**

- Simplify Policy booleans handling \#96 [\#97](https://github.com/RedHatInsights/insights-core/issues/97)
- Falafel reference in image [\#23](https://github.com/RedHatInsights/insights-core/issues/23)

**Merged pull requests:**

- add new shared parser [\#129](https://github.com/RedHatInsights/insights-core/pull/129) ([xiaoyu74](https://github.com/xiaoyu74))
- Unitfiles parser enhanced to deal with all unit states and enhanced w… [\#114](https://github.com/RedHatInsights/insights-core/pull/114) ([jsvob](https://github.com/jsvob))
- Simplify 'Policy booleans' handling [\#96](https://github.com/RedHatInsights/insights-core/pull/96) ([PaulWay](https://github.com/PaulWay))

## [insights-core-1.41.0-43](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.41.0-43) (2017-06-20)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/falafel-1.40.0-23...insights-core-1.41.0-43)

**Closed issues:**

- Update ceph\_version to add version 2.2 \#105 [\#106](https://github.com/RedHatInsights/insights-core/issues/106)
- Removing previously used but abandoned test functions \#98 [\#99](https://github.com/RedHatInsights/insights-core/issues/99)
- Expose associated satellite information in system metadata \#65 [\#87](https://github.com/RedHatInsights/insights-core/issues/87)
- Added keyword\_search function \#69 [\#86](https://github.com/RedHatInsights/insights-core/issues/86)
- Rename from falafel to insights-core [\#8](https://github.com/RedHatInsights/insights-core/issues/8)

**Merged pull requests:**

- Update ceph\_version to add version 2.2 [\#107](https://github.com/RedHatInsights/insights-core/pull/107) ([shzhou12](https://github.com/shzhou12))
- Enhance parser openshift\_get in master [\#102](https://github.com/RedHatInsights/insights-core/pull/102) ([wushiqinlou](https://github.com/wushiqinlou))
- Removing previously used but abandoned test functions [\#98](https://github.com/RedHatInsights/insights-core/pull/98) ([PaulWay](https://github.com/PaulWay))
- Expose satellite information in the system metadata [\#89](https://github.com/RedHatInsights/insights-core/pull/89) ([jeudy100](https://github.com/jeudy100))
- Update docs and consolidate tests for parsers module [\#78](https://github.com/RedHatInsights/insights-core/pull/78) ([bfahr](https://github.com/bfahr))
- Added ``keyword\_search`` function [\#69](https://github.com/RedHatInsights/insights-core/pull/69) ([PaulWay](https://github.com/PaulWay))
- Rename parser module tests [\#68](https://github.com/RedHatInsights/insights-core/pull/68) ([PaulWay](https://github.com/PaulWay))
- Fix exception 'unexpected keyword argument' when calling a rule. [\#64](https://github.com/RedHatInsights/insights-core/pull/64) ([matysek](https://github.com/matysek))
- Fix netstat rows\_by\(\) method to implement AND rather than OR search [\#62](https://github.com/RedHatInsights/insights-core/pull/62) ([PaulWay](https://github.com/PaulWay))
- Bond module tests at 100% code coverage [\#58](https://github.com/RedHatInsights/insights-core/pull/58) ([PaulWay](https://github.com/PaulWay))
- AlternativesOutput mapper class definition [\#47](https://github.com/RedHatInsights/insights-core/pull/47) ([PaulWay](https://github.com/PaulWay))

## [falafel-1.40.0-23](https://github.com/RedHatInsights/insights-core/tree/falafel-1.40.0-23) (2017-06-07)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/falafel-1.39.0-11...falafel-1.40.0-23)

**Fixed bugs:**

- Transaction check error w/python-requests on falafel-1.38.0-25 installation [\#12](https://github.com/RedHatInsights/insights-core/issues/12)

**Closed issues:**

- uname parser fails for kernel 2.6.32-504.8.2.bgq.el6 [\#52](https://github.com/RedHatInsights/insights-core/issues/52)

**Merged pull requests:**

- Enhance grub\_conf coverage test to 100% [\#60](https://github.com/RedHatInsights/insights-core/pull/60) ([xiangce](https://github.com/xiangce))
- Remove the deprecated method: get\_expiration\_date\(\). \(master\) [\#59](https://github.com/RedHatInsights/insights-core/pull/59) ([JoySnow](https://github.com/JoySnow))
- df parser at 100% code coverage in tests [\#56](https://github.com/RedHatInsights/insights-core/pull/56) ([PaulWay](https://github.com/PaulWay))
- Skip newline 4 rhel6.3 [\#55](https://github.com/RedHatInsights/insights-core/pull/55) ([chenlizhong](https://github.com/chenlizhong))
- Fix uname to accept 5 sections in release string. \(master\) [\#54](https://github.com/RedHatInsights/insights-core/pull/54) ([jsvob](https://github.com/jsvob))
- SMARTctl parser at 100% code coverage in tests [\#51](https://github.com/RedHatInsights/insights-core/pull/51) ([PaulWay](https://github.com/PaulWay))
- tomcat\_web\_xml at 100% code coverage in tests [\#50](https://github.com/RedHatInsights/insights-core/pull/50) ([PaulWay](https://github.com/PaulWay))
- Enhance grub\_conf.py [\#49](https://github.com/RedHatInsights/insights-core/pull/49) ([xiangce](https://github.com/xiangce))
- Uptime improved processing and test coverage [\#48](https://github.com/RedHatInsights/insights-core/pull/48) ([PaulWay](https://github.com/PaulWay))
- Don't process blank lines from blkid [\#44](https://github.com/RedHatInsights/insights-core/pull/44) ([kylape](https://github.com/kylape))
- Revert deletion of test for systemctl\_show\_mariadb [\#41](https://github.com/RedHatInsights/insights-core/pull/41) ([bfahr](https://github.com/bfahr))
- Use correct base archive version [\#39](https://github.com/RedHatInsights/insights-core/pull/39) ([kylape](https://github.com/kylape))
- Moved test\_systemctl\_show\_mariadb.py to ./insights/parsers/tests [\#38](https://github.com/RedHatInsights/insights-core/pull/38) ([vishwanathjadhav](https://github.com/vishwanathjadhav))
- Enhance httpd\_conf mapper and shared reducer [\#36](https://github.com/RedHatInsights/insights-core/pull/36) ([skontar](https://github.com/skontar))
- cpuinfo\_max\_freq mapper is no longer in use - removing mapper files entirely [\#34](https://github.com/RedHatInsights/insights-core/pull/34) ([PaulWay](https://github.com/PaulWay))
- Prepare for release on pypi [\#30](https://github.com/RedHatInsights/insights-core/pull/30) ([kylape](https://github.com/kylape))
- Updated multipath config to use mapper class [\#22](https://github.com/RedHatInsights/insights-core/pull/22) ([PaulWay](https://github.com/PaulWay))
- Enhance grub\_conf.py [\#21](https://github.com/RedHatInsights/insights-core/pull/21) ([xiangce](https://github.com/xiangce))
- Netstat mapper improvements [\#20](https://github.com/RedHatInsights/insights-core/pull/20) ([PaulWay](https://github.com/PaulWay))
- XFS info improvements [\#19](https://github.com/RedHatInsights/insights-core/pull/19) ([PaulWay](https://github.com/PaulWay))
- fd\_total\_limit mapper is unused - remove it and improve tests  [\#18](https://github.com/RedHatInsights/insights-core/pull/18) ([PaulWay](https://github.com/PaulWay))
- Added Shared Mapper for mariadb service parameters check [\#4](https://github.com/RedHatInsights/insights-core/pull/4) ([vishwanathjadhav](https://github.com/vishwanathjadhav))
- Enhance mapper certificates\_enddate.py [\#2](https://github.com/RedHatInsights/insights-core/pull/2) ([JoySnow](https://github.com/JoySnow))

## [falafel-1.39.0-11](https://github.com/RedHatInsights/insights-core/tree/falafel-1.39.0-11) (2017-05-31)
**Merged pull requests:**

- Adding missing files from rhel7 base archive [\#29](https://github.com/RedHatInsights/insights-core/pull/29) ([kylape](https://github.com/kylape))
- Use new naming conventions. [\#27](https://github.com/RedHatInsights/insights-core/pull/27) ([csams](https://github.com/csams))
- cpuinfo\_max\_freq mapper is no longer in use - removing mapper files entirely [\#17](https://github.com/RedHatInsights/insights-core/pull/17) ([PaulWay](https://github.com/PaulWay))
- Package archive tool data files [\#16](https://github.com/RedHatInsights/insights-core/pull/16) ([kylape](https://github.com/kylape))
- Update ansible repo references to RedHatInsights. [\#15](https://github.com/RedHatInsights/insights-core/pull/15) ([csams](https://github.com/csams))
- Add back the archive tool [\#6](https://github.com/RedHatInsights/insights-core/pull/6) ([kylape](https://github.com/kylape))



\* *This Change Log was automatically generated by [github_changelog_generator](https://github.com/skywinder/Github-Changelog-Generator)*