from amends import _socket,requisition
from amends.text.command_manager import TextCommandManager

from cheesse import dimensional_cheesse
import pygame_servers


natpunch_client = _socket.NATPunchClient(soll_client_address=('',5555),soll_server_address=('193.31.25.224',5555),label='server',debug=1)
natpunch_client.connect()
server_address=('',natpunch_client.client_address()[1],)
natpunch_client.close()

command_manager = TextCommandManager()
@command_manager.command()
def q():
    raise KeyboardInterrupt
@command_manager.command()
def restart_server():
    global server
    if server:
        server.close()
    server = pygame_servers.Friends2Server(
        board_state = dimensional_cheesse.BoardState2PlayerDimensionalChess.standard_board(),
        debug=1,
        server_address = server_address,
    )
    server.start()
server = None
restart_server()

try:
    while 1:
        command_manager.execute(input('>'))
except KeyboardInterrupt:
    if server:
        server.stop()
        natpunch_client = _socket.NATPunchClient(soll_server_address=('193.31.25.224',5555),label='server',debug=1)
        natpunch_client.connect()
        natpunch_client.go_offline()
        natpunch_client.close()
