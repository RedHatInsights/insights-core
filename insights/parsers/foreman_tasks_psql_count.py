"""
Foreman Tasks table size
========================

Module for parsing size of foreman_tasks_tasks table.

This module is supposed to consume this output:

```
# su - postgres -c "echo 'select count(*) from foreman_tasks_tasks' | psql -d foreman"
 count 
-------
   209
(1 row)
```

and provides `count` value.

"""   # noqa: W291

from insights import Parser, parser, get_active_lines
from insights.parsers import ParseException, SkipException
from insights.specs import Specs


@parser(Specs.foreman_tasks_psql_count)
class ForemanTasksPsqlCount(Parser):

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
