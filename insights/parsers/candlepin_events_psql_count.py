"""
Candlepin Events table size
===========================

Module for parsing size of cp_event table.

This module is supposed to consume this output:

```
# su - postgres -c "echo 'select count(*) from cp_event' | psql -d candlepin"
 count 
-------
  8061
(1 row)
```

and provides `count` value.

"""   # noqa: W291

from insights import Parser, parser, get_active_lines
from insights.parsers import ParseException, SkipException
from insights.specs import Specs


@parser(Specs.candlepin_events_psql_count)
class CandlepinEventsPsqlCount(Parser):

    def parse_content(self, content):
        next_line = False
        for line in get_active_lines(content):
            if line.strip().startswith('---'):
                next_line = True
                continue
            if next_line:
                try:
                    self.count = int(line.strip())
                except ValueError:
                    raise ParseException("Failed to parse count from '%s'" % line)
                break
        else:
            raise SkipException("Empty or unexpected content '%s'." % content)
