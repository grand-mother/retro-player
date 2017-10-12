# GRAND player

_This is an interactive event display for GRAND._

## Installation

The player is built on the [Panda3D][Panda3D] engine. In order to run it
you'll need to install the Panda3D SDK, e.g. from [here][Panda3D:SDK]. In
addition, the player has the following dependencies:

3. [GRAND-TOUR][GRAND-TOUR], Python bindings for TURTLE, encapsulating GRAND's
   topography.
2. [PUPPY][PUPPY], an encapsulation of Panda3D providing procedural builders.
3. [TURTLE][TURTLE], a topography library in C.

If needed, they can be installed locally as submodules via git, running the
[deps/install.sh](deps/install.sh) script. Then one can source
[deps/setup.sh](deps/setup.sh) in order to set the environment accordingly.

[Panda3D]: https://www.panda3d.org/
[Panda3D:SDK]: https://www.panda3d.org/download.php?sdk&version=1.9.4
[TURTLE]: https://github.com/niess/turtle
[PUPPY]: https://github.com/niess/puppy
[GRAND-TOUR]: https://github.com/grand/grand-tour

## Documentation

In order to run the player you'll need a configuration card,
e.g. [example/ulastai.json](example/ulastai.json) as well as the
[ASTER-GDEM2][ASTER-GDEM2] tiles corresponding to your location. The run :

```bash
./scripts/player.py examples/ulastai.json
```

[ASTER-GDEM2]: https://asterweb.jpl.nasa.gov/gdem.asp

## License
The GRAND player is under the **GNU LGPLv3** license. See the provided
`LICENSE` and `COPYING.LESSER` files.
