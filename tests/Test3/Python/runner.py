import tests.Test3.Python.target as target

class OutputListener:
	def add(self, event):
		if event.port == "ui":
			print(event.name, event.parameters[0], ":", event.parameters[1], "seconds")

if __name__ == '__main__':
	controller = target.Controller()
	controller.keep_running = False
	controller.addMyOwnOutputListener(OutputListener())
	controller.setVerbose(None)
	controller.start()
