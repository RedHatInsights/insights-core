from .. import mapper, Mapper, get_active_lines

foreman_sat6_ver_map = {
    '1.5': '6.0',
    '1.6.0.53': '6.0.8',
    '1.7': '6.1',
    '1.7.2.33': '6.1.1',
    '1.7.2.36': '6.1.2',
    '1.7.2.43': '6.1.3',
    '1.7.2.46': '6.1.4',
    '1.7.2.49': '6.1.5',
    '1.7.2.50': '6.1.6',
    '1.7.2.53': '6.1.7',
    '1.7.2.55': '6.1.8',
    '1.7.2.56': '6.1.9',
    '1.11': '6.2',
}


@mapper('satellite_version.rb')
@mapper('installed-rpms')
class SatelliteVersion(Mapper):
    """
    Version of Satellite 5.x and 6.x:
    - E.g.
      Satellite 5.x:
       version:      "5.3.0"
       version_full: "5.3.0.27-1.el5sat-noarch"

      Satellite 6.x:
       version:      "6.2.0"
       version_full: "6.2.0.11-1.el7sat.noarch"

       version:      "6.1"
       version_full: None
    ---
    For Satellite 6.x
    - https://access.redhat.com/articles/1343683
    - https://bugzilla.redhat.com/show_bug.cgi?id=1191584
    1. Check the version information in below files at first:
       - satellite_version
       - usr/share/foreman/lib/satellite/version.rb
    2. Check the version of foreman or satellite-installer, when the files
       listed in (1) are not found.
                            Sat 6.0     Sat 6.1     Sat 6.2
       foreman              1.5.x       1.7.x       1.11.0
       satellite-installer  -           -           6.2.x

    For Satellite 5.x
    - https://access.redhat.com/solutions/1224043
      Return the version of satellite-schema directly
      > 5.3~5.7: satellite-schema
      > 5.0~5.2: rhn-satellite-schema
      Because of satellite-branding is not deployed in Sat 5.0~5.2, and
      satellite-schema can also be used for checking the version, so here we use
      satellite-schema instead of satellite-branding
    """
    def parse_content(self, content):
        self.version_full = None
        self.version = None
        # Spec: satellite_version
        if 'version' in self.file_path.lower():
            for line in content:
                if line.strip().upper().startswith('VERSION'):
                    self.version = line.split()[-1].strip('"')
                    break
        # Spec: installed-rpms
        else:
            sat5_pkg = ('satellite-schema-', 'rhn-satellite-schema-')
            sat6_pkg = ('foreman-1')  # Add "-1" to check the `foreman` package only
            # From Sat 6.2, we can also check `satellite-installer` instead of `foreman`
            sat62_pkg = ('satellite-installer-')
            for line in get_active_lines(content, comment_char="COMMAND>"):
                # for 6.x
                if line.startswith(sat6_pkg):
                    pkg_ver = line.split('-')[1]
                    self.version = foreman_sat6_ver_map.get(pkg_ver)
                    # for `1.5`, `1.7` and `1.11`
                    if self.version is None:
                        pkg_mj_ver = '.'.join(pkg_ver.split('.')[:2])
                        self.version = foreman_sat6_ver_map.get(pkg_mj_ver)
                    # for 6.2, need to check `satellite-installer` further
                    if self.version != '6.2':
                        break
                # for 6.2 (if `satellite-installer` is installed)
                elif line.startswith(sat62_pkg):
                    # get the version of `satellite-installer`
                    self.version_full = line.split()[0][len(sat62_pkg):]
                    self.version = '.'.join(self.version_full.split('.')[:3])
                    break
                # for 5.x
                elif line.startswith(sat5_pkg):
                    # get the version of `[rhn-]satellite-schema`
                    pkg = line.split()[0]
                    self.version_full = pkg[pkg.find('schema-') + 7:]
                    self.version = '.'.join(self.version_full.split('.')[:3])
                    break
