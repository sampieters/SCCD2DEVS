import target as target
from sccd.runtime.DEVSSimulatorWrapper import DEVSSimulator
import matplotlib.pyplot as plt

sim_time_data = [0]
act_time_data = [0]

class OutputListener:
	def add(self, events):
		for event in events:
			sim_time = event.getParameters()[0] / 1000.0  # Convert from milliseconds to seconds
			act_time = event.getParameters()[1]

			# Append times to the lists
			sim_time_data.append(sim_time)
			act_time_data.append(act_time)
		
            

if __name__ == '__main__':
	model = target.Controller(name="controller")

	sim = DEVSSimulator(model)
	sim.setRealTime()

	listener = OutputListener()
	sim.setListenPorts(model.out_output, listener.add)
	sim.simulate()

	while sim_time_data[-1] <= 3:
		pass

	# Now plot the data in the main thread
	plt.figure(figsize=(10, 6))
	plt.plot(sim_time_data, label='SIMTIME (s)')
	plt.plot(act_time_data, label='ACTTIME (s)')
	plt.xlabel('Event Index')
	plt.ylabel('Time (s)')
	plt.title('Simulation Time vs. Actual Time (SCCD DEVS)')
	plt.legend()
	plt.grid(True)
	plt.show()

