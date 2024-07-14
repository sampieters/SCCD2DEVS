import sys

import target as client
import examples.HTTP_client.socket2event as socket2event

controller = client.Controller(sys.argv[1:])
socket2event.boot_translation_service(controller)
controller.start()