import sys

import target as server
import examples.HTTP_server.socket2event as socket2event

#controller = server.Controller(sys.argv[1:])
controller = server.Controller("hello")
socket2event.boot_translation_service(controller)
controller.start()