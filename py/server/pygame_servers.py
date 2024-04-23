from amends import _socket
from cheesse import dimensional_cheesse

import pickle
import socket
import threading




class Friends2Server():
    class _(_socket.ConnectionInteractionInterface):
        def __init__(s,friends_2_server):
            s.friends_2_server = friends_2_server
        def on_connect(s, server, connection, connection_data, buffer):
            player_ids_left = list(set(range(s.friends_2_server.board_state.players)) - set(s.friends_2_server.address_to_player_id_mapping.values()))
            if player_ids_left:
                s.friends_2_server.address_to_player_id_mapping[connection_data['peername']] = player_id = player_ids_left[0]
                connection.send(pickle.dumps(player_id))
            else:
                raise Exception(f"{s}: no player id left to assign")
            server.send_broadcast(pickle.dumps(s.friends_2_server.board_state))
        def on_receive(s, server, connection, connection_data, buffer, recv_value):
            recv_value = buffer.pop()
            move = pickle.loads(recv_value)
            player_id = s.friends_2_server.address_to_player_id_mapping[connection_data['peername']]
            if s.friends_2_server.board_state.mover == player_id:
                if s.friends_2_server.board_state.is_legal_move(move):
                    s.friends_2_server.board_state = s.friends_2_server.board_state.after_move(move)
                    server.send_broadcast(pickle.dumps(s.friends_2_server.board_state))
        def on_close(s, server, connection, connection_data, buffer):
            s.friends_2_server.address_to_player_id_mapping.pop(connection_data['peername'])
    def __init__(s,
        board_state = None,
        server_address = ('',5555),
        debug=0,):
        s.socket_server = _socket.Server(
            soll_server_address=server_address,
            limit=2,
            interaction_interface=s._(s),
            debug=debug,
            )
        s.board_state = dimensional_cheesse.BoardState2PlayerDimensionalChess.standard_board()if board_state is None else board_state
        s.address_to_player_id_mapping = {}
    def start(s):
        return s.socket_server.start()
    def stop(s):
        return s.socket_server.stop()
    def server_address(s):
        return s.socket_server.server_address()
