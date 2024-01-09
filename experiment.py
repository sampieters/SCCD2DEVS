# Import code for model simulation:
from pypdevs.simulator import Simulator

# Import the model to be simulated
from sccd.compiler.sccdc import xmlToSccd
from sccdDEV import SCCD

#    ======================================================================

# 1. Instantiate the (Coupled or Atomic) DEVS at the root of the
#  hierarchical model. This effectively instantiates the whole model
#  thanks to the recursion in the DEVS model constructors (__init__).
#
sccdObject = xmlToSccd("input.xml")
sccdDEV = SCCD(sccdObject)

#    ======================================================================

# 2. Link the model to a DEVS Simulator:
#  i.e., create an instance of the 'Simulator' class,
#  using the model as a parameter.
sim = Simulator(sccdDEV)

#    ======================================================================

# 3. Perform all necessary configurations, the most commonly used are:

# A. Termination time (or termination condition)
#    Using a termination condition will execute a provided function at
#    every simulation step, making it possible to check for certain states
#    being reached.
#    It should return True to stop simulation, or Falso to continue.
#def terminate_whenStateIsReached(clock, model):
#    return model.trafficLight.state.get() == "manual"
#sim.setTerminationCondition(terminate_whenStateIsReached)

#    A termination time is prefered over a termination condition,
#    as it is much simpler to use.
#    e.g. to simulate until simulation time 400.0 is reached
sim.setTerminationTime(400.0)

# B. Set the use of a tracer to show what happened during the simulation run
#    Both writing to stdout or file is possible:
#    pass None for stdout, or a filename for writing to that file
sim.setVerbose("Trace.txt")

# C. Use Classic DEVS instead of Parallel DEVS
#    If your model uses Classic DEVS, this configuration MUST be set as
#    otherwise errors are guaranteed to happen.
#    Without this option, events will be remapped and the select function
#    will never be called.
sim.setClassicDEVS()

#    ======================================================================

# 4. Simulate the model
sim.simulate()

#    ======================================================================

# 5. (optional) Extract data from the simulated model
print("Simulation terminated")