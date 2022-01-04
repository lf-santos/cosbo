import numpy as np
import math

import os 
from pathlib import Path
import sys
from dwsimopt.sim_opt import SimulationOptimization

from cosbo.utils import PATH2COSBO

# Define SimulationOptimization object and Automation2() instance in this scope to avoid problems
dir_path = PATH2COSBO #str(Path(os.getcwd()).parent.absolute())
# Getting DWSIM path from system path
for k,v in enumerate(os.environ['path'].split(';')):
    if v.find('\DWSIM')>-1:
        path2dwsim = os.path.join(v, '')
if path2dwsim == None:
    path2dwsim = "C:\\Users\\lfsfr\\AppData\\Local\\DWSIM7\\"   #insert manuall
# Loading DWSIM simulation into Python (Simulation object)
sim_smr = SimulationOptimization(dof=np.array([]), path2sim= os.path.join(dir_path, "examples\\SMR.dwxmz"), 
                    path2dwsim = path2dwsim)
sim_smr.savepath = os.path.join(dir_path, "examples\\SMR2.dwxmz")
sim_smr.add_refs()
# Instanciate automation manager object
from DWSIM.Automation import Automation2
if ('interf' not in locals()):    # create automation manager
    interf = Automation2()
# Connect simulation in sim.path2sim
sim_smr.connect(interf)

from pySOT.optimization_problems import OptimizationProblem
class SMR_optProblem(OptimizationProblem):

# from optimization_problems.optimization_problems import OptProblem
# class SMR_optProblem(OptProblem):
    
    def __init__(self):

        # Import dwsim-python data exchange interface (has to be after Automation2)
        from dwsimopt.py2dwsim import create_pddx, assign_pddx

        # Assign DoF:
        create_pddx( ["MR-1", "CompoundMassFlow", "Nitrogen", "kg/s"],    sim_smr, element="dof" )
        create_pddx( ["MR-1", "CompoundMassFlow", "Methane", "kg/s"],     sim_smr, element="dof" )
        create_pddx( ["MR-1", "CompoundMassFlow", "Ethane", "kg/s"],      sim_smr, element="dof" )
        create_pddx( ["MR-1", "CompoundMassFlow", "Propane", "kg/s"],     sim_smr, element="dof" )
        create_pddx( ["MR-1", "CompoundMassFlow", "Isopentane", "Pa"],    sim_smr, element="dof" )
        create_pddx( ["VALV-01", "OutletPressure", "Mixture", "Pa"],      sim_smr, element="dof" )
        create_pddx( ["COMP-1", "OutletPressure", "Mixture", "Pa"],       sim_smr, element="dof" )
        create_pddx( ["COOL-08", "OutletTemperature", "Mixture", "K"],    sim_smr, element="dof" )

        # Assign F
        create_pddx( ["Sum_W", "EnergyFlow", "Mixture", "kW"], sim_smr, element="fobj" )

        # adding constraints (g_i <= 0):
        g1 = create_pddx( ["MITA1-Calc", "OutputVariable", "mita", "°C"], sim_smr, element="constraint", assign=False )
        assign_pddx( lambda: 3-g1[0]() , ["MITA1-Calc", "OutputVariable", "mita", "°C"], sim_smr, element="constraint" )
        g2 = create_pddx( ["MITA2-Calc", "OutputVariable", "mita", "°C"], sim_smr, element="constraint", assign=False )
        assign_pddx( lambda: 3-g2[0]() , ["MITA2-Calc", "OutputVariable", "mita", "°C"], sim_smr, element="constraint" )

        # decision variables bounds
        x0 = np.array( [0.25/3600, 0.70/3600, 1.0/3600, 1.10/3600, 1.80/3600, 2.50e5, 50.00e5, -60+273.15] )
        bounds_raw = np.array( [0.5*np.asarray(x0), 1.5*np.asarray(x0)] )   # 50 % around base case
        bounds_raw[0][-1] = 153     # precool temperature low limit manually
        bounds_raw[1][-1] = 253     # precool temperature upper limit manually

        # regularizer calculation
        regularizer = np.zeros(x0.size)
        for i in range(len(regularizer)):
            regularizer[i] = 10**(-1*math.floor(math.log(x0[i],10))) # regularizer for magnitude order of 1e0

        # bounds regularized
        bounds_reg = regularizer*bounds_raw
        
        # objective and constraints lambda definitions
        f = lambda x: sim_smr.calculate_optProblem(np.asarray(x)/regularizer)[0:sim_smr.n_f]
        g = lambda x: sim_smr.calculate_optProblem(np.asarray(x)/regularizer)[sim_smr.n_f:(sim_smr.n_f+sim_smr.n_g)]

        # class properties and methods
        self.dim = len(x0)
        self.lb = bounds_reg[0,:]
        self.ub = bounds_reg[1,:]
        self.n_f = sim_smr.n_f
        self.n_g = sim_smr.n_g
        self.f = f
        self.g = g
        self.reg = regularizer
        self.int_var = np.array([])
        self.cont_var = np.arange(self.dim)
    

    def eval(self, x):
        self.__check_input__(x)
        results = np.array( [self.f(x), self.g(x)], dtype=object )

        if len(results[0]) != self.n_f:
            raise ValueError("Objective function dimension mismatch")
        
        if len(results[1]) != self.n_g:
            raise ValueError("Constraint dimension mismatch")

        results[1][results[1]>1] = 1
        results[1][results[1]<0] = 0
        results = sum( results[0], np.sum(results[1]) )

        return results