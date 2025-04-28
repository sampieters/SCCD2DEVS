from pypdevs.simulator import Simulator
import SmartHome

sim = Simulator(SmartHome.SmartHome("Home Of Sam"))
sim.setClassicDEVS()
sim.simulate()