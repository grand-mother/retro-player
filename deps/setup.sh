#!/bin/bash

# Script base directory.
deps_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Setup the dependencies.
. $deps_dir/grand-tour/setup.sh
. $deps_dir/puppy/setup.sh
. $deps_dir/turtle/setup.sh
