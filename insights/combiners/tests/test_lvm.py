from collections import namedtuple

import pytest
from insights.parsers.lvm import (Lvs, LvsHeadings, Pvs, PvsHeadings, Vgs,
                                  VgsHeadings)
from insights.parsers.lvm import (LvsAll, PvsAll, VgsAll)
from insights.combiners.lvm import Lvm, LvmAll
from insights.combiners import lvm
from insights.tests import context_wrap


LVS_HEADINGS = """
  WARNING: Locking disabled. Be careful! This could corrupt your metadata.
  LV            VG              Attr       LSize   Pool  Origin Data%  Meta%  Move Log Cpy%Sync Convert LV Tags Devices
  lv_brick1     data1           Vwi-aotz--   3.62t pool1        0.05
  lv_hdfs1      data1           Vwi-aotz--   3.62t pool1        0.05
  pool1         data1           twi-aotz--   3.62t              0.10   0.11                                     pool1_tdata(0)
  [pool1_tdata] data1           Twi-ao----   3.62t                                                              /dev/sdb1(4096)
  [pool1_tmeta] data1           ewi-ao----  16.00g                                                              /dev/sdb1(0)
  lv_brick2     data2           Vwi-aotz--   3.62t pool2        0.05
  lv_hdfs2      data2           Vwi-aotz--   3.62t pool2        0.05
  pool2         data2           twi-aotz--   3.62t              0.10   0.11                                     pool2_tdata(0)
  [pool2_tdata] data2           Twi-ao----   3.62t                                                              /dev/sdc1(4096)
  [pool2_tmeta] data2           ewi-ao----  16.00g                                                              /dev/sdc1(0)
  lv_brick3     data3           Vwi-aotz--   3.62t pool3        0.05
  lv_hdfs3      data3           Vwi-aotz--   3.62t pool3        0.05
  pool3         data3           twi-aotz--   3.62t              0.10   0.11                                     pool3_tdata(0)
  [pool3_tdata] data3           Twi-ao----   3.62t                                                              /dev/sdd1(4096)
  [pool3_tmeta] data3           ewi-ao----  16.00g                                                              /dev/sdd1(0)
  lv_brick4     data4           Vwi-aotz--   3.62t pool4        0.05
  lv_hdfs4      data4           Vwi-aotz--   3.62t pool4        0.05
  pool4         data4           twi-aotz--   3.62t              0.10   0.11                                     pool4_tdata(0)
  [pool4_tdata] data4           Twi-ao----   3.62t                                                              /dev/sde1(4096)
  [pool4_tmeta] data4           ewi-ao----  16.00g                                                              /dev/sde1(0)
  lv_brick5     data5           Vwi-aotz--   3.62t pool5        0.05
  lv_hdfs5      data5           Vwi-aotz--   3.62t pool5        0.05
  pool5         data5           twi-aotz--   3.62t              0.10   0.11                                     pool5_tdata(0)
  [pool5_tdata] data5           Twi-ao----   3.62t                                                              /dev/sdf1(4096)  
  [pool5_tmeta] data5           ewi-ao----  16.00g                                                              /dev/sdf1(0)     
  lv_brick6     data6           Vwi-aotz--   3.62t pool6        0.05                                                             
  lv_hdfs6      data6           Vwi-aotz--   3.62t pool6        0.05                                                             
  pool6         data6           twi-aotz--   3.62t              0.10   0.11                                     pool6_tdata(0)   
  [pool6_tdata] data6           Twi-ao----   3.62t                                                              /dev/sdg1(4096)  
  [pool6_tmeta] data6           ewi-ao----  16.00g                                                              /dev/sdg1(0)     
  lv_brick7     data7           Vwi-aotz--   3.62t pool7        0.05                                                             
  lv_hdfs7      data7           Vwi-aotz--   3.62t pool7        0.05                                                             
  pool7         data7           twi-aotz--   3.62t              0.10   0.11                                     pool7_tdata(0)   
  [pool7_tdata] data7           Twi-ao----   3.62t                                                              /dev/sdh1(4096)  
  [pool7_tmeta] data7           ewi-ao----  16.00g                                                              /dev/sdh1(0)     
  home          rhel_ceehadoop1 -wi-ao---- 976.00g                                                              /dev/sda3(12800) 
  opt           rhel_ceehadoop1 -wi-ao----   2.57t                                                              /dev/sda3(279551)
  root          rhel_ceehadoop1 -wi-ao----  50.00g                                                              /dev/sda3(0)     
  swap          rhel_ceehadoop1 -wi-ao----  16.00g                                                              /dev/sda3(262656)
  var           rhel_ceehadoop1 -wi-ao----  50.00g                                                              /dev/sda3(266752)
""".strip()   # noqa: W291

LVS_NO_HEADINGS = """
  WARNING: Locking disabled. Be careful! This could corrupt your metadata.
  LVM2_LV_NAME='lv_brick1'|LVM2_VG_NAME='data1'|LVM2_LV_SIZE='3.62t'|LVM2_REGION_SIZE='0 '|LVM2_MIRROR_LOG=''|LVM2_LV_ATTR='Vwi-aotz--'|LVM2_DEVICES=''|LVM2_REGION_SIZE='0 '
  LVM2_LV_NAME='lv_hdfs1'|LVM2_VG_NAME='data1'|LVM2_LV_SIZE='3.62t'|LVM2_REGION_SIZE='0 '|LVM2_MIRROR_LOG=''|LVM2_LV_ATTR='Vwi-aotz--'|LVM2_DEVICES=''|LVM2_REGION_SIZE='0 '
  LVM2_LV_NAME='pool1'|LVM2_VG_NAME='data1'|LVM2_LV_SIZE='3.62t'|LVM2_REGION_SIZE='0 '|LVM2_MIRROR_LOG=''|LVM2_LV_ATTR='twi-aotz--'|LVM2_DEVICES='pool1_tdata(0)'|LVM2_REGION_SIZE='0 '
  LVM2_LV_NAME='[pool1_tdata]'|LVM2_VG_NAME='data1'|LVM2_LV_SIZE='3.62t'|LVM2_REGION_SIZE='0 '|LVM2_MIRROR_LOG=''|LVM2_LV_ATTR='Twi-ao----'|LVM2_DEVICES='/dev/sdb1(4096)'|LVM2_REGION_SIZE='0 '
  LVM2_LV_NAME='[pool1_tmeta]'|LVM2_VG_NAME='data1'|LVM2_LV_SIZE='16.00g'|LVM2_REGION_SIZE='0 '|LVM2_MIRROR_LOG=''|LVM2_LV_ATTR='ewi-ao----'|LVM2_DEVICES='/dev/sdb1(0)'|LVM2_REGION_SIZE='0 '
  LVM2_LV_NAME='lv_brick2'|LVM2_VG_NAME='data2'|LVM2_LV_SIZE='3.62t'|LVM2_REGION_SIZE='0 '|LVM2_MIRROR_LOG=''|LVM2_LV_ATTR='Vwi-aotz--'|LVM2_DEVICES=''|LVM2_REGION_SIZE='0 '
  LVM2_LV_NAME='lv_hdfs2'|LVM2_VG_NAME='data2'|LVM2_LV_SIZE='3.62t'|LVM2_REGION_SIZE='0 '|LVM2_MIRROR_LOG=''|LVM2_LV_ATTR='Vwi-aotz--'|LVM2_DEVICES=''|LVM2_REGION_SIZE='0 '
  LVM2_LV_NAME='pool2'|LVM2_VG_NAME='data2'|LVM2_LV_SIZE='3.62t'|LVM2_REGION_SIZE='0 '|LVM2_MIRROR_LOG=''|LVM2_LV_ATTR='twi-aotz--'|LVM2_DEVICES='pool2_tdata(0)'|LVM2_REGION_SIZE='0 '
  LVM2_LV_NAME='[pool2_tdata]'|LVM2_VG_NAME='data2'|LVM2_LV_SIZE='3.62t'|LVM2_REGION_SIZE='0 '|LVM2_MIRROR_LOG=''|LVM2_LV_ATTR='Twi-ao----'|LVM2_DEVICES='/dev/sdc1(4096)'|LVM2_REGION_SIZE='0 '
  LVM2_LV_NAME='[pool2_tmeta]'|LVM2_VG_NAME='data2'|LVM2_LV_SIZE='16.00g'|LVM2_REGION_SIZE='0 '|LVM2_MIRROR_LOG=''|LVM2_LV_ATTR='ewi-ao----'|LVM2_DEVICES='/dev/sdc1(0)'|LVM2_REGION_SIZE='0 '
  LVM2_LV_NAME='lv_brick3'|LVM2_VG_NAME='data3'|LVM2_LV_SIZE='3.62t'|LVM2_REGION_SIZE='0 '|LVM2_MIRROR_LOG=''|LVM2_LV_ATTR='Vwi-aotz--'|LVM2_DEVICES=''|LVM2_REGION_SIZE='0 '
  LVM2_LV_NAME='lv_hdfs3'|LVM2_VG_NAME='data3'|LVM2_LV_SIZE='3.62t'|LVM2_REGION_SIZE='0 '|LVM2_MIRROR_LOG=''|LVM2_LV_ATTR='Vwi-aotz--'|LVM2_DEVICES=''|LVM2_REGION_SIZE='0 '
  LVM2_LV_NAME='pool3'|LVM2_VG_NAME='data3'|LVM2_LV_SIZE='3.62t'|LVM2_REGION_SIZE='0 '|LVM2_MIRROR_LOG=''|LVM2_LV_ATTR='twi-aotz--'|LVM2_DEVICES='pool3_tdata(0)'|LVM2_REGION_SIZE='0 '
  LVM2_LV_NAME='[pool3_tdata]'|LVM2_VG_NAME='data3'|LVM2_LV_SIZE='3.62t'|LVM2_REGION_SIZE='0 '|LVM2_MIRROR_LOG=''|LVM2_LV_ATTR='Twi-ao----'|LVM2_DEVICES='/dev/sdd1(4096)'|LVM2_REGION_SIZE='0 '
  LVM2_LV_NAME='[pool3_tmeta]'|LVM2_VG_NAME='data3'|LVM2_LV_SIZE='16.00g'|LVM2_REGION_SIZE='0 '|LVM2_MIRROR_LOG=''|LVM2_LV_ATTR='ewi-ao----'|LVM2_DEVICES='/dev/sdd1(0)'|LVM2_REGION_SIZE='0 '
  LVM2_LV_NAME='lv_brick4'|LVM2_VG_NAME='data4'|LVM2_LV_SIZE='3.62t'|LVM2_REGION_SIZE='0 '|LVM2_MIRROR_LOG=''|LVM2_LV_ATTR='Vwi-aotz--'|LVM2_DEVICES=''|LVM2_REGION_SIZE='0 '
  LVM2_LV_NAME='lv_hdfs4'|LVM2_VG_NAME='data4'|LVM2_LV_SIZE='3.62t'|LVM2_REGION_SIZE='0 '|LVM2_MIRROR_LOG=''|LVM2_LV_ATTR='Vwi-aotz--'|LVM2_DEVICES=''|LVM2_REGION_SIZE='0 '
  LVM2_LV_NAME='pool4'|LVM2_VG_NAME='data4'|LVM2_LV_SIZE='3.62t'|LVM2_REGION_SIZE='0 '|LVM2_MIRROR_LOG=''|LVM2_LV_ATTR='twi-aotz--'|LVM2_DEVICES='pool4_tdata(0)'|LVM2_REGION_SIZE='0 '
  LVM2_LV_NAME='[pool4_tdata]'|LVM2_VG_NAME='data4'|LVM2_LV_SIZE='3.62t'|LVM2_REGION_SIZE='0 '|LVM2_MIRROR_LOG=''|LVM2_LV_ATTR='Twi-ao----'|LVM2_DEVICES='/dev/sde1(4096)'|LVM2_REGION_SIZE='0 '
  LVM2_LV_NAME='[pool4_tmeta]'|LVM2_VG_NAME='data4'|LVM2_LV_SIZE='16.00g'|LVM2_REGION_SIZE='0 '|LVM2_MIRROR_LOG=''|LVM2_LV_ATTR='ewi-ao----'|LVM2_DEVICES='/dev/sde1(0)'|LVM2_REGION_SIZE='0 '
  LVM2_LV_NAME='lv_brick5'|LVM2_VG_NAME='data5'|LVM2_LV_SIZE='3.62t'|LVM2_REGION_SIZE='0 '|LVM2_MIRROR_LOG=''|LVM2_LV_ATTR='Vwi-aotz--'|LVM2_DEVICES=''|LVM2_REGION_SIZE='0 '
  LVM2_LV_NAME='lv_hdfs5'|LVM2_VG_NAME='data5'|LVM2_LV_SIZE='3.62t'|LVM2_REGION_SIZE='0 '|LVM2_MIRROR_LOG=''|LVM2_LV_ATTR='Vwi-aotz--'|LVM2_DEVICES=''|LVM2_REGION_SIZE='0 '
  LVM2_LV_NAME='pool5'|LVM2_VG_NAME='data5'|LVM2_LV_SIZE='3.62t'|LVM2_REGION_SIZE='0 '|LVM2_MIRROR_LOG=''|LVM2_LV_ATTR='twi-aotz--'|LVM2_DEVICES='pool5_tdata(0)'|LVM2_REGION_SIZE='0 '
  LVM2_LV_NAME='[pool5_tdata]'|LVM2_VG_NAME='data5'|LVM2_LV_SIZE='3.62t'|LVM2_REGION_SIZE='0 '|LVM2_MIRROR_LOG=''|LVM2_LV_ATTR='Twi-ao----'|LVM2_DEVICES='/dev/sdf1(4096)'|LVM2_REGION_SIZE='0 '
  LVM2_LV_NAME='[pool5_tmeta]'|LVM2_VG_NAME='data5'|LVM2_LV_SIZE='16.00g'|LVM2_REGION_SIZE='0 '|LVM2_MIRROR_LOG=''|LVM2_LV_ATTR='ewi-ao----'|LVM2_DEVICES='/dev/sdf1(0)'|LVM2_REGION_SIZE='0 '
  LVM2_LV_NAME='lv_brick6'|LVM2_VG_NAME='data6'|LVM2_LV_SIZE='3.62t'|LVM2_REGION_SIZE='0 '|LVM2_MIRROR_LOG=''|LVM2_LV_ATTR='Vwi-aotz--'|LVM2_DEVICES=''|LVM2_REGION_SIZE='0 '
  LVM2_LV_NAME='lv_hdfs6'|LVM2_VG_NAME='data6'|LVM2_LV_SIZE='3.62t'|LVM2_REGION_SIZE='0 '|LVM2_MIRROR_LOG=''|LVM2_LV_ATTR='Vwi-aotz--'|LVM2_DEVICES=''|LVM2_REGION_SIZE='0 '
  LVM2_LV_NAME='pool6'|LVM2_VG_NAME='data6'|LVM2_LV_SIZE='3.62t'|LVM2_REGION_SIZE='0 '|LVM2_MIRROR_LOG=''|LVM2_LV_ATTR='twi-aotz--'|LVM2_DEVICES='pool6_tdata(0)'|LVM2_REGION_SIZE='0 '
  LVM2_LV_NAME='[pool6_tdata]'|LVM2_VG_NAME='data6'|LVM2_LV_SIZE='3.62t'|LVM2_REGION_SIZE='0 '|LVM2_MIRROR_LOG=''|LVM2_LV_ATTR='Twi-ao----'|LVM2_DEVICES='/dev/sdg1(4096)'|LVM2_REGION_SIZE='0 '
  LVM2_LV_NAME='[pool6_tmeta]'|LVM2_VG_NAME='data6'|LVM2_LV_SIZE='16.00g'|LVM2_REGION_SIZE='0 '|LVM2_MIRROR_LOG=''|LVM2_LV_ATTR='ewi-ao----'|LVM2_DEVICES='/dev/sdg1(0)'|LVM2_REGION_SIZE='0 '
  LVM2_LV_NAME='lv_brick7'|LVM2_VG_NAME='data7'|LVM2_LV_SIZE='3.62t'|LVM2_REGION_SIZE='0 '|LVM2_MIRROR_LOG=''|LVM2_LV_ATTR='Vwi-aotz--'|LVM2_DEVICES=''|LVM2_REGION_SIZE='0 '
  LVM2_LV_NAME='lv_hdfs7'|LVM2_VG_NAME='data7'|LVM2_LV_SIZE='3.62t'|LVM2_REGION_SIZE='0 '|LVM2_MIRROR_LOG=''|LVM2_LV_ATTR='Vwi-aotz--'|LVM2_DEVICES=''|LVM2_REGION_SIZE='0 '
  LVM2_LV_NAME='pool7'|LVM2_VG_NAME='data7'|LVM2_LV_SIZE='3.62t'|LVM2_REGION_SIZE='0 '|LVM2_MIRROR_LOG=''|LVM2_LV_ATTR='twi-aotz--'|LVM2_DEVICES='pool7_tdata(0)'|LVM2_REGION_SIZE='0 '
  LVM2_LV_NAME='[pool7_tdata]'|LVM2_VG_NAME='data7'|LVM2_LV_SIZE='3.62t'|LVM2_REGION_SIZE='0 '|LVM2_MIRROR_LOG=''|LVM2_LV_ATTR='Twi-ao----'|LVM2_DEVICES='/dev/sdh1(4096)'|LVM2_REGION_SIZE='0 '
  LVM2_LV_NAME='[pool7_tmeta]'|LVM2_VG_NAME='data7'|LVM2_LV_SIZE='16.00g'|LVM2_REGION_SIZE='0 '|LVM2_MIRROR_LOG=''|LVM2_LV_ATTR='ewi-ao----'|LVM2_DEVICES='/dev/sdh1(0)'|LVM2_REGION_SIZE='0 '
  LVM2_LV_NAME='home'|LVM2_VG_NAME='rhel_ceehadoop1'|LVM2_LV_SIZE='976.00g'|LVM2_REGION_SIZE='0 '|LVM2_MIRROR_LOG=''|LVM2_LV_ATTR='-wi-ao----'|LVM2_DEVICES='/dev/sda3(12800)'|LVM2_REGION_SIZE='0 '
  LVM2_LV_NAME='opt'|LVM2_VG_NAME='rhel_ceehadoop1'|LVM2_LV_SIZE='2.57t'|LVM2_REGION_SIZE='0 '|LVM2_MIRROR_LOG=''|LVM2_LV_ATTR='-wi-ao----'|LVM2_DEVICES='/dev/sda3(279551)'|LVM2_REGION_SIZE='0 '
  LVM2_LV_NAME='root'|LVM2_VG_NAME='rhel_ceehadoop1'|LVM2_LV_SIZE='50.00g'|LVM2_REGION_SIZE='0 '|LVM2_MIRROR_LOG=''|LVM2_LV_ATTR='-wi-ao----'|LVM2_DEVICES='/dev/sda3(0)'|LVM2_REGION_SIZE='0 '
  LVM2_LV_NAME='swap'|LVM2_VG_NAME='rhel_ceehadoop1'|LVM2_LV_SIZE='16.00g'|LVM2_REGION_SIZE='0 '|LVM2_MIRROR_LOG=''|LVM2_LV_ATTR='-wi-ao----'|LVM2_DEVICES='/dev/sda3(262656)'|LVM2_REGION_SIZE='0 '
  LVM2_LV_NAME='var'|LVM2_VG_NAME='rhel_ceehadoop1'|LVM2_LV_SIZE='50.00g'|LVM2_REGION_SIZE='0 '|LVM2_MIRROR_LOG=''|LVM2_LV_ATTR='-wi-ao----'|LVM2_DEVICES='/dev/sda3(266752)'|LVM2_REGION_SIZE='0 '
""".strip()   # noqa: W291

LVS_NOHEADINGS_POOL7 = {
    'LV': 'pool7',
    'VG': 'data7',
    'LSize': '3.62t',
    'Region': '0',
    'Attr': 'twi-aotz--',
    'Log': None,
    'Devices': 'pool7_tdata(0)'
}

LVS_HEADINGS_POOL7 = {
    'LV': 'pool7',
    'VG': 'data7',
    'Attr': 'twi-aotz--',
    'LSize': '3.62t',
    'Pool': None,
    'Origin': None,
    'Data%': '0.10',
    'Meta%': '0.11',
    'Move': None,
    'Log': None,
    'Cpy%Sync': None,
    'Convert': None,
    'LV_Tags': None,
    'Devices': 'pool7_tdata(0)'
}

PVS_HEADINGS = """
  WARNING: Locking disabled. Be careful! This could corrupt your metadata.
    Wiping internal VG cache
    Wiping cache of LVM-capable devices
  PV                                      VG              Fmt  Attr PSize PFree DevSize PV UUID                                PMdaFree  PMdaSize  #PMda #PMdaUse PE    
  /dev/data1/lv_brick1                                         ---     0     0    3.62t                                               0         0      0        0      0
  /dev/data1/lv_hdfs1                                          ---     0     0    3.62t                                               0         0      0        0      0
  /dev/data2/lv_brick2                                         ---     0     0    3.62t                                               0         0      0        0      0
  /dev/data2/lv_hdfs2                                          ---     0     0    3.62t                                               0         0      0        0      0
  /dev/data3/lv_brick3                                         ---     0     0    3.62t                                               0         0      0        0      0
  /dev/data3/lv_hdfs3                                          ---     0     0    3.62t                                               0         0      0        0      0
  /dev/data4/lv_brick4                                         ---     0     0    3.62t                                               0         0      0        0      0
  /dev/data4/lv_hdfs4                                          ---     0     0    3.62t                                               0         0      0        0      0
  /dev/data5/lv_brick5                                         ---     0     0    3.62t                                               0         0      0        0      0
  /dev/data5/lv_hdfs5                                          ---     0     0    3.62t                                               0         0      0        0      0
  /dev/data6/lv_brick6                                         ---     0     0    3.62t                                               0         0      0        0      0
  /dev/data6/lv_hdfs6                                          ---     0     0    3.62t                                               0         0      0        0      0
  /dev/data7/lv_brick7                                         ---     0     0    3.62t                                               0         0      0        0      0
  /dev/data7/lv_hdfs7                                          ---     0     0    3.62t                                               0         0      0        0      0
  /dev/loop0                                                   ---     0     0  100.00g                                               0         0      0        0      0
  /dev/loop1                                                   ---     0     0    2.00g                                               0         0      0        0      0
  /dev/mapper/docker-253:3-100685290-pool                      ---     0     0  100.00g                                               0         0      0        0      0
  /dev/rhel_ceehadoop1/home                                    ---     0     0  976.00g                                               0         0      0        0      0
  /dev/rhel_ceehadoop1/opt                                     ---     0     0    2.57t                                               0         0      0        0      0
  /dev/rhel_ceehadoop1/root                                    ---     0     0   50.00g                                               0         0      0        0      0
  /dev/rhel_ceehadoop1/swap                                    ---     0     0   16.00g                                               0         0      0        0      0
  /dev/rhel_ceehadoop1/var                                     ---     0     0   50.00g                                               0         0      0        0      0
  /dev/sda2                                                    ---     0     0    1.00g                                               0         0      0        0      0
  /dev/sda3                               rhel_ceehadoop1 lvm2 a--  3.63t    0    3.63t 3e2mRe-1y3a-iUSj-F3tH-yG1M-t3qD-8uNDf5        0   1020.00k     1        1 952831
  /dev/sdb1                               data1           lvm2 a--  3.64t 4.00m   3.64t dhr134-VxSA-R7dW-op7s-HCco-7J2A-7MvaeN        0    252.00k     1        1 953853
  /dev/sdc1                               data2           lvm2 a--  3.64t 4.00m   3.64t sxTsQE-raAM-8s3b-FSy0-LhL2-Naue-f2ebcA        0    252.00k     1        1 953853
  /dev/sdd1                               data3           lvm2 a--  3.64t 4.00m   3.64t yxj2qs-qOKA-57XF-228r-qWQj-3zez-i0Vaiw        0    252.00k     1        1 953853
  /dev/sde1                               data4           lvm2 a--  3.64t 4.00m   3.64t 94oczR-Utni-dOzj-3CMQ-efOJ-TVa8-yak25P        0    252.00k     1        1 953853
  /dev/sdf1                               data5           lvm2 a--  3.64t 4.00m   3.64t r3UW8H-pLz5-rpsn-GK2u-1kJE-GKsy-uOeoIz        0    252.00k     1        1 953853
  /dev/sdg1                               data6           lvm2 a--  3.64t 4.00m   3.64t oZtJSv-HM9w-4She-1TU0-Z31G-dgKX-liJNID        0    252.00k     1        1 953853
  /dev/sdh1                               data7           lvm2 a--  3.64t 4.00m   3.64t Ys0p6S-WJOW-TAZT-czmX-iOYq-0Tgg-v4cl0H        0    252.00k     1        1 953853
    Reloading config files
    Wiping internal VG cache
""".strip()   # noqa: W291

PVS_NO_HEADINGS = """
  WARNING: Locking disabled. Be careful! This could corrupt your metadata.
  LVM2_PV_FMT=''|LVM2_PV_UUID=''|LVM2_DEV_SIZE='3.62t'|LVM2_PV_NAME='/dev/data1/lv_brick1'|LVM2_PV_MAJOR='253'|LVM2_PV_MINOR='28'|LVM2_PV_MDA_FREE='0 '|LVM2_PV_MDA_SIZE='0 '|LVM2_PV_EXT_VSN=''|LVM2_PE_START='0 '|LVM2_PV_SIZE='0 '|LVM2_PV_FREE='0 '|LVM2_PV_USED='0 '|LVM2_PV_ATTR='---'|LVM2_PV_ALLOCATABLE=''|LVM2_PV_EXPORTED=''|LVM2_PV_MISSING=''|LVM2_PV_PE_COUNT='0'|LVM2_PV_PE_ALLOC_COUNT='0'|LVM2_PV_TAGS=''|LVM2_PV_MDA_COUNT='0'|LVM2_PV_MDA_USED_COUNT='0'|LVM2_PV_BA_START='0 '|LVM2_PV_BA_SIZE='0 '|LVM2_PV_IN_USE=''|LVM2_PV_DUPLICATE=''|LVM2_VG_NAME=''
  LVM2_PV_FMT=''|LVM2_PV_UUID=''|LVM2_DEV_SIZE='3.62t'|LVM2_PV_NAME='/dev/data1/lv_hdfs1'|LVM2_PV_MAJOR='253'|LVM2_PV_MINOR='41'|LVM2_PV_MDA_FREE='0 '|LVM2_PV_MDA_SIZE='0 '|LVM2_PV_EXT_VSN=''|LVM2_PE_START='0 '|LVM2_PV_SIZE='0 '|LVM2_PV_FREE='0 '|LVM2_PV_USED='0 '|LVM2_PV_ATTR='---'|LVM2_PV_ALLOCATABLE=''|LVM2_PV_EXPORTED=''|LVM2_PV_MISSING=''|LVM2_PV_PE_COUNT='0'|LVM2_PV_PE_ALLOC_COUNT='0'|LVM2_PV_TAGS=''|LVM2_PV_MDA_COUNT='0'|LVM2_PV_MDA_USED_COUNT='0'|LVM2_PV_BA_START='0 '|LVM2_PV_BA_SIZE='0 '|LVM2_PV_IN_USE=''|LVM2_PV_DUPLICATE=''|LVM2_VG_NAME=''
  LVM2_PV_FMT=''|LVM2_PV_UUID=''|LVM2_DEV_SIZE='3.62t'|LVM2_PV_NAME='/dev/data2/lv_brick2'|LVM2_PV_MAJOR='253'|LVM2_PV_MINOR='30'|LVM2_PV_MDA_FREE='0 '|LVM2_PV_MDA_SIZE='0 '|LVM2_PV_EXT_VSN=''|LVM2_PE_START='0 '|LVM2_PV_SIZE='0 '|LVM2_PV_FREE='0 '|LVM2_PV_USED='0 '|LVM2_PV_ATTR='---'|LVM2_PV_ALLOCATABLE=''|LVM2_PV_EXPORTED=''|LVM2_PV_MISSING=''|LVM2_PV_PE_COUNT='0'|LVM2_PV_PE_ALLOC_COUNT='0'|LVM2_PV_TAGS=''|LVM2_PV_MDA_COUNT='0'|LVM2_PV_MDA_USED_COUNT='0'|LVM2_PV_BA_START='0 '|LVM2_PV_BA_SIZE='0 '|LVM2_PV_IN_USE=''|LVM2_PV_DUPLICATE=''|LVM2_VG_NAME=''
  LVM2_PV_FMT=''|LVM2_PV_UUID=''|LVM2_DEV_SIZE='3.62t'|LVM2_PV_NAME='/dev/data2/lv_hdfs2'|LVM2_PV_MAJOR='253'|LVM2_PV_MINOR='42'|LVM2_PV_MDA_FREE='0 '|LVM2_PV_MDA_SIZE='0 '|LVM2_PV_EXT_VSN=''|LVM2_PE_START='0 '|LVM2_PV_SIZE='0 '|LVM2_PV_FREE='0 '|LVM2_PV_USED='0 '|LVM2_PV_ATTR='---'|LVM2_PV_ALLOCATABLE=''|LVM2_PV_EXPORTED=''|LVM2_PV_MISSING=''|LVM2_PV_PE_COUNT='0'|LVM2_PV_PE_ALLOC_COUNT='0'|LVM2_PV_TAGS=''|LVM2_PV_MDA_COUNT='0'|LVM2_PV_MDA_USED_COUNT='0'|LVM2_PV_BA_START='0 '|LVM2_PV_BA_SIZE='0 '|LVM2_PV_IN_USE=''|LVM2_PV_DUPLICATE=''|LVM2_VG_NAME=''
  LVM2_PV_FMT=''|LVM2_PV_UUID=''|LVM2_DEV_SIZE='3.62t'|LVM2_PV_NAME='/dev/data3/lv_brick3'|LVM2_PV_MAJOR='253'|LVM2_PV_MINOR='32'|LVM2_PV_MDA_FREE='0 '|LVM2_PV_MDA_SIZE='0 '|LVM2_PV_EXT_VSN=''|LVM2_PE_START='0 '|LVM2_PV_SIZE='0 '|LVM2_PV_FREE='0 '|LVM2_PV_USED='0 '|LVM2_PV_ATTR='---'|LVM2_PV_ALLOCATABLE=''|LVM2_PV_EXPORTED=''|LVM2_PV_MISSING=''|LVM2_PV_PE_COUNT='0'|LVM2_PV_PE_ALLOC_COUNT='0'|LVM2_PV_TAGS=''|LVM2_PV_MDA_COUNT='0'|LVM2_PV_MDA_USED_COUNT='0'|LVM2_PV_BA_START='0 '|LVM2_PV_BA_SIZE='0 '|LVM2_PV_IN_USE=''|LVM2_PV_DUPLICATE=''|LVM2_VG_NAME=''
  LVM2_PV_FMT=''|LVM2_PV_UUID=''|LVM2_DEV_SIZE='3.62t'|LVM2_PV_NAME='/dev/data3/lv_hdfs3'|LVM2_PV_MAJOR='253'|LVM2_PV_MINOR='43'|LVM2_PV_MDA_FREE='0 '|LVM2_PV_MDA_SIZE='0 '|LVM2_PV_EXT_VSN=''|LVM2_PE_START='0 '|LVM2_PV_SIZE='0 '|LVM2_PV_FREE='0 '|LVM2_PV_USED='0 '|LVM2_PV_ATTR='---'|LVM2_PV_ALLOCATABLE=''|LVM2_PV_EXPORTED=''|LVM2_PV_MISSING=''|LVM2_PV_PE_COUNT='0'|LVM2_PV_PE_ALLOC_COUNT='0'|LVM2_PV_TAGS=''|LVM2_PV_MDA_COUNT='0'|LVM2_PV_MDA_USED_COUNT='0'|LVM2_PV_BA_START='0 '|LVM2_PV_BA_SIZE='0 '|LVM2_PV_IN_USE=''|LVM2_PV_DUPLICATE=''|LVM2_VG_NAME=''
  LVM2_PV_FMT=''|LVM2_PV_UUID=''|LVM2_DEV_SIZE='3.62t'|LVM2_PV_NAME='/dev/data4/lv_brick4'|LVM2_PV_MAJOR='253'|LVM2_PV_MINOR='34'|LVM2_PV_MDA_FREE='0 '|LVM2_PV_MDA_SIZE='0 '|LVM2_PV_EXT_VSN=''|LVM2_PE_START='0 '|LVM2_PV_SIZE='0 '|LVM2_PV_FREE='0 '|LVM2_PV_USED='0 '|LVM2_PV_ATTR='---'|LVM2_PV_ALLOCATABLE=''|LVM2_PV_EXPORTED=''|LVM2_PV_MISSING=''|LVM2_PV_PE_COUNT='0'|LVM2_PV_PE_ALLOC_COUNT='0'|LVM2_PV_TAGS=''|LVM2_PV_MDA_COUNT='0'|LVM2_PV_MDA_USED_COUNT='0'|LVM2_PV_BA_START='0 '|LVM2_PV_BA_SIZE='0 '|LVM2_PV_IN_USE=''|LVM2_PV_DUPLICATE=''|LVM2_VG_NAME=''
  LVM2_PV_FMT=''|LVM2_PV_UUID=''|LVM2_DEV_SIZE='3.62t'|LVM2_PV_NAME='/dev/data4/lv_hdfs4'|LVM2_PV_MAJOR='253'|LVM2_PV_MINOR='44'|LVM2_PV_MDA_FREE='0 '|LVM2_PV_MDA_SIZE='0 '|LVM2_PV_EXT_VSN=''|LVM2_PE_START='0 '|LVM2_PV_SIZE='0 '|LVM2_PV_FREE='0 '|LVM2_PV_USED='0 '|LVM2_PV_ATTR='---'|LVM2_PV_ALLOCATABLE=''|LVM2_PV_EXPORTED=''|LVM2_PV_MISSING=''|LVM2_PV_PE_COUNT='0'|LVM2_PV_PE_ALLOC_COUNT='0'|LVM2_PV_TAGS=''|LVM2_PV_MDA_COUNT='0'|LVM2_PV_MDA_USED_COUNT='0'|LVM2_PV_BA_START='0 '|LVM2_PV_BA_SIZE='0 '|LVM2_PV_IN_USE=''|LVM2_PV_DUPLICATE=''|LVM2_VG_NAME=''
  LVM2_PV_FMT=''|LVM2_PV_UUID=''|LVM2_DEV_SIZE='3.62t'|LVM2_PV_NAME='/dev/data5/lv_brick5'|LVM2_PV_MAJOR='253'|LVM2_PV_MINOR='36'|LVM2_PV_MDA_FREE='0 '|LVM2_PV_MDA_SIZE='0 '|LVM2_PV_EXT_VSN=''|LVM2_PE_START='0 '|LVM2_PV_SIZE='0 '|LVM2_PV_FREE='0 '|LVM2_PV_USED='0 '|LVM2_PV_ATTR='---'|LVM2_PV_ALLOCATABLE=''|LVM2_PV_EXPORTED=''|LVM2_PV_MISSING=''|LVM2_PV_PE_COUNT='0'|LVM2_PV_PE_ALLOC_COUNT='0'|LVM2_PV_TAGS=''|LVM2_PV_MDA_COUNT='0'|LVM2_PV_MDA_USED_COUNT='0'|LVM2_PV_BA_START='0 '|LVM2_PV_BA_SIZE='0 '|LVM2_PV_IN_USE=''|LVM2_PV_DUPLICATE=''|LVM2_VG_NAME=''
  LVM2_PV_FMT=''|LVM2_PV_UUID=''|LVM2_DEV_SIZE='3.62t'|LVM2_PV_NAME='/dev/data5/lv_hdfs5'|LVM2_PV_MAJOR='253'|LVM2_PV_MINOR='45'|LVM2_PV_MDA_FREE='0 '|LVM2_PV_MDA_SIZE='0 '|LVM2_PV_EXT_VSN=''|LVM2_PE_START='0 '|LVM2_PV_SIZE='0 '|LVM2_PV_FREE='0 '|LVM2_PV_USED='0 '|LVM2_PV_ATTR='---'|LVM2_PV_ALLOCATABLE=''|LVM2_PV_EXPORTED=''|LVM2_PV_MISSING=''|LVM2_PV_PE_COUNT='0'|LVM2_PV_PE_ALLOC_COUNT='0'|LVM2_PV_TAGS=''|LVM2_PV_MDA_COUNT='0'|LVM2_PV_MDA_USED_COUNT='0'|LVM2_PV_BA_START='0 '|LVM2_PV_BA_SIZE='0 '|LVM2_PV_IN_USE=''|LVM2_PV_DUPLICATE=''|LVM2_VG_NAME=''
  LVM2_PV_FMT=''|LVM2_PV_UUID=''|LVM2_DEV_SIZE='3.62t'|LVM2_PV_NAME='/dev/data6/lv_brick6'|LVM2_PV_MAJOR='253'|LVM2_PV_MINOR='38'|LVM2_PV_MDA_FREE='0 '|LVM2_PV_MDA_SIZE='0 '|LVM2_PV_EXT_VSN=''|LVM2_PE_START='0 '|LVM2_PV_SIZE='0 '|LVM2_PV_FREE='0 '|LVM2_PV_USED='0 '|LVM2_PV_ATTR='---'|LVM2_PV_ALLOCATABLE=''|LVM2_PV_EXPORTED=''|LVM2_PV_MISSING=''|LVM2_PV_PE_COUNT='0'|LVM2_PV_PE_ALLOC_COUNT='0'|LVM2_PV_TAGS=''|LVM2_PV_MDA_COUNT='0'|LVM2_PV_MDA_USED_COUNT='0'|LVM2_PV_BA_START='0 '|LVM2_PV_BA_SIZE='0 '|LVM2_PV_IN_USE=''|LVM2_PV_DUPLICATE=''|LVM2_VG_NAME=''
  LVM2_PV_FMT=''|LVM2_PV_UUID=''|LVM2_DEV_SIZE='3.62t'|LVM2_PV_NAME='/dev/data6/lv_hdfs6'|LVM2_PV_MAJOR='253'|LVM2_PV_MINOR='46'|LVM2_PV_MDA_FREE='0 '|LVM2_PV_MDA_SIZE='0 '|LVM2_PV_EXT_VSN=''|LVM2_PE_START='0 '|LVM2_PV_SIZE='0 '|LVM2_PV_FREE='0 '|LVM2_PV_USED='0 '|LVM2_PV_ATTR='---'|LVM2_PV_ALLOCATABLE=''|LVM2_PV_EXPORTED=''|LVM2_PV_MISSING=''|LVM2_PV_PE_COUNT='0'|LVM2_PV_PE_ALLOC_COUNT='0'|LVM2_PV_TAGS=''|LVM2_PV_MDA_COUNT='0'|LVM2_PV_MDA_USED_COUNT='0'|LVM2_PV_BA_START='0 '|LVM2_PV_BA_SIZE='0 '|LVM2_PV_IN_USE=''|LVM2_PV_DUPLICATE=''|LVM2_VG_NAME=''
  LVM2_PV_FMT=''|LVM2_PV_UUID=''|LVM2_DEV_SIZE='3.62t'|LVM2_PV_NAME='/dev/data7/lv_brick7'|LVM2_PV_MAJOR='253'|LVM2_PV_MINOR='40'|LVM2_PV_MDA_FREE='0 '|LVM2_PV_MDA_SIZE='0 '|LVM2_PV_EXT_VSN=''|LVM2_PE_START='0 '|LVM2_PV_SIZE='0 '|LVM2_PV_FREE='0 '|LVM2_PV_USED='0 '|LVM2_PV_ATTR='---'|LVM2_PV_ALLOCATABLE=''|LVM2_PV_EXPORTED=''|LVM2_PV_MISSING=''|LVM2_PV_PE_COUNT='0'|LVM2_PV_PE_ALLOC_COUNT='0'|LVM2_PV_TAGS=''|LVM2_PV_MDA_COUNT='0'|LVM2_PV_MDA_USED_COUNT='0'|LVM2_PV_BA_START='0 '|LVM2_PV_BA_SIZE='0 '|LVM2_PV_IN_USE=''|LVM2_PV_DUPLICATE=''|LVM2_VG_NAME=''
  LVM2_PV_FMT=''|LVM2_PV_UUID=''|LVM2_DEV_SIZE='3.62t'|LVM2_PV_NAME='/dev/data7/lv_hdfs7'|LVM2_PV_MAJOR='253'|LVM2_PV_MINOR='47'|LVM2_PV_MDA_FREE='0 '|LVM2_PV_MDA_SIZE='0 '|LVM2_PV_EXT_VSN=''|LVM2_PE_START='0 '|LVM2_PV_SIZE='0 '|LVM2_PV_FREE='0 '|LVM2_PV_USED='0 '|LVM2_PV_ATTR='---'|LVM2_PV_ALLOCATABLE=''|LVM2_PV_EXPORTED=''|LVM2_PV_MISSING=''|LVM2_PV_PE_COUNT='0'|LVM2_PV_PE_ALLOC_COUNT='0'|LVM2_PV_TAGS=''|LVM2_PV_MDA_COUNT='0'|LVM2_PV_MDA_USED_COUNT='0'|LVM2_PV_BA_START='0 '|LVM2_PV_BA_SIZE='0 '|LVM2_PV_IN_USE=''|LVM2_PV_DUPLICATE=''|LVM2_VG_NAME=''
  LVM2_PV_FMT=''|LVM2_PV_UUID=''|LVM2_DEV_SIZE='100.00g'|LVM2_PV_NAME='/dev/loop0'|LVM2_PV_MAJOR='7'|LVM2_PV_MINOR='0'|LVM2_PV_MDA_FREE='0 '|LVM2_PV_MDA_SIZE='0 '|LVM2_PV_EXT_VSN=''|LVM2_PE_START='0 '|LVM2_PV_SIZE='0 '|LVM2_PV_FREE='0 '|LVM2_PV_USED='0 '|LVM2_PV_ATTR='---'|LVM2_PV_ALLOCATABLE=''|LVM2_PV_EXPORTED=''|LVM2_PV_MISSING=''|LVM2_PV_PE_COUNT='0'|LVM2_PV_PE_ALLOC_COUNT='0'|LVM2_PV_TAGS=''|LVM2_PV_MDA_COUNT='0'|LVM2_PV_MDA_USED_COUNT='0'|LVM2_PV_BA_START='0 '|LVM2_PV_BA_SIZE='0 '|LVM2_PV_IN_USE=''|LVM2_PV_DUPLICATE=''|LVM2_VG_NAME=''
  LVM2_PV_FMT=''|LVM2_PV_UUID=''|LVM2_DEV_SIZE='2.00g'|LVM2_PV_NAME='/dev/loop1'|LVM2_PV_MAJOR='7'|LVM2_http://m.arkansasonline.com/obituaries/2017/apr/10/charles-dietz-2017-04-10/PV_MINOR='1'|LVM2_PV_MDA_FREE='0 '|LVM2_PV_MDA_SIZE='0 '|LVM2_PV_EXT_VSN=''|LVM2_PE_START='0 '|LVM2_PV_SIZE='0 '|LVM2_PV_FREE='0 '|LVM2_PV_USED='0 '|LVM2_PV_ATTR='---'|LVM2_PV_ALLOCATABLE=''|LVM2_PV_EXPORTED=''|LVM2_PV_MISSING=''|LVM2_PV_PE_COUNT='0'|LVM2_PV_PE_ALLOC_COUNT='0'|LVM2_PV_TAGS=''|LVM2_PV_MDA_COUNT='0'|LVM2_PV_MDA_USED_COUNT='0'|LVM2_PV_BA_START='0 '|LVM2_PV_BA_SIZE='0 '|LVM2_PV_IN_USE=''|LVM2_PV_DUPLICATE=''|LVM2_VG_NAME=''
  LVM2_PV_FMT=''|LVM2_PV_UUID=''|LVM2_DEV_SIZE='100.00g'|LVM2_PV_NAME='/dev/mapper/docker-253:3-100685290-pool'|LVM2_PV_MAJOR='253'|LVM2_PV_MINOR='5'|LVM2_PV_MDA_FREE='0 '|LVM2_PV_MDA_SIZE='0 '|LVM2_PV_EXT_VSN=''|LVM2_PE_START='0 '|LVM2_PV_SIZE='0 '|LVM2_PV_FREE='0 '|LVM2_PV_USED='0 '|LVM2_PV_ATTR='---'|LVM2_PV_ALLOCATABLE=''|LVM2_PV_EXPORTED=''|LVM2_PV_MISSING=''|LVM2_PV_PE_COUNT='0'|LVM2_PV_PE_ALLOC_COUNT='0'|LVM2_PV_TAGS=''|LVM2_PV_MDA_COUNT='0'|LVM2_PV_MDA_USED_COUNT='0'|LVM2_PV_BA_START='0 '|LVM2_PV_BA_SIZE='0 '|LVM2_PV_IN_USE=''|LVM2_PV_DUPLICATE=''|LVM2_VG_NAME=''
  LVM2_PV_FMT=''|LVM2_PV_UUID=''|LVM2_DEV_SIZE='976.00g'|LVM2_PV_NAME='/dev/rhel_ceehadoop1/home'|LVM2_PV_MAJOR='253'|LVM2_PV_MINOR='2'|LVM2_PV_MDA_FREE='0 '|LVM2_PV_MDA_SIZE='0 '|LVM2_PV_EXT_VSN=''|LVM2_PE_START='0 '|LVM2_PV_SIZE='0 '|LVM2_PV_FREE='0 '|LVM2_PV_USED='0 '|LVM2_PV_ATTR='---'|LVM2_PV_ALLOCATABLE=''|LVM2_PV_EXPORTED=''|LVM2_PV_MISSING=''|LVM2_PV_PE_COUNT='0'|LVM2_PV_PE_ALLOC_COUNT='0'|LVM2_PV_TAGS=''|LVM2_PV_MDA_COUNT='0'|LVM2_PV_MDA_USED_COUNT='0'|LVM2_PV_BA_START='0 '|LVM2_PV_BA_SIZE='0 '|LVM2_PV_IN_USE=''|LVM2_PV_DUPLICATE=''|LVM2_VG_NAME=''
  LVM2_PV_FMT=''|LVM2_PV_UUID=''|LVM2_DEV_SIZE='2.57t'|LVM2_PV_NAME='/dev/rhel_ceehadoop1/opt'|LVM2_PV_MAJOR='253'|LVM2_PV_MINOR='4'|LVM2_PV_MDA_FREE='0 '|LVM2_PV_MDA_SIZE='0 '|LVM2_PV_EXT_VSN=''|LVM2_PE_START='0 '|LVM2_PV_SIZE='0 '|LVM2_PV_FREE='0 '|LVM2_PV_USED='0 '|LVM2_PV_ATTR='---'|LVM2_PV_ALLOCATABLE=''|LVM2_PV_EXPORTED=''|LVM2_PV_MISSING=''|LVM2_PV_PE_COUNT='0'|LVM2_PV_PE_ALLOC_COUNT='0'|LVM2_PV_TAGS=''|LVM2_PV_MDA_COUNT='0'|LVM2_PV_MDA_USED_COUNT='0'|LVM2_PV_BA_START='0 '|LVM2_PV_BA_SIZE='0 '|LVM2_PV_IN_USE=''|LVM2_PV_DUPLICATE=''|LVM2_VG_NAME=''
  LVM2_PV_FMT=''|LVM2_PV_UUID=''|LVM2_DEV_SIZE='50.00g'|LVM2_PV_NAME='/dev/rhel_ceehadoop1/root'|LVM2_PV_MAJOR='253'|LVM2_PV_MINOR='0'|LVM2_PV_MDA_FREE='0 '|LVM2_PV_MDA_SIZE='0 '|LVM2_PV_EXT_VSN=''|LVM2_PE_START='0 '|LVM2_PV_SIZE='0 '|LVM2_PV_FREE='0 '|LVM2_PV_USED='0 '|LVM2_PV_ATTR='---'|LVM2_PV_ALLOCATABLE=''|LVM2_PV_EXPORTED=''|LVM2_PV_MISSING=''|LVM2_PV_PE_COUNT='0'|LVM2_PV_PE_ALLOC_COUNT='0'|LVM2_PV_TAGS=''|LVM2_PV_MDA_COUNT='0'|LVM2_PV_MDA_USED_COUNT='0'|LVM2_PV_BA_START='0 '|LVM2_PV_BA_SIZE='0 '|LVM2_PV_IN_USE=''|LVM2_PV_DUPLICATE=''|LVM2_VG_NAME=''
  LVM2_PV_FMT=''|LVM2_PV_UUID=''|LVM2_DEV_SIZE='16.00g'|LVM2_PV_NAME='/dev/rhel_ceehadoop1/swap'|LVM2_PV_MAJOR='253'|LVM2_PV_MINOR='1'|LVM2_PV_MDA_FREE='0 '|LVM2_PV_MDA_SIZE='0 '|LVM2_PV_EXT_VSN=''|LVM2_PE_START='0 '|LVM2_PV_SIZE='0 '|LVM2_PV_FREE='0 '|LVM2_PV_USED='0 '|LVM2_PV_ATTR='---'|LVM2_PV_ALLOCATABLE=''|LVM2_PV_EXPORTED=''|LVM2_PV_MISSING=''|LVM2_PV_PE_COUNT='0'|LVM2_PV_PE_ALLOC_COUNT='0'|LVM2_PV_TAGS=''|LVM2_PV_MDA_COUNT='0'|LVM2_PV_MDA_USED_COUNT='0'|LVM2_PV_BA_START='0 '|LVM2_PV_BA_SIZE='0 '|LVM2_PV_IN_USE=''|LVM2_PV_DUPLICATE=''|LVM2_VG_NAME=''
  LVM2_PV_FMT=''|LVM2_PV_UUID=''|LVM2_DEV_SIZE='50.00g'|LVM2_PV_NAME='/dev/rhel_ceehadoop1/var'|LVM2_PV_MAJOR='253'|LVM2_PV_MINOR='3'|LVM2_PV_MDA_FREE='0 '|LVM2_PV_MDA_SIZE='0 '|LVM2_PV_EXT_VSN=''|LVM2_PE_START='0 '|LVM2_PV_SIZE='0 '|LVM2_PV_FREE='0 '|LVM2_PV_USED='0 '|LVM2_PV_ATTR='---'|LVM2_PV_ALLOCATABLE=''|LVM2_PV_EXPORTED=''|LVM2_PV_MISSING=''|LVM2_PV_PE_COUNT='0'|LVM2_PV_PE_ALLOC_COUNT='0'|LVM2_PV_TAGS=''|LVM2_PV_MDA_COUNT='0'|LVM2_PV_MDA_USED_COUNT='0'|LVM2_PV_BA_START='0 '|LVM2_PV_BA_SIZE='0 '|LVM2_PV_IN_USE=''|LVM2_PV_DUPLICATE=''|LVM2_VG_NAME=''
  LVM2_PV_FMT=''|LVM2_PV_UUID=''|LVM2_DEV_SIZE='1.00g'|LVM2_PV_NAME='/dev/sda2'|LVM2_PV_MAJOR='8'|LVM2_PV_MINOR='2'|LVM2_PV_MDA_FREE='0 '|LVM2_PV_MDA_SIZE='0 '|LVM2_PV_EXT_VSN=''|LVM2_PE_START='0 '|LVM2_PV_SIZE='0 '|LVM2_PV_FREE='0 '|LVM2_PV_USED='0 '|LVM2_PV_ATTR='---'|LVM2_PV_ALLOCATABLE=''|LVM2_PV_EXPORTED=''|LVM2_PV_MISSING=''|LVM2_PV_PE_COUNT='0'|LVM2_PV_PE_ALLOC_COUNT='0'|LVM2_PV_TAGS=''|LVM2_PV_MDA_COUNT='0'|LVM2_PV_MDA_USED_COUNT='0'|LVM2_PV_BA_START='0 '|LVM2_PV_BA_SIZE='0 '|LVM2_PV_IN_USE=''|LVM2_PV_DUPLICATE=''|LVM2_VG_NAME=''
  LVM2_PV_FMT='lvm2'|LVM2_PV_UUID='3e2mRe-1y3a-iUSj-F3tH-yG1M-t3qD-8uNDf5'|LVM2_DEV_SIZE='3.63t'|LVM2_PV_NAME='/dev/sda3'|LVM2_PV_MAJOR='8'|LVM2_PV_MINOR='3'|LVM2_PV_MDA_FREE='0 '|LVM2_PV_MDA_SIZE='1020.00k'|LVM2_PV_EXT_VSN='2'|LVM2_PE_START='1.00m'|LVM2_PV_SIZE='3.63t'|LVM2_PV_FREE='0 '|LVM2_PV_USED='3.63t'|LVM2_PV_ATTR='a--'|LVM2_PV_ALLOCATABLE='allocatable'|LVM2_PV_EXPORTED=''|LVM2_PV_MISSING=''|LVM2_PV_PE_COUNT='952831'|LVM2_PV_PE_ALLOC_COUNT='952831'|LVM2_PV_TAGS=''|LVM2_PV_MDA_COUNT='1'|LVM2_PV_MDA_USED_COUNT='1'|LVM2_PV_BA_START='0 '|LVM2_PV_BA_SIZE='0 '|LVM2_PV_IN_USE='used'|LVM2_PV_DUPLICATE=''|LVM2_VG_NAME='rhel_ceehadoop1'
  LVM2_PV_FMT='lvm2'|LVM2_PV_UUID='dhr134-VxSA-R7dW-op7s-HCco-7J2A-7MvaeN'|LVM2_DEV_SIZE='3.64t'|LVM2_PV_NAME='/dev/sdb1'|LVM2_PV_MAJOR='8'|LVM2_PV_MINOR='17'|LVM2_PV_MDA_FREE='0 '|LVM2_PV_MDA_SIZE='252.00k'|LVM2_PV_EXT_VSN='2'|LVM2_PE_START='256.00k'|LVM2_PV_SIZE='3.64t'|LVM2_PV_FREE='4.00m'|LVM2_PV_USED='3.64t'|LVM2_PV_ATTR='a--'|LVM2_PV_ALLOCATABLE='allocatable'|LVM2_PV_EXPORTED=''|LVM2_PV_MISSING=''|LVM2_PV_PE_COUNT='953853'|LVM2_PV_PE_ALLOC_COUNT='953852'|LVM2_PV_TAGS=''|LVM2_PV_MDA_COUNT='1'|LVM2_PV_MDA_USED_COUNT='1'|LVM2_PV_BA_START='0 '|LVM2_PV_BA_SIZE='0 '|LVM2_PV_IN_USE='used'|LVM2_PV_DUPLICATE=''|LVM2_VG_NAME='data1'
  LVM2_PV_FMT='lvm2'|LVM2_PV_UUID='sxTsQE-raAM-8s3b-FSy0-LhL2-Naue-f2ebcA'|LVM2_DEV_SIZE='3.64t'|LVM2_PV_NAME='/dev/sdc1'|LVM2_PV_MAJOR='8'|LVM2_PV_MINOR='33'|LVM2_PV_MDA_FREE='0 '|LVM2_PV_MDA_SIZE='252.00k'|LVM2_PV_EXT_VSN='2'|LVM2_PE_START='256.00k'|LVM2_PV_SIZE='3.64t'|LVM2_PV_FREE='4.00m'|LVM2_PV_USED='3.64t'|LVM2_PV_ATTR='a--'|LVM2_PV_ALLOCATABLE='allocatable'|LVM2_PV_EXPORTED=''|LVM2_PV_MISSING=''|LVM2_PV_PE_COUNT='953853'|LVM2_PV_PE_ALLOC_COUNT='953852'|LVM2_PV_TAGS=''|LVM2_PV_MDA_COUNT='1'|LVM2_PV_MDA_USED_COUNT='1'|LVM2_PV_BA_START='0 '|LVM2_PV_BA_SIZE='0 '|LVM2_PV_IN_USE='used'|LVM2_PV_DUPLICATE=''|LVM2_VG_NAME='data2'
  LVM2_PV_FMT='lvm2'|LVM2_PV_UUID='yxj2qs-qOKA-57XF-228r-qWQj-3zez-i0Vaiw'|LVM2_DEV_SIZE='3.64t'|LVM2_PV_NAME='/dev/sdd1'|LVM2_PV_MAJOR='8'|LVM2_PV_MINOR='49'|LVM2_PV_MDA_FREE='0 '|LVM2_PV_MDA_SIZE='252.00k'|LVM2_PV_EXT_VSN='2'|LVM2_PE_START='256.00k'|LVM2_PV_SIZE='3.64t'|LVM2_PV_FREE='4.00m'|LVM2_PV_USED='3.64t'|LVM2_PV_ATTR='a--'|LVM2_PV_ALLOCATABLE='allocatable'|LVM2_PV_EXPORTED=''|LVM2_PV_MISSING=''|LVM2_PV_PE_COUNT='953853'|LVM2_PV_PE_ALLOC_COUNT='953852'|LVM2_PV_TAGS=''|LVM2_PV_MDA_COUNT='1'|LVM2_PV_MDA_USED_COUNT='1'|LVM2_PV_BA_START='0 '|LVM2_PV_BA_SIZE='0 '|LVM2_PV_IN_USE='used'|LVM2_PV_DUPLICATE=''|LVM2_VG_NAME='data3'
  LVM2_PV_FMT='lvm2'|LVM2_PV_UUID='94oczR-Utni-dOzj-3CMQ-efOJ-TVa8-yak25P'|LVM2_DEV_SIZE='3.64t'|LVM2_PV_NAME='/dev/sde1'|LVM2_PV_MAJOR='8'|LVM2_PV_MINOR='65'|LVM2_PV_MDA_FREE='0 '|LVM2_PV_MDA_SIZE='252.00k'|LVM2_PV_EXT_VSN='2'|LVM2_PE_START='256.00k'|LVM2_PV_SIZE='3.64t'|LVM2_PV_FREE='4.00m'|LVM2_PV_USED='3.64t'|LVM2_PV_ATTR='a--'|LVM2_PV_ALLOCATABLE='allocatable'|LVM2_PV_EXPORTED=''|LVM2_PV_MISSING=''|LVM2_PV_PE_COUNT='953853'|LVM2_PV_PE_ALLOC_COUNT='953852'|LVM2_PV_TAGS=''|LVM2_PV_MDA_COUNT='1'|LVM2_PV_MDA_USED_COUNT='1'|LVM2_PV_BA_START='0 '|LVM2_PV_BA_SIZE='0 '|LVM2_PV_IN_USE='used'|LVM2_PV_DUPLICATE=''|LVM2_VG_NAME='data4'
  LVM2_PV_FMT='lvm2'|LVM2_PV_UUID='r3UW8H-pLz5-rpsn-GK2u-1kJE-GKsy-uOeoIz'|LVM2_DEV_SIZE='3.64t'|LVM2_PV_NAME='/dev/sdf1'|LVM2_PV_MAJOR='8'|LVM2_PV_MINOR='81'|LVM2_PV_MDA_FREE='0 '|LVM2_PV_MDA_SIZE='252.00k'|LVM2_PV_EXT_VSN='2'|LVM2_PE_START='256.00k'|LVM2_PV_SIZE='3.64t'|LVM2_PV_FREE='4.00m'|LVM2_PV_USED='3.64t'|LVM2_PV_ATTR='a--'|LVM2_PV_ALLOCATABLE='allocatable'|LVM2_PV_EXPORTED=''|LVM2_PV_MISSING=''|LVM2_PV_PE_COUNT='953853'|LVM2_PV_PE_ALLOC_COUNT='953852'|LVM2_PV_TAGS=''|LVM2_PV_MDA_COUNT='1'|LVM2_PV_MDA_USED_COUNT='1'|LVM2_PV_BA_START='0 '|LVM2_PV_BA_SIZE='0 '|LVM2_PV_IN_USE='used'|LVM2_PV_DUPLICATE=''|LVM2_VG_NAME='data5'
  LVM2_PV_FMT='lvm2'|LVM2_PV_UUID='oZtJSv-HM9w-4She-1TU0-Z31G-dgKX-liJNID'|LVM2_DEV_SIZE='3.64t'|LVM2_PV_NAME='/dev/sdg1'|LVM2_PV_MAJOR='8'|LVM2_PV_MINOR='97'|LVM2_PV_MDA_FREE='0 '|LVM2_PV_MDA_SIZE='252.00k'|LVM2_PV_EXT_VSN='2'|LVM2_PE_START='256.00k'|LVM2_PV_SIZE='3.64t'|LVM2_PV_FREE='4.00m'|LVM2_PV_USED='3.64t'|LVM2_PV_ATTR='a--'|LVM2_PV_ALLOCATABLE='allocatable'|LVM2_PV_EXPORTED=''|LVM2_PV_MISSING=''|LVM2_PV_PE_COUNT='953853'|LVM2_PV_PE_ALLOC_COUNT='953852'|LVM2_PV_TAGS=''|LVM2_PV_MDA_COUNT='1'|LVM2_PV_MDA_USED_COUNT='1'|LVM2_PV_BA_START='0 '|LVM2_PV_BA_SIZE='0 '|LVM2_PV_IN_USE='used'|LVM2_PV_DUPLICATE=''|LVM2_VG_NAME='data6'
  LVM2_PV_FMT='lvm2'|LVM2_PV_UUID='Ys0p6S-WJOW-TAZT-czmX-iOYq-0Tgg-v4cl0H'|LVM2_DEV_SIZE='3.64t'|LVM2_PV_NAME='/dev/sdh1'|LVM2_PV_MAJOR='8'|LVM2_PV_MINOR='113'|LVM2_PV_MDA_FREE='0 '|LVM2_PV_MDA_SIZE='252.00k'|LVM2_PV_EXT_VSN='2'|LVM2_PE_START='256.00k'|LVM2_PV_SIZE='3.64t'|LVM2_PV_FREE='4.00m'|LVM2_PV_USED='3.64t'|LVM2_PV_ATTR='a--'|LVM2_PV_ALLOCATABLE='allocatable'|LVM2_PV_EXPORTED=''|LVM2_PV_MISSING=''|LVM2_PV_PE_COUNT='953853'|LVM2_PV_PE_ALLOC_COUNT='953852'|LVM2_PV_TAGS=''|LVM2_PV_MDA_COUNT='1'|LVM2_PV_MDA_USED_COUNT='1'|LVM2_PV_BA_START='0 '|LVM2_PV_BA_SIZE='0 '|LVM2_PV_IN_USE='used'|LVM2_PV_DUPLICATE=''|LVM2_VG_NAME='data7'
""".strip()   # noqa: W291

VGS_HEADINGS = """
  WARNING: Locking disabled. Be careful! This could corrupt your metadata.
  VG              Attr   Ext   #PV #LV #SN VSize VFree VG UUID                                VProfile #VMda VMdaFree  VMdaSize  #VMdaUse VG Tags
  data1           wz--n- 4.00m   1   3   0 3.64t 4.00m cYvfbB-tIzb-d4yt-5AFp-wM66-IBRx-JxF0zp              1        0    252.00k        1        
  data2           wz--n- 4.00m   1   3   0 3.64t 4.00m kdziV0-Xoh0-9al9-5E9N-1WU3-qCoH-v96zbG              1        0    252.00k        1        
  data3           wz--n- 4.00m   1   3   0 3.64t 4.00m rZUP2i-zoTb-HbrL-Ehk1-6kEr-Km20-UrbZfn              1        0    252.00k        1        
  data4           wz--n- 4.00m   1   3   0 3.64t 4.00m 6eCaHM-Yaoj-A2vy-V12P-mA0x-l6Hf-WwTlz0              1        0    252.00k        1        
  data5           wz--n- 4.00m   1   3   0 3.64t 4.00m tcu5Ur-WtaF-0fES-LEQE-YzVi-WYYU-iTyEDT              1        0    252.00k        1        
  data6           wz--n- 4.00m   1   3   0 3.64t 4.00m ey8e3g-BkbG-u877-TVQW-S7df-hsF9-D6BkCe              1        0    252.00k        1        
  data7           wz--n- 4.00m   1   3   0 3.64t 4.00m r58iLs-sYla-lC4h-UURW-bZOG-P2Yd-lambpM              1        0    252.00k        1        
  rhel_ceehadoop1 wz--n- 4.00m   1   5   0 3.63t    0  IIfj5y-6deS-aBaO-M4no-sQUg-0UEU-wo0IFM              1        0   1020.00k        1        
    Reloading config files
    Wiping internal VG cache
""".strip()   # noqa: W291

VGS_NO_HEADINGS = """
  WARNING: Locking disabled. Be careful! This could corrupt your metadata.
  LVM2_VG_FMT='lvm2'|LVM2_VG_UUID='cYvfbB-tIzb-d4yt-5AFp-wM66-IBRx-JxF0zp'|LVM2_VG_NAME='data1'|LVM2_VG_ATTR='wz--n-'|LVM2_VG_PERMISSIONS='writeable'|LVM2_VG_EXTENDABLE='extendable'|LVM2_VG_EXPORTED=''|LVM2_VG_PARTIAL=''|LVM2_VG_ALLOCATION_POLICY='normal'|LVM2_VG_CLUSTERED=''|LVM2_VG_SIZE='3.64t'|LVM2_VG_FREE='4.00m'|LVM2_VG_SYSID=''|LVM2_VG_SYSTEMID=''|LVM2_VG_LOCK_TYPE=''|LVM2_VG_LOCK_ARGS=''|LVM2_VG_EXTENT_SIZE='4.00m'|LVM2_VG_EXTENT_COUNT='953853'|LVM2_VG_FREE_COUNT='1'|LVM2_MAX_LV='0'|LVM2_MAX_PV='0'|LVM2_PV_COUNT='1'|LVM2_VG_MISSING_PV_COUNT='0'|LVM2_LV_COUNT='3'|LVM2_SNAP_COUNT='0'|LVM2_VG_SEQNO='8'|LVM2_VG_TAGS=''|LVM2_VG_PROFILE=''|LVM2_VG_MDA_COUNT='1'|LVM2_VG_MDA_USED_COUNT='1'|LVM2_VG_MDA_FREE='0 '|LVM2_VG_MDA_SIZE='252.00k'|LVM2_VG_MDA_COPIES='unmanaged'
  LVM2_VG_FMT='lvm2'|LVM2_VG_UUID='kdziV0-Xoh0-9al9-5E9N-1WU3-qCoH-v96zbG'|LVM2_VG_NAME='data2'|LVM2_VG_ATTR='wz--n-'|LVM2_VG_PERMISSIONS='writeable'|LVM2_VG_EXTENDABLE='extendable'|LVM2_VG_EXPORTED=''|LVM2_VG_PARTIAL=''|LVM2_VG_ALLOCATION_POLICY='normal'|LVM2_VG_CLUSTERED=''|LVM2_VG_SIZE='3.64t'|LVM2_VG_FREE='4.00m'|LVM2_VG_SYSID=''|LVM2_VG_SYSTEMID=''|LVM2_VG_LOCK_TYPE=''|LVM2_VG_LOCK_ARGS=''|LVM2_VG_EXTENT_SIZE='4.00m'|LVM2_VG_EXTENT_COUNT='953853'|LVM2_VG_FREE_COUNT='1'|LVM2_MAX_LV='0'|LVM2_MAX_PV='0'|LVM2_PV_COUNT='1'|LVM2_VG_MISSING_PV_COUNT='0'|LVM2_LV_COUNT='3'|LVM2_SNAP_COUNT='0'|LVM2_VG_SEQNO='8'|LVM2_VG_TAGS=''|LVM2_VG_PROFILE=''|LVM2_VG_MDA_COUNT='1'|LVM2_VG_MDA_USED_COUNT='1'|LVM2_VG_MDA_FREE='0 '|LVM2_VG_MDA_SIZE='252.00k'|LVM2_VG_MDA_COPIES='unmanaged'
  LVM2_VG_FMT='lvm2'|LVM2_VG_UUID='rZUP2i-zoTb-HbrL-Ehk1-6kEr-Km20-UrbZfn'|LVM2_VG_NAME='data3'|LVM2_VG_ATTR='wz--n-'|LVM2_VG_PERMISSIONS='writeable'|LVM2_VG_EXTENDABLE='extendable'|LVM2_VG_EXPORTED=''|LVM2_VG_PARTIAL=''|LVM2_VG_ALLOCATION_POLICY='normal'|LVM2_VG_CLUSTERED=''|LVM2_VG_SIZE='3.64t'|LVM2_VG_FREE='4.00m'|LVM2_VG_SYSID=''|LVM2_VG_SYSTEMID=''|LVM2_VG_LOCK_TYPE=''|LVM2_VG_LOCK_ARGS=''|LVM2_VG_EXTENT_SIZE='4.00m'|LVM2_VG_EXTENT_COUNT='953853'|LVM2_VG_FREE_COUNT='1'|LVM2_MAX_LV='0'|LVM2_MAX_PV='0'|LVM2_PV_COUNT='1'|LVM2_VG_MISSING_PV_COUNT='0'|LVM2_LV_COUNT='3'|LVM2_SNAP_COUNT='0'|LVM2_VG_SEQNO='8'|LVM2_VG_TAGS=''|LVM2_VG_PROFILE=''|LVM2_VG_MDA_COUNT='1'|LVM2_VG_MDA_USED_COUNT='1'|LVM2_VG_MDA_FREE='0 '|LVM2_VG_MDA_SIZE='252.00k'|LVM2_VG_MDA_COPIES='unmanaged'
  LVM2_VG_FMT='lvm2'|LVM2_VG_UUID='6eCaHM-Yaoj-A2vy-V12P-mA0x-l6Hf-WwTlz0'|LVM2_VG_NAME='data4'|LVM2_VG_ATTR='wz--n-'|LVM2_VG_PERMISSIONS='writeable'|LVM2_VG_EXTENDABLE='extendable'|LVM2_VG_EXPORTED=''|LVM2_VG_PARTIAL=''|LVM2_VG_ALLOCATION_POLICY='normal'|LVM2_VG_CLUSTERED=''|LVM2_VG_SIZE='3.64t'|LVM2_VG_FREE='4.00m'|LVM2_VG_SYSID=''|LVM2_VG_SYSTEMID=''|LVM2_VG_LOCK_TYPE=''|LVM2_VG_LOCK_ARGS=''|LVM2_VG_EXTENT_SIZE='4.00m'|LVM2_VG_EXTENT_COUNT='953853'|LVM2_VG_FREE_COUNT='1'|LVM2_MAX_LV='0'|LVM2_MAX_PV='0'|LVM2_PV_COUNT='1'|LVM2_VG_MISSING_PV_COUNT='0'|LVM2_LV_COUNT='3'|LVM2_SNAP_COUNT='0'|LVM2_VG_SEQNO='8'|LVM2_VG_TAGS=''|LVM2_VG_PROFILE=''|LVM2_VG_MDA_COUNT='1'|LVM2_VG_MDA_USED_COUNT='1'|LVM2_VG_MDA_FREE='0 '|LVM2_VG_MDA_SIZE='252.00k'|LVM2_VG_MDA_COPIES='unmanaged'
  LVM2_VG_FMT='lvm2'|LVM2_VG_UUID='tcu5Ur-WtaF-0fES-LEQE-YzVi-WYYU-iTyEDT'|LVM2_VG_NAME='data5'|LVM2_VG_ATTR='wz--n-'|LVM2_VG_PERMISSIONS='writeable'|LVM2_VG_EXTENDABLE='extendable'|LVM2_VG_EXPORTED=''|LVM2_VG_PARTIAL=''|LVM2_VG_ALLOCATION_POLICY='normal'|LVM2_VG_CLUSTERED=''|LVM2_VG_SIZE='3.64t'|LVM2_VG_FREE='4.00m'|LVM2_VG_SYSID=''|LVM2_VG_SYSTEMID=''|LVM2_VG_LOCK_TYPE=''|LVM2_VG_LOCK_ARGS=''|LVM2_VG_EXTENT_SIZE='4.00m'|LVM2_VG_EXTENT_COUNT='953853'|LVM2_VG_FREE_COUNT='1'|LVM2_MAX_LV='0'|LVM2_MAX_PV='0'|LVM2_PV_COUNT='1'|LVM2_VG_MISSING_PV_COUNT='0'|LVM2_LV_COUNT='3'|LVM2_SNAP_COUNT='0'|LVM2_VG_SEQNO='8'|LVM2_VG_TAGS=''|LVM2_VG_PROFILE=''|LVM2_VG_MDA_COUNT='1'|LVM2_VG_MDA_USED_COUNT='1'|LVM2_VG_MDA_FREE='0 '|LVM2_VG_MDA_SIZE='252.00k'|LVM2_VG_MDA_COPIES='unmanaged'
  LVM2_VG_FMT='lvm2'|LVM2_VG_UUID='ey8e3g-BkbG-u877-TVQW-S7df-hsF9-D6BkCe'|LVM2_VG_NAME='data6'|LVM2_VG_ATTR='wz--n-'|LVM2_VG_PERMISSIONS='writeable'|LVM2_VG_EXTENDABLE='extendable'|LVM2_VG_EXPORTED=''|LVM2_VG_PARTIAL=''|LVM2_VG_ALLOCATION_POLICY='normal'|LVM2_VG_CLUSTERED=''|LVM2_VG_SIZE='3.64t'|LVM2_VG_FREE='4.00m'|LVM2_VG_SYSID=''|LVM2_VG_SYSTEMID=''|LVM2_VG_LOCK_TYPE=''|LVM2_VG_LOCK_ARGS=''|LVM2_VG_EXTENT_SIZE='4.00m'|LVM2_VG_EXTENT_COUNT='953853'|LVM2_VG_FREE_COUNT='1'|LVM2_MAX_LV='0'|LVM2_MAX_PV='0'|LVM2_PV_COUNT='1'|LVM2_VG_MISSING_PV_COUNT='0'|LVM2_LV_COUNT='3'|LVM2_SNAP_COUNT='0'|LVM2_VG_SEQNO='8'|LVM2_VG_TAGS=''|LVM2_VG_PROFILE=''|LVM2_VG_MDA_COUNT='1'|LVM2_VG_MDA_USED_COUNT='1'|LVM2_VG_MDA_FREE='0 '|LVM2_VG_MDA_SIZE='252.00k'|LVM2_VG_MDA_COPIES='unmanaged'
  LVM2_VG_FMT='lvm2'|LVM2_VG_UUID='r58iLs-sYla-lC4h-UURW-bZOG-P2Yd-lambpM'|LVM2_VG_NAME='data7'|LVM2_VG_ATTR='wz--n-'|LVM2_VG_PERMISSIONS='writeable'|LVM2_VG_EXTENDABLE='extendable'|LVM2_VG_EXPORTED=''|LVM2_VG_PARTIAL=''|LVM2_VG_ALLOCATION_POLICY='normal'|LVM2_VG_CLUSTERED=''|LVM2_VG_SIZE='3.64t'|LVM2_VG_FREE='4.00m'|LVM2_VG_SYSID=''|LVM2_VG_SYSTEMID=''|LVM2_VG_LOCK_TYPE=''|LVM2_VG_LOCK_ARGS=''|LVM2_VG_EXTENT_SIZE='4.00m'|LVM2_VG_EXTENT_COUNT='953853'|LVM2_VG_FREE_COUNT='1'|LVM2_MAX_LV='0'|LVM2_MAX_PV='0'|LVM2_PV_COUNT='1'|LVM2_VG_MISSING_PV_COUNT='0'|LVM2_LV_COUNT='3'|LVM2_SNAP_COUNT='0'|LVM2_VG_SEQNO='8'|LVM2_VG_TAGS=''|LVM2_VG_PROFILE=''|LVM2_VG_MDA_COUNT='1'|LVM2_VG_MDA_USED_COUNT='1'|LVM2_VG_MDA_FREE='0 '|LVM2_VG_MDA_SIZE='252.00k'|LVM2_VG_MDA_COPIES='unmanaged'
  LVM2_VG_FMT='lvm2'|LVM2_VG_UUID='IIfj5y-6deS-aBaO-M4no-sQUg-0UEU-wo0IFM'|LVM2_VG_NAME='rhel_ceehadoop1'|LVM2_VG_ATTR='wz--n-'|LVM2_VG_PERMISSIONS='writeable'|LVM2_VG_EXTENDABLE='extendable'|LVM2_VG_EXPORTED=''|LVM2_VG_PARTIAL=''|LVM2_VG_ALLOCATION_POLICY='normal'|LVM2_VG_CLUSTERED=''|LVM2_VG_SIZE='3.63t'|LVM2_VG_FREE='0 '|LVM2_VG_SYSID=''|LVM2_VG_SYSTEMID=''|LVM2_VG_LOCK_TYPE=''|LVM2_VG_LOCK_ARGS=''|LVM2_VG_EXTENT_SIZE='4.00m'|LVM2_VG_EXTENT_COUNT='952831'|LVM2_VG_FREE_COUNT='0'|LVM2_MAX_LV='0'|LVM2_MAX_PV='0'|LVM2_PV_COUNT='1'|LVM2_VG_MISSING_PV_COUNT='0'|LVM2_LV_COUNT='5'|LVM2_SNAP_COUNT='0'|LVM2_VG_SEQNO='6'|LVM2_VG_TAGS=''|LVM2_VG_PROFILE=''|LVM2_VG_MDA_COUNT='1'|LVM2_VG_MDA_USED_COUNT='1'|LVM2_VG_MDA_FREE='0 '|LVM2_VG_MDA_SIZE='1020.00k'|LVM2_VG_MDA_COPIES='unmanaged'
""".strip()   # noqa: W291

PRIMARY_DATA = [
    {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'name_key': 'xyz'},
    {'a': None, 'b': 12, 'c': 13, 'd': 14, 'name_key': 'qrs'},
    {'a': None, 'b': 12, 'c': 13, 'd': 14, 'f': '', 'name_key': 'def'}
]

PRIMARY_KEY_DATA = {
    'xyz': {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'name_key': 'xyz'},
    'qrs': {'a': None, 'b': 12, 'c': 13, 'd': 14, 'name_key': 'qrs'},
    'def': {'a': None, 'b': 12, 'c': 13, 'd': 14, 'f': '', 'name_key': 'def'}
}

SECONDARY_DATA = [
    {'a': 31, 'e': 33, 'name_key': 'xyz'},
    {'a': 11, 'e': 23, 'name_key': 'qrs'},
    {'a': 1, 'e': 3, 'name_key': 'ghi'}
]


class DataClass:
    def __init__(self):
        self.data = [PRIMARY_DATA, SECONDARY_DATA]


class ContentClass:
    def __init__(self):
        self.data = {'content': [PRIMARY_DATA, SECONDARY_DATA]}


def test_get_shared_data():
    data = lvm.get_shared_data(DataClass())
    assert data == [PRIMARY_DATA, SECONDARY_DATA]
    data = lvm.get_shared_data(ContentClass())
    assert data == [PRIMARY_DATA, SECONDARY_DATA]


def test_to_name_key_dict():
    assert lvm.to_name_key_dict(PRIMARY_DATA, 'name_key') == PRIMARY_KEY_DATA


def test_merge_lvm_data():
    combined = lvm.merge_lvm_data(PRIMARY_DATA, SECONDARY_DATA, 'name_key')
    assert combined == {
        'xyz': {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 33, 'name_key': 'xyz'},
        'qrs': {'a': 11, 'b': 12, 'c': 13, 'd': 14, 'e': 23, 'name_key': 'qrs'},
        'def': {'a': None, 'b': 12, 'c': 13, 'd': 14, 'f': None, 'name_key': 'def'},
        'ghi': {'a': 1, 'e': 3, 'name_key': 'ghi'}
    }


def test_set_defaults():
    assert lvm.set_defaults(PRIMARY_KEY_DATA) == {
        'xyz': {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'name_key': 'xyz'},
        'qrs': {'a': None, 'b': 12, 'c': 13, 'd': 14, 'name_key': 'qrs'},
        'def': {'a': None, 'b': 12, 'c': 13, 'd': 14, 'f': None, 'name_key': 'def'}
    }


@pytest.fixture
def lvm_data():
    vgs = Vgs(context_wrap(VGS_NO_HEADINGS))
    vgs_headings = VgsHeadings(context_wrap(VGS_HEADINGS))
    pvs = Pvs(context_wrap(PVS_NO_HEADINGS))
    pvs_headings = PvsHeadings(context_wrap(PVS_HEADINGS))
    lvs = Lvs(context_wrap(LVS_NO_HEADINGS))
    lvs_headings = LvsHeadings(context_wrap(LVS_HEADINGS))
    shared_list = [
        {Vgs: vgs, VgsHeadings: vgs_headings},
        {Vgs: vgs},
        {VgsHeadings: vgs_headings},
        {Pvs: pvs, PvsHeadings: pvs_headings},
        {Pvs: pvs},
        {PvsHeadings: pvs_headings},
        {Lvs: lvs, LvsHeadings: lvs_headings},
        {Lvs: lvs},
        {LvsHeadings: lvs_headings}
    ]
    LvmData = namedtuple('LvmData', ['lvm_info', 'shared'])
    yield [LvmData(Lvm(shared.get(Lvs),
                       shared.get(LvsHeadings),
                       shared.get(Pvs),
                       shared.get(PvsHeadings),
                       shared.get(Vgs),
                       shared.get(VgsHeadings)),
                   shared)
           for shared in shared_list]


def test_combiner_vgs(lvm_data):
    for data in lvm_data:
        if Vgs in data.shared or VgsHeadings in data.shared:
            lvm_info = data.lvm_info
            assert lvm_info.volume_groups is not None
            assert len(list(lvm_info.volume_groups)) == 8
            assert lvm_info.volume_groups['data7']['VG_UUID'] == 'r58iLs-sYla-lC4h-UURW-bZOG-P2Yd-lambpM'
            assert lvm_info.volume_group_names == set([
                'data1', 'data2', 'data3', 'data4', 'data5', 'data6', 'data7',
                'rhel_ceehadoop1'
            ])
            if Vgs in data.shared:
                assert lvm_info.volume_groups['data1']['VPerms'] == 'writeable'
            else:
                assert lvm_info.volume_groups['data1']['VPerms'] is None
            filtered_lvm_info = lvm_info.filter_volume_groups('data')
            assert set(filtered_lvm_info.keys()) == set([
                'data1', 'data2', 'data3', 'data4', 'data5', 'data6', 'data7'
            ])
            assert filtered_lvm_info['data7']['VG_UUID'] == 'r58iLs-sYla-lC4h-UURW-bZOG-P2Yd-lambpM'


def test_combiner_pvs(lvm_data):
    for data in lvm_data:
        if Pvs in data.shared or PvsHeadings in data.shared:
            lvm_info = data.lvm_info
            assert lvm_info.physical_volumes is not None
            assert len(list(lvm_info.physical_volumes)) == 31
            assert lvm_info.physical_volumes['/dev/sdh1+Ys0p6S-WJOW-TAZT-czmX-iOYq-0Tgg-v4cl0H']['VG'] == 'data7'
            assert lvm_info.physical_volume_names == set([
                '/dev/data1/lv_brick1',
                '/dev/data1/lv_hdfs1',
                '/dev/data2/lv_brick2',
                '/dev/data2/lv_hdfs2',
                '/dev/data3/lv_brick3',
                '/dev/data3/lv_hdfs3',
                '/dev/data4/lv_brick4',
                '/dev/data4/lv_hdfs4',
                '/dev/data5/lv_brick5',
                '/dev/data5/lv_hdfs5',
                '/dev/data6/lv_brick6',
                '/dev/data6/lv_hdfs6',
                '/dev/data7/lv_brick7',
                '/dev/data7/lv_hdfs7',
                '/dev/loop0',
                '/dev/loop1',
                '/dev/mapper/docker-253:3-100685290-pool',
                '/dev/rhel_ceehadoop1/home',
                '/dev/rhel_ceehadoop1/opt',
                '/dev/rhel_ceehadoop1/root',
                '/dev/rhel_ceehadoop1/swap',
                '/dev/rhel_ceehadoop1/var',
                '/dev/sda2',
                '/dev/sda3',
                '/dev/sdb1',
                '/dev/sdc1',
                '/dev/sdd1',
                '/dev/sde1',
                '/dev/sdf1',
                '/dev/sdg1',
                '/dev/sdh1'
            ])
            pv_sdg1 = lvm_info.filter_physical_volumes('/dev/sdg1')
            assert len(pv_sdg1) == 1
            pv_sdg1_key, pv_sdg1_values = pv_sdg1.popitem()
            assert '/dev/sdg1' in lvm_info.physical_volume_names
            if Pvs in data.shared:
                assert lvm_info.physical_volumes[pv_sdg1_key]['LVM2_PV_MINOR'] == '97'
                assert lvm_info.physical_volumes[pv_sdg1_key]['Missing'] is None
            else:
                assert 'LVM2_PV_MINOR' not in lvm_info.physical_volumes[pv_sdg1_key]
                assert lvm_info.physical_volumes[pv_sdg1_key]['Missing'] is None
            filtered_lvm_info = lvm_info.filter_physical_volumes('sda')
            assert set([p['PV'] for p in filtered_lvm_info.values()]) == set(['/dev/sda2', '/dev/sda3'])
            for pv in filtered_lvm_info.values():
                if pv['PV'] == '/dev/sda2':
                    assert pv['DevSize'] == '1.00g'


def test_combiner_lvs(lvm_data):
    for data in lvm_data:
        if Lvs in data.shared or LvsHeadings in data.shared:
            lvm_info = data.lvm_info
            assert lvm_info.logical_volumes is not None
            assert len(list(lvm_info.logical_volumes)) == 40
            pool7 = lvm_info.logical_volumes[Lvm.LvVgName(LV='pool7', VG='data7')]
            if Lvs in data.shared:
                assert pool7['LVM2_REGION_SIZE'] == '0'
                for k, v in LVS_NOHEADINGS_POOL7.items():
                    assert pool7[k] == v
            else:
                assert 'LVM2_REGION_SIZE' not in pool7
                assert pool7['Region'] is None
            if LvsHeadings in data.shared:
                for k, v in LVS_HEADINGS_POOL7.items():
                    assert pool7[k] == v
            assert lvm_info.logical_volume_names == set([
                Lvm.LvVgName(LV='lv_brick1', VG='data1'),
                Lvm.LvVgName(LV='lv_hdfs1', VG='data1'),
                Lvm.LvVgName(LV='pool1', VG='data1'),
                Lvm.LvVgName(LV='[pool1_tdata]', VG='data1'),
                Lvm.LvVgName(LV='[pool1_tmeta]', VG='data1'),
                Lvm.LvVgName(LV='lv_brick2', VG='data2'),
                Lvm.LvVgName(LV='lv_hdfs2', VG='data2'),
                Lvm.LvVgName(LV='pool2', VG='data2'),
                Lvm.LvVgName(LV='[pool2_tdata]', VG='data2'),
                Lvm.LvVgName(LV='[pool2_tmeta]', VG='data2'),
                Lvm.LvVgName(LV='lv_brick3', VG='data3'),
                Lvm.LvVgName(LV='lv_hdfs3', VG='data3'),
                Lvm.LvVgName(LV='pool3', VG='data3'),
                Lvm.LvVgName(LV='[pool3_tdata]', VG='data3'),
                Lvm.LvVgName(LV='[pool3_tmeta]', VG='data3'),
                Lvm.LvVgName(LV='lv_brick4', VG='data4'),
                Lvm.LvVgName(LV='lv_hdfs4', VG='data4'),
                Lvm.LvVgName(LV='pool4', VG='data4'),
                Lvm.LvVgName(LV='[pool4_tdata]', VG='data4'),
                Lvm.LvVgName(LV='[pool4_tmeta]', VG='data4'),
                Lvm.LvVgName(LV='lv_brick5', VG='data5'),
                Lvm.LvVgName(LV='lv_hdfs5', VG='data5'),
                Lvm.LvVgName(LV='pool5', VG='data5'),
                Lvm.LvVgName(LV='[pool5_tdata]', VG='data5'),
                Lvm.LvVgName(LV='[pool5_tmeta]', VG='data5'),
                Lvm.LvVgName(LV='lv_brick6', VG='data6'),
                Lvm.LvVgName(LV='lv_hdfs6', VG='data6'),
                Lvm.LvVgName(LV='pool6', VG='data6'),
                Lvm.LvVgName(LV='[pool6_tdata]', VG='data6'),
                Lvm.LvVgName(LV='[pool6_tmeta]', VG='data6'),
                Lvm.LvVgName(LV='lv_brick7', VG='data7'),
                Lvm.LvVgName(LV='lv_hdfs7', VG='data7'),
                Lvm.LvVgName(LV='pool7', VG='data7'),
                Lvm.LvVgName(LV='[pool7_tdata]', VG='data7'),
                Lvm.LvVgName(LV='[pool7_tmeta]', VG='data7'),
                Lvm.LvVgName(LV='home', VG='rhel_ceehadoop1'),
                Lvm.LvVgName(LV='opt', VG='rhel_ceehadoop1'),
                Lvm.LvVgName(LV='root', VG='rhel_ceehadoop1'),
                Lvm.LvVgName(LV='swap', VG='rhel_ceehadoop1'),
                Lvm.LvVgName(LV='var', VG='rhel_ceehadoop1'),
            ])
            filtered_lvm_info = lvm_info.filter_logical_volumes('pool7')
            for lv in filtered_lvm_info:
                assert lv.LV in ['pool7', '[pool7_tdata]', '[pool7_tmeta]']
            assert Lvm.LvVgName(LV='pool7', VG='data7') in filtered_lvm_info


@pytest.fixture
def lvm_data_all():
    vgsall = VgsAll(context_wrap(VGS_NO_HEADINGS))
    pvsall = PvsAll(context_wrap(PVS_NO_HEADINGS))
    lvsall = LvsAll(context_wrap(LVS_NO_HEADINGS))
    shared_list = [
        {VgsAll: vgsall},
        {PvsAll: pvsall},
        {LvsAll: lvsall},
    ]
    LvmData = namedtuple('LvmData', ['lvm_info', 'shared'])
    yield [LvmData(LvmAll(shared.get(LvsAll),
                          shared.get(PvsAll),
                          shared.get(VgsAll)),
                   shared)
           for shared in shared_list]


def test_combiner_vgsall(lvm_data_all):
    has_vgsall = False
    for data in lvm_data_all:
        if VgsAll in data.shared:
            has_vgsall = True
            lvm_info = data.lvm_info
            assert lvm_info.volume_groups is not None
            assert len(list(lvm_info.volume_groups)) == 8
            assert lvm_info.volume_groups['data7']['VG_UUID'] == 'r58iLs-sYla-lC4h-UURW-bZOG-P2Yd-lambpM'
            assert lvm_info.volume_group_names == set([
                'data1', 'data2', 'data3', 'data4', 'data5', 'data6', 'data7',
                'rhel_ceehadoop1'
            ])
            assert lvm_info.volume_groups['data1']['VPerms'] == 'writeable'
            filtered_lvm_info = lvm_info.filter_volume_groups('data')
            assert set(filtered_lvm_info.keys()) == set([
                'data1', 'data2', 'data3', 'data4', 'data5', 'data6', 'data7'
            ])
            assert filtered_lvm_info['data7']['VG_UUID'] == 'r58iLs-sYla-lC4h-UURW-bZOG-P2Yd-lambpM'
    assert has_vgsall


def test_combiner_pvsall(lvm_data_all):
    has_pvsall = False
    for data in lvm_data_all:
        if PvsAll in data.shared:
            has_pvsall = True
            lvm_info = data.lvm_info
            assert lvm_info.physical_volumes is not None
            assert len(list(lvm_info.physical_volumes)) == 31
            assert lvm_info.physical_volumes['/dev/sdh1+Ys0p6S-WJOW-TAZT-czmX-iOYq-0Tgg-v4cl0H']['VG'] == 'data7'
            assert lvm_info.physical_volume_names == set([
                '/dev/data1/lv_brick1',
                '/dev/data1/lv_hdfs1',
                '/dev/data2/lv_brick2',
                '/dev/data2/lv_hdfs2',
                '/dev/data3/lv_brick3',
                '/dev/data3/lv_hdfs3',
                '/dev/data4/lv_brick4',
                '/dev/data4/lv_hdfs4',
                '/dev/data5/lv_brick5',
                '/dev/data5/lv_hdfs5',
                '/dev/data6/lv_brick6',
                '/dev/data6/lv_hdfs6',
                '/dev/data7/lv_brick7',
                '/dev/data7/lv_hdfs7',
                '/dev/loop0',
                '/dev/loop1',
                '/dev/mapper/docker-253:3-100685290-pool',
                '/dev/rhel_ceehadoop1/home',
                '/dev/rhel_ceehadoop1/opt',
                '/dev/rhel_ceehadoop1/root',
                '/dev/rhel_ceehadoop1/swap',
                '/dev/rhel_ceehadoop1/var',
                '/dev/sda2',
                '/dev/sda3',
                '/dev/sdb1',
                '/dev/sdc1',
                '/dev/sdd1',
                '/dev/sde1',
                '/dev/sdf1',
                '/dev/sdg1',
                '/dev/sdh1'
            ])
            pv_sdg1 = lvm_info.filter_physical_volumes('/dev/sdg1')
            assert len(pv_sdg1) == 1
            pv_sdg1_key, pv_sdg1_values = pv_sdg1.popitem()
            assert '/dev/sdg1' in lvm_info.physical_volume_names
            assert lvm_info.physical_volumes[pv_sdg1_key]['LVM2_PV_MINOR'] == '97'
            assert lvm_info.physical_volumes[pv_sdg1_key]['Missing'] is None
            filtered_lvm_info = lvm_info.filter_physical_volumes('sda')
            assert set([p['PV'] for p in filtered_lvm_info.values()]) == set(['/dev/sda2', '/dev/sda3'])
            for pv in filtered_lvm_info.values():
                if pv['PV'] == '/dev/sda2':
                    assert pv['DevSize'] == '1.00g'
    assert has_pvsall


def test_combiner_lvsall(lvm_data_all):
    has_lvsall = False
    for data in lvm_data_all:
        if LvsAll in data.shared:
            has_lvsall = True
            lvm_info = data.lvm_info
            assert lvm_info.logical_volumes is not None
            assert len(list(lvm_info.logical_volumes)) == 40
            pool7 = lvm_info.logical_volumes[Lvm.LvVgName(LV='pool7', VG='data7')]
            assert pool7['LVM2_REGION_SIZE'] == '0'
            for k in LVS_NOHEADINGS_POOL7.keys():
                assert pool7[k] == LVS_NOHEADINGS_POOL7[k]
            assert lvm_info.logical_volume_names == set([
                LvmAll.LvVgName(LV='lv_brick1', VG='data1'),
                LvmAll.LvVgName(LV='lv_hdfs1', VG='data1'),
                LvmAll.LvVgName(LV='pool1', VG='data1'),
                LvmAll.LvVgName(LV='[pool1_tdata]', VG='data1'),
                LvmAll.LvVgName(LV='[pool1_tmeta]', VG='data1'),
                LvmAll.LvVgName(LV='lv_brick2', VG='data2'),
                LvmAll.LvVgName(LV='lv_hdfs2', VG='data2'),
                LvmAll.LvVgName(LV='pool2', VG='data2'),
                LvmAll.LvVgName(LV='[pool2_tdata]', VG='data2'),
                LvmAll.LvVgName(LV='[pool2_tmeta]', VG='data2'),
                LvmAll.LvVgName(LV='lv_brick3', VG='data3'),
                LvmAll.LvVgName(LV='lv_hdfs3', VG='data3'),
                LvmAll.LvVgName(LV='pool3', VG='data3'),
                LvmAll.LvVgName(LV='[pool3_tdata]', VG='data3'),
                LvmAll.LvVgName(LV='[pool3_tmeta]', VG='data3'),
                LvmAll.LvVgName(LV='lv_brick4', VG='data4'),
                LvmAll.LvVgName(LV='lv_hdfs4', VG='data4'),
                LvmAll.LvVgName(LV='pool4', VG='data4'),
                LvmAll.LvVgName(LV='[pool4_tdata]', VG='data4'),
                LvmAll.LvVgName(LV='[pool4_tmeta]', VG='data4'),
                LvmAll.LvVgName(LV='lv_brick5', VG='data5'),
                LvmAll.LvVgName(LV='lv_hdfs5', VG='data5'),
                LvmAll.LvVgName(LV='pool5', VG='data5'),
                LvmAll.LvVgName(LV='[pool5_tdata]', VG='data5'),
                LvmAll.LvVgName(LV='[pool5_tmeta]', VG='data5'),
                LvmAll.LvVgName(LV='lv_brick6', VG='data6'),
                LvmAll.LvVgName(LV='lv_hdfs6', VG='data6'),
                LvmAll.LvVgName(LV='pool6', VG='data6'),
                LvmAll.LvVgName(LV='[pool6_tdata]', VG='data6'),
                LvmAll.LvVgName(LV='[pool6_tmeta]', VG='data6'),
                LvmAll.LvVgName(LV='lv_brick7', VG='data7'),
                LvmAll.LvVgName(LV='lv_hdfs7', VG='data7'),
                LvmAll.LvVgName(LV='pool7', VG='data7'),
                LvmAll.LvVgName(LV='[pool7_tdata]', VG='data7'),
                LvmAll.LvVgName(LV='[pool7_tmeta]', VG='data7'),
                LvmAll.LvVgName(LV='home', VG='rhel_ceehadoop1'),
                LvmAll.LvVgName(LV='opt', VG='rhel_ceehadoop1'),
                LvmAll.LvVgName(LV='root', VG='rhel_ceehadoop1'),
                LvmAll.LvVgName(LV='swap', VG='rhel_ceehadoop1'),
                LvmAll.LvVgName(LV='var', VG='rhel_ceehadoop1'),
            ])
            filtered_lvm_info = lvm_info.filter_logical_volumes('pool7')
            for lv in filtered_lvm_info:
                assert lv.LV in ['pool7', '[pool7_tdata]', '[pool7_tmeta]']
            assert LvmAll.LvVgName(LV='pool7', VG='data7') in filtered_lvm_info
    assert has_lvsall
