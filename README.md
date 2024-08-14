# SCCD2DEVS
This project focuses on the conversion of SCCD XML files into a format compatible with PypDEVS, a Python implementation of the Parallel DEVS (PypDEVS) formalism. The SCCDXML format is commonly used for describing the configuration and behavior of complex systems, while pypDEVS provides a framework for modeling and simulating discrete-event systems.

In this thesis project, we explore the process of transforming SCCD XML files into pypDEVS models, enabling seamless integration of SCCD-based system descriptions into the PypDEVS simulation environment. By leveraging the capabilities of both SCCD and pypDEVS, we aim to facilitate the analysis and simulation of intricate systems, contributing to the advancement of modeling and simulation techniques in various domains.

A small documentation for the project can be found here, providing insights into the conversion methodology, implementation details, and examples of utilizing the converted models within the PypDEVS framework. Through this work, we endeavor to bridge the gap between SCCD-based system specifications and the pypDEVS simulation paradigm, fostering greater flexibility and efficiency in system analysis and design processes.

## Compiler
To compile a conforming SCCD XML file, the provided Python compiler can be used. The compiler can compile conforming SCCD models to two languages: Python and Javascript. Four platforms are supported:

- threads: Most basic platform. Runs the SCCD model on the main thread.
- eventloop: Works only in combination with a UI system that allows for scheduling events.
- gameloop: Works in combination with a game engine, which calls the update function of the controller at regular intervals.
- classicdevs (**NEW**): Classical Hierarchical DEVS, for simulating in discrete time.

The compiler can be used from the command line as follows:
```
$python -m sccd.compiler.sccdc --help
usage: python -m sccd.compiler.sccdc [-h] [-o OUTPUT] [-v VERBOSE]
                                     [-p PLATFORM] [-l LANGUAGE]
                                     input

positional arguments:
  input                 The path to the XML file to be compiled.

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        The path to the generated code. Defaults to the same
                        name as the input file but with matching extension.
  -v VERBOSE, --verbose VERBOSE
                        2 = all output; 1 = only warnings and errors; 0 = only
                        errors; -1 = no output. Defaults to 2.
  -p PLATFORM, --platform PLATFORM
                        Let the compiled code run on top of threads, gameloop
                        , eventloop or pypDEVS. The default is eventloop. PypDEVS is only supported for python
  -l LANGUAGE, --language LANGUAGE
                        Target language, either "javascript" or "python".
                        Defaults to the latter.
```

## The New Runtime Platform (classicdevs)
The ```classicdevs``` platform works only in the Python language. The platform works both with and without combination of a UI system that allows for scheduling events. Default implementations are provided for the Tkinter UI library on Python.

## Testing Framework
To check if the translation approach from SCCD constructs to classical, hierarchical DEVS constructs is good. 



## How to run?
For an example to be run, two files need to be provided: A runner file (usually called ```runner.py```) which will provide the necessary logic to execute a model and a SSCDXML file (.xml extension) which defines the model. To properly run an example, the following needs to be done:

First off, compile the SCCDXML file to a target file. This can be done with the following command:

```bash
python3 sccds.py -o "path_to_output_file" -p "classicdevs" "path_to_input_file"
```

This generic command can be adapted to a specific example by replacing the placeholders:

- `path_to_output_file`: Replace with the path where you want to save the output file.
- `path_to_input_file`: Replace with the path to the input file you are processing.

This will generate a target (python) file for the runner file to execute. 

A basic implementation of a DEVS execution file is the following:
```python
import target as target

if __name__ == '__main__':
	# Initialize the model
    model = target.Controller()
	# Create a simulator instance with the model
    sim = Simulator(model)   
	# Set the simulator to use Classic DEVS 
    sim.setClassicDEVS()   
	# Start the simulation     
    sim.simulate()             
```

This will run the simulation as fast as possible and will not transmit or receive events to/from the model. To make the simulation execute in real time an infinite loop can be provided in the runner file or the threading platform implemented in PypDEVS can be used. 

To receive events from the simulation, PypDEVS provides functionality which can easily be used in the runner file. A basic example printing all event to the terminal is given below: 
```python
def listen(self, events):
	for event in events:
		print(event)

if __name__ == '__main__':
	# Initialize the model
    model = target.Controller()
	# Create a simulator instance with the model
    sim = Simulator(model)   
	# Set the simulator to use Classic DEVS 
    sim.setClassicDEVS()

	# EXTRA: Add listener to the simulation
	# output_port should be replaced with the actual output 
	# port of the model.
	sim.setListenPorts(model.output_port, listen)

	# Start the simulation     
    sim.simulate()  

```

Transmitting event becomes a lot more complex as the user should know the id of the private port over which he wants to send the event, if he know this he has to sent over the general port with a realtime interrupt but keep the port of the event the private port. For example, if the user wants to sent to the following private port:
```
# TODO
```
The user needs to define the following realtime interrupt
```
# TODO
```
Of course a global input port can also be used. To simplify this, a new class is created which provides a wrapper around the simulator class of PypDEVS to automatically. A modeller needs to add the following to the runner file:
```python
import target as target
from sccd.runtime.DEVSSimulatorWrapper import DEVSSimulator

if __name__ == '__main__':
	model = target.Controller(name="controller")

	sim = DEVSSimulator(model)
	sim.simulate()
```
This will send the user defined events to the correct SCCD object.

Further all platforms provides in the PypDEVS package can be used to execute the model.

## Examples

### TrafficLight
The ```TrafficLight``` example is one of the most simple examples. This example illustrates the dynamics of the statechart in a SCCD class. The example defines one SCCD class with a corresponding statechart

### Timer

### BouncingBalls
The ```BouncingBalls``` example used Tkinter to simulate the behaviour of balls bouncing around in a window. A user can create a ball in the window by right clicking in the window field. The ball will be given a random velocity on the clicked position and will never leave the confines of the window. This creation of a ball illustrates the dynamic creation of SCCD classes and their corresponding statechart.

To further illustrate this, a button on the bottom of the window can be clicked to create a totally new window which will exexute its own logic independently from the other window. 

A window can also be deleted by clicking on the close window button on the top right of the screen. Visualizing the dynamic deletion of the earlier created SCCD classes.

### BouncingBallsCollision

### ElevatorBalls



## TODO
- [] Create elevator balls example
- [] Fix bug in narrow cast for testing framework
- [] Finish README
- [] Check paper
- [] Ask for deadline + presentation
- [] Check if tests are properly named
- [] Add examples to test (bouncing balls, predefine velocity)
- [] Send in paper, FINALLY!