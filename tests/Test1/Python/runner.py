import tests.Test1.Python.target as target

if __name__ == '__main__':
	controller = target.Controller()
	controller.keep_running = False
	controller.setVerbose(None)
	controller.start()

	
