class State:
    def __init__(self):
        self.ancestors = []
        self.descendants = []
        self.descendant_bitmap = 0
        self.children = []
        self.parent = None
        self.enter = None
        self.exit = None
        self.default_state = None
        self.transitions = []
        self.history = []
        self.has_eventless_transitions = False

    def getEffectiveTargetStates(self):
        pass

    def fixTree(self):
        pass

    def addChild(self, child):
        self.children.append(child)

    def addTransition(self, transition):
        self.transitions.append(transition)

    def setEnter(self, enter):
        self.enter = enter

    def setExit(self, exit):
        self.exit = exit

class CompositeState(State):
    def __init__(self, start_state):
        State.__init__(self)


class HistoryState(State):
    def __init__(self, state_id, obj):
        State.__init__(self)


class ShallowHistoryState(HistoryState):
    def __init__(self, state_id, obj):
        HistoryState.__init__(self, state_id, obj)

    def getEffectiveTargetStates(self):
        pass


class DeepHistoryState(HistoryState):
    def __init__(self, state_id, obj):
        HistoryState.__init__(self, state_id, obj)

    def getEffectiveTargetStates(self):
        pass

class ParallelState(State):
    def __init__(self, state_id, obj):
        State.__init__(self)

    def getEffectiveTargetStates(self):
        pass


class Transition:
    def __init__(self, source, targets):
        self.guard = None
        self.action = None
        self.trigger = None
        self.source = source
        self.targets = targets
        self.enabled_event = None  # the event that enabled this transition
        self.optimize()

    def isEnabled(self, events):
        pass

    # @profile
    def fire(self):
        pass

    def __getEffectiveTargetStates(self):
        pass

    def __exitSet(self, targets):
        pass

    def __enterSet(self, targets):
        pass

    def setGuard(self, guard):
        self.guard = guard

    def setAction(self, action):
        self.action = action

    def setTrigger(self, trigger):
        self.trigger = trigger
        if self.trigger is None:
            self.source.has_eventless_transitions = True

    def optimize(self):
        pass

    def __repr__(self):
        return "Transition(%s, %s)" % (self.source, self.targets[0])