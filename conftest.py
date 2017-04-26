def pytest_addoption(parser):
    parser.addoption("--runslow", action="store_true", default=False, help="run slow tests")
    parser.addoption("--smokey", action="store_true", default=False, help="run tests fast")
