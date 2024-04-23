import pdb

from amends import data_proxy
from PIL import Image

import io
import numpy
import pygame


ass_path = "assets/"
asss_path = f"{ass_path}2d/"

class DimensionalCheesseAssetManager:
    def __init__(
        s,
        board_assets,
        user_assets,
        modified_file_asset_cache,
    ):
        s.user_assets = user_assets
        s.board_assets = board_assets
        s.modified_file_asset_cache = modified_file_asset_cache
        s.window_caption = "Dimensional Strike Cheesse"
        s.window_icon = pygame.image.load(f"{ass_path}game_icon.png")

    def get_file_asset(self, *a):
        return self.modified_file_asset_cache[a]


class BoardAssets():
    def get_square_color(s, dimension, max_dimension, dark):
        raise NotImplementedError
    def get_text_color(s):
        raise NotImplementedError
class UserAssets():
    def __init__(s):
        super().__init__()
    def get_selection_color(s):
        raise NotImplementedError
    def get_move_color(s,move_type):
        raise NotImplementedError
    def get_text_color(s):
        raise NotImplementedError

class StandardBoardAssets(BoardAssets):
    def __init__(s,min_dim_square_color,max_dim_square_color):
        super().__init__()
        s.min_dim_square_color = numpy.array(min_dim_square_color)
        s.max_dim_square_color = numpy.array(max_dim_square_color)
    def get_square_color(s,dimension,max_dimension,dark):
        if dimension==-1:
            return (255,255,255,255)
        r = s.min_dim_square_color + dimension / max_dimension * (s.max_dim_square_color - s.min_dim_square_color)
        if dark:
            r *= .25
        return tuple(numpy.concatenate((r,(255,))).astype(int))
    def get_text_color(s):
        return (0,0,0,255,)

class StandardUserAssets(UserAssets):
    def __init__(s,
        selection_color = (  0,255,  0,127),
        move_colors = (
            (0, 127, 0, 127),
            (255, 0, 0, 127),
            (0, 0, 127, 127),
        ),
        text_color = (0,0,0,255,),
    ):
        s.selection_color = selection_color
        s.move_colors = move_colors
        s.text_color = text_color
    def get_selection_color(s):
        return s.selection_color
    def get_move_color(s,move_type):
        return s.move_colors[move_type]
    def get_text_color(s):
        return s.text_color