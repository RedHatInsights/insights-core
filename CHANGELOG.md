## 1.39.0

### Bug Fixes
- Fix filename attribute when walking an egg file
- Bypass file reading if a mapper is not registered
- Skip "command not found" as well as "timeout" mapper inputs
- Fix failure when unprivileged user tries to unpack /dev/null from insights
  archive
- Various issues with LVM

### Documentation
- Adding documentation folder
- Mappers with added/modified docstrings:
    - netconsole
    - lvm
    - mariadb
    - multipath
    - sssd_logs
    - modprobe

### Removals
Old-style mapper functions that have been removed:

- haproxy_cfg_parser
- get_netstat_s
- dcbtool_gc_dcb
- oracle_pfile
- oracle_spfile
- dmesg
- vmcore_dmesg
- docker_list

### Features/Improvements
- Improved test coverage
- Integration tests honor filters set by plugins/mappers
- Adding archive tool to project
- Reworking dependency handling during rule execution
