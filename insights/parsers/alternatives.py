"""
Alternatives - command ``/usr/bin/alternatives`` output
=======================================================
"""

from insights import parser, CommandParser
from insights.core.exceptions import ParseException
from insights.specs import Specs


class AlternativesOutput(CommandParser):
    """
    Read the output of ``/usr/sbin/alternatives --display *program*`` and
    convert into information about the given program's alternatives.

    Typical input is::

        java - status is auto.
         link currently points to /usr/lib/jvm/java-1.8.0-openjdk-1.8.0.111-1.b15.el7_2.x86_64/jre/bin/java
        /usr/lib/jvm/java-1.7.0-openjdk-1.7.0.111-2.6.7.2.el7_2.x86_64/jre/bin/java - priority 1700111
        /usr/lib/jvm/java-1.8.0-openjdk-1.8.0.111-1.b15.el7_2.x86_64/jre/bin/java - priority 1800111
        /usr/lib/jvm/jre-1.6.0-ibm.x86_64/bin/java - priority 16091
         slave ControlPanel: /usr/lib/jvm/jre-1.6.0-ibm.x86_64/bin/ControlPanel
         slave keytool: /usr/lib/jvm/jre-1.6.0-ibm.x86_64/bin/keytool
         slave policytool: /usr/lib/jvm/jre-1.6.0-ibm.x86_64/bin/policytool
         slave rmid: /usr/lib/jvm/jre-1.6.0-ibm.x86_64/bin/rmid
        Current `best' version is /usr/lib/jvm/jre-1.6.0-ibm.x86_64/bin/java.

    Lines are interpreted this way:

    * Program lines are of the form '*name* - status is *status*', and start
      the information for a program.  Lines before this are ignored.
    * The current link to this program is found on lines starting with 'link
      currently points to'.
    * Lines starting with '/' and with ' - priority ' in them record an
      alternative path and its priority.
    * Lines starting with 'slave *program*: *path*' are recorded against the
      alternative path.
    * Lines starting with 'Current \`best' version is' indicate the default
      choice of an 'auto' status alternative.

    The output of ``alternatives --display *program*`` can only ever list one
    program, so as long as one 'status is' line is found (as described above),
    the content of the object displays that program.

    Attributes:
        program (str): The name of the program found in the 'status is' line.
            This attribute is set to ``None`` if a status line is not found.
        status (str): The status of the program, or ``None`` if not found.
        link (str): The link to this program, or ``None`` if the 'link
            currently points to`` line is not found.
        best (str): The 'best choice' path that ``alternatives`` would use, or
            ``None`` if the 'best choice' line is not found.
        paths (dict): The alternative paths for this program.  Each path is a
            dictionary containing the following keys:

              * ``path``: the actual path of this alternative for the program
              * ``priority``: the priority, as an integer (e.g. 1700111)
              * ``slave``: a dictionary of programs dependent on this alternative -
                the key is the program name (e.g. 'ControlPanel') and the value is
                the path to that program for this alternative path.

    Examples:
        >>> java_alt.program
        'java'
        >>> java_alt.link
        '/usr/lib/jvm/jre-1.6.0-ibm.x86_64/bin/java'
        >>> len(java_alt.paths)
        2
        >>> java_alt.paths[0]['path']
        '/usr/lib/jvm/jre-1.6.0-ibm.x86_64/bin/java'
        >>> java_alt.paths[0]['priority']
        16091
        >>> java_alt.paths[0]['slave']['ControlPanel']
        '/usr/lib/jvm/jre-1.6.0-ibm.x86_64/bin/ControlPanel'
    """

    def parse_content(self, content):
        """
        Parse the output of the ``alternatives`` command.
        """
        self.program = None
        self.status = None
        self.link = None
        self.best = None
        self.paths = []
        current_path = None
        # Set up instance variable

        for line in content:
            words = line.split(None)
            if ' - status is' in line:
                # alternatives only displays one program, so finding
                # this line again is an error.
                if self.program:
                    raise ParseException(
                        "Program line for {newprog} found in output for {oldprog}".format(
                            newprog=words[0], oldprog=self.program
                        )
                    )
                # Set up new program data
                self.program = words[0]
                self.status = words[4][:-1]  # remove trailing .
                self.alternatives = []
                current_path = {}
            elif not self.program:
                # Lines before 'status is' line are ignored
                continue
            elif line.startswith(' link currently points to ') and len(words) == 5:
                # line: ' link currently points to /usr/lib/jvm/java-1.8.0-openjdk-1.8.0.111-1.b15.el7_2.x86_64/jre/bin/java'
                self.link = words[4]
            elif ' - priority ' in line and len(words) == 4 and words[3].isdigit():
                # line: /usr/lib/jvm/jre-1.6.0-ibm.x86_64/bin/java - priority 16091
                # New path - save current path if set
                self.paths.append({
                    'path': words[0],
                    'priority': int(words[3]),
                    'slave': {},
                })
                current_path = self.paths[-1]
            elif line.startswith(' slave ') and len(words) == 3 and current_path:
                # line: ' slave ControlPanel: /usr/lib/jvm/jre-1.6.0-ibm.x86_64/bin/ControlPanel'
                current_path['slave'][words[1][:-1]] = words[2]  # remove final : from program
            elif line.startswith("Current `best' version is ") and len(words) == 5:
                # line: 'Current `best' version is /usr/lib/jvm/jre-1.6.0-ibm.x86_64/bin/java.'
                self.best = words[4][:-1]  # strip trailing . from path


@parser(Specs.display_java)
class JavaAlternatives(AlternativesOutput):
    """
    Class to read the ``/usr/sbin/alternatives --display java`` output.

    Uses the ``AlternativesOutput`` base class to get information about the
    alternatives for ``java`` available and which one is currently in use.

    Examples:
        >>> java_alt.program
        'java'
        >>> java_alt.link
        '/usr/lib/jvm/jre-1.6.0-ibm.x86_64/bin/java'
        >>> len(java_alt.paths)
        2
        >>> java_alt.paths[0]['path']
        '/usr/lib/jvm/jre-1.6.0-ibm.x86_64/bin/java'
        >>> java_alt.paths[0]['priority']
        16091
        >>> java_alt.paths[0]['slave']['ControlPanel']
        '/usr/lib/jvm/jre-1.6.0-ibm.x86_64/bin/ControlPanel'
    """
    pass


@parser(Specs.alternatives_display_python)
class PythonAlternatives(AlternativesOutput):
    """
    Class to read the ``/usr/sbin/alternatives --display python`` output.

    Uses the ``AlternativesOutput`` base class to get information about the
    alternatives for ``best`` available and which one is currently in use.

    Examples:
        >>> python_alt.program
        'python'
        >>> python_alt.link
        '/usr/bin/python3'
        >>> len(python_alt.paths)
        2
        >>> python_alt.paths[0]['path']
        '/usr/libexec/no-python'
        >>> python_alt.paths[0]['priority']
        404
    """
    pass
