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
        """Parsing rules from :
        https://www.postgresql.org/docs/9.3/static/config-setting.html
        One parameter is specified per line. The equal sign between name
        and value is optional. Whitespace is insignificant and blank lines
        are ignored.   Hash marks (#) designate the remainder of the line as
        a comment. Parameter values that are not simple identifiers or
        numbers must be single-quoted. To embed a single quote in a
        parameter value, write either two quotes (preferred) or
        backslash-quote."""
        pg_dict = {}
        for line in get_active_lines(content):
            # Remove commented remainder of line
            if '#' in line:
                (line, _) = [s.strip() for s in line.split('#', 1)]
            # Ignore blank lines
            if not line:
                continue
            # Split on equals or on first word
            if '=' in line:
                key, value = [s.strip() for s in line.split("=")]
            else:
                key, value = [s.strip() for s in line.split(' ')]
            # If value is quoted, quotes appear first and last - remove them.
            if value[0] == "'" and value[-1] == "'":
                value = value[1:-1]
            # If value contains '' or \', change to single quote
            if "''" in value:
                value = value.replace("''", "'")
            elif "\\'" in value:
                value = value.replace("\\'", "'")
            # Now save value in key
            pg_dict[key] = value
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

        value = self.data[item]
        lval = value.lower()
        if lval in ('on', 't', 'tr', 'tru', 'true', 'y', 'ye', 'yes', '1'):
            return True
        if lval in ('of','off', 'f', 'fa', 'fal', 'fals', 'false', 'n', 'no',
                    '0'):
            return False
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
