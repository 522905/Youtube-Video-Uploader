import threading

progress = {
    "status": "",
    "percent": 0
}

lock = threading.Lock()

def update_progress(status: str, percent: int):
    with lock:
        progress["status"] = status
        progress["percent"] = percent

    if percent >= 100:
        threading.Timer(10.0, reset_progress).start()

def reset_progress():
    with lock:
        progress["status"] = ""
        progress["percent"] = 0

def get_progress():
    with lock:
        return progress.copy()
