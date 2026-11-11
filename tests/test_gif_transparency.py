# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from io import BytesIO
from os.path import abspath, dirname, join

from PIL import Image

from thumbor.config import Config
from thumbor.context import Context
from thumbor.engines.pil import Engine

COURSE_IMAGES = abspath(join(dirname(__file__), "../course/images"))


def get_context():
    cfg = Config(
        SECURITY_KEY="ACME-SEC",
        ENGINE="thumbor.engines.pil",
        PILLOW_PRESERVE_INDEXED_MODE=True,
    )
    cfg.LOADER = "thumbor.loaders.file_loader"
    cfg.FILE_LOADER_ROOT_PATH = COURSE_IMAGES
    cfg.STORAGE = "thumbor.storages.no_storage"

    return Context(config=cfg)


def test_resized_gif_keeps_transparent_pixels():
    with open(join(COURSE_IMAGES, "sticker.gif"), "rb") as image_file:
        buffer = image_file.read()

    engine = Engine(get_context())
    engine.load(buffer, ".gif")
    engine.resize(240, 160)

    result = Image.open(BytesIO(engine.read(".gif")))

    assert "transparency" in result.info
    alpha = result.convert("RGBA").getchannel("A")
    transparent_pixels = sum(1 for value in alpha.getdata() if value < 255)
    assert transparent_pixels > 0
