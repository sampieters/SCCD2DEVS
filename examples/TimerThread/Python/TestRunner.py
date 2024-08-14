import target as target
from sccd.runtime.statecharts_core import Event
import threading
import matplotlib.pyplot as plt

sim_time_data = []
act_time_data = []

if __name__ == '__main__':
    controller = target.Controller() 
    
    def raw_inputter():
        while 1:
            controller.addInput(Event(input(), "input", []))
    input_thread = threading.Thread(target=raw_inputter)
    input_thread.daemon = True
    input_thread.start()
    
    output_listener = controller.addOutputListener(["output"])

    def outputter():
        sim_time = 0
        act_time = 0
        while sim_time <= 3:
            event = output_listener.fetch(-1)

            sim_time = event.getParameters()[0] / 1000.0  # Convert from milliseconds to seconds
            act_time = event.getParameters()[1]
            
            # Append times to the lists
            sim_time_data.append(sim_time)
            act_time_data.append(act_time)
            

            print("SIMTIME: %.2fs" % (sim_time))
            print("ACTTIME: %.2fs" % (act_time))

        controller.stop()

    output_thread = threading.Thread(target=outputter)
    output_thread.daemon = True
    output_thread.start()
    
    controller.start()

    # Now plot the data in the main thread
    plt.figure(figsize=(10, 6))
    plt.plot(sim_time_data, label='SIMTIME (s)')
    plt.plot(act_time_data, label='ACTTIME (s)')
    plt.xlabel('Event Index')
    plt.ylabel('Time (s)')
    plt.title('Simulation Time vs. Actual Time (SCCD Python)')
    plt.legend()
    plt.grid(True)
    plt.show()