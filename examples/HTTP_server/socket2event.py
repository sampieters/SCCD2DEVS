import threading
from sccd.runtime.statecharts_core import Event
import socket

send_data_queues = {}
send_events = {}
recv_events = {}
run_sockets = {}

def start_socket_threads(controller, sock):
    recv_events[sock] = recv_event = threading.Event()
    send_events[sock] = send_event = threading.Event()
    send_data_queues[sock] = send_data_queue = []
    run_sockets[sock] = True

    thrd = threading.Thread(target=receive_from_socket, args=[controller, sock, recv_event])
    thrd.daemon = True
    thrd.start()

    thrd = threading.Thread(target=send_to_socket, args=[controller, sock, send_data_queue, send_event])
    thrd.daemon = True
    thrd.start()

def receive_from_socket(controller, sock, recv_event):
    while 1:
        recv_event.wait()
        recv_event.clear()
        if not run_sockets[sock]:
            break
        data = sock.recv(2**16)
        controller.addInput(Event("received_socket", "socket_in", [sock, data]))

def send_to_socket(controller, sock, data_queue, send_event):
    while run_sockets[sock]:
        send_event.wait()
        send_event.clear()
        while data_queue:
            send = sock.send(data_queue.pop(0))
            controller.addInput(Event("sent_socket", "socket_in", [sock, send]))
        if not run_sockets[sock]:
            break

def _accept(controller, sock):
    conn, addr = sock.accept()
    start_socket_threads(controller, conn)
    controller.addInput(Event("accepted_socket", "socket_in", [sock, conn]))

def _connect(controller, sock, destination):
    sock.connect(destination)
    controller.addInput(Event("connected_socket", "socket_in", [sock]))

def _close(controller, sock):
    run_sockets[sock] = False
    send_events[sock].set()
    recv_events[sock].set()
    sock.close()
    controller.addInput(Event("closed_socket", "socket_in", [sock]))

def _bind(controller, sock, addr):
    sock.bind(addr)
    controller.addInput(Event("bound_socket", "socket_in", [sock]))

def _listen(controller, sock):
    sock.listen(1)
    controller.addInput(Event("listened_socket", "socket_in", [sock]))

def _wrapper_func(*args):
    func = args[0]
    controller = args[1]
    sock = args[2]
    try:
        func(*args[1:])
    except socket.error as e:
        print("ERROR " + str(e))
        controller.addInput(Event("error_socket", "socket_in", [sock, e]))
    except Exception as e:
        print("UNKNOWN ERROR " + str(e))
        controller.addInput(Event("unknown_error_socket", "socket_in", [sock, e]))

def _start_on_daemon_thread(func, args):
    new_args = [func]
    new_args.extend(args)
    args = new_args
    thrd = threading.Thread(target=_wrapper_func, args=args)
    thrd.daemon = True
    thrd.start()

def boot_translation_service(controller):
    _start_on_daemon_thread(_poll, [controller, None])

def _poll(controller, _):
    socket_out = controller.addOutputListener("socket_out")
    while 1:
        evt = socket_out.fetch(-1)
        name, params = evt.getName(), evt.getParameters()
        if name == "accept_socket":
            _start_on_daemon_thread(_accept, [controller, params[0]])
        elif name == "recv_socket":
            recv_events[params[0]].set()
        elif name == "connect_socket":
            _start_on_daemon_thread(_connect, [controller, params[0], params[1]])
        elif name == "create_socket":
            sock = socket.socket()
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            start_socket_threads(controller, sock)
            controller.addInput(Event("created_socket", "socket_in", [sock]))
        elif name == "close_socket":
            _start_on_daemon_thread(_close, [controller, params[0]])
        elif name == "send_socket":
            send_data_queues[params[0]].append(params[1])
            send_events[params[0]].set()
        elif name == "bind_socket":
            _start_on_daemon_thread(_bind, [controller, params[0], params[1]])
        elif name == "listen_socket":
            _start_on_daemon_thread(_listen, [controller, params[0]])
        elif name == "stop":
            break
