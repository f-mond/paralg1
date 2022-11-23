#!/usr/bin/env python3

# Copyright (C) 2022
# Klaus Kraßnitzer
# reimplementation of verify_schedule.jl by Sascha Hunold

import argparse
import sys
from parse_instance import read_instance
from parse_schedule import read_schedule
import math

class ValidationException(Exception):
    pass


def validate_schedule(inst, sched):
    cmax = max(sched["jobs"], key=lambda j: j["end"])["end"]

    if not math.isclose(cmax, sched["cmax"]):
        raise ValidationException("cmax is invalid") 

    if cmax > inst["deadline"]:
        raise ValidationException("deadline exceeded") 
    
    machines = [j["machine"] for j in sched["jobs"]]
    max_m = max(machines)
    min_m = min(machines)

    if min_m < 1:
        raise ValidationException("invalid machine index encountered")
    elif max_m > inst["M"]:
        raise ValidationException("too many machines uesd")

    # recompute job running times
    for i in range(inst["N"]):
        sj = sched["jobs"][i]
        rtime = sj["end"] - sj["start"]

        if sj["pstate"]-1 not in range(len(inst["freq_list"])):
            raise ValidationException(f"Invalid power state index {sj['pstate']-1}")

        job_time = inst["work"][i] / inst["freq_list"][sj["pstate"]-1]

        if rtime < 0:
            raise ValidationException(f"Job {sched['jobs'][i]['id']} has negative running time")

        if abs(job_time-rtime)/job_time > 0.01:
            raise ValidationException(f"Invalid job running time encountered for job {sched['jobs'][i]['id']}")
    
    # check overlaps
    for m in range(1,inst["M"]+1):
        machine_jobs = list(filter(lambda j: j["machine"] == m,sched["jobs"]))
        machine_jobs = sorted(machine_jobs, key=lambda j: j["start"])
        # (0,1), (1,2), ..., (len(machine_jobs)-2, len(machine_jobs)-1)
        for i,j in enumerate(range(1,len(machine_jobs))):
            # since jobs ordered by starting time, this is sufficient for fast overlap check
            if machine_jobs[i]["end"] > machine_jobs[j]["start"]:
                raise ValidationException(f"Jobs {machine_jobs[i]['id']} and {machine_jobs[j]['id']} on machine {m} overlap")
    
    # check dependencies
    jobs = sched["jobs"]
    preds = inst["predecessors"]
    for i in range(1,inst["N"]+1):
        if i in preds:
            # i has dependencies
            for j in preds[i]:
                if jobs[j-1]["end"] > jobs[i-1]["start"]:
                    raise ValidationException(f"Precedence for jobs {jobs[j-1]['id']}🡢{jobs[i-1]['start']} not correctly fulfilled")

    # validate energy and job times
    energy = 0
    total_time = 0
    cmax = max(jobs, key=lambda j: j["end"])["end"]
    pstates = list(zip(inst["freq_list"],inst["power_list"]))

    for i in range(inst["N"]):
        job_size = jobs[i]["end"] - jobs[i]["start"]
        sched_pstate = pstates[jobs[i]["pstate"]-1]
        energy += job_size*sched_pstate[1]
        total_time += job_size
    
    # add idle energy
    idle_pl = list(filter(lambda a: a[0] == 0, pstates))[0]
    idle_time = cmax*inst["M"]-total_time
    energy += idle_time*idle_pl[1]
    
    if abs(energy-sched["energy"]) > 0.01:
        print(energy, sched["energy"])
        raise ValidationException("Schedule energy is incorrect")
             

def main():
    parser = argparse.ArgumentParser("energyscheduling schedule validator")
    parser.add_argument("instance", help="problem instance path", type=str)
    parser.add_argument("-s", "--schedule", help="solution schedule path, read from stdin if not provided", type=str)
    args = parser.parse_args()

    instance = read_instance(args.instance)

    # try parsing generated schedule
    try:
        if args.schedule is None:
            sched_content = sys.stdin.readlines() 
        else:
            with open(args.schedule, "r") as f:
                sched_content = f.readlines() 
        schedule = read_schedule(sched_content)
    except Exception as e:
        print(e)
        print("Failed to parse schedule")
        exit(1)
    
    # verify the schedule and give the user an indiciation of what went wrong (ValidationException)
    try:
        validate_schedule(instance, schedule)
    except ValidationException as e:
        print(f"INVALID Schedule: {e}")
        exit(1)
            
    print("Schedule is VALID")
    exit(0)


if __name__ == "__main__":
    main()