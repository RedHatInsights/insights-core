import re
import datetime
from .. import Mapper, mapper


@mapper('facts')
@mapper("uptime")
class Uptime(Mapper):
    """Class for uptime content."""

    def parse_content(self, content):
        """
        Sample uptime outputs:
            " 11:51:06 up  3:17,  1 user,  load average: 0.12, 0.20, 0.28"
        Return a dict with 6 keys with information available:
        {
            'currtime': '11:51:06',
            'loadavg': ['0.12', '0.20', '0.28'],
            'updays': '',
            'uphhmm': '3:17',
            'users': '1'
            'uptime': datetime.timedelta()

        }
        --- time printing logic of uptime ---
        if (!human_readable) {
            if (updays)
                pos += sprintf(buf + pos, "%d day%s, ", updays, (updays != 1) ? "s" : "");
            }
        upminutes = (int) uptime_secs / 60;
        uphours = upminutes / 60;
        uphours = uphours % 24;
        upminutes = upminutes % 60;

        if (!human_readable) {
            if(uphours)
                pos += sprintf(buf + pos, "%2d:%02d, ", uphours, upminutes);
            else
                pos += sprintf(buf + pos, "%d min, ", upminutes);
        -------------------------------------
        """
        self.currtime = None
        self.loadavg = None
        self.updays = None
        self.uphhmm = None
        self.users = None
        self.uptime = None

        uptime_info = {}
        uptime_info['uptime'] = datetime.timedelta()
        uptime_info['updays'] = ""
        uptime_info['uphhmm'] = ""
        if len(content) == 1:
            line = content[0].strip()
            line_split = re.split(', |: ', line)
            has_day = False

            mix_part = line_split[0].strip().split()
            uptime_info['currtime'] = mix_part[0]
            uptime_info['users'] = ""
            uptime_info['loadavg'] = []

            if len(mix_part) == 4:
                # check days
                if 'day' in mix_part[3]:
                    uptime_info['updays'] = mix_part[2]
                    has_day = True
                # check min
                if 'min' in mix_part[3]:
                    uptime_info['uphhmm'] = '00:%02d' % int(mix_part[2])

            if len(mix_part) == 3:
                uptime_info['uphhmm'] = mix_part[2]

            if has_day:
                hhmm_data = line_split[1].strip().split()
                if len(hhmm_data) == 2:
                    if 'min' in hhmm_data[1]:
                        uptime_info['uphhmm'] = '00:%02d' % int(hhmm_data[0])
                else:
                    uptime_info['uphhmm'] = hhmm_data[0]
                regular_data = line_split[2:]
            else:
                regular_data = line_split[1:]
            # users
            users_info = regular_data[0].strip().split()
            if len(users_info) == 2:
                uptime_info['users'] = users_info[0]
            # load
            load_values = regular_data[2:]
            if len(load_values) == 3:
                uptime_info['loadavg'] = load_values

            if uptime_info['uphhmm']:
                hours, _, mins = uptime_info['uphhmm'].partition(':')
                uptime_info['uptime'] += datetime.timedelta(hours=int(hours))
                uptime_info['uptime'] += datetime.timedelta(minutes=int(mins))
            if uptime_info['updays']:
                uptime_info['uptime'] += datetime.timedelta(days=int(uptime_info['updays']))

        else:
            for line in content:
                if line.startswith('uptime_seconds'):
                    secs = int(line.split()[-1])
                    up_dd = secs / (3600 * 24)
                    up_hh = (secs % (3600 * 24)) / 3600
                    up_mm = (secs % 3600) / 60
                    uptime_info['updays'] = str(up_dd) if up_dd > 0 else ''
                    uptime_info['uphhmm'] = '%02d:%02d' % (up_hh, up_mm)
                    uptime_info['uptime'] += datetime.timedelta(seconds=secs)

        for k, v in uptime_info.iteritems():
            setattr(self, k, v)

        self.data = uptime_info


@mapper("uptime")
def get_uptime(context):
    """Deprecated, do not use. """
    return Uptime(context).data
