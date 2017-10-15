# RETRO player

_This is a plugin for RETRO providing an interactive event display._

## Installation

The player is built on the [Panda3D][Panda3D] engine. In order to run it
you'll need to install the Panda3D SDK, e.g. from [here][Panda3D:SDK]. Then,
from [RETRO][RETRO]'s directory run:

```bash
mkdir -p plugins
git clone https://github.com/grand-mother/retro-player plugins/player
make && make plugins
```

[Panda3D]: https://www.panda3d.org/
[Panda3D:SDK]: https://www.panda3d.org/download.php?sdk&version=1.9.4
[RETRO]: https://github.com/grand-mother/retro

## Documentation

In order to run the player you'll need a configuration card,
e.g. [example/ulastai.json](example/ulastai.json). Then run:

```bash
retro-play plugins/retro-player/examples/ulastai.json
```

## License
The player plugin for RETRO is under the **GNU LGPLv3** license. See the
provided [LICENSE](LICENSE) and [COPYING.LESSER](COPYING.LESSER) files.
