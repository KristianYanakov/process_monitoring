import time
import psutil
import argparse
from tabulate import tabulate

from collections import defaultdict, deque

DATA_AVAILABLE_ELEMENTS_AT_A_TIME = 5
THRESHOLD_COEFFICIENT = 3

cpu_data_log = defaultdict(lambda: deque(maxlen=DATA_AVAILABLE_ELEMENTS_AT_A_TIME))
mem_data_log = defaultdict(lambda: deque(maxlen=DATA_AVAILABLE_ELEMENTS_AT_A_TIME))

def detect_spikes(curr, log_history):
    if len(log_history) < DATA_AVAILABLE_ELEMENTS_AT_A_TIME:
        return False #We don't have enough data yet and are still collecting to have 5 el

    avg = sum(log_history) / len(log_history)

    if curr > (avg * THRESHOLD_COEFFICIENT):
        return True

def get_processes():
    processes = []

    for process in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            process_info = process.info

            pid = process_info['pid']
            name = process_info['name']
            cpu = process_info['cpu_percent']
            mem = process_info['memory_percent']

            cpu_data_log[pid].append(cpu)
            mem_data_log[pid].append(mem)

            cpu_spike = detect_spikes(cpu, cpu_data_log[pid])
            mem_spike = detect_spikes(mem, mem_data_log[pid])

            processes.append({
                'pid': process_info['pid'],
                'name': process_info['name'],
                'cpu': process_info['cpu_percent'],
                'mem': process_info['memory_percent'],
                'cpu_spike': cpu_spike,
                'mem_spike': mem_spike,
            })




        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return processes

#print(get_processes())

def display_processes(processes:list, sort_by:str, descending:bool):
    sorted_processes = sorted(processes, key = lambda x: x[sort_by], reverse=descending)

    table = []
    #table = [[process['pid'], process['name'], f"{process['cpu']:.1f}%", f"{process['mem']:.1f}%"] for process in sorted_processes]

    for process in sorted_processes:
        alert = ""

        if process.get('cpu_spike'):
            alert += "DANGEROUS CPU"

        if process.get("mem_spike"):
            alert += "DANGEROUS MEM"

        table.append([
            process['pid'],
            process['name'],
            f"{process['cpu']:.2f}%",
            f"{process['mem']:.2f}%",
            alert,
        ])
    print(tabulate(table, headers=['PID', 'Name', 'CPU %', "Memory %", "Alert"], tablefmt='pretty'))


#display_processes(get_processes(), 'pid', True)

def monitor(interval: float, sort_by: str, descending: bool):
    print(f"Monitoring processes every {interval} seconds. Sort by: {sort_by}, Order by: {"Descending" if descending else "Ascending"}\n")

    while True:
        processes = get_processes()
        display_processes(processes, sort_by, descending)
        print("\n-- Press Ctrl+C f2 to stop -----\n")
        time.sleep(interval)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Process Monitoring Application")
    parser.add_argument("-i", "--interval", type=int, default=3, help="Refresh interval in seconds")
    parser.add_argument("-s", "--sort", choices=['pid', 'name', 'cpu', 'mem'], default='cpu', help='Sort by')
    parser.add_argument("-d", "--descending", action="store_true", help = "Sort in descending order")

    args = parser.parse_args()
    monitor(args.interval, args.sort, args.descending)
    #this is if you want to call it with given values:
    #python main.py --interval 2 --sort mem --desc
    #refresh the table every 2 seconds, sort by memory usage descending
