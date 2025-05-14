from flask import Flask, render_template
import psutil
from operator import itemgetter

app = Flask(__name__)

def get_processes(sort_by:str='cpu', descending:bool=True):
    processes = []

    for process in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            process_info = process.info
            processes.append({
                'pid': process_info['pid'],
                'name': process_info['name'],
                'cpu': process_info['cpu_percent'],
                'mem': process_info['memory_percent'],
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