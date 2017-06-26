System time configuration
=========================

file ``/etc/chrony.conf``
-------------------------
.. autoclass:: insights.parsers.system_time.ChronyConf
   :members:
   :show-inheritance:

file ``/etc/sysconfig/chronyd``
-------------------------------
.. autoclass:: insights.parsers.system_time.ChronydService
   :members:
   :show-inheritance:

command ``file -L /etc/localtime``
----------------------------------
.. autoclass:: insights.parsers.system_time.LocalTime
   :members:
   :show-inheritance:

file ``/etc/ntp.conf``
----------------------
.. autoclass:: insights.parsers.system_time.NTP_conf
   :members:
   :show-inheritance:

command ``ntptime``
-------------------
.. autoclass:: insights.parsers.system_time.NtpTime
   :members:
   :show-inheritance:

file ``/etc/sysconfig/ntpd``
----------------------------
.. autoclass:: insights.parsers.system_time.NTPDService
   :members:
   :show-inheritance:
