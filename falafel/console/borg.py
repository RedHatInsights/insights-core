class Borg:
    """
    The Borg design pattern, use to share the
    state between objects.
    It is similar to Singleton, but a lot
    simpler!
    Reference: http://www.aleax.it/5ep.html
    """

    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state
