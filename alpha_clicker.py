#!/usr/bin/env python3
import sys
import subprocess
import time
from pymavlink import mavutil

try:
    master = mavutil.mavlink_connection('/dev/ttyACM0', baud=115200)
    master.wait_heartbeat()
    print("succesfully connected to vehicle")
except Exception as e:
    print(f"Failed to connect to vehicle: {e}")
    sys.exit(1)

master.mav.request_data_stream_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_DATA_STREAM_RC_CHANNELS,
    1,1)
    
button_pressed = False
subprocess.run([
    "sudo","modprobe","v4l2loopback",
    "devices=1", "video_nr=0", 'card_label="SonyAlpha"', "exclusive_caps=1"
    ])
counter = 0
while True:
    msg = master.recv_match(type=['RC_CHANNELS_RAW','RC_CHANNELS'], blocking=True, timeout=1)
    if not msg:
        continue
    rc_channel = msg.chan9_raw

    if rc_channel > 1500 and not button_pressed:
        button_pressed = True

    if rc_channel < 1500:
        button_pressed = False

    if button_pressed == True:
        filename = f"image{counter}.jpg"
        subprocess.run([
            "gphoto2", "--capture-image-and-download", "--filename", filename
        ])
        counter += 1
    time.sleep(0.5)
