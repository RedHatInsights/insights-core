"""
display_java - Command ``/usr/sbin/alternatives --display java``
================================================================

Reads the output of the ``alternatives`` command to look at the current
location of ``java``.

Returns the last item on the line starting with 'link currently points to'.
If this is not found, returns None.

Example input::

    java - status is auto.
     link currently points to /usr/lib/jvm/java-1.8.0-openjdk-1.8.0.111-1.b15.el7_2.x86_64/jre/bin/java
    /usr/lib/jvm/java-1.7.0-openjdk-1.7.0.111-2.6.7.2.el7_2.x86_64/jre/bin/java - priority 1700111
    /usr/lib/jvm/java-1.8.0-openjdk-1.8.0.111-1.b15.el7_2.x86_64/jre/bin/java - priority 1800111

Examples:

    >>> java = shared[display_java]
    >>> java
    '/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.111-1.b15.el7_2.x86_64/jre/bin/java'
"""

from .. import parser

JAVA_LINK_FLAG = 'link currently points to'


@parser('display_java')
def default_java(context):
    """
    str: Returns the full path of the linked java, e.g.
    "/usr/lib/jvm/jre-1.7.0-openjdk.x86_64/bin/java"
    If no line contains 'link currently points to', then `None` is returned.
    """
    for line in context.content:
        if JAVA_LINK_FLAG in line:
            line_splits = line.split()
            if len(line_splits) == 5:
                return line_splits[-1]
