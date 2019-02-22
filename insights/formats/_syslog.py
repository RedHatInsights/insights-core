import os
import sys
from getpass import getuser

from insights.core.evaluators import Formatter
from insights.formats import FormatterAdapter
from insights import dr, rule, condition, incident, parser
import logging
from logging import handlers


class SysLogFormat(Formatter):
    """
    This class gathers exceptions and logs the content to syslog. It should be used
    as a context manager and given an instance of an
    ``insights.core.dr.Broker``. ``dr.run`` should be called within the context
    using the same broker.

    Args:
        broker (Broker): the broker to watch and provide a summary about.
    """

    def __init__(self, broker, stream=None):
        self.broker = broker
        self.exceptions = []
        self.rules = []
        self.user = getuser()
        self.pid = str(os.getpid())
        self.stream = stream

        self.logger = logging.getLogger('sysLogLogger')
        self.logger.propagate = False
        self.logger.setLevel(logging.INFO)
        self.handler = handlers.SysLogHandler('/dev/log')
        self.handler.formatter = logging.Formatter('%(message)s')
        self.logger.addHandler(self.handler)

    def logit(self, msg, pid, user, cname, priority=None):
        """Function for formatting content and logging to syslog"""

        if priority == logging.WARNING:
            self.logger.warning("{0}[pid:{1}] user:{2}: WARNING - {3}".format(cname, pid, user, msg))
        elif priority == logging.ERROR:
            self.logger.error("{0}[pid:{1}] user:{2}: ERROR - {3}".format(cname, pid, user, msg))
        else:
            self.logger.info("{0}[pid:{1}] user:{2}: INFO - {3}".format(cname, pid, user, msg))

        if self.stream:
            print(msg, file=self.stream)

    def log_rule_info(self, broker):
        """Collects rule information and send to logit function to log to syslog"""

        for c in sorted(self.broker.get_by_type(rule), key=dr.get_name):
            v = self.broker[c]
            _type = v.get("type")
            if _type:
                if _type != "skip":
                    msg = "Running {0} ".format(dr.get_name(c))
                    self.logit(msg, self.pid, self.user, "insights-run", logging.INFO)
                else:
                    msg = "Rule skipped {0} ".format(dr.get_name(c))
                    self.logit(msg, self.pid, self.user, "insights-run", logging.WARNING)

    def log_exceptions(self, c, broker):
        """Gets exceptions to be logged and sends to logit function to be logged to syslog"""

        if c in broker.exceptions:
            ex = broker.exceptions.get(c)
            ex = "Exception running {0} - {1}".format(dr.get_name(c), str(ex))
            self.logit(ex, self.pid, self.user, "insights-run", logging.ERROR)

    def preprocess(self):

        self.broker.add_observer(self.log_exceptions, rule)
        self.broker.add_observer(self.log_exceptions, condition)
        self.broker.add_observer(self.log_exceptions, incident)
        self.broker.add_observer(self.log_exceptions, parser)

    def postprocess(self):

        cmd = "Command Line - {}".format(" ".join(sys.argv))
        self.logit(cmd, self.pid, self.user, "insights-run", logging.INFO)

        self.log_rule_info(self.broker)


class SysLogFormatterAdapter(FormatterAdapter):
    """Logs Rules run and exceptions to syslog."""

    def __init__(self, args):
        self.formatter = None

    def preprocess(self, broker):
        self.formatter = SysLogFormat(broker)
        self.formatter.preprocess()

    def postprocess(self, broker):
        self.formatter.postprocess()
