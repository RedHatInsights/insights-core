from insights.parsers import osa_dispatcher_log
from insights.tests import context_wrap

from datetime import datetime

# Note use of r'' here and in tests because of literal '\n' in text of log
OSA_DISPATCHER_LOG = r"""
2015/12/23 04:40:58 -04:00 28307 0.0.0.0: osad/jabber_lib.__init__
2015/12/23 04:40:58 -04:00 28307 0.0.0.0: osad/jabber_lib.setup_connection('Connected to jabber server', u'example.com')
2015/12/23 04:40:58 -04:00 28307 0.0.0.0: osad/osa_dispatcher.fix_connection('Upstream notification server started on port', 1290)
2015/12/23 04:40:58 -04:00 28307 0.0.0.0: osad/jabber_lib.process_forever
2015/12/27 22:48:50 -04:00 28307 0.0.0.0: osad/jabber_lib.main('ERROR', 'Error caught:')
2015/12/27 22:48:50 -04:00 28307 0.0.0.0: osad/jabber_lib.main('ERROR', 'Traceback (most recent call last):\\n  File "/usr/share/rhn/osad/jabber_lib.py", line 121, in main\\n    self.process_forever(c)\\n  File "/usr/share/rhn/osad/jabber_lib.py", line 179, in process_forever\\n    self.process_once(client)\\n  File "/usr/share/rhn/osad/osa_dispatcher.py", line 187, in process_once\\n    client.retrieve_roster()\\n  File "/usr/share/rhn/osad/jabber_lib.py", line 729, in retrieve_roster\\n    stanza = self.get_one_stanza()\\n  File "/usr/share/rhn/osad/jabber_lib.py", line 801, in get_one_stanza\\n    self.process(timeout=tm)\\n  File "/usr/share/rhn/osad/jabber_lib.py", line 1063, in process\\n    self._parser.Parse(data)\\n  File "/usr/lib/python2.6/site-packages/jabber/xmlstream.py", line 269, in unknown_endtag\\n    self.dispatch(self._mini_dom)\\n  File "/usr/share/rhn/osad/jabber_lib.py", line 829, in _orig_dispatch\\n    jabber.Client.dispatch(self, stanza)\\n  File "/usr/lib/python2.6/site-packages/jabber/jabber.py", line 290, in dispatch\\n    else: handler[\'func\'](self,stanza)\\n  File "/usr/share/rhn/osad/jabber_lib.py", line 380, in dispatch\\n    callback(client, stanza)\\n  File "/usr/share/rhn/osad/dispatcher_client.py", line 145, in _message_callback\\n    sig = self._check_signature_from_message(stanza, actions)\\n  File "/usr/share/rhn/osad/jabber_lib.py", line 1325, in _check_signature_from_message\\n    sig = self._check_signature(stanza, actions=actions)\\n  File "/usr/share/rhn/osad/dispatcher_client.py", line 69, in _check_signature\\n    row = lookup_client_by_name(x_client_id)\\n  File "/usr/share/rhn/osad/dispatcher_client.py", line 213, in lookup_client_by_name\\n    raise InvalidClientError(client_name)\\nInvalidClientError: 870d55ffbb949fae\\n')
"""

OSA_DISPATCHER_TRUNC = r"""
2015/12/27 22:48:50 -04:00 28307 0.0.0
"""


def test_get_osa_dispatcher_log():
    log = osa_dispatcher_log.OSADispatcherLog(context_wrap(
        OSA_DISPATCHER_LOG, path='var/log/rhn/osa-dispatcher.log'
    ))

    # Check the fields in a typical full line
    line = log.get('setup_connection')[0]
    assert line['timestamp'] == '2015/12/23 04:40:58 -04:00'
    assert line['pid'] == '28307'
    assert line['client_ip'] == '0.0.0.0'
    assert line['module'] == 'osad'
    assert line['function'] == 'jabber_lib.setup_connection'
    assert line['info'] == "'Connected to jabber server', u'example.com'"

    # Check lines that don't have an info field
    line = log.get('process_forever')[0]
    assert line['info'] is None

    last = log.last()
    assert last['timestamp'] == '2015/12/27 22:48:50 -04:00'
    assert last['pid'] == '28307'
    assert last['client_ip'] == '0.0.0.0'
    assert last['module'] == 'osad'
    assert last['function'] == 'jabber_lib.main'
    # Problems with literal '\n' in line for comparison, so fall back...
    assert last['info'].startswith("""'ERROR', 'Traceback (most recent call last):""")

    # Test get_after functionality with different inputs
    assert len(list(log.get_after(datetime(2015, 12, 27, 22, 48, 40)))) == 2
    assert len(list(log.get_after(datetime(2015, 12, 23, 4, 40, 0), 'connection'))) == 2

    trunc = osa_dispatcher_log.OSADispatcherLog(context_wrap(
        OSA_DISPATCHER_TRUNC, path='var/log/rhn/osa-dispatcher.log'
    ))
    last = trunc.last()
    assert last['raw_message'] == '2015/12/27 22:48:50 -04:00 28307 0.0.0'
    for k in ['timestamp', 'pid', 'client_ip', 'module', 'function', 'info']:
        assert k not in last
