"""
Custom datasources for "ls -lan target_file" information
"""
import json
import os

from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.plugins import datasource
from insights.parsers.fstab import FSTab
from insights.parsers.lvm import Pvs
from insights.parsers.blkid import BlockIDInfo
from insights.core.spec_factory import DatasourceProvider


@datasource([FSTab, Pvs, BlockIDInfo], HostContext)
def check_ls_files(broker):
    result = {}
    try:
        fstab_mounts = broker[FSTab]
    except:
        fstab_mounts = ""
    try:
        blkid_infos = broker[BlockIDInfo]
    except:
        blkid_infos = ""
    try:
        pvs_info = broker[Pvs]
    except:
        pvs_info = ""

    if fstab_mounts and blkid_infos:
        blk_uuid_name_map = {}
        blk_label_name_map = {}
        focus_entries = []
        for blk in blkid_infos.data:
            uuid = blk.get("UUID", None)
            label = blk.get("LABEL", None)
            name = blk.get("NAME")
            if uuid:
                blk_uuid_name_map[uuid] = name
            if label:
                blk_label_name_map[label] = name
        for record in fstab_mounts:
            original_config = record.raw
            record = {k: v for k, v in record.items()}
            record['raw'] = original_config
            fs_spec = record['fs_spec']
            fs_spec_pair = fs_spec.split("=", 1)
            if fs_spec_pair[0] == "UUID" and fs_spec_pair[1] in blk_uuid_name_map:
                blkid_name = blk_uuid_name_map.get(fs_spec_pair[1])
                record['fs_spec'] = blkid_name
                record['uuid_or_label'] = fs_spec
            elif fs_spec_pair[0] == "LABEL" and fs_spec_pair[1] in blk_label_name_map:
                blkid_name = blk_label_name_map.get(fs_spec_pair[1])
                record['fs_spec'] = blkid_name
                record['uuid_or_label'] = fs_spec
            # Filter out devices like tmpfs, sysfs, proc ...
            if "/" in record['fs_spec'] and "bind" not in record['fs_mntops']:
                focus_entries.append(record)

        for item in focus_entries:
            filesystem_path = item['fs_spec']
            if os.path.exists(filesystem_path) and filesystem_path not in result:
                ls_command = "ls -lan " + filesystem_path
                output = os.popen(ls_command).read().strip('\n')
                if output:
                    result[filesystem_path] = output

    if pvs_info:
        for item in pvs_info:
            pv_path = item['PV']
            if os.path.exists(pv_path) and pv_path not in result:
                ls_command = "ls -lan " + pv_path
                output = os.popen(ls_command).read().strip('\n')
                if output:
                    result[pv_path] = output

    if result:
        relative_path = 'insights_datasources/ls_files'
        return DatasourceProvider(content=json.dumps(result), relative_path=relative_path)
    raise SkipComponent("The targets are not existing")
