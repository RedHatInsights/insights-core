from falafel.core.plugins import mapper


def get_sat6_version(content):
    """
    Return the version of Satellite 6.x
    - https://access.redhat.com/articles/1343683
    - https://bugzilla.redhat.com/show_bug.cgi?id=1191584
      > Check the version in foreman_debug/satellite_version
    """
    for line in content:
        # For Satellite 6.x, context is satellite_version in foreman_debug
        line_split = line.split()
        if len(line_split) == 3 and line_split[0] == 'VERSION':
            return line_split[-1].strip('"')
    # Returns None for no satellite installed
    return None


def get_sat5_version(content):
    """
    Return the version of Satellite 5.x
    - https://access.redhat.com/solutions/1224043
      Return the version of satellite-schema directly
      > 5.3~5.7: satellite-schema
      > 5.0~5.2: rhn-satellite-schema
      Because satellite-branding is not deployed in 5.0~5.2, and
      satellite-schema can also be used for checking the version, so here we use
      satellite-schema instead of satellite-branding
    """
    for line in content:
        # For Satellite 5.0, context is installed-rpms
        if line.startswith(('satellite-schema-', 'rhn-satellite-schema-')):
            line = line.split()[0]
            return line[line.find('schema-') + 7:]
    # Returns None for no satellite installed
    return None


@mapper('satellite_version.rb')
@mapper('installed-rpms')
def get_sat_version(context):
    """
    Returns the full version of Satellite 5.x and 6.x:
    - E.g.
    - Sat 5.x: "5.3.0.27-1.el5sat-noarch"
    - Sat 6.x: "6.1.3"
    """
    sat6_ver = get_sat6_version(context.content)
    sat_ver = sat6_ver if sat6_ver else get_sat5_version(context.content)
    return sat_ver
