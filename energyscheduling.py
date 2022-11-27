from parse_instance import read_instance
import numpy as np
import random

def build_minimal(inst,filename):
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
    #print(inst)
    free_to_schedule=[]
    free_to_schedule_work=[]
    for i in range(1,N+1):
        free_to_schedule.append(i)
        #free_to_schedule_work.append(inst.get('work')[i])
    for i in range(N):
        if i in preds:
            if priority[i-1]==0:
                priority[i-1] = 1
                free_to_schedule.remove(i)
                #free_to_schedule_work.remove(i)
            for j in preds.get(i):
                priority[j-1] = 2
                if j in free_to_schedule:
                    free_to_schedule.remove(j)
                    #free_to_schedule_work.pop(i)
    flag = True
    current_max=2
    for i in free_to_schedule:
        #print(i)
        free_to_schedule_work.append(inst.get('work')[i-1])
    print(len(free_to_schedule))
    #print(free_to_schedule_work)

    
    while(flag):
        flag=False
        for i in range(1,N+1):
            if(priority[i-1]==current_max):
                if i in preds:
                    for j in preds.get(i):
                        priority[j-1]=current_max+1
                        flag=True
        current_max=current_max+1
    #print(priority)
    scheduling = {}
    cpu_busy = {}
    current_process=1
    for i in range(current_max-1,0,-1):
        free=[*range(1,M+1)]
        scheduled=[]
        #print("Priority: " + str(i))
        for j in range(N):
            if(priority[j] == i):
                start_time = 0
                #print(current_process)
                if j+1 in preds:
                    start_time=0
                    for k in preds.get(j+1):
                        if scheduling.get(k)[-1] > start_time:
                            start_time = scheduling.get(k)[-1]
                            if scheduling.get(k)[1] in free:
                                #print("process its trying to schedule to: " + str(scheduling.get(k)[1]))
                                #print(free)
                                current_process=scheduling.get(k)[1]
                if current_process in cpu_busy:
                    start_time = max(cpu_busy.get(current_process),start_time)
                runtime = inst.get('work')[j]/inst.get('freq_list')[inst.get('S')-1]
                scheduling[j+1] = [j+1, current_process, inst.get('S'), start_time, start_time+runtime]
                cpu_busy[current_process] = start_time+runtime
                #print("process trying to be removed from free: " + str(current_process))
                free.remove(current_process)
                #print(free)
                scheduled.append(current_process)
                #current_process = (current_process)%M+1
                if not free:
                    free=[*range(1,M+1)]
                current_process = random.choice(free)
        #print(scheduling)
        #print("\n\n")
        #second path, prio 0
        #print(free)
        #print(cpu_busy)
        for i in free:
            if not free_to_schedule:
                print('break')
                break
            if len(free)==1:
                print('len=1')
                current = free_to_schedule[free_to_schedule_work.index(min(free_to_schedule_work))]
            else:
                current = random.choice(free_to_schedule)
            current_process = random.choice(free)
            if current_process in cpu_busy:
                start_time=cpu_busy.get(current_process)
            else:
                start_time=0
            #print(start_time)
            runtime = inst.get('work')[current]/inst.get('freq_list')[inst.get('S')-1]
            #print('scheduling ' + str(current)+' from '+str(start_time)+' to ' + str(start_time+runtime))
            scheduling[current] = [current, current_process, inst.get('S'), start_time, start_time+runtime]
            cpu_busy[current_process] = start_time+runtime
            free.remove(current_process)
            scheduled.append(current_process)
            free_to_schedule_work.pop(free_to_schedule.index(current))
            free_to_schedule.remove(current)
            print(free)
            
        if not free:
            free=[*range(1,M+1)]

                

    makespan = 0
    for i in range(1,M+1):
        if(i in cpu_busy):
            if cpu_busy.get(i) > makespan:
                makespan = cpu_busy.get(i)
    energy = 0
    idletime = 0
    print(scheduling)
    for i in range(1,N+1):
        energy+= inst.get('power_list')[scheduling.get(i)[2]-1] * (scheduling.get(i)[4]-scheduling.get(i)[3])
        idletime+=scheduling.get(i)[4]-scheduling.get(i)[3]
    idletime = makespan*M-idletime
    energy+=idletime*inst.get('power_list')[0]
    #print(preds)
    #print(priority)
    print(makespan)
    with open(filename+'_output.dat', 'w') as outfile:
        outfile.write(str(N)+'\n')
        outfile.write(str(makespan)+'\n')
        outfile.write(str(energy)+'\n')
        for i in range(1,N+1):
            outfile.write(str(i) + ' '+ str(scheduling.get(i)[1]) + ' ' + str(scheduling.get(i)[2])+ ' '+ str(scheduling.get(i)[3]) + ' ' + str(scheduling.get(i)[4])+'\n')
    

def main():
    filename = "instances/student_instance_3"
    inst = read_instance(filename+'.dat')
    #print(inst)
    build_minimal(inst, filename)


if __name__ == "__main__":
    main()
