# Import the model to be simulated
from sccd.compiler.sccdc import xmlToSccd


def build_statechart(root, statechart_string=""):
    if root.is_parallel_state:
        for child in root.children:
            statechart_string += build_statechart(child)
        statechart_string += f"{root.full_name} = ParallelState(["
        for child in root.children:
            statechart_string += child.full_name + ", "
        statechart_string = statechart_string[:-2]
        statechart_string += f"])\n"
    elif root.is_composite:
        for child in root.children:
            statechart_string += build_statechart(child)

        statechart_string += f"{root.full_name} = CompositeState("
        for child in root.children:
            if child.new_full_name == root.initial:
                statechart_string += child.full_name
        statechart_string += f")\n"
    elif root.is_basic:
        statechart_string += f"{root.full_name} = State()\n"
    return statechart_string

def build_statechart_transitions(root, statechart_string=""):
    for child in root.children:
        statechart_string += build_statechart_transitions(child)
    for transition in root.transitions:
        statechart_string += f"Transition(None, {root.full_name}, {transition.target.target_nodes[0].full_name})\n"
    return statechart_string



sccdObject = xmlToSccd("../input.xml")
print("")
with open('output/DEVS.py', 'w') as file:
    file.write("from pypdevs.DEVS import *\n"
               "from pypdevs.infinity import INFINITY\n"
               "from ..statecharts_core import *")
    file.write(sccdObject.top.replace('\t', '') + "\n")

    # Define the Coupled DEVS
    file.write("\nclass SCCD(CoupledDEVS):\n"
               "\tdef __init__(self):\n"
               "\t\tCoupledDEVS.__init__(self)\n")

    file.write("\n")

    # Define in- and outports
    file.write("\t\tself.inports = []\n")
    file.write(f"\t\tfor inport in range({len(sccdObject.inports)}):\n")
    file.write(f"\t\t\tself.inports.append(self.addInPort())\n")
    file.write("\n")
    file.write("\t\tself.outports = []\n")
    file.write(f"\t\tfor outport in range({len(sccdObject.outports)}):\n")
    file.write(f"\t\t\tself.outports.append(self.addOutPort())\n")
    file.write("\n")

    # Define the atomic DEVS in the coupled DEVS
    for sccd_class in sccdObject.classes:
        file.write(f"\t\t{sccd_class.name.lower()} = self.addSubModel({sccd_class.name}())\n")

    file.write("\n")
    # Define the links between the classes
    for sccd_class in sccdObject.classes:
        for association in sccd_class.associations:
            file.write(f"\t\tself.connectPorts({sccd_class.name.lower()}.outport, {association.to_class.lower()}.inport)\n")

    for sccd_class in sccdObject.classes:
        # Define an instance state
        file.write(f"\n\nclass {sccd_class.name}State:\n")

        file.write("\tdef __init__(self")
        for constructor in sccd_class.constructors:
            for parameter in constructor.parameters:
                file.write(f", {parameter.identifier}")
                if parameter.default is not None:
                    file.write(f"= {parameter.default}")
        file.write(f"):")

        for constructor in sccd_class.constructors:
            file.write(f"{constructor.body.replace("\t\t\t\t", "\t\t")}")

        # Define user-defined Statechart model
        file.write("\n")
        statechart_model = build_statechart(sccd_class.statechart.root)
        statechart_model += build_statechart_transitions(sccd_class.statechart.root)
        statechart_model = "\t\t" + statechart_model.replace("\n", "\n\t\t")
        file.write(statechart_model)

        file.write("\n")
        # Define user-defined methods
        for method in sccd_class.methods:
            file.write(f"\tdef {method.name}(self):")
            file.write(method.body.replace("\t\t\t\t", "\t\t"))



        # Define all classes as atomic DEVS
        file.write(f"\n\nclass {sccd_class.name}(AtomicDEVS):\n"
                   f"\tdef __init__(self):\n"
                   f"\t\tAtomicDEVS.__init__(self)\n")

        # Define time to check
        if sccd_class == sccdObject.default_class:
            file.write(f"\t\tself.advance = 0\n")
        else:
            file.write(f"\t\tself.advance = INFINITY\n")

        # Define the state: statechart, methods, and parameters
        file.write(f"\t\tself.state = [")
        if sccd_class == sccdObject.default_class:
            # TODO: Parameters on initialization?
            file.write(f"{sccd_class.name}State()")
        file.write(f"]\n")

        file.write("\n")
        # Define DEVS methods
        file.write("\tdef timeAdvance(self):\n"
                   "\t\tpass\n")
        file.write("\tdef extTransition(self, inputs):\n"
                   "\t\tpass\n")
        file.write("\tdef intTransition(self):\n"
                   "\t\tpass\n")
        file.write("\tdef outputFnc(self):\n"
                   "\t\tpass\n")




print("File writing complete.")