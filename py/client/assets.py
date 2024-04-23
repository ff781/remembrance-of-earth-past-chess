import io

import numpy
import pygame, posixpath
from PIL import Image

from amends import image
from amends import data_proxy



pygame.font.init()
fonts = {
    'Impact': pygame.font.SysFont('Impact', 88),
}


def asss_function(key, asss_path):
    asss_type, parameters, = key
    if asss_type == "piece":
        color, piece_type, = parameters
        b = io.BytesIO()
        Image.fromarray(
            image.replace_color(
                numpy.array(
                    Image.open(posixpath.join(asss_path, f'{piece_type}.png')).convert("RGBA")
                ),
                (50, 50, 50, 255),
                color
            ),
            "RGBA"
        ).save(b, "PNG")
        b.seek(0)
        return pygame.image.load(b)
    elif asss_type == "text":
        font, text, antialias, color = parameters
        return fonts[font].render(text, antialias, color)


def modified_asss_function(asss_manager):
    def _(key):
        (asss_type, parameters,), (modifier_type, modifier_parameters,) = key
        if modifier_type == "scale":
            target_size = modifier_parameters
            asss = asss_manager[(asss_type, parameters,)]
            return pygame.transform.scale(asss, target_size, )
        elif modifier_type == "proportional_scale":
            target_size = modifier_parameters
            asss = asss_manager[(asss_type, parameters,)]
            current_size = numpy.array(asss.get_size())
            scale = min(target_size / current_size)
            target_size = tuple(scale * current_size)
            return pygame.transform.scale(asss, target_size, )
        raise "gay"

    return _


class ModifiedFileAssetCache(data_proxy.Cache):
    def __init__(self, asss_path):
        file_asset_cache = data_proxy.Cache(
            data_proxy.FunctionSource(
                lambda key: asss_function(key, asss_path)
            ),
        )

        super().__init__(data_proxy.FunctionSource(
            lambda key: modified_asss_function(file_asset_cache)(key)
        ))
