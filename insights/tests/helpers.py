# -*- coding: utf-8 -*-

from threading import Timer
from multiprocessing import Process
from os import getenv
from requests import Session
from requests.adapters import BaseAdapter
from requests.exceptions import ConnectionError, ConnectTimeout
from time import sleep, time


class Timeout:
    """
    Runs a function for a limited amount of time. Reports whether it finished in time.
    """
    PRISTINE = 0
    RUNNING = 1
    SUCCESS = 2
    FAIL = 3
    TIMEOUT = 4

    def __init__(self):
        """
        New timeout service. self.state becomes PRISTINE.
        """
        self.reset()

    def reset(self):
        """
        Prepares the service for the next run, setting the state to PRISTINE.
        """
        self.state = self.PRISTINE

    def start(self, worker, timeout):
        """
        Spawns given function in a subprocess. Regularly checks whether it has finished or whether the set time-out has
        been reached. Sets self.state accordingly. Terminates the process on time-out.
        """
        def tick():
            """
            Relaunches itself every second until the process finishes or time runs out.
            """
            if not process.is_alive():
                self.state = self.FAIL if process.exitcode else self.SUCCESS
                return

            now = time()
            lapsed = now - started
            if lapsed > timeout:
                process.terminate()
                self.state = self.TIMEOUT
                return

            timer = Timer(1, tick)
            timer.start()
            timer.join()

        self.reset()

        process = Process(target=worker)
        process.start()
        started = time()
        self.state = self.RUNNING

        tick()


class DummyRequestsAdapter(BaseAdapter):
    """
    Emulates timeout behavior without making actual requests. Supports only simple numeric timeout values.
    """
    def send(self, request, **kwargs):
        if kwargs["timeout"] is not None:
            sleep(kwargs["timeout"])
            raise ConnectTimeout
        else:
            sleep(60)  # One minute, don't hang for eternity.
            raise ConnectionError

    def close(self):
        pass


def dummy_requests_session():
    """
    Mount our dummy adapter to every requests.Session instance created.
    """
    instance = Session()
    adapter = DummyRequestsAdapter()
    instance.mount("https://", adapter)  # All our requests are HTTPS.
    return instance


def getenv_bool(name, default=None):
    """
    Get a boolean value from an environment variable. Accepts only True or False.
    """
    env_string = getenv(name)
    if env_string == "True":
        bool_value = True
    elif env_string == "False":
        bool_value = False
    elif env_string is None:
        if default is None:
            raise ValueError("{0} must be set. Provide True/False.".format(name))
        bool_value = default
    else:
        raise ValueError("{0}={1} is not a valid value. Provide True/False.".format(name, env_string))
    return bool_value
