from ...parsers import hammer_task_list
from ...tests import context_wrap

import doctest

hammer_task_list_csv_data = '''
ID,Name,Owner,Started at,Ended at,State,Result,Task action,Task errors
92b732ea-7423-4644-8890-80e054f1799a,,foreman_api_admin,2016/11/11 07:18:32,2016/11/11 07:18:34,stopped,success,Refresh repository,""
e9cb6455-a433-467e-8404-7d01bd726689,,foreman_api_admin,2016/11/11 07:18:28,2016/11/11 07:18:31,stopped,success,Refresh repository,""
e30f3e7e-c023-4380-9594-337fdc4967e4,,foreman_api_admin,2016/11/11 07:18:24,2016/11/11 07:18:28,stopped,success,Refresh repository,""
3197f6a1-891f-4f42-9e4d-92c83c3ed035,,foreman_api_admin,2016/11/11 07:18:20,2016/11/11 07:18:24,stopped,success,Refresh repository,""
22169621-7175-411c-86be-46b4254a4e77,,foreman_api_admin,2016/11/11 07:18:16,2016/11/11 07:18:19,stopped,success,Refresh repository,""
f111e8f7-c956-470b-abb6-2e436ecd5866,,foreman_api_admin,2016/11/11 07:18:14,2016/11/11 07:18:16,stopped,success,Refresh repository,""
dfc702ea-ce46-427c-8a07-43e2a68e1320,,foreman_api_admin,2016/11/11 07:18:12,2016/11/11 07:18:14,stopped,success,Refresh repository,""
e8cac892-e666-4f2c-ab97-2be298da337e,,foreman_api_admin,2016/11/11 07:18:09,2016/11/11 07:18:12,stopped,success,Refresh repository,""
e6c1e1b2-a29d-4fd0-891e-e736dc9b7150,,,2016/11/11 07:14:06,2016/11/12 05:10:17,stopped,success,Listen on candlepin events,""
44a42c49-3038-4cae-8067-4d1cc305db05,,,2016/11/11 07:11:44,2016/11/11 07:12:47,stopped,success,Listen on candlepin events,""
72669288-54ac-41ba-a3b2-314a2c81f438,,,2016/11/11 06:57:15,2016/11/11 07:07:03,stopped,success,Listen on candlepin events,""
1314c91e-19d6-4d71-9bca-31db0df0aad2,,foreman_admin,2016/11/11 06:55:59,2016/11/11 06:55:59,stopped,error,Update for host sat62disc.example.org,"There was an issue with the backend service candlepin: 404 Resource Not Found, There was an issue with the backend service candlepin: 404 Resource Not Found"
303ef924-9845-4267-a705-194a4ebfbcfb,,foreman_admin,2016/11/11 06:55:58,2016/11/11 06:55:58,stopped,error,Package Profile Update,500 Internal Server Error
cffa5990-23ba-49f5-828b-ae0c77e8257a,,foreman_admin,2016/11/11 06:55:53,2016/11/11 06:55:56,stopped,error,Update for host sat62disc.example.org,"There was an issue with the backend service candlepin: 404 Resource Not Found, There was an issue with the backend service candlepin: 404 Resource Not Found"
07780e8f-dd81-49c4-a792-c4d4d162eb10,,foreman_admin,2016/11/11 06:55:50,2016/11/11 06:55:51,stopped,error,Update for host sat62disc.example.org,"There was an issue with the backend service candlepin: 404 Resource Not Found, There was an issue with the backend service candlepin: 404 Resource Not Found"
749a17a1-a8cb-46f0-98f6-017576481df8,,foreman_admin,2016/11/11 06:51:28,2016/11/11 06:51:29,stopped,error,Update for host sat62disc.example.org,"There was an issue with the backend service candlepin: 404 Resource Not Found, There was an issue with the backend service candlepin: 404 Resource Not Found"
d8f41819-b492-46e5-b0e3-ead3b4b6810c,,foreman_admin,2016/11/11 06:51:22,2016/11/11 06:51:28,stopped,error,Package Profile Update,500 Internal Server Error
'''


def test_HTL_doc_examples():
    tasks = hammer_task_list.HammerTaskList(context_wrap(hammer_task_list_csv_data))
    globs = {
        'tasks': tasks
    }
    failed, tested = doctest.testmod(hammer_task_list, globs=globs)
    assert failed == 0
