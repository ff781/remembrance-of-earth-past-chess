from amends import _socket,requisition
from amends.text.command_manager import TextCommandManager

from cheesse import dimensional_cheesse
import pygame_servers


command_manager = TextCommandManager()
@command_manager.command()
def q():
    raise KeyboardInterrupt
@command_manager.command()
def restart_server(ip='', port=5556):
    global server
    if globals().get('server'):
        server.stop()
    server = pygame_servers.Friends2Server(
        board_state=dimensional_cheesse.BoardState2PlayerDimensionalChess.standard_board(),
        server_address=(ip,port),
        debug=1,
    )
    server.start()
restart_server()



try:
    while 1:
        command_manager.execute(input('>'))
except KeyboardInterrupt:
    if globals().get('server'):
        server.stop()
