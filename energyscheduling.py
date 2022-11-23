from parse_instance import read_instance
import numpy as np

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
    for i in range(N):
        if i in preds:
            if priority[i-1]==0:
                priority[i-1] = 1
            for j in preds.get(i):
                priority[j-1] = 2
    flag = True
    current_max=2
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
    current_process=1
    for i in range(current_max,-1,-1):
        for j in range(N):
            if(priority[j] == i):
                start_time = 0
                if j+1 in preds:
                    start_time=0
                    for k in preds.get(j+1):
                        if scheduling.get(k)[-1] > start_time:
                            start_time = scheduling.get(k)[-1]
                if current_process in cpu_busy:
                    start_time = max(cpu_busy.get(current_process),start_time)
                runtime = inst.get('work')[j]/inst.get('freq_list')[inst.get('S')-1]
                scheduling[j+1] = [j+1, current_process, inst.get('S'), start_time, start_time+runtime]
                cpu_busy[current_process] = start_time+runtime
                current_process = (current_process)%M+1
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
    with open(filename+'_output.dat', 'w') as outfile:
        outfile.write(str(N)+'\n')
        outfile.write(str(makespan)+'\n')
        outfile.write(str(energy)+'\n')
        for i in range(1,N+1):
            outfile.write(str(i) + ' '+ str(scheduling.get(i)[1]) + ' ' + str(scheduling.get(i)[2])+ ' '+ str(scheduling.get(i)[3]) + ' ' + str(scheduling.get(i)[4])+'\n')
    

def main():
    filename = "instances/student_instance_4"
    inst = read_instance(filename+'.dat')
    print(inst)
    build_minimal(inst, filename)


if __name__ == "__main__":
    main()
