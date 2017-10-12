#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright (C) 2017 Université Clermont Auvergne, CNRS/IN2P3, LPC
#  Author: Valentin NIESS (niess@in2p3.fr)
#
#  GRAND player, an interactive event display for GRAND.
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>

import json
import sys
import time
# Pand3D modules.
from direct.gui.OnscreenImage import OnscreenImage
# Extra modules.
from grand_tour import Topography
import numpy
import puppy.build
import puppy.control
import puppy.texture

def Paint():
    """Closure for texturing.
    """
    properties = {
        "grass" : ["grass-flat", "grass-dark", 1E-03],
        "sand" : ["grass-dark", "sand-desert", 1E-03]}

    textures = {}
    def get_texture(name):
        try:
            return textures[name]
        except KeyError:
            path = "shared/textures/{:}.jpg".format(name)
            t = puppy.texture.load(path)
            textures[name] = t
            return t

    for v in properties.values():
        v[0] = get_texture(v[0])
        if len(v) > 1: v[1] = get_texture(v[1])
    stencil = get_texture("stencil")

    def paint(node, material, offset=None):
        try: args = properties[material]
        except KeyError: return
        n = len(args)
        if n == 1:
            node.setTexture(args[0])
            if offset: node.setTexOffset(*offset)
        elif n == 3:
            puppy.texture.splatting(node, args[0], args[1],
                stencil, args[2], offset)

    return paint
paint = Paint()

class Player(puppy.control.KeyboardCamera):
    """Interactive event display for GRAND.
    """
    def __init__(self, topography=None, comment=None):
        """Initialise the player.
        """
        puppy.control.KeyboardCamera.__init__(self)

        # Initialise the topography provider.
        if topography:
            try: texture = topography["texture"]
            except KeyError: texture = None
            else: del topography["texture"]
            try: points = topography["resolution"]
            except KeyError: points = 201
            else: del topography["resolution"]
            scale = 0.5 * topography["size"]
            del topography["size"]

            topo = Topography(**topography)

            # Interpolate the topography on a mesh.
            t0 = time.time()
            print "o Interpolating the topography ..."
            x = numpy.linspace(-scale, scale, points)
            y = numpy.linspace(-scale, scale, points)
            z = numpy.zeros((len(y), len(x)))
            for i, yi in enumerate(y):
                for j, xj in enumerate(x):
                    z[i,j] = topo.ground_altitude(xj, yi)
            print "  -> Done in {:.1f}s".format(time.time() - t0)

            # Render the terrain.
            t0 = time.time()
            print "o Rendering the terrain ..."
            lod = 3
            dlim = scale / 2**lod
            if texture: fc, lc = (1,1,1,1), None
            else: fc, lc = None, (1,1,1,1)
            node = puppy.build.Terrain(x, y, z, face_color=fc, line_color=lc,
              lod=lod, dlim=dlim).render()
            paint(node, texture)
            print "  -> Done in {:.1f}s".format(time.time() - t0)

            # Relocate the camera position.
            self.camera.setPos(0., 0., topo.ground_altitude(0., 0.) + 1.7)

        # Add a background image.
        OnscreenImage(parent=render2d, image="shared/textures/stars.jpg")
        base.cam.node().getDisplayRegion(0).setSort(20)

if __name__ == "__main__":
    try: config_path = sys.argv[1]
    except IndexError: config = {}
    else:
        with open(config_path) as f: config = json.load(f)
    Player(**config).run()
