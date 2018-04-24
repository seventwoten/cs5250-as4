'''
CS5250 Assignment 4, Scheduling policies simulator
Sample skeleton program
Author: Minh Ho
Input file:
    input.txt
Output files:
    FCFS.txt
    RR.txt
    SRTF.txt
    SJF.txt

Apr 10th Revision 1:
    Update FCFS implementation, fixed the bug when there are idle time slices between processes
    Thanks Huang Lung-Chen for pointing out
Revision 2:
    Change requirement for future_prediction SRTF => future_prediction shortest job first(SJF), the simpler non-preemptive version.
    Let initial guess = 5 time units.
    Thanks Lee Wei Ping for trying and pointing out the difficulty & ambiguity with future_prediction SRTF.
'''
import sys
from collections import deque
from Queue import PriorityQueue

input_file = 'input.txt'

class Process:
    last_scheduled_time = 0
    def __init__(self, id, arrive_time, burst_time):
        self.id = id
        self.arrive_time = arrive_time
        self.burst_time = burst_time
        
        # add remaining time 
        self.remaining_time = burst_time
        
    #for printing purpose
    def __repr__(self):
        return ('[id %d : arrive_time %d,  burst_time %d]'%(self.id, self.arrive_time, self.burst_time))

def FCFS_scheduling(process_list):
    #store the (switching time, proccess_id) pair
    schedule = []
    current_time = 0
    waiting_time = 0
    for process in process_list:
        if(current_time < process.arrive_time):
            current_time = process.arrive_time
        schedule.append((current_time,process.id))
        waiting_time = waiting_time + (current_time - process.arrive_time)
        current_time = current_time + process.burst_time
    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time

#Input: process_list, time_quantum (Positive Integer)
#Output_1 : Schedule list contains pairs of (time_stamp, proccess_id) indicating the time switching to that proccess_id
#Output_2 : Average Waiting Time
def RR_scheduling(process_list, time_quantum ):
    schedule = [] 
    current_time = 0
    waiting_time = 0
    ready = deque()
    remaining_procs = len(process_list)
    i = 0
    
    while remaining_procs != 0: 
        # update ready queue (look ahead to all processes arriving within next time quantum)
        while i < len(process_list) and process_list[i].arrive_time <= current_time + time_quantum: 
            process_list[i].remaining_time = process_list[i].burst_time
            ready.append(process_list[i])
            i += 1
        
        if len(ready) != 0:
            # run next process
            process = ready.popleft()
            
            # handle case where process is erroneously queued before true arrival time
            if process.arrive_time > current_time: 
                current_time = process.arrive_time 
            
            schedule.append((current_time,process.id))
            run_time = process.remaining_time if process.remaining_time <= time_quantum else time_quantum
            current_time += run_time
            process.remaining_time -= run_time
            
            # check if process has finished
            if process.remaining_time == 0: 
                remaining_procs -= 1
                waiting_time += current_time - process.arrive_time - process.burst_time
            else: 
                # append the process at the back of the ready queue
                ready.append(process)
        else: 
            # fastforward to next process
            current_time = process_list[i].arrive_time
        
        
    return schedule, waiting_time/float(len(process_list))
    
    
def SRTF_scheduling(process_list):
    schedule = [] 
    current_time = 0
    waiting_time = 0
    sorted_ready = PriorityQueue()
    remaining_procs = len(process_list)
    i = 0
    process = process_list[i]
    
    while remaining_procs != 0: 
        # update sorted ready queue 
        if i < len(process_list) and process_list[i].arrive_time == current_time: 
            process_list[i].remaining_time = process_list[i].burst_time
            sorted_ready.put((process_list[i].remaining_time, process_list[i]))
            i += 1
            
        if not sorted_ready.empty(): 
            # run next process
            process = sorted_ready.get()[1]
            
            # run process until next process arrives, or until it finishes, whichever is earlier
            time_to_next_arrival = process_list[i].arrive_time - current_time if i < len(process_list) else float("inf")
            
            schedule.append((current_time,process.id))
            run_time = process.remaining_time if process.remaining_time < time_to_next_arrival else time_to_next_arrival
            current_time += run_time
            process.remaining_time -= run_time
            
            # check if process has finished
            if process.remaining_time == 0: 
                remaining_procs -= 1
                waiting_time += current_time - process.arrive_time - process.burst_time
            else: 
                # add the process to the sorted ready queue 
                sorted_ready.put((process.remaining_time, process))
   
        else: 
            # fastforward to next process
            current_time = process_list[i].arrive_time
        
            
    return schedule, waiting_time/float(len(process_list))
    

def SJF_scheduling(process_list, alpha):
    schedule = [] 
    current_time = 0
    waiting_time = 0
    ready = {}               # ready is a dictionary of pids : deques of process objects
    predicted_burst = {}     # predicted_burst is a dictionary of pids : predicted_burst values
    i = 0
    remaining_procs = len(process_list)

    while remaining_procs != 0: 
    
        # update ready queues with new processes arriving before current_time
        while i < len(process_list) and process_list[i].arrive_time <= current_time: 
            process_list[i].remaining_time = process_list[i].burst_time
            
            if process_list[i].id not in predicted_burst: # initialise predicted bursts for new pids
                predicted_burst[process_list[i].id] = 5 
                
            if process_list[i].id not in ready:           # add process to its ready queue
                ready[process_list[i].id] = deque([process_list[i]])
            else: 
                ready[process_list[i].id].append(process_list[i])
                
            i += 1
        
        # check if there are ready processes
        ready_size = 0
        for key, q in ready.items():
            ready_size += len(q)
            
        if ready_size != 0: 
            
            # find next ready process with shortest predicted burst
            sorted_ids = sorted(predicted_burst, key=predicted_burst.get)
            for id in sorted_ids: 
                if len(ready[id]) != 0:
                    process = ready[id].popleft()
                    break
            
            # run next process
            schedule.append((current_time,process.id))
            current_time += process.remaining_time
            process.remaining_time = 0
            remaining_procs -= 1
            waiting_time += current_time - process.arrive_time - process.burst_time
            
            # update estimate of predicted_burst
            predicted_burst[process.id] = alpha * predicted_burst[process.id] + (1-alpha) * process.burst_time
            
        else: 
            # fastforward to next process
            current_time = process_list[i].arrive_time
            
    return schedule, waiting_time/float(len(process_list))

def read_input():
    result = []
    with open(input_file) as f:
        for line in f:
            array = line.split()
            if (len(array)!= 3):
                print ("wrong input format")
                exit()
            result.append(Process(int(array[0]),int(array[1]),int(array[2])))
    return result
def write_output(file_name, schedule, avg_waiting_time):
    with open(file_name,'w') as f:
        for item in schedule:
            f.write(str(item) + '\n')
        f.write('average waiting time %.2f \n'%(avg_waiting_time))


def main(argv):
    process_list = read_input()
    print ("printing input ----")
    for process in process_list:
        print (process)
    print ("simulating FCFS ----")
    FCFS_schedule, FCFS_avg_waiting_time =  FCFS_scheduling(process_list)
    write_output('FCFS.txt', FCFS_schedule, FCFS_avg_waiting_time )
    print ("simulating RR ----")
    RR_schedule, RR_avg_waiting_time =  RR_scheduling(process_list,time_quantum = 2)
    write_output('RR.txt', RR_schedule, RR_avg_waiting_time )
    print ("simulating SRTF ----")
    SRTF_schedule, SRTF_avg_waiting_time =  SRTF_scheduling(process_list)
    write_output('SRTF.txt', SRTF_schedule, SRTF_avg_waiting_time )
    print ("simulating SJF ----")
    SJF_schedule, SJF_avg_waiting_time =  SJF_scheduling(process_list, alpha = 0.5)
    write_output('SJF.txt', SJF_schedule, SJF_avg_waiting_time )

    # Test different values of Q for RR 
    print ("simulating RR with varying Q (start = 1, stop_inclusive = 10, step = 1) ----")
    RR_wt_list = []
    for q in range(1, 11):
        RR_schedule, RR_avg_waiting_time = RR_scheduling(process_list,time_quantum = q)
        RR_wt_list.append((q, RR_avg_waiting_time))
    write_output('RR_test.txt', RR_wt_list, min(RR_wt_list, key = lambda t: t[1])[1] )
    
    # Test different values of alpha for SJF 
    print ("simulating SJF with varying alpha (start = 0, stop_inclusive = 1, step = 0.1) ----")
    SJF_wt_list = []
    for a in [round(x * 0.1, 1) for x in range(0, 11)]:
        SJF_schedule, SJF_avg_waiting_time =  SJF_scheduling(process_list, alpha = a)
        SJF_wt_list.append((a, SJF_avg_waiting_time))
    write_output('SJF_test.txt', SJF_wt_list, min(SJF_wt_list, key = lambda t: t[1])[1] )
    
if __name__ == '__main__':
    main(sys.argv[1:])