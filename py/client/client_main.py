from amends import _socket,_pygame, data_proxy, timer
from amends.image import bounding_boxes, transform
from cheesse import dimensional_cheesse

import assets
import datetime
import numpy
import pygame
import pygame_assets
import pygame_clients
import sys
import os



os.environ['SDL_VIDEO_CENTERED'] = 'True'


debug = 1
fps = 60

client = pygame_clients.Friends2Client(
    asset_manager=pygame_assets.DimensionalCheesseAssetManager(
        modified_file_asset_cache=assets.ModifiedFileAssetCache(pygame_assets.asss_path),
        board_assets=pygame_assets.StandardBoardAssets(
            min_dim_square_color=(255,160,122,),
            max_dim_square_color=(127,0,255,),
        ),
        user_assets=pygame_assets.StandardUserAssets(),
    ),
    server_address=(sys.argv[1]if len(sys.argv)>=2 else 'localhost',5556),
    debug=debug,
)
client.connect()

pygame_window = pygame.display.set_mode(flags=pygame.RESIZABLE, display=0)
@_pygame.track_fps
def draw(events):
    client.draw(pygame_window)
    pygame.display.update()
def update(events):
    client.update(pygame_window, events)
_pygame.main(update,draw,fps=60)