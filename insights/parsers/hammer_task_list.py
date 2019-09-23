"""
HammerTaskList - command ``hammer --csv task list``
===================================================

This parser reads the task list of a Satellite server using hammer, in CSV
format.  It relies on the root user running the command being able to do
authenticated commands, which currently relies on the Satellite administrator
setting up an authentication file.  This is often done as a convenience; if
the command is unable to authenticate then no tasks will be shown and an
error flag will be recorded in the parser.

Sample output from the ``hammer --csv task list`` command::

    ID,Name,Owner,Started at,Ended at,State,Result,Task action,Task errors
    92b732ea-7423-4644-8890-80e054f1799a,,foreman_api_admin,2016/11/11 07:18:32,2016/11/11 07:18:34,stopped,success,Refresh repository,""
    e9cb6455-a433-467e-8404-7d01bd726689,,foreman_api_admin,2016/11/11 07:18:28,2016/11/11 07:18:31,stopped,success,Refresh repository,""
    e30f3e7e-c023-4380-9594-337fdc4967e4,,foreman_api_admin,2016/11/11 07:18:24,2016/11/11 07:18:28,stopped,success,Refresh repository,""
    3197f6a1-891f-4f42-9e4d-92c83c3ed035,,foreman_api_admin,2016/11/11 07:18:20,2016/11/11 07:18:24,stopped,success,Refresh repository,""
    22169621-7175-411c-86be-46b4254a4e77,,foreman_api_admin,2016/11/11 07:18:16,2016/11/11 07:18:19,stopped,success,Refresh repository,""
    f111e8f7-c956-470b-abb6-2e436ecd5866,,foreman_api_admin,2016/11/11 07:18:14,2016/11/11 07:18:16,stopped,success,Refresh repository,""
    dfc702ea-ce46-427c-8a07-43e2a68e1320,,foreman_api_admin,2016/11/11 07:18:12,2016/11/11 07:18:14,stopped,success,Refresh repository,""
    e8cac892-e666-4f2c-ab97-2be298da337e,,foreman_api_admin,2016/11/11 07:18:09,2016/11/11 07:18:12,stopped,success,Refresh repository,""
    e6c1e1b2-a29d-4fd0-891e-e736dc9b7150,,,2016/11/11 07:14:06,2016/11/12 05:10:17,stopped,success,Listen on candlepin events,""
    44a42c49-3038-4cae-8067-4d1cc305db05,,,2016/11/11 07:11:44,2016/11/11 07:12:47,stopped,success,Listen on candlepin events,""
    72669288-54ac-41ba-a3b2-314a2c81f438,,,2016/11/11 06:57:15,2016/11/11 07:07:03,stopped,success,Listen on candlepin events,""
    1314c91e-19d6-4d71-9bca-31db0df0aad2,,foreman_admin,2016/11/11 06:55:59,2016/11/11 06:55:59,stopped,error,Update for host sat62disc.example.org,"There was an issue with the backend service candlepin: 404 Resource Not Found, There was an issue with the backend service candlepin: 404 Resource Not Found"
    303ef924-9845-4267-a705-194a4ebfbcfb,,foreman_admin,2016/11/11 06:55:58,2016/11/11 06:55:58,stopped,error,Package Profile Update,500 Internal Server Error
    cffa5990-23ba-49f5-828b-ae0c77e8257a,,foreman_admin,2016/11/11 06:55:53,2016/11/11 06:55:56,stopped,error,Update for host sat62disc.example.org,"There was an issue with the backend service candlepin: 404 Resource Not Found, There was an issue with the backend service candlepin: 404 Resource Not Found"
    07780e8f-dd81-49c4-a792-c4d4d162eb10,,foreman_admin,2016/11/11 06:55:50,2016/11/11 06:55:51,stopped,error,Update for host sat62disc.example.org,"There was an issue with the backend service candlepin: 404 Resource Not Found, There was an issue with the backend service candlepin: 404 Resource Not Found"
    749a17a1-a8cb-46f0-98f6-017576481df8,,foreman_admin,2016/11/11 06:51:28,2016/11/11 06:51:29,stopped,error,Update for host sat62disc.example.org,"There was an issue with the backend service candlepin: 404 Resource Not Found, There was an issue with the backend service candlepin: 404 Resource Not Found"
    d8f41819-b492-46e5-b0e3-ead3b4b6810c,,foreman_admin,2016/11/11 06:51:22,2016/11/11 06:51:28,stopped,error,Package Profile Update,500 Internal Server Error

Examples:

    >>> type(tasks)
    <class 'insights.parsers.hammer_task_list.HammerTaskList'>
    >>> tasks.can_authenticate
    True
    >>> len(tasks)  # Can act as a list
    17
    >>> tasks[0]['ID']  # Fetch rows directly
    '92b732ea-7423-4644-8890-80e054f1799a'
    >>> tasks[0]['Task errors']  # Literal contents of field - quotes not stripped
    ''
    >>> error_tasks = tasks.search(Result='error')  # List of dictionaries
    >>> len(error_tasks)
    6
    >>> error_tasks[0]['ID']
    '1314c91e-19d6-4d71-9bca-31db0df0aad2'
    >>> error_tasks[-1]['Task errors']
    '500 Internal Server Error'
"""

from insights import parser, CommandParser
from insights.parsers import keyword_search, SkipException
from insights.specs import Specs
import csv


@parser(Specs.hammer_task_list)
class HammerTaskList(CommandParser, list):
    """
    Parse the CSV output from the ``hammer --output csv task list`` command.

    Raises:
        SkipException: When nothing is parsed.

    Attributes:
        can_authenticate (bool): Whether we have valid data; if False it's
            probably due to not being able to authenticate.
    """

    def parse_content(self, content):
        self.can_authenticate = content[0].startswith('ID')
        if self.can_authenticate:
            headings = [c.strip() for c in content[0].split(',')]
            creader = csv.reader(content[1:], skipinitialspace=True)
            for line in creader:
                strip_line = [item.strip() for item in line]
                self.append(dict(zip(headings, strip_line)))
        if len(self) <= 0:
            raise SkipException()
        self._running_tasks = [t for t in self if t.get('State', t.get('state')) == 'running']

    @property
    def tasks(self):
        """Return a list of tasks, in the order they appear in the file, as dictionaries of fields and values."""
        return self

    @property
    def running_tasks(self):
        """Return a list of running tasks"""
        return self._running_tasks

    def search(self, **kwargs):
        """
        Search the process list for matching rows based on key-value pairs.

        This uses the py:func:`insights.parsers.keyword_search` function for
        searching; see its documentation for usage details.  If no search
        parameters are given, no rows are returned.

        Examples:

            >>> no_owner_tasks = tasks.search(Owner='')
            >>> len(no_owner_tasks)
            3
            >>> no_owner_tasks[0]['Task action']
            'Listen on candlepin events'
            >>> len(tasks.search(State='stopped', Result='error'))
            6
        """
        return keyword_search(self, **kwargs)
