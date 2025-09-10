# monitor.py
import requests
import time

def check_server_health():
    try:
        response = requests.get('http://localhost:5000/api/player/stats?username=TestAgent', timeout=5)
        if response.status_code == 200:
            print(f"✓ Server healthy at {time.ctime()}")
        else:
            print(f"✗ Server error: {response.status_code}")
    except:
        print("✗ Server unreachable")

if __name__ == '__main__':
    while True:
        check_server_health()
        time.sleep(300)  # Check every 5 minutes
