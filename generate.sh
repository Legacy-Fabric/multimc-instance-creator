#!/bin/sh
cd legacy-fixes/
./gradlew clean build
cd ..
cp legacy-fixes/build/libs/*.jar .
./generate.py

