'''
Module responsible for running the --support option for collecting debug information
'''
from __future__ import absolute_import
import logging
import shlex
import re
import os
import requests
import tempfile
import time
import subprocess
from insights import get_nvr
from subprocess import Popen, PIPE, STDOUT

from .constants import InsightsConstants as constants
from .connection import InsightsConnection
from .utilities import write_registered_file, write_unregistered_file

APP_NAME = constants.app_name
logger = logging.getLogger(__name__)


def _legacy_registration_check(pconn):
    # check local registration record
    unreg_date = None
    unreachable = False
    if os.path.isfile(constants.registered_files[0]):
        local_record = 'System is registered locally via .registered file.'
        with open(constants.registered_files[0]) as reg_file:
            local_record += ' Registered at ' + reg_file.readline()
    else:
        local_record = 'System is NOT registered locally via .registered file.'
    if os.path.isfile(constants.unregistered_files[0]):
        with open(constants.unregistered_files[0]) as reg_file:
            local_record += ' Unregistered at ' + reg_file.readline()

    api_reg_status = pconn.api_registration_check()
    logger.debug('Registration status: %s', api_reg_status)
    if type(api_reg_status) is bool:
        if api_reg_status:
            api_record = 'Insights API confirms registration.'
        else:
            api_record = 'Insights API could not be reached to confirm registration status.'
            unreachable = True
    elif api_reg_status is None:
        api_record = 'Insights API says this machine is NOT registered.'
        api_reg_status = False
    else:
        api_record = 'Insights API says this machine was unregistered at ' + api_reg_status
        unreg_date = api_reg_status
        api_reg_status = False

    return {'messages': [local_record, api_record],
            'status': api_reg_status,
            'unreg_date': unreg_date,
            'unreachable': unreachable}


def registration_check(pconn):
    if pconn.config.legacy_upload:
        return _legacy_registration_check(pconn)
    status = pconn.api_registration_check()
    if status:
        write_registered_file()
    else:
        write_unregistered_file()
    return status


class InsightsSupport(object):
    '''
    Build the support logfile
    '''
    def __init__(self, config):
        self.config = config

    def collect_support_info(self):
        logger.info('Collecting logs...')
        self._support_diag_dump()
        logger.info('Copying Insights logs to archive...')
        log_archive_dir = tempfile.mkdtemp(prefix='/var/tmp/')
        tar_file = os.path.join(log_archive_dir,
                                'insights-client-logs-' +
                                time.strftime('%Y%m%d%H%M%S') +
                                '.tar.gz')
        tar_cmd = 'tar czfS {0} -C {1} .'.format(
            tar_file,
            constants.log_dir)
        subprocess.call(shlex.split(tar_cmd),
                        stderr=subprocess.PIPE)
        logger.info('Support information collected in %s', tar_file)

    def _support_diag_dump(self):
        '''
        Collect log info for debug
        '''
        # check insights config
        cfg_block = []

        pconn = InsightsConnection(self.config)
        logger.info('Insights version: %s', get_nvr())

        reg_check = registration_check(pconn)
        cfg_block.append('Registration check:')
        for key in reg_check:
            cfg_block.append(key + ': ' + str(reg_check[key]))

        lastupload = 'never'
        if os.path.isfile(constants.lastupload_file):
            with open(constants.lastupload_file) as upl_file:
                lastupload = upl_file.readline().strip()
        cfg_block.append('\nLast successful upload was ' + lastupload)

        cfg_block.append('auto_config: ' + str(self.config.auto_config))
        if self.config.proxy:
            obfuscated_proxy = re.sub(r'(.*)(:)(.*)(@.*)',
                                      r'\1\2********\4',
                                      self.config.proxy)
        else:
            obfuscated_proxy = 'None'
        cfg_block.append('proxy: ' + obfuscated_proxy)

        logger.info('\n'.join(cfg_block))
        logger.info('python-requests: %s', requests.__version__)

        succ = pconn.test_connection()
        if succ == 0:
            logger.info('Connection test: PASS\n')
        else:
            logger.info('Connection test: FAIL\n')

        # run commands
        commands = ['uname -a',
                    'cat /etc/redhat-release',
                    'env',
                    'sestatus',
                    'subscription-manager identity',
                    'systemctl cat insights-client.timer',
                    'systemctl cat insights-client.service',
                    'systemctl status insights-client.timer',
                    'systemctl status insights-client.service']
        for cmd in commands:
            logger.info("Running command: %s", cmd)
            try:
                proc = Popen(
                    shlex.split(cmd), shell=False, stdout=PIPE, stderr=STDOUT,
                    close_fds=True)
                stdout, stderr = proc.communicate()
            except OSError as o:
                if 'systemctl' not in cmd:
                    # suppress output for systemctl cmd failures
                    logger.info('Error running command "%s": %s', cmd, o)
            except Exception as e:
                # unknown error
                logger.info("Process failed: %s", e)
            logger.info("Process output: \n%s", stdout)
        # check available disk space for /var/tmp
        tmp_dir = '/var/tmp'
        dest_dir_stat = os.statvfs(tmp_dir)
        dest_dir_size = (dest_dir_stat.f_bavail * dest_dir_stat.f_frsize)
        logger.info('Available space in %s:\t%s bytes\t%.1f 1K-blocks\t%.1f MB',
                    tmp_dir, dest_dir_size,
                    dest_dir_size / 1024.0,
                    (dest_dir_size / 1024.0) / 1024.0)
