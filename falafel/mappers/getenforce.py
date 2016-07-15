from falafel.core.plugins import mapper

@mapper('getenforce')
def getenforcevalue(context):
    """
    The output of "getenforce" command is in ["Enforcing","Permissive","Disabled"], so we can return the content directly.
    """
    return {"status": context.content[0]}
