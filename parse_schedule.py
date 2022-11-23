#! /usr/bin/env python

# Copyright (C) 2016
# Sascha Hunold

import sys
import os
import pprint

def read_schedule(content):
    schedule = {}

    cnt = 0

    line = content[cnt]
    
    #print(cnt, ":", line)
    #print("stripped:{}:".format(line.strip()))
    schedule["n"]      = int(line.strip())
    schedule["cmax"]   = float(content[cnt+1].strip())
    schedule["energy"] = float(content[cnt+2].strip())
    schedule["jobs"]  = []
    for j in range(cnt+3,cnt+3+schedule["n"]):
        line2 = content[j]
        data  = line2.strip().split(" ")
        job = {}
        job["id"] = int(data[0])
        job["machine"] = int(data[1])
        job["pstate"] = int(data[2])
        job["start"] = float(data[3])
        job["end"] = float(data[4])
        schedule["jobs"].append(job)
    
    schedule["jobs"] = sorted(schedule["jobs"], key=lambda j: j["id"])

    cnt = cnt+3+schedule["n"]

    return schedule
