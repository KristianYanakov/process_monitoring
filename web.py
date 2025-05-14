from flask import Flask, render_template
import psutil
from operator import itemgetter
from collections import defaultdict, deque
app = Flask(__name__)

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

def get_processes(sort_by:str='cpu', descending:bool=True):
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

    return sorted(processes, key=itemgetter(sort_by), reverse=descending)

@app.route('/')
def index():
    sort_by = 'cpu'
    descending = True
    processes = get_processes(sort_by, descending)

    return render_template("index.html", processes=processes)


if __name__ == "__main__":
    app.run(debug=True)

#run by typing
#python web.py
