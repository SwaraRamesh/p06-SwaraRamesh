# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

# Issue 2: transparent round_corner leaves a dark ring on the curve.
# Edge pixels stay fully opaque and their color is scaled toward black.
# This test fails while any opaque pixel is darker than the white source.

from thumbor.ext.filters import _round_corner

WIDTH = 200
HEIGHT = 200
RADIUS = 50
SOURCE_MIN_CHANNEL = 255


def test_transparent_round_corner_has_no_dark_opaque_edge():
    # Solid opaque white source, RGBA, one pixel per 4 bytes.
    data = bytes([255, 255, 255, 255]) * (WIDTH * HEIGHT)

    # Same call the round_corner filter makes with transparent=1.
    out = bytes(
        _round_corner.apply(
            1,
            "RGBA",
            RADIUS,
            RADIUS,
            255,
            0,
            0,
            WIDTH,
            HEIGHT,
            data,
            1,
        )
    )

    dark_opaque = []
    for y in range(HEIGHT):
        for x in range(WIDTH):
            i = 4 * (y * WIDTH + x)
            r, g, b, a = out[i : i + 4]
            if a == 255 and min(r, g, b) < SOURCE_MIN_CHANNEL - 5:
                dark_opaque.append((x, y, (r, g, b)))

    assert dark_opaque == [], (
        f"{len(dark_opaque)} fully opaque curve pixels are darker than "
        f"the white source, e.g. {dark_opaque[:3]}"
    )
