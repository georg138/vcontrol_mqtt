#!/bin/python3

import os

for item in range(7):

    stream = os.popen("vclient -c 'getEnergy " + str(item) + "'")
    output = stream.read()
    arr = output.split("\n")[1].split()

    year = 2000 + int(arr[2], base=16)
    day = int(arr[1], base=16)
    week = int(arr[3], base=16)

    electricH = int(arr[7] + arr[6], base=16) / 10.0
    electricW = int(arr[11] + arr[10], base=16) / 10.0

    print(day)
    print(week)
    print(electricH)
    print(electricW)
