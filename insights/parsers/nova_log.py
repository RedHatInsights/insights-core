"""
nova_log - files ``/var/log/nova/*.log``
========================================
"""
from .. import LogFileOutput, parser


@parser('nova-compute.log')
class NovaComputeLog(LogFileOutput):
    """Class for parsing the ``/var/log/nova/nova-compute.log`` file.

    .. note::
        Please refer to its super-class ``LogFileOutput``
    """
    def get(self, keywords):
        """
        Returns all lines that contain all keywords.

        Parameters:
            keywords(str or list): one or more strings to find in the lines.

        Returns:
            (list): The list of lines that contain all the keywords given.
        """
        r = []
        for l in self.lines:
            if type(keywords) == list and all([word in l for word in keywords]):
                r.append(l)
            elif type(keywords) == str and keywords in l:
                r.append(l)
        return r
