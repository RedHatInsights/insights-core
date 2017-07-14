"""
Secure -  file ``/var/log/secure``
==================================
"""
from .. import LogFileOutput, parser


@parser('secure')
class Secure(LogFileOutput):
    """Class for parsing the ``/var/log/secure`` file.

    Sample log text::

        Aug 24 09:31:39 localhost polkitd[822]: Finished loading, compiling and executing 6 rules
        Aug 24 09:31:39 localhost polkitd[822]: Acquired the name org.freedesktop.PolicyKit1 on the system bus
        Aug 25 13:52:54 localhost sshd[23085]: pam_unix(sshd:session): session opened for user zjj by (uid=0)
        Aug 25 13:52:54 localhost sshd[23085]: error: openpty: No such file or directory

    Note:
        Because timestamps in the secure log by default have no year,
        the year of the logs will be inferred from the year in your
        timestamp. This will also work around December/January crossovers.

    Examples:
        >>> secure = shared[Secure]
        >>> secure.get('session opened')
        [{'timestamp':'Aug 25 13:52:54',
          'hostname':'localhost',
          'procname': 'sshd[23085]',
          'message': 'pam_unix(sshd:session): session opened for user zjj by (uid=0)',
          'raw_message': 'Aug 25 13:52:54 localhost sshd[23085]: pam_unix(sshd:session): session opened for user zjj by (uid=0)'
         }]
        >>> len(list(secure.get_after(datetime(2017, 8, 25, 0, 0, 0))))
        2
    """
    time_format = '%b %d %H:%M:%S'

    def get(self, s):
        """
        Returns all lines that contain 's' and wrap them into a list of
        dictionaries, with the fields parsed in this way::

            May 18 14:24:14 lxc-rhel68-sat56 kernel: BIOS-e820: 000000000009bc00..
            <- timestamp-> ^ <- hostname -> ^<proc>^ <- message ->
            <-           raw_message                    ...     ->

        Parameters:
            s(str): String to search for

        Returns:
            (list) List of dictionary of lines parsed into fields as above.
        """
        r = []
        for l in self.lines:
            if s in l:
                msg_info = {
                    'raw_message': l
                }
                if ': ' in l:
                    info, msg = [i.strip() for i in l.split(': ', 1)]
                    msg_info['message'] = msg

                    info_splits = info.split()
                    if len(info_splits) == 5:
                        msg_info['timestamp'] = ' '.join(info_splits[:3])
                        msg_info['hostname'] = info_splits[3]
                        msg_info['procname'] = info_splits[4]
                r.append(msg_info)
        return r
