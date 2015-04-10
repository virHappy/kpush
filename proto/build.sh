#!/bin/sh

rm -rf python cpp java
mkdir -p python cpp java
protoc -I=. --python_out=python --cpp_out=cpp --java_out=java ./net.proto
