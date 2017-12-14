System time configuration
=========================

ChronyConf - file ``/etc/chronyd.conf``
---------------------------------------
.. autoclass:: insights.parsers.system_time.ChronyConf
   :members:
   :show-inheritance:

ChronydService - file ``/etc/sysconfig/chronyd``
------------------------------------------------
.. autoclass:: insights.parsers.system_time.ChronydService
   :members:
   :show-inheritance:

LocalTime - command ``file -L /etc/localtime``
----------------------------------------------
.. autoclass:: insights.parsers.system_time.LocalTime
   :members:
   :show-inheritance:

NTPConfParser base class
------------------------
.. autoclass:: insights.parsers.system_time.NTPConfParser
   :members:
   :show-inheritance:

NTPDService - file ``/etc/sysconfig/ntpd``
------------------------------------------
.. autoclass:: insights.parsers.system_time.NTPDService
   :members:
   :show-inheritance:

NTPConf - file ``/etc/ntpd.conf``
---------------------------------
.. autoclass:: insights.parsers.system_time.NTPConf
   :members:
   :show-inheritance:

NtpTime - command ``ntptime``
-----------------------------
.. autoclass:: insights.parsers.system_time.NtpTime
   :members:
   :show-inheritance:
