from falafel.core.plugins import mapper
from falafel.core import LogFileOutput


@mapper('messages')
class Messages(LogFileOutput):

    def get(self, s):
        """
        Returns all lines that contain 's' and wrap them into a list of dict.
        [
         {'timestamp':'May 18 14:24:14',
          'procname': 'kernel',
          'hostname':'lxc-rhel68-sat56',
          'message': '...',
          'raw_message': '...: ...'
         },
        ]

        -- Sample --
        May 18 14:24:14 lxc-rhel68-sat56 kernel: BIOS-e820: 000000000009bc00..
        <- timestamp-> ^ <- hostname -> ^<proc>^ <- message ->
        <-           raw_message          ->
        ------------
        """
        r = []
        for l in self.lines:
            if s in l:
                info, msg = [i.strip() for i in l.split(': ', 1)]

                msg_info = {
                    'message': msg,
                    'raw_message': l
                }

                info_splits = info.split()
                if len(info_splits) == 5:
                    msg_info['timestamp'] = ' '.join(info_splits[:3])
                    msg_info['hostname'] = info_splits[3]
                    msg_info['procname'] = info_splits[4]
                r.append(msg_info)
        return r
