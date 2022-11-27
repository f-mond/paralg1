from parse_instance import read_instance
import numpy as np
import random
import sys
from optparse import OptionParser
import time

def simulated_annealing(inst, start_time):
    array_of_power_states = [1*inst.get('S')]*inst.get('N')
    #print(array_of_power_states)
    N, makespan, energy, scheduling = build_minimal(inst, array_of_power_states)
    #print('energy: ' + str(energy))
    while True:
        if(time.time()>start_time):
            break
        modification_array = (np.random.randint(-1,1,inst.get('N')))
        new_array_of_power_states = modification_array + array_of_power_states
        #array_of_power_states = array_of_power_states%(inst.get('S')+1)
        new_array_of_power_states = [ x if x>1 else 2 for x in new_array_of_power_states]
        new_array_of_power_states = [ x if x<=inst.get('S') else inst.get('S') for x in new_array_of_power_states]
        #print(new_array_of_power_states)
        #print('ran')
        N, new_makespan, new_energy, new_scheduling = build_minimal(inst, new_array_of_power_states)
        #print(new_makespan)
        if((new_energy < energy ) or random.betavariate(4,1)<(start_time - time.time())/10) and new_makespan < inst.get('deadline'):
            #print('better schedule found')
            scheduling = new_scheduling
            energy = new_energy
            array_of_power_states = new_array_of_power_states
            makespan = new_makespan
    #every one of the power states gets assigned a random number
    #state = energy, array_of_power_states
    #search neighbour, build new power states, check if valid makespan, compare energies: if better, take new state, if not, choose new state randomly, with likelyhood of jump higher at the start
    print(str(N))
    print(str(makespan))
    print(str(energy))
    for i in range(1,N+1):
        print(str(i) + ' '+ str(scheduling.get(i)[1]) + ' ' + str(scheduling.get(i)[2])+ ' '+ str(scheduling.get(i)[3]) + ' ' + str(scheduling.get(i)[4]))



def build_minimal(inst,power_states):
    N=inst.get('N')
    limit = inst.get("deadline")
    M = inst.get("M")
    S=inst.get("S")
    preds=inst.get("predecessors")
    priority = np.zeros(N)
    # get all values from the keys in predecessor and make their priority 1
    # check if those with priority=1 are in the keys of predecessor, if so take their values and set priority=2
    # loop through until there are no more keys found
    # have priority list, higher value higher priority
    free_to_schedule=[]
    free_to_schedule_work=[]
    for i in range(1,N+1):
        free_to_schedule.append(i)
    for i in range(1,N+1):
        if i in preds:
            if priority[i-1]==0:
                priority[i-1] = 1
                free_to_schedule.remove(i)
            for j in preds.get(i):
                priority[j-1] = 2
                if j in free_to_schedule:
                    free_to_schedule.remove(j)
    flag = True
    current_max=2
    for i in free_to_schedule:
        free_to_schedule_work.append(inst.get('work')[i-1])
    
    while(flag):
        flag=False
        for i in range(1,N+1):
            if(priority[i-1]==current_max):
                if i in preds:
                    for j in preds.get(i):
                        priority[j-1]=current_max+1
                        flag=True
        current_max=current_max+1

    
    scheduling = {}
    cpu_busy = {}
    for i in range(1,M+1):
        cpu_busy[i]=0
    current_process=1
    scheduled = [*range(1,N+1)]

    for i in range(current_max-1,-1,-1):
        free=[*range(1,M+1)]
        for j in range(N):
            if(priority[j] == i) and j+1 in scheduled:
                start_time = 0
                if j+1 in preds:
                    start_time=0
                    for k in preds.get(j+1):
                        if scheduling.get(k)[-1] > start_time:
                            start_time = scheduling.get(k)[-1]
                            if scheduling.get(k)[1] in free:
                                current_process=scheduling.get(k)[1]

                if current_process in cpu_busy:
                    start_time = max(cpu_busy.get(current_process),start_time)
                runtime = inst.get('work')[j]/inst.get('freq_list')[power_states[j]-1]
                scheduling[j+1] = [j+1, current_process, power_states[j], start_time, start_time+runtime]
                cpu_busy[current_process] = start_time+runtime
                free.remove(current_process)
                scheduled.remove(j+1)

                if j+1 in free_to_schedule:
                    free_to_schedule_work.pop(free_to_schedule.index(j+1))
                    free_to_schedule.remove(j+1)

                if not free:
                    free=[*range(1,M+1)]
                current_process=random.choice(free)

                for u in free:
                    if u in cpu_busy:
                        if(cpu_busy[current_process]>cpu_busy[u]):
                            current_process = u

        for i in free:
            if not free_to_schedule:
                break

            if len(free)==1:
                break
            else:
                current = free_to_schedule[free_to_schedule_work.index(max(free_to_schedule_work))]
            current_process = i

            if current_process in cpu_busy:
                start_time=cpu_busy.get(current_process)
            else:
                start_time=0
            
            runtime = inst.get('work')[current-1]/inst.get('freq_list')[power_states[current-1]-1]
            scheduling[current] = [current, current_process, power_states[current-1], start_time, start_time+runtime]
            cpu_busy[current_process] = start_time+runtime
            free.remove(current_process)
            scheduled.remove((current))
            free_to_schedule_work.pop(free_to_schedule.index(current))
            free_to_schedule.remove(current)
            
        if not free:
            free=[*range(1,M+1)]

    makespan = 0
    for i in range(1,M+1):
        if(i in cpu_busy):
            if cpu_busy.get(i) > makespan:
                makespan = cpu_busy.get(i)
    energy = 0
    idletime = 0

    for i in range(1,N+1):
        energy+= inst.get('power_list')[scheduling.get(i)[2]-1] * (scheduling.get(i)[4]-scheduling.get(i)[3])
        idletime+=scheduling.get(i)[4]-scheduling.get(i)[3]
    idletime = makespan*M-idletime
    energy+=idletime*inst.get('power_list')[0]
    return N, makespan, energy, scheduling

    

def read_and_check_one_elem_line(f, expected_element_type, error_message):
    try:
        res = expected_element_type(f.readline())
    except ValueError:
        print(error_message, file=sys.stderr)
        exit(1)
    if res <= 0:
        print(error_message, file=sys.stderr)
        exit(1)
    return res

def read_and_check_list(f, expected_length, expected_element_type, error_message):
    s = f.readline()
    res_list = s.split(" ")
    try:
        res_list = list(map(expected_element_type, res_list))
    except ValueError:
        print(error_message, file=sys.stderr)
        exit(1)
    if len(res_list) != expected_length:
        print(error_message, file=sys.stderr)
        exit(1)
    return res_list


def read_instance(inputfile=None):
    instance = {}

    if inputfile is not None:
        if not os.path.isfile(inputfile):
            print("ERROR: Cannot open file %s" % inputfile, file=sys.stderr)
            exit(1)
        f = open(inputfile, 'r')
    else:
        f = sys.stdin


    # number of tasks
    instance["N"] = read_and_check_one_elem_line(f, int,
                                    "ERROR: Number of tasks not correctly specified")

    # work in operations (e.g., FLOPS)
    instance["work"] = read_and_check_list(f, instance["N"], float,
                                    "ERROR: work list not correctly specified")

    # number of machines
    instance["M"] = read_and_check_one_elem_line(f, int,
                                    "ERROR: Number of machines not correctly specified")

    # number of states
    instance["S"] = read_and_check_one_elem_line(f, int,
                                    "ERROR: Number of states not correctly specified")

    # list of states (frequencies)
    instance["freq_list"] = read_and_check_list(f, instance["S"], float,
                                    "ERROR: States list not correctly specified")

    # list of power values for each state
    instance["power_list"] = read_and_check_list(f, instance["S"], float,
                                    "ERROR: Power values list not correctly specified")

    instance["predecessors"] = {}
    for j in range(1, instance["N"] + 1):
        pred_list = f.readline().split(" ")
        try:
            pred_list = list(map(int, pred_list))
        except ValueError:
            print("ERROR: Predecessor list not correctly specified for task %d" % (j), file=sys.stderr)
            exit(1)
        if len(pred_list) == 0:
            print("ERROR: Predecessor list not correctly specified for task %d" % (j), file=sys.stderr)
            exit(1)
        if len(pred_list) == 1 and pred_list[0] == 0:
            # no predecessors for current task
            continue
        instance["predecessors"][j] = pred_list

    instance["deadline"] = read_and_check_one_elem_line(f, float,
                            "ERROR: Deadline not correctly specified")

    if f != sys.stdin:
        f.close()

    return instance

def main():
    start_time = time.time()+27
    inst = read_instance()
    simulated_annealing(inst, start_time)
    #build_minimal(inst)

if __name__ == "__main__":
    main()