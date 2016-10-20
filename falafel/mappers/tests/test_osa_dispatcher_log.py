from falafel.mappers import osa_dispatcher_log
from falafel.tests import context_wrap

OSA_DISPATCHER_LOG = """
2015/12/23 04:40:58 -04:00 28307 0.0.0.0: osad/jabber_lib.__init__
2015/12/23 04:40:58 -04:00 28307 0.0.0.0: osad/jabber_lib.setup_connection('Connected to jabber server', u'example.com')
2015/12/23 04:40:58 -04:00 28307 0.0.0.0: osad/osa_dispatcher.fix_connection('Upstream notification server started on port', 1290)
2015/12/23 04:40:58 -04:00 28307 0.0.0.0: osad/jabber_lib.process_forever
2015/12/27 22:48:50 -04:00 28307 0.0.0.0: osad/jabber_lib.main('ERROR', 'Error caught:')
2015/12/27 22:48:50 -04:00 28307 0.0.0.0: osad/jabber_lib.main('ERROR', 'Traceback (most recent call last):\n  File "/usr/share/rhn/osad/jabber_lib.py", line 121, in main\n    self.process_forever(c)\n  File "/usr/share/rhn/osad/jabber_lib.py", line 179, in process_forever\n    self.process_once(client)\n  File "/usr/share/rhn/osad/osa_dispatcher.py", line 187, in process_once\n    client.retrieve_roster()\n  File "/usr/share/rhn/osad/jabber_lib.py", line 729, in retrieve_roster\n    stanza = self.get_one_stanza()\n  File "/usr/share/rhn/osad/jabber_lib.py", line 801, in get_one_stanza\n    self.process(timeout=tm)\n  File "/usr/share/rhn/osad/jabber_lib.py", line 1063, in process\n    self._parser.Parse(data)\n  File "/usr/lib/python2.6/site-packages/jabber/xmlstream.py", line 269, in unknown_endtag\n    self.dispatch(self._mini_dom)\n  File "/usr/share/rhn/osad/jabber_lib.py", line 829, in _orig_dispatch\n    jabber.Client.dispatch(self, stanza)\n  File "/usr/lib/python2.6/site-packages/jabber/jabber.py", line 290, in dispatch\n    else: handler[\'func\'](self,stanza)\n  File "/usr/share/rhn/osad/jabber_lib.py", line 380, in dispatch\n    callback(client, stanza)\n  File "/usr/share/rhn/osad/dispatcher_client.py", line 145, in _message_callback\n    sig = self._check_signature_from_message(stanza, actions)\n  File "/usr/share/rhn/osad/jabber_lib.py", line 1325, in _check_signature_from_message\n    sig = self._check_signature(stanza, actions=actions)\n  File "/usr/share/rhn/osad/dispatcher_client.py", line 69, in _check_signature\n    row = lookup_client_by_name(x_client_id)\n  File "/usr/share/rhn/osad/dispatcher_client.py", line 213, in lookup_client_by_name\n    raise InvalidClientError(client_name)\nInvalidClientError: 870d55ffbb949fae\n')
"""


def test_get_osa_dispatcher_log():
    log = osa_dispatcher_log.OSADispatcherLog(context_wrap(
        OSA_DISPATCHER_LOG, path='/var/log/rhn/osa-dispatcher.log'
    ))

    # Check the fields in a typical full line
    line = log.get_parsed_lines('setup_connection')[0]
    assert line['timestamp'] == '2015/12/23 04:40:58 -04:00'
    assert line['pid'] == '28307'
    assert line['client_ip'] == '0.0.0.0'
    assert line['module'] == 'osad'
    assert line['function'] == 'jabber_lib.setup_connection'
    assert line['info'] == "'Connected to jabber server', u'example.com'"

    # Check lines that don't have an info field
    line = log.get_parsed_lines('process_forever')[0]
    assert line['info'] is None
