from falafel.core.plugins import mapper


@mapper("redhat-release")
def redhat_release(context):
    """
    As the content of file /etc/redhat-release is a string, we can return the content directly.
    """
    return {
        'file_content': context.content[0],
        'rhel_release': context.release,
        'rhel_version': context.version
    }
