from .. import Mapper, mapper, get_active_lines, LegacyItemAccess
import re


@mapper("postgresql.conf")
class PostgreSQLConf(LegacyItemAccess, Mapper):
    """
    Parses postgresql.conf and returns a dict.
    - {
        "port": '5344',
        "listen_addresses": 'localhost',
        "shared_buffers": '128MB'
      }

      Helper functions as_duration, as_boolean and as_memory_bytes are
      available for converting the values of specific configuration items
      into more Pythonic values.
    """
    _value_error_str = "Do not recognise '{val}' for setting '{item}' " +\
                       "as a {_type}"

    def parse_content(self, content):
        pg_dict = {}
        for line in get_active_lines(content):
            if '=' in line:
                key, value = line.split("=")
                # In postgresql.conf, there are lines like:
                # - plog_line_prefix = '%m '
                # strip the " and ' (reserve the space inner the " or ')
                # {"plig_line_prefix": "%m "}; but not {"plig_line_prefix": "'%m '"}
                pg_dict[key.strip()] = value.strip().strip('\'"')
        self.data = pg_dict

    def as_duration(self, item):
        """
        Postgres's time durations for checkpoint_timeout can have 's', 'm', or
        'h' suffixes.  We convert all of them here to seconds.
        See https://www.postgresql.org/docs/9.3/static/config-setting.html :-
        "valid time units are ms (milliseconds), s (seconds), min (minutes), h
        (hours), and d (days)"
        We return a floating point number because of the possibility of
        convertion from milliseconds.
        """
        if not item:
            return None
        if item not in self.data:
            return None
        dur_re = re.compile(r'^(?P<number>\d+)(?P<suffix>ms|s|min|h|d)?$')
        length_of = {'ms': 0.001, 's': 1, 'min': 60, 'h': 3600, 'd': 86400}

        value = self.data[item]
        match = dur_re.search(value)
        if match:
            # Do we have a suffix at all?  If not, assume seconds, return float
            number, suffix = match.group('number', 'suffix')
            if suffix is None:
                return float(number)
            # Do we have a matching suffix?
            # assert: suffix in length_of, due to regex
            return float(number) * length_of[suffix]
        else:
            raise ValueError(self._value_error_str.format(
                             val=value, item=item, _type='duration'
                             ))

    def as_boolean(self, item):
        """
        See https://www.postgresql.org/docs/9.3/static/config-setting.html :-
        "Boolean values can be written as on, off, true, false, yes, no, 1,
        0 (all case-insensitive) or any unambiguous prefix of these."
        """
        if not item:
            return None
        if item not in self.data:
            return None
        trues = ('on', 't', 'tr', 'tru', 'true', 'y', 'ye', 'yes', '0')
        falses = ('off', 'f', 'fa', 'fal', 'fals', 'false', 'n', 'no', '0')
        boolean_of = {}
        boolean_of.update({key: True for key in trues})
        boolean_of.update({key: False for key in falses})

        value = self.data[item]
        lval = value.lower()
        if lval in boolean_of:
            return boolean_of[lval]
        else:
            raise ValueError(self._value_error_str.format(
                             val=value, item=item, _type='boolean'
                             ))

    def as_memory_bytes(self, item):
        """
        See https://www.postgresql.org/docs/9.3/static/config-setting.html :-
        "Valid memory units are kB (kilobytes), MB (megabytes), and GB
        (gigabytes).  Note that the multiplier for memory units is 1024, not
        1000."
        """
        if not item:
            return None
        if item not in self.data:
            return None
        size_of = {'kB': 1024, 'MB': 1048576, 'GB': 1048576 * 1024}

        value = self.data[item]
        suffix = value[-2:]
        if suffix in size_of:
            return int(value[:-2]) * size_of[suffix]
        else:
            raise ValueError(self._value_error_str.format(
                             val=value, item=item, _type='memory unit'
                             ))
