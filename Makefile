PLAYER_DIRNAME := $(notdir $(abspath .))

.PHONY: all

all: ../../lib/python/puppy ../../bin/retro-play

../../lib/python/puppy:
	@git submodule update --init
	@cd ../../lib/python && ln -s ../../plugins/$(PLAYER_DIRNAME)/deps/puppy/lib/puppy puppy

../../bin/retro-play:
	@mkdir -p ../../bin
	@cd ../../bin && ln -s ../plugins/$(PLAYER_DIRNAME)/scripts/play.py retro-play
