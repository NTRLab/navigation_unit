#!/bin/bash

mavproxy.py \
    --aircraft=pixhawk \
    --master=/dev/ttyACM99,921600 \
    --out=udp:192.168.0.94:14540 \
    --out=udpin:0.0.0.0:14550 \
    --source-system=1 \
    --source-component=158 \
    --target-system=1 \
    --target-component=1 \
    --streamrate=-1 \
    --default-modules="cmdlong"
