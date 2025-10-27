# notify_matches.py
import os
import glob
from utils import load_json, save_json
from model import get_job_matches # Job match function import karein
from notify import notify_user
from pathlib import Path
import traceback # Error debugging ke liye

USERS_DIR = Path("users")
JOBS_PATH = Path("data_resume/jobs.json")

def load_jobs():
    """Jobs file load karta hai aur har job ko ek unique ID deta hai."""
    if not JOBS_PATH.exists() or os.path.getsize(JOBS_PATH) == 0:
        print(f"⚠️ Jobs file not found or empty at {JOBS_PATH}. Exiting notifier.")
        return []
    try:
        jobs = load_json(str(JOBS_PATH))
        if not isinstance(jobs, list):
            print(f"❌ Error: {JOBS_PATH} does not contain a list.")
            return []

        # Har job ko ek unique ID dein (title+desc ke hash se)
        processed_jobs = []
        for j in jobs:
            # ID banane ke liye title aur description ka shuruati hissa istemaal karein
            identifier = (j.get("title","").strip() + "|" + j.get("description","").strip())[:250]
            # Hash se stable ID banayein (string format mein)
            j["__id"] = str(abs(hash(identifier)))
            processed_jobs.append(j)
        print(f"Loaded {len(processed_jobs)} jobs with IDs.")
        return processed_jobs
    except Exception as e:
        print(f"❌ Error reading or processing {JOBS_PATH}: {e}")
        return []

def load_user_files():
    """'users' directory se sabhi .json files load karta hai."""
    if not USERS_DIR.is_dir():
        print(f"⚠️ Users directory '{USERS_DIR}' not found. No notifications to send.")
        return []

    user_files = []
    for p in sorted(USERS_DIR.glob("*.json")):
        u = load_json(str(p))
        if u and isinstance(u, dict) and "id" in u and "resume_text" in u:
            # Default values set karein agar missing hain
            u.setdefault("last_notified_job_ids", [])
            u.setdefault("match_threshold", 0.70) # Default threshold 70%
            u.setdefault("notify_email", False)
            u.setdefault("notify_telegram", False)
            u.setdefault("notify_whatsapp", False)
            user_files.append((p, u)) # Path aur user data dono store karein
        else:
            print(f"⚠️ Skipping invalid or incomplete user file: {p.name}")
    print(f"Loaded {len(user_files)} valid user profiles.")
    return user_files

def main():
    print("\n--- Starting Notification Process ---")
    jobs = load_jobs()
    if not jobs:
        print("No jobs loaded. Exiting.")
        return

    user_files = load_user_files()
    if not user_files:
        print("No users loaded. Exiting.")
        return

    total_notifications_sent = 0

    for user_path, user in user_files:
        user_id = user.get('id', user_path.stem)
        print(f"\nProcessing user: {user.get('name', user_id)} (Threshold: {user.get('match_threshold') * 100:.0f}%)")
        resume_text = user.get("resume_text", "")
        if not resume_text:
            print("  ❌ No resume_text found for user. Skipping.")
            continue

        # Get job matches for this user's resume
        try:
            # get_job_matches ab score ke saath jobs return karta hai
            matches = get_job_matches(resume_text)
            if not matches:
                 print("  ⚠️ No matches returned by model for this resume.")
                 continue
            print(f"  Found {len(matches)} potential matches from model.")

        except Exception as e:
            print(f"  ❌ Error getting job matches for user {user_id}: {e}")
            print(traceback.format_exc()) # Print full error for debugging
            continue

        # Filter and notify
        current_notified_ids = set(user.get("last_notified_job_ids", []))
        newly_notified_for_this_user = []
        user_notification_count = 0

        for job in matches:
            job_id = job.get("__id")
            score = job.get("score", 0.0)

            if not job_id:
                print(f"  ⚠️ Skipping job with missing ID: {job.get('title','Unknown Title')}")
                continue

            # Check threshold and if already notified
            if score >= float(user.get("match_threshold", 0.7)) and job_id not in current_notified_ids:
                print(f"  -> Match Found! Notifying about '{job.get('title')[:80]}' (Score: {score:.3f})")
                try:
                    # Notify function ko score bhi pass karein taaki woh use message mein daal sake
                    job_with_score = job.copy() # Make a copy to add score for notify_user
                    job_with_score['score'] = score
                    notify_user(user, job_with_score)
                    newly_notified_for_this_user.append(job_id)
                    user_notification_count += 1
                    total_notifications_sent += 1
                except Exception as e:
                     print(f"  ❌ Error during notification for job {job_id}: {e}")
                # Limit notifications per run per user (optional)
                # if user_notification_count >= 5:
                #     print("  Reached notification limit for this user in this run.")
                #     break

        # Update user file if new notifications were sent
        if newly_notified_for_this_user:
            updated_notified_ids = list(current_notified_ids.union(newly_notified_for_this_user))
            # Limit history size (optional, keep last 200 notified IDs)
            user["last_notified_job_ids"] = updated_notified_ids[-200:]
            if save_json(str(user_path), user):
                print(f"  ✅ Updated {user_path.name} with {len(newly_notified_for_this_user)} new notified job IDs (Total: {len(user['last_notified_job_ids'])})")
            else:
                print(f"  ❌ Failed to update {user_path.name}")
        else:
            print("  ✅ No new jobs above threshold found for this user.")

    print(f"\n--- Notification Process Complete ---")
    print(f"Total notifications sent in this run: {total_notifications_sent}")

if __name__ == "__main__":
    main()