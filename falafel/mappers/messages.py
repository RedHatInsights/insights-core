from falafel.core.plugins import mapper
from falafel.core.mapper import MapperOutput


class MessageLineList(MapperOutput):

    def __contains__(self, s):
        """
        Check if the specified string 's' is contained in one line of
        /var/log/messages
        """
        return any(s in l for l in self.data)

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
        r = list()
        for l in self.data:
            if s in l:
                info, msg = [i.strip() for i in l.split(': ', 1)]
                msg_info = dict()
                msg_info['message'] = msg
                msg_info['raw_message'] = l

                info_splits = info.split()
                if len(info_splits) == 5:
                    msg_info['timestamp'] = ' '.join(info_splits[:3])
                    msg_info['hostname'] = info_splits[3]
                    msg_info['procname'] = info_splits[4]
                r.append(msg_info)
        return r

    def scan(self, token, result_key):
        self._add_to_computed(result_key, token in self)


@mapper('messages')
def messages(context):
    """
    Returns an object in type of MessageLineList which provide two methods:
    - Usage:
      in:
        msg_info = shared.get(messages)
        if "Abort command issued" in msg_info:
            ...
      get:
        kernel_lines = msg_info.get('kernel')
        for line in kernel_lines:
            ts = line.get('timestamp')
            ...

    -- Sample of /var/log/messages --
    May 18 14:24:14 lxc-rhel68-sat56 kernel: BIOS-e820: 0000000000000000 - 000000000009bc00 (usable)
    May 18 14:24:14 lxc-rhel68-sat56 kernel: BIOS-e820: 000000000009bc00 - 00000000000a0000 (reserved)
    -----------

    """
    return MessageLineList(context.content)
