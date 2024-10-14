#!/bin/sh
cd legacy-fixes/ || exit
./gradlew clean build
cd ..
cp legacy-fixes/build/libs/*.jar .
./generate.py

