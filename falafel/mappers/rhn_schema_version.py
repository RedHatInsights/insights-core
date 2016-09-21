from .. import mapper


@mapper('rhn-schema-version')
def rhn_schema_version(context):
    """
    Returns the database schema version:
    - E.g.: "5.6.0.10-2.el6sat"
    """
    return context.content[0].strip()
