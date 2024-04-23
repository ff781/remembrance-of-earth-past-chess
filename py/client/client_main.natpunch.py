
from amends import _socket,_pygame, data_proxy, timer
from amends.image import bounding_boxes, transform

import datetime
from cheesse import dimensional_cheesse
import numpy
import pygame
import pygame_assets
import pygame_clients


debug = 1

pygame_window = pygame.display.set_mode((900,500,),pygame.RESIZABLE)
pygame.display.set_caption("Dimensional Strike Cheesse")
#pygame.display.set_icon(pygame_assets.ICON)

fps = 60

#use natpunch_client to find server
natpunch_client = _socket.NATPunchClient(soll_server_address=('193.31.25.224',5555),debug=1)
natpunch_client.connect()
while 1:
    servers = tuple(filter(lambda a:a.get('label')=='server',natpunch_client.known_clients))
    if servers:
        server_address = servers[0]['public']
        break
natpunch_client.close()

client = pygame_clients.Friends2Client(
    asset_manager=pygame_assets.modified_asss_manager,
    server_address=server_address,
    debug=debug,
)
client.connect()


frames_this_second = 0
start = datetime.datetime.now()
start2 = datetime.datetime.now()
urknall = datetime.datetime.now()
total_frames = 0
def draw():
    global start,start2,urknall,total_frames
    global frames_this_second

    client.draw(pygame_window)

    frames_this_second += 1
    total_frames += 1
    if 1 and (datetime.datetime.now() - start).seconds >= 1:
        print(f"fps:{frames_this_second}")
        start = datetime.datetime.now()
        frames_this_second = 0
    if (datetime.datetime.now() - start2).seconds >= 30:
        start2 = datetime.datetime.now()
        print(f"avg fps:{total_frames/(datetime.datetime.now()-urknall).seconds}")
    pygame.display.update()

def update():
    vents = _pygame.process_events(events)

    client.update(pygame_window, vents)

events = None
def main():
    global events

    clock = pygame.time.Clock()
    run=1
    while run:
        clock.tick(fps)
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                run = 0
        update()
        draw()

main()
