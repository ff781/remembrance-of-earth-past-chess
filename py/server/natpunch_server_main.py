from amends import _socket, requisition
from amends.text.command_manager import TextCommandManager


command_manager = TextCommandManager()
@command_manager.command()
def q():
    exit(69)
@command_manager.command()
def clear_clients():
    server.clear_clients()

server = _socket.NATPunchServer(soll_server_address=('',5555),debug=1)
server.start()
while 1:
    print(f"server addr: {requisition.get_public_ip()}, mask: {server.server_address()}")
    print(f"known_clients: {server.known_clients}")
    command_manager.execute(input('>'))
