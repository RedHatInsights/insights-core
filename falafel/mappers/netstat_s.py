from falafel.core.plugins import mapper


@mapper('netstat-s')
def get_netstat_s(context):
    '''
    Return a dict nested dicts, and each key consist of lower case letters and
    "_". For example:

    {
        "ip": {
            "forwarded": "0",
            "fragments_received_ok": "4",
            "requests_sent_out": "2886201",
            "total_packets_received": "3405107",
            "fragments_created": "8",
            "incoming_packets_delivered": "2900146",
            "outgoing_packets_dropped": "456",
            "incoming_packets_discarded": "0"
        }
         "icmp": {
            "input_icmp_message_failed.": "0",
            "icmp_messages_failed": "0",
            "icmp_output_histogram": {
                "echo_request": "3",
                "destination_unreachable": "254",
                "echo_replies": "4"
            },
            "icmp_messages_sent": "261",
            "icmp_input_histogram": {
                "echo_requests": "4",
                "destination_unreachable": "107",
                "echo_replies": "3"
            },
            "icmp_messages_received": "114"
        }
        ......
    }
    '''
    info = dict()
    session = None
    first_layer = dict()
    second_layer = dict()
    has_scd_layer = False

    # There maybe some error metadata, such as:
    # 'cannot open /proc/net/snmp: No such file or directory'
    # or  '/bin/sh: /bin/netstat: No such file or directory'
    # In this situation, return {} directly.
    if 'cannot open' in context.content[0] or 'bin' in context.content[0]:
        return info

    # The right metadata(content) will start with "Ip". Some metadata may start
    # with 'error' or 'ERROR' and the rest of lines are right datas.For example:
    # ~~~~~~~
    # error parsing /proc/net/netstat: No such file or directory
    # Ip:
    #   515 total packets received
    #   5 with invalid addresses
    #   0 forwarded
    # .....
    # ~~~~~~~~
    # In this situation, 'error...' line will be ignore.
    for line in context.content:
        if session:
            if line.startswith("  "):
                if ":" in line:
                    key, val = line.split(":")
                    key = key.strip().replace(" ", "_").lower()
                    # For example:
                    # ~~~~~~~
                    # ICMP input histogram:
                    #        echo requests: 309
                    # ...
                    # ~~~~~~~
                    # There need second layer dict
                    if val == "" and not has_scd_layer:
                        has_scd_layer = True
                        layer_key = key
                    else:
                        if has_scd_layer:
                            second_layer[key] = val.strip().lower()
                        else:
                            first_layer[key] = val.strip().lower()
                else:
                    # To deal with lines look like:
                    # 0 bad segments received.
                    if has_scd_layer:
                        first_layer[layer_key] = second_layer
                        has_scd_layer = False
                        second_layer = dict()
                    data = line.split()

                    # Some line's end has a '.', it'll be removed
                    tmp_data = data[-1]
                    if tmp_data[-1] == ".":
                        data.remove(tmp_data)
                        data.append(tmp_data[:-1])
                    for d in data:
                        if d.isdigit():
                            tmp = d
                            break
                    data.remove(tmp)
                    key, val = "_".join([k.lower() for k in data]), tmp
                    first_layer[key] = val
            else:
                if has_scd_layer:
                    first_layer[layer_key] = second_layer
                    has_scd_layer = False
                    second_layer = dict()
                info[session] = first_layer
                first_layer = dict()
                session = None
        if not session:
            session = line.split(":")[0].lower()
            if session.startswith('error'):
                session = None

    # Assign to the last seesion
    info[session] = first_layer
    return info
