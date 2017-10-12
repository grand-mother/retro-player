#!/bin/bash

echo "1. Fetching dependencies ..."
git submodule update --init
cd deps/turtle && git submodule update --init && cd  ../..
echo "--> Done"
echo ""

echo "2. Building TURTLE library ..."
cd deps/turtle && make clean && make && cd ../..
echo "--> Done"
