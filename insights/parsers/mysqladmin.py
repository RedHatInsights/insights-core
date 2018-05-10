"""
mysqladmin command - Command
============================

Parsing and extracting data from output of command ``/bin/mysqladmin variables``.
Parsers contained in this module are:

MysqladminVars - command ``/bin/mysqladmin variables``
------------------------------------------------------

"""

from .. import Parser, parser
from insights.parsers import ParseException
from insights.specs import Specs


@parser(Specs.mysqladmin_vars)
class MysqladminVars(Parser):
    """
    The output of command ``/bin/mysqladmin variables`` is in mysql table format,
    contains 'Variable_name' and 'Value' two columns.
    This parser will parse the table and set each variable as an class attribute.

    Sample command output::

        +-------------------------------------------------+------------------+
        | Variable_name                                   | Value            |
        +-------------------------------------------------+------------------+
        | aria_block_size                                 | 8192             |
        | aria_checkpoint_interval                        | 30               |
        | aria_checkpoint_log_activity                    | 1048576          |
        | datadir                                         | /var/lib/mysql/  |
        | version                                         | 5.5.56-MariaDB   |
        +-------------------------------------------------+------------------+


    Example:
        >>> output.version
        '5.5.56-MariaDB'
        >>> 'DataDir' in output
        True
        >>> output.get('what', '233')
        '233'
        >>> config.getint('aria_block_size', '4096')
        8192
    """
    def parse_content(self, content):
        """
        Parse output content table of command ``/bin/mysqladmin variables``.
        Set each variable as an class attribute.
        """
        if len(content) < 5:
            raise ParseException("Empty or wrong content in table.")

        self._data = {}
        for l in content[3:-1]:
            lsp = l.split('|')
            if len(lsp) != 4:
                raise ParseException("Unparseable line in table.")
            self._data[lsp[1].strip().lower()] = lsp[2].strip()

        for k, v in self._data.items():
            setattr(self, k, v)

    def items(self):
        """
        To make the parsed content can be iterated as a dictionary directly.
        """
        for k, v in self._data.items():
            yield k, v

    def get(self, keyword, default=None):
        """
        Get value for specified keyword, use default if keyword not found.
        A "dictionary like" method.

        Example:

            >>> output.get('wait_timeout')
            '3000'
            >>> output.get('wait_what')
            None
            >>> output.get('wait_what', '100')
            '100'

        Args:

            keyword (str): A key, case insensitive. For ex. `wait_timeout`.
            default (str): A value.

        Returns:

            value (str or None): Values associated with a keyword. Returns
            specific value in `default` if `keyword` does not exist, or None
            if no `default` value set.
        """
        if default and not isinstance(default, str):
            raise TypeError("Default value should be str type.")
        return self._data.get(keyword.lower(), default)

    def getint(self, keyword, default=None):
        """
        Get value for specified keyword, use default if keyword not found.

        Example:

            >>> output.getint('wait_timeout')
            3000
            >>> output.getint('wait_what')
            None
            >>> output.getiny('wait_what', 100)
            100

        Args:

            keyword (str): A key, case insensitive. For ex. `wait_timeout`.
            default (int): A value.

        Returns:

            value (int or None): Values associated with a keyword.i
            If `keyword` does not exist or it's not a number, returns specific
            value in `default`.
        """
        if default and not isinstance(default, int):
            raise TypeError("Default value should be int type.")
        v = self._data.get(keyword.lower())
        return int(v) if v and v.isdigit() else default

    def __contains__(self, keyword):
        return keyword.lower() in self._data
