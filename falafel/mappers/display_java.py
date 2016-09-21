from .. import mapper

JAVA_LINK_FLAG = 'link currently points to'


@mapper('display_java')
def default_java(context):
    """
    Returns the full path of the linked java
    - E.g.
      "/usr/lib/jvm/jre-1.7.0-openjdk.x86_64/bin/java"
    """
    for line in context.content:
        if JAVA_LINK_FLAG in line:
            line_splits = line.split()
            if len(line_splits) == 5:
                return line_splits[-1]
