import target as target
import os


class OutputListener:
	def add(self, event):
		if event.port == "ui":
			print(event.name, ":", event.parameters[0], "seconds")

if __name__ == '__main__':
	controller = target.Controller()
	controller.keep_running = False
	controller.addMyOwnOutputListener(OutputListener())
	
	# Get the directory where the currently running Python file is located
	current_file_directory = os.path.dirname(os.path.abspath(__file__))

	# Create the full path for the log file
	log_file_path = os.path.join(current_file_directory, "new_log.txt")

	# Set verbose to the log file path
	controller.setVerbose(log_file_path)

	controller.start()