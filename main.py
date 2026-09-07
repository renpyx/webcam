import json
import os
import shutil
import time
from datetime import datetime, timedelta
import subprocess


def download(webcam_name, hour, ffmpeg_path, url_template, custom):
    current_time = datetime.now().replace(hour=int(hour), minute=0, second=0, microsecond=0)

    target_time = current_time

    if custom == "earlier":
        target_time = current_time - timedelta(minutes=5)

    f_year = target_time.strftime("%Y")
    f_month = target_time.strftime("%m")
    f_day = target_time.strftime("%d")
    f_hour = target_time.strftime("%H")
    f_minute = target_time.strftime("%M")

    f_date_path = current_time.strftime("%Y-%m-%d")

    info_time = f"{datetime.now():%d.%m.%Y %H:%M}"
    print(f"{info_time} > '{webcam_name}' -> {f_day}.{f_month}. {f_hour}:{f_minute} ...")

    url = url_template.replace("%year%", f_year) \
        .replace("%month%", f_month) \
        .replace("%day%", f_day) \
        .replace("%hour%", f_hour) \
        .replace("%minute%", f_minute)

    time_stamp = str(int(time.time()))

    archive_dir = os.path.join("archive", webcam_name, f_date_path)
    filepath = os.path.join(archive_dir, f"{hour}.jpg")

    os.makedirs(archive_dir, exist_ok=True)
    if custom == "ffmpeg_first_frame":
        cmd = [
            ffmpeg_path,
            "-y",
            "-loglevel", "error",
            "-i", url,
            "-update", "1",
            "-frames:v", "1",
            "-q:v", "2",
            filepath,
        ]
        _run_with_retries(cmd, attempts=3, delay=30)
    else:
        cmd = ["curl", "-L", "-s", "-k", "-o", filepath, f"{url}?ts={time_stamp}"]
    subprocess.run(cmd, check=True)

    time.sleep(0.1)


def _run_with_retries(cmd, attempts=3, delay=10):
    last_err = ""
    for i in range(1, attempts + 1):
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return
        last_err = result.stderr.strip()
        print(f"    ffmpeg attempt {i}/{attempts} failed: {last_err}")
        if i < attempts:
            time.sleep(delay)
    raise RuntimeError(f"ffmpeg failed after {attempts} attempts: {last_err}")


def main():
    info_time = f"{datetime.now():%d.%m.%Y %H:%M}"
    print(f"{info_time} > starting...")
    print(f"{info_time} > loading config...")

    with open("settings/config.json") as f:
        config = json.load(f)

    cfg_ffmpeg_path = config.get("ffmpeg_path")
    print(f"{info_time} > ffmpeg: {cfg_ffmpeg_path}")

    hour = datetime.now().strftime("%H")

    shutil.rmtree("wc_test", ignore_errors=True)

    for root, dirs, files in os.walk("settings/webcams"):
        for file in files:
            try:
                with open(os.path.join(root, file)) as f:
                    json_data = json.load(f)

                webcam_name = json_data.get("name")
                url = json_data.get("url")
                custom = json_data.get("custom", "")

                download(webcam_name, hour, cfg_ffmpeg_path, url, custom)
                time.sleep(0.1)
            except Exception as e:
                print(f"Error processing {file}: {e}")


if __name__ == "__main__":
    main()
