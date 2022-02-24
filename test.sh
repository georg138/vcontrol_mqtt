#!/bin/bash

prefixes="16"

for prefix in $prefixes; do
    for i in $(seq 1 255); do
        n=$(printf %02x $i)
        base="$prefix$n $prefix$n"
        echo "test1_"$base "1 Char r"
        echo "test2_"$base "2 Short r"
        echo "test4_"$base "4 Int r"
    done
done
