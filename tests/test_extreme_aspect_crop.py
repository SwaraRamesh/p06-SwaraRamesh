# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import shutil
import tempfile
from io import BytesIO
from os.path import abspath, dirname, join

from PIL import Image
from tornado.testing import gen_test

from tests.handlers.test_base_handler import BaseImagingTestCase
from thumbor.config import Config
from thumbor.context import Context, ServerParameters
from thumbor.importer import Importer

COURSE_IMAGES = abspath(join(dirname(__file__), "..", "course", "images"))


class ExtremeAspectCropTestCase(BaseImagingTestCase):
    def get_context(self):
        self.image_root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.image_root, True)

        # Issue #4's source: a 16x16 RGBA PNG with vertical rainbow bars.
        rainbow = [
            (255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0),
            (0, 0, 255), (75, 0, 130), (148, 0, 211),
        ]
        source = Image.new("RGBA", (16, 16))
        for x in range(16):
            colour = rainbow[x * len(rainbow) // 16]
            for y in range(16):
                source.putpixel((x, y), colour + (255,))
        source.save(join(self.image_root, "rainbow.png"), "PNG")
        # A copy of the course's very wide image, so both cases share one
        # file loader root and course/ is left untouched.
        shutil.copy(join(COURSE_IMAGES, "940x2.png"), self.image_root)

        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = self.image_root
        cfg.STORAGE = "thumbor.storages.no_storage"
        cfg.FILTERS = []

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(
            8889, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"
        return Context(server, cfg, importer)

    @gen_test
    async def test_800x20_rainbow_source_is_not_blank(self):
        response = await self.async_fetch("/unsafe/800x20/rainbow.png")
        assert response.code == 200
        image = Image.open(BytesIO(response.body)).convert("RGBA")
        assert image.size == (800, 20)
        alpha = image.getchannel("A")
        assert any(value > 0 for value in alpha.getdata())

    @gen_test
    async def test_fit_in_1x1_returns_1x1_image(self):
        response = await self.async_fetch("/unsafe/fit-in/1x1/940x2.png")
        assert response.code == 200
        image = Image.open(BytesIO(response.body))
        assert image.size == (1, 1)

    @gen_test
    async def test_fit_in_100x0_returns_100x1_image(self):
        response = await self.async_fetch("/unsafe/fit-in/100x0/940x2.png")
        assert response.code == 200
        image = Image.open(BytesIO(response.body))
        assert image.size == (100, 1)
