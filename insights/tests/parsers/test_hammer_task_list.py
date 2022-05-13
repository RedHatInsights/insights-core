from insights.parsers import hammer_task_list
from insights.tests import context_wrap

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

hammer_running_task_on_sat_65 = """
ID,Action,State,Result,Started at,Ended at,Owner,Task errors
4a22f7c6-ca65-4aee-8292-209e5742cce8,Listen on candlepin events ,running,pending,2019/09/10 05:46:39,"",,""
f3faa058-f155-4200-a70b-279b85772ca6,Monitor Event Queue ,running,pending,2019/09/10 05:46:39,"",,""
""".strip()

hammer_running_task_on_sat_64 = """
ID,Name,Owner,Started at,Ended at,State,Result,Task action,Task errors
2ffc3f0d-da4f-4b05-b86a-443ff21d27d3,"Monitor Event Queue {""locale""=>""en"", ""current_user_id""=>nil}",,2019/09/02 08:38:37,"",running,pending,Monitor Event Queue,""
32e6c73f-d373-4e40-8c11-4674bf346cbc,"Listen on candlepin events {""locale""=>""en"", ""current_user_id""=>nil}",,2019/09/02 08:38:36,"",running,pending,Listen on candlepin events,""
""".strip()

hammer_all_tasks_list_on_sat_64 = """
ID,Name,Owner,Started at,Ended at,State,Result,Task action,Task errors
80645ff3-b168-4de9-8751-536ce2f319a9,"Remove orphans {""services_checked""=>[""pulp"", ""pulp_auth""],
 ""capsule_id""=>1,
 ""remote_user""=>""admin"",
 ""remote_cp_user""=>""admin""}",foreman_admin,2019/08/05 02:00:31,2019/08/05 02:00:33,running,success,Remove orphans,""
c39c3dca-4dca-45d3-8d0f-1f1307ba174c,Create RSS notifications,,2019/08/04 14:59:46,2019/08/04 14:59:47,stopped,success,Create RSS notifications,""
09c8e998-b674-42f5-a12b-68b8662aa261,Pulp disk space notification,,2019/08/04 14:59:30,2019/08/04 14:59:30,stopped,success,Pulp disk space notification,""
8574e54f-1329-4f08-89e3-f2427a3d4318,Scan cdn,admin,2019/08/23 09:38:15,2019/08/23 09:38:17,stopped,success,Scan cdn,""
436acc7d-35ea-4f02-a389-b6f359e106b6,Update organization 'Default Organization',admin,2019/08/23 09:37:06,2019/08/23 09:37:06,stopped,error,Update,"Required lock is already taken by other running tasks.
Please inspect their state, fix their errors and resume them.

Required lock: read
Conflicts with tasks:
- https://vm37-76.gsslab.pek2.redhat.com/foreman_tasks/tasks/f3f1704c-679e-4c49-a9e7-e896fa7bb9fd"
ac350b3f-6128-4ab9-989f-c7546fe54cb6,Update organization 'Default Organization',admin,2019/08/23 09:37:06,2019/08/23 09:37:07,stopped,error,Update,"Required lock is already taken by other running tasks.
Please inspect their state, fix their errors and resume them.

Required lock: read
Conflicts with tasks:
- https://vm37-76.gsslab.pek2.redhat.com/foreman_tasks/tasks/f3f1704c-679e-4c49-a9e7-e896fa7bb9fd"
51670134-7363-48cc-8db8-eb42f97763a5,Update organization 'Default Organization',admin,2019/08/23 09:37:05,2019/08/23 09:37:05,stopped,error,Update,"Required lock is already taken by other running tasks.
Please inspect their state, fix their errors and resume them.

Required lock: read
Conflicts with tasks:
- https://vm37-76.gsslab.pek2.redhat.com/foreman_tasks/tasks/f3f1704c-679e-4c49-a9e7-e896fa7bb9fd"
cbe81691-7ddf-4857-a112-2a73a2041f8a,Update organization 'Default Organization',admin,2019/08/23 09:37:04,2019/08/23 09:37:04,stopped,error,Update,"Required lock is already taken by other running tasks.
Please inspect their state, fix their errors and resume them.

Required lock: read
Conflicts with tasks:
- https://vm37-76.gsslab.pek2.redhat.com/foreman_tasks/tasks/f3f1704c-679e-4c49-a9e7-e896fa7bb9fd"
dc472eb1-f18b-483f-a77d-1953a3c0aa58,Update organization 'Default Organization',admin,2019/08/23 09:37:02,2019/08/23 09:37:02,stopped,error,Update,"Required lock is already taken by other running tasks.
Please inspect their state, fix their errors and resume them.

Required lock: read
Conflicts with tasks:
- https://vm37-76.gsslab.pek2.redhat.com/foreman_tasks/tasks/f3f1704c-679e-4c49-a9e7-e896fa7bb9fd"
f3f1704c-679e-4c49-a9e7-e896fa7bb9fd,Update organization 'Default Organization',admin,2019/08/23 09:31:46,2019/08/23 09:38:35,stopped,success,Update,""
8e1aaaca-73a2-46e8-b792-d7e4af21e3bf,Update organization 'Default Organization',admin,2019/08/23 09:30:36,2019/08/23 09:30:36,stopped,error,Update,"Required lock is already taken by other running tasks.
Please inspect their state, fix their errors and resume them.

Required lock: read
Conflicts with tasks:
- https://vm37-76.gsslab.pek2.redhat.com/foreman_tasks/tasks/1430bd27-dacd-4a91-bb1f-9930550a3879, Required lock is already taken by other running tasks.
Please inspect their state, fix their errors and resume them.

Required lock: read
Conflicts with tasks:
- https://vm37-76.gsslab.pek2.redhat.com/foreman_tasks/tasks/1430bd27-dacd-4a91-bb1f-9930550a3879"
""".strip()

hammer_all_tasks_list_on_sat_65 = '''
ID,Action,State,Result,Started at,Ended at,Owner,Task errors
1d9fb216-ce00-446d-b001-97b38cb02c9c,Update for host dhcp-136-65.nay.redhat.com ,stopped,error,2019/06/13 05:27:10,2019/06/13 05:27:10,foreman_admin,"Required lock is already taken by other running tasks.
Please inspect their state, fix their errors and resume them.

Required lock: update
Conflicts with tasks:
- https://vm37-45.gsslab.pek2.redhat.com/foreman_tasks/tasks/9dc0ef6d-08a6-41d0-b941-5f0e79da0428"
9dc0ef6d-08a6-41d0-b941-5f0e79da0428,Update for host dhcp-136-65.nay.redhat.com ,stopped,success,2019/06/13 05:27:07,2019/06/13 05:27:12,foreman_admin,""
f38a6d82-b85b-48b8-85f8-44030f37161f,Listen on candlepin events ,stopped,error,2019/06/13 03:01:38,2019/06/13 03:01:38,,Action Actions::Candlepin::ListenOnCandlepinEvents is already active
f0ed64ad-15e4-4710-877e-ab972e7c3471,Listen on candlepin events ,stopped,error,2019/06/13 02:27:02,2019/06/13 02:27:02,,Action Actions::Candlepin::ListenOnCandlepinEvents is already active
0d229121-0da4-4d36-9373-30222c300bdf,Update for host dhcp-136-65.nay.redhat.com ,running,success,2019/06/12 17:27:06,2019/06/12 17:27:07,foreman_admin,""
4a816bcf-c035-400c-86db-161d5287b2a5,Update for host dhcp-136-65.nay.redhat.com ,stopped,error,2019/06/12 13:27:07,2019/06/12 13:27:07,foreman_admin,"Required lock is already taken by other running tasks.
Please inspect their state, fix their errors and resume them.

Required lock: update
Conflicts with tasks:
- https://vm37-45.gsslab.pek2.redhat.com/foreman_tasks/tasks/10e70826-acff-4ff9-94c3-174c3b289745"
10e70826-acff-4ff9-94c3-174c3b289745,Update for host dhcp-136-65.nay.redhat.com ,stopped,success,2019/06/12 13:27:06,2019/06/12 13:27:08,foreman_admin,""
3348390f-db34-448b-8775-e22f12a41dd4,Update for host vm37-186.gsslab.pek2.redhat.com ,stopped,success,2019/06/12 11:42:50,2019/06/12 11:42:51,foreman_admin,""
79e37493-45d1-490d-8164-2847e1677675,Update for host dhcp-136-65.nay.redhat.com ,running,error,2019/06/12 09:27:03,2019/06/12 09:27:03,foreman_admin,"Required lock is already taken by other running tasks.
Please inspect their state, fix their errors and resume them.

Required lock: update
Conflicts with tasks:
- https://vm37-45.gsslab.pek2.redhat.com/foreman_tasks/tasks/5c46cdec-ad59-4bb1-bec7-61ed1aa1b504"
87e5a505-6bc6-41ce-b56e-429f756329a3,"Create activation_key {""text""=>""activation key 'act-keys-1'"", ""link""=>""/activation_keys/1/info""} organization {""text""=>""organization 'org1'"", ""link""=>""/organizations/3/edit""}",stopped,success,2019/05/23 09:11:37,2019/05/23 09:11:38,admin,""
'''.strip()


def test_HTL_doc_examples():
    tasks = hammer_task_list.HammerTaskList(context_wrap(hammer_task_list_csv_data))
    globs = {
        'tasks': tasks
    }
    failed, tested = doctest.testmod(hammer_task_list, globs=globs)
    assert failed == 0


def test_tasks_on_sat_65():
    tasks = hammer_task_list.HammerTaskList(context_wrap(hammer_running_task_on_sat_65))
    assert len(tasks.running_tasks) == 2
    assert tasks[0]['Action'] == 'Listen on candlepin events'


def test_tasks_on_sat_64():
    tasks = hammer_task_list.HammerTaskList(context_wrap(hammer_running_task_on_sat_64))
    assert len(tasks.running_tasks) == 2
    assert tasks[0]['Task action'] == 'Monitor Event Queue'


def test_all_tasks_on_sat_64():
    tasks = hammer_task_list.HammerTaskList(context_wrap(hammer_all_tasks_list_on_sat_64))
    assert len(tasks) == 11
    assert len(tasks.running_tasks) == 1


def test_all_tasks_on_sat_65():
    tasks = hammer_task_list.HammerTaskList(context_wrap(hammer_all_tasks_list_on_sat_65))
    assert len(tasks) == 10
    assert len(tasks.running_tasks) == 2
