import abc
from abc import abstractclassmethod

class OptProblem(object):
    """Base class for optimization problems"""

    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.dim = None
        self.lb = None
        self.ub = None
        self.n_f = None
        self.n_g = None

    def __check_input__(self, x):
        if len(x) != self.dim:
            raise ValueError("Dimension mismatch")

    @abstractclassmethod
    def eval(self, record): # pragma: no cover
        pass
