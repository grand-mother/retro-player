#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright (C) 2017 Université Clermont Auvergne, CNRS/IN2P3, LPC
#  Author: Valentin NIESS (niess@in2p3.fr)
#
#  RETRO player, an interactive event display for RETRO.
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

import collections
import json
import os
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

# Directory where the player is located.
PLAYER_DIR = os.path.abspath(
  os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    ".."))

class EventIterator:
    """Iterator over GRAND events stored in a JSON file."""
    def __init__(self, path):
        f = open(path)
        self._file = f
        self._prev = -1
        self._current = None

    def __del__(self):
        if self._file:
            self._file.close()
            self._file = None

    def __iter__(self):
        self.rewind()
        return self

    def next(self):
        """Pop the next event from file."""
        try: event = json.loads(self._file.readline())
        except ValueError: raise StopIteration()
        self._prev = event["previous"]
        self._current = event
        return event

    def previous(self):
        """Pop the previous event from file."""
        if self._prev >= 0: self._file.seek(self._prev, 0)
        else: self._file.seek(0, 0)
        return self.next()

    def rewind(self):
        """Rewind the file."""
        self._file.seek(0, 0)
        self._prev = -1
        self._current = None

class EventManager(object):
    """Manage GRAND events."""
    def __init__(self, path=None, on_start=None):

        if path: self.events = EventIterator(path)
        self._current_vertex = None
        self._all_vertices = collections.deque([])
        if on_start:
            for process in on_start:
                try: method, kwargs = process
                except ValueError: method, kwargs = process, {}
                getattr(self, method)(**kwargs)

        # Register the extra event handlers.
        self.accept("raw-e", self.show_next_event)
        self.accept("raw-q", self.show_previous_event)
        self.accept("raw-t", self.toggle_all_decays)

    def toggle_all_decays(self):
        """Toggle the display of all the tau decay vertices."""
        t0 = time.time()
        print "o Toggling all tau decays ..."
        if self._all_vertices:
            while True:
                try: node = self._all_vertices.pop()
                except IndexError: break
                node.removeNode()
        else:
            for event in self.events:
                self._all_vertices.append(self._render_decay(event))
            self.events.rewind()
        print "  -> Done in {:.1f}s".format(time.time() - t0)

    def show_next_event(self):
        """Render the next event and relocate to it."""
        try: event = self.events.next()
        except StopIteration: event = self.events.current
        self._update_event(event)

    def show_previous_event(self):
        """Render the previous event and relocate to it."""
        event = self.events.previous()
        self._update_event(event)

    def _render_decay(self, event):
        """Render a decay."""
        energy, position, direction, _, _  = event["tau_at_decay"]
        size = numpy.log10(energy)
        vertex = puppy.build.Box(
          size, face_color=(1,1,0,1), line_color=(0,0,0,1)).render()
        vertex.setPos(*position)
        edges = (position, position - 100. * numpy.array(direction))
        track = puppy.build.Track(edges, line_color=(1,1,0,1)).render()
        vertex.reparentTo(track)
        return track

    def _update_event(self, event):
        """Update the current event and relocate to it."""
        self._relocate_camera(event)
        if not self._all_vertices:
            if self._current_vertex: self._current_vertex.removeNode()
            self._current_vertex = self._render_decay(event)

    def _relocate_camera(self, event):
        """Relocate the camera to the given event."""
        position = event["tau_at_decay"][1] + numpy.array((100., 100., 100.))
        self.camera.setPos(*position)
        self.camera.lookAt(*event["tau_at_decay"][1])

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
            path = "{:}/share/textures/{:}.jpg".format(PLAYER_DIR, name)
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

class Player(puppy.control.KeyboardCamera, EventManager):
    """Interactive event display for GRAND.
    """
    def __init__(self, topography=None, events=None, comment=None):
        """Initialise the player.
        """
        puppy.control.KeyboardCamera.__init__(self)
        EventManager.__init__(self, **events)

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
        OnscreenImage(parent=render2d,
          image="{:}/share/textures/stars.jpg".format(PLAYER_DIR))
        base.cam.node().getDisplayRegion(0).setSort(20)

if __name__ == "__main__":
    try: config_path = sys.argv[1]
    except IndexError: config = {}
    else:
        with open(config_path) as f: config = json.load(f)
    Player(**config).run()
