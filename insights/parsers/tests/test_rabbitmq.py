from insights.core.context import OSP
from insights.parsers import rabbitmq
from insights.tests import context_wrap

osp_controller = OSP()
osp_controller.role = "Controller"

rabbitmq_report = """
 {listeners,[{clustering,35672,"::"},{amqp,5672,"172.168.1.24"}]},
 {vm_memory_high_watermark,0.4},
 {vm_memory_limit,3281425203},
 {disk_free_limit,50000000},
 {disk_free,44166623232},
 {file_descriptors,[{total_limit,3996},
                    {total_used,176},
                    {sockets_limit,3594},
                    {sockets_used,174}]},
 {processes,[{limit,1048576},{used,3003}]},
 {run_queue,0},
 {uptime,2770222}]
"""


def test_detect_fd_limit():
    context = context_wrap(rabbitmq_report, hostname="controller_1", osp=osp_controller)
    map_result = rabbitmq.fd_total_limit(context)
    assert 3996 == map_result


def test_fd_limit_class():
    context = context_wrap(rabbitmq_report, hostname="controller_1", osp=osp_controller)
    map_result = rabbitmq.RabbitMQFileDescriptors(context)
    assert 3996 == map_result.fd_total_limit
