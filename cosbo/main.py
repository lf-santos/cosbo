import numpy as np
import os

from optimization_problems.smr_problem import SMR_optProblem

import logging
import os.path

import numpy as np
from poap.controller import BasicWorkerThread, ThreadController

from pySOT.experimental_design import SymmetricLatinHypercube
from pySOT.optimization_problems import Hartmann6
from pySOT.strategy import LCBStrategy, SOPStrategy
from pySOT.surrogate import GPRegressor
from pySOT.surrogate import CubicKernel, LinearTail, RBFInterpolant

def main():
    if not os.path.exists("./logfiles"):
        os.makedirs("logfiles")
    if os.path.exists("./logfiles/example_lower_confidence_bounds.log"):
        os.remove("./logfiles/example_lower_confidence_bounds.log")
    logging.basicConfig(filename="./logfiles/example_lower_confidence_bounds.log", level=logging.INFO)

    num_threads = 1
    max_evals = 80

    smr1 = SMR_optProblem()
    gp = GPRegressor(dim=smr1.dim, lb=smr1.lb, ub=smr1.ub)
    rbf = RBFInterpolant(dim=smr1.dim, lb=smr1.lb, ub=smr1.ub, kernel=CubicKernel(), tail=LinearTail(smr1.dim))
    slhd = SymmetricLatinHypercube(dim=smr1.dim, num_pts=10 * (smr1.dim + 1))

    # Create a strategy and a controller
    controller = ThreadController()
    # controller.strategy = LCBStrategy(
    #     max_evals=max_evals, opt_prob=smr1, exp_design=slhd, surrogate=gp, asynchronous=True
    # )
    controller.strategy = SOPStrategy(
        max_evals=max_evals,
        opt_prob=smr1,
        exp_design=slhd,
        surrogate=rbf,
        asynchronous=False,
        ncenters=num_threads,
        batch_size=num_threads,
    )

    print("Number of threads: {}".format(num_threads))
    print("Maximum number of evaluations: {}".format(max_evals))
    print("Strategy: {}".format(controller.strategy.__class__.__name__))
    print("Experimental design: {}".format(slhd.__class__.__name__))
    print("Surrogate: {}".format(gp.__class__.__name__))

    # Launch the threads and give them access to the objective function
    for _ in range(num_threads):
        worker = BasicWorkerThread(controller, smr1.eval)
        controller.launch_worker(worker)

    # Run the optimization strategy
    result = controller.run()

    print("Best value found: {0}".format(result.value))
    print(
        "Best solution found: {0}\n".format(
            np.array_str(result.params[0], max_line_width=np.inf, precision=5, suppress_small=True)
        )
    )
    
def main2():
    smr1 = SMR_optProblem()
    x0 = np.array( [0.25/3600, 0.70/3600, 1.0/3600, 1.10/3600, 1.80/3600, 2.50e5, 50.00e5, -60+273.15] )*smr1.reg
    print(smr1.eval(1.0*x0))

if __name__ == "__main__":
    main2()
