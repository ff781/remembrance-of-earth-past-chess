from amends import _numpy, _pygame, _socket, data_proxy, requisition, timer
from amends.image import bounding_boxes, transform
from PIL import Image

import cheesse.dimensional_cheesse
import cvxpy
import datetime
import functools
import io
import numpy
import pickle
import pygame
import random
import socket


def index_to_perimeter_index_2d(i,shape,):
    i = i % (2*(shape[0]+shape[1]-2))
    if i < shape[1]:
        return (0,i,)
    elif i < shape[1] + shape[0] - 1:
        return (i - (shape[1] - 1), shape[1] - 1,)
    elif i < 2 * shape[1] + shape[0] - 2:
        return (shape[0] - 1, shape[1] - 1 - (i - (shape[1] + shape[0] - 2)),)
    else:
        return (shape[0] - 1 - (i - (2 * shape[1] + shape[0] - 3)),0,)

def shape_to_subboards_in_subboard_func(key):
    shape = key
    assert len(shape)>=2
    subboards_in_subboard = []
    for k in range(2,len(shape)+1,2):
        subboards_in_subboard.append((2,numpy.array(shape[k-2:k]),))
    #if the number of dimensions is odd, render the last dimension in a perimeter tile arrangement instead of a linear arrangement
    if len(shape)%2!=0:
        sides = subboards_in_subboard[-1][1]
        total_len = shape[-1]

        x=cvxpy.Variable(2,integer=True)
        diff = cvxpy.abs(cvxpy.multiply(x,sides)@numpy.array([1, -1]))
        objective=cvxpy.Minimize(diff)
        constraints=[(2*(x[0]+x[1]-2)) == total_len]

        cvxpy.Problem(objective,constraints,).solve()
        subboards_in_subboard.append((1,x.value,))
    return subboards_in_subboard
shape_to_subboards_in_subboard = data_proxy.Cache(
    data_proxy.FunctionSource(shape_to_subboards_in_subboard_func),
)

class BaseClient():
    def __init__(s,board_state,asset_manager,debug=0):
        s.debug = debug

        world_to_cam_transform = numpy.identity(4)
        world_to_cam_transform[:3,:3] = numpy.diag((255,)*3)
        s.board_state_camera = transform.Camera3D(world_to_cam_transform = world_to_cam_transform)

        s.axes_permutation = None
        s.set_board_state(board_state)

        s.asset_manager = asset_manager
        pygame.display.set_caption(asset_manager.window_caption)
        pygame.display.set_icon(asset_manager.window_icon)

        s.bounding_box_hierarchy_root = bounding_boxes.AllBox()
        s.player_colors = [
            (109, 63, 91,255),
            (189,236,182,255),
            (  2, 86,105,255),
            (255,255,255,255),
            (190,189,127,255),
            ( 24, 23, 28,255),
        ]
    def set_board_state(s,board_state):
        s.board_state = board_state
        if s.board_state is not None:
            if s.axes_permutation is None or len(s.axes_permutation)!=s.board_state.a.ndim:
                s.axes_permutation = tuple(reversed(range(s.board_state.a.ndim)))
    def draw(s, window):
        s.bounding_box_hierarchy_root.kill_children()
        window.fill((255,255,255,100,))
        if s.board_state is not None:
            board_transform = s.board_state_camera.world_to_cam_transform
            board_to_actual_board_transform = numpy.identity(4)
            board_to_actual_board_transform[:3,:3] = numpy.diag((.8,)*3)
            board_to_side_information_transform = numpy.identity(4)
            board_to_side_information_transform[:3,:3] = numpy.diag((.2,)*3)
            board_to_side_information_transform[:3,3] = (.8,0,0,)
            s.draw_actual_board(window, board_transform @ board_to_actual_board_transform,)
            s.draw_side_information(window, board_transform @ board_to_side_information_transform,)
    def update(s, window, events):
        new_events = []
        for event in events:
            if event.type == pygame.MOUSEWHEEL:
                s.board_state_camera.world_to_cam_transform[:3,:3] *= 1.1**event.y
            elif event.type == _pygame.MOUSEDRAG:
                s.board_state_camera.world_to_cam_transform[:2,3] -= event.drag_vector
            else:
                new_events.append(event)
        events.clear()
        events.extend(new_events)

    def draw_side_information(s, window, transform,):
        my_transform = transform
        my_to_mover_transform = numpy.identity(4)
        my_to_mover_transform[:2,:2] = numpy.diag((1,.2,))
        mover_transform = my_transform @ my_to_mover_transform
        area = tuple(mover_transform.diagonal()[:2],)
        pos = tuple(mover_transform[:2,3])
        pygame.draw.rect(window,s.player_colors[s.board_state.mover],pygame.Rect(pos,area))
        my_to_info_transform = numpy.identity(4)
        my_to_info_transform[:2,:2] = numpy.diag((1,.8,))
        my_to_info_transform[:2,3] = (0,.2,)
        info_transform = my_transform @ my_to_info_transform
        info_to_general_info_transform = numpy.identity(4)
        info_to_general_info_transform[:2,:2] = numpy.diag((1,.1,))
        general_info_transform = info_transform @ info_to_general_info_transform
        area = tuple(general_info_transform.diagonal()[:2],)
        pos = tuple(general_info_transform[:2,3])
        window.blit(
            s.asset_manager.get_file_asset(
                ("text",("Impact",str(s.board_state.get_dimensional_strike_research_req()),True,'black',)),
                ("proportional_scale",area,)
            ),
            pos,
        )
        info_to_all_player_info_transform = numpy.identity(4)
        info_to_all_player_info_transform[:2,:2] = numpy.diag((1,.9,))
        info_to_all_player_info_transform[:2,3] = (0,.1,)
        all_player_info_transform = info_transform @ info_to_all_player_info_transform
        for player in range(s.board_state.players):
            all_player_info_to_player_info_transform = numpy.identity(4)
            all_player_info_to_player_info_transform[:2,:2] = numpy.diag((1,1/s.board_state.players,))
            all_player_info_to_player_info_transform[:2,3] = (0,player/s.board_state.players,)
            player_info_transform = all_player_info_transform @ all_player_info_to_player_info_transform
            area = tuple(player_info_transform.diagonal()[:2],)
            pos = tuple(player_info_transform[:2,3])
            window.blit(
            s.asset_manager.get_file_asset(
                ("text",("Impact",str(s.board_state.get_research(player)),True,s.player_colors[player],)),
                ("proportional_scale",area,)
            ),
            pos,
            )
    def draw_actual_board(
        s,
        window,
        transform,):
        axes_permutation_mat = _numpy.permutation2d(s.axes_permutation)
        #axes_permutation_mat_homo = numpy.identity(4)
        #axes_permutation_mat_homo[:3,:3] = axes_permutation_mat
        shape = s.board_state.a.shape
        permuted_shape = tuple((axes_permutation_mat @ shape).astype(int))
        permuted_axes_in_subboard = [list(s.axes_permutation[i:i+2])for i in range(0, len(s.axes_permutation), 2)]
        subboards_in_subboard = shape_to_subboards_in_subboard[permuted_shape]
        unit_tiles_in_subboard = [subboards_in_subboard[0][1]]
        for i in range(1,len(subboards_in_subboard)):
            unit_tiles_in_subboard.append(unit_tiles_in_subboard[i-1]*subboards_in_subboard[i][1])
        pixel_per_tile = 1 / max(unit_tiles_in_subboard[-1])

        s.render_subboard(
            window,
            s.bounding_box_hierarchy_root,
            transform,
            len(subboards_in_subboard)-1,
            s.board_state,
            numpy.full(s.board_state.dim,-1,dtype=numpy.intc),
            subboards_in_subboard,
            permuted_axes_in_subboard)

    def render_subboard(
            s,
            window,
            parent_bounding_box,
            my_transform,
            render_index,
            board_state,
            superboard_multi_index,
            subboards_in_subboard,
            permuted_axes_in_subboard):
        area = tuple(my_transform.diagonal()[:2], )
        pos = tuple(my_transform[:2, 3])
        tupled_superboard_multi_index = tuple(superboard_multi_index)
        my_bounding_box = bounding_boxes.AlignedRectBoundingBoxNode(
            pos, area,
            data=tupled_superboard_multi_index)
        parent_bounding_box.add_child(my_bounding_box)
        if render_index == -1:
            quersum = functools.reduce(lambda a, b: a + b, tupled_superboard_multi_index)
            dimensionality = s.board_state.get_dimension(tupled_superboard_multi_index)
            color = s.asset_manager.board_assets.get_square_color(dimensionality, board_state.dim,
                                                                                   quersum % 2)
            pygame.draw.rect(window, color, pygame.Rect(pos, area))
            s.render_board_selection(window, tupled_superboard_multi_index, pos, area)
            if s.board_state[tupled_superboard_multi_index] is not None:
                player, piece, = s.board_state[tupled_superboard_multi_index]
                window.blit(
                    s.asset_manager.get_file_asset(
                        ("piece", (s.player_colors[player], piece,)),
                        ("scale", area,)
                    ),
                    pos,
                )
                if piece == 'k':
                    my_to_text_transform = numpy.identity(4)
                    my_to_text_transform[:3, :3] = numpy.diag((0.4,) * 3)
                    text_transform = my_transform @ my_to_text_transform
                    text_area = tuple(text_transform.diagonal()[:2], )
                    text_pos = tuple(text_transform[:2, 3])
                    total_cd = s.board_state.get_castle_cd_total(player)
                    current_cd = min(total_cd, s.board_state.get_castle_cd_current(player))
                    window.blit(
                        s.asset_manager.get_file_asset(
                            ("text", ("Impact",
                                      str(f"{current_cd}/{total_cd}"),
                                      True, 'black',)),
                            ("proportional_scale", text_area,)
                        ),
                        text_pos,
                    )
                elif piece == 'c':
                    equipped_dimensional_foil = s.board_state.get_piece_data(tupled_superboard_multi_index)[0]
                    if equipped_dimensional_foil >= 0:
                        my_to_dimensional_foil_indicator_transform = numpy.identity(4)
                        my_to_dimensional_foil_indicator_transform[:2, :2] = numpy.diag((.2, .2,))
                        my_to_dimensional_foil_indicator_transform[:2, 3] = (.5, .5,)
                        dimensional_foil_indicator_transform = my_transform @ my_to_dimensional_foil_indicator_transform
                        area = tuple(dimensional_foil_indicator_transform.diagonal()[:2], )
                        pos = tuple(dimensional_foil_indicator_transform[:2, 3])
                        pygame.draw.circle(window,
                                           s.asset_manager.board_assets.get_square_color(equipped_dimensional_foil,
                                                                                         board_state.dim, 0), pos,
                                           min(area))
        else:
            subboard_dim, subsubboards, = subboards_in_subboard[render_index]
            subboard_size_in_my_coords = numpy.diag(1 / subsubboards)

            my_to_next_transform = numpy.identity(4)
            my_to_next_transform[:2, :2] = subboard_size_in_my_coords

            # subboards arranged in perimeter
            if subboard_dim == 1:
                total_subboards_in_subboard = int(2 * (numpy.add.reduce(subsubboards) - 2))
                for i in range(total_subboards_in_subboard):
                    pi = numpy.array(index_to_perimeter_index_2d(i, subsubboards))
                    my_to_next_transform[:2, 3] = numpy.diag(pi * subboard_size_in_my_coords)
                    next_transform = my_transform @ my_to_next_transform
                    next_superboard_multi_index = superboard_multi_index.copy()
                    next_superboard_multi_index[permuted_axes_in_subboard[render_index]] = i
                    s.render_subboard(window, my_bounding_box, next_transform, render_index - 1, board_state,
                                    next_superboard_multi_index,subboards_in_subboard,permuted_axes_in_subboard)
            # subboards arranged in 2d grid
            elif subboard_dim == 2:
                for i in numpy.ndindex(*subsubboards):
                    my_to_next_transform[:2, 3] = numpy.diag(i * subboard_size_in_my_coords)
                    next_transform = my_transform @ my_to_next_transform
                    next_superboard_multi_index = superboard_multi_index.copy()
                    next_superboard_multi_index[permuted_axes_in_subboard[render_index]] = i
                    s.render_subboard(window, my_bounding_box, next_transform, render_index - 1, board_state,
                                    next_superboard_multi_index,subboards_in_subboard,permuted_axes_in_subboard)
            else:
                raise "gay"
    def render_board_selection(s,window,tupled_superboard_multi_index,pos,area):
        1
#this client allows for the selection of moves
class MoveSelectionBaseClient(BaseClient):
    def __init__(s,
        board_state,
        asset_manager,
        debug=0,
        **k,):
        super().__init__(
            board_state = board_state,
            asset_manager = asset_manager,
            **k,
            debug=debug,
        )
        s.selected_square = None
        s.movable_moves = []
        s.move_timer = timer.Timer()
    def draw(s, window):
        super().draw(window)
    def update(s, window, events):
        super().update(window, events)

        new_events = []
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    hit_square = s.bounding_box_hierarchy_root.hit_recursive(event.pos).data
                    if s.selected_square is not None:
                        for _ in s.movable_moves:
                            move_type,(srt,tgt) = _
                            if hit_square == tgt[0]:
                                s.execute_move(_)
                                hit_square = None
                                break
                    if hit_square is not None and len(hit_square) == s.board_state.dim:
                        if s.debug:
                            print(f"selected square {hit_square}")
                        s.selected_square = hit_square
                    else:
                        s.selected_square = None
            else:
                new_events.append(event)
        events.clear()
        events.extend(new_events)

        s.movable_moves = []
        if s.selected_square is not None:
            if s.fill_legal_moves_for_square(s.selected_square):
                s.movable_moves = s.board_state.legal_moves_from(
                    s.selected_square,
                    respect_mover = 0,
                    )

        if 0 and s.move_timer.diff().total_seconds() >= 1:
            legal_moves = s.board_state.legal_moves()
            s.set_board_state(s.board_state.after_move(random.choice(legal_moves)))
            s.move_timer.start()
    #defines the behaviour when a move is locked in
    #overwrite this for custom behaviour
    def execute_move(s, move):
        s.set_board_state(s.board_state.after_move(move))
    #returns whether the legal moves should be generated for this srt tile
    def fill_legal_moves_for_square(s, square):
        return cheesse.apply_piece_regex(s.board_state[square],s.board_state.mover,None)

    def render_board_selection(s, window, tupled_superboard_multi_index, pos, area):
        super().render_board_selection(window, tupled_superboard_multi_index, pos, area)
        if s.selected_square is not None and (tupled_superboard_multi_index == s.selected_square):
            pygame.draw.rect(window, s.asset_manager.user_assets.get_selection_color(), pygame.Rect(pos, area))
        for move_type, (_, tgt) in s.movable_moves:
            if tupled_superboard_multi_index == tgt[0]:
                pygame.draw.rect(window, s.asset_manager.user_assets.get_move_color(move_type),
                                 pygame.Rect(pos, area))


class Friends2Client(MoveSelectionBaseClient):
    class _(_socket.ConnectionInteractionInterface):
        def __init__(s,friends_2_client):
            s.friends_2_client = friends_2_client
        def on_receive(s, client, connection, connection_data, buffer, recv_value):
            recv_value = buffer.pop()
            unpickled_recv_value = pickle.loads(recv_value)
            if type(unpickled_recv_value) is int:
                s.friends_2_client.player_id = unpickled_recv_value
            elif isinstance(unpickled_recv_value, cheesse.BoardState):
                s.friends_2_client.set_board_state(unpickled_recv_value)
            else:
                print(f"{s}: there is something sussy recv from server")
    def __init__(s,
        asset_manager,
        server_address,
        debug=0,
        **k,
        ):
        super().__init__(
            board_state=None,
            asset_manager=asset_manager,
            **k,
            debug=debug,)
        s.socket_client = _socket.Client(
            soll_server_address = server_address,
            recv_size = 2**16,
            interaction_interface = s._(s),
            debug=debug,
        )
        s.player_id = None
    def connect(s):
        try:
            s.socket_client.connect()
        except:
            raise
    def execute_move(s, move):
        s.socket_client.send(pickle.dumps(move))
    def fill_legal_moves_for_square(s, square):
        i_am_mover_condition = s.board_state.mover==s.player_id
        piece_is_my_piece_condition = cheesse.apply_piece_regex(s.board_state[square],s.board_state.mover,None)
        return i_am_mover_condition and piece_is_my_piece_condition
