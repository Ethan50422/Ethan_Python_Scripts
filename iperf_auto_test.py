# Program: USB Tethering Embedded Performance(iPerf)
import subprocess
import time
import re
from os import _exit, getcwd
import argparse

runtime = "120"
host_pc_port = "5201"

# Get arguments from outside
parser = argparse.ArgumentParser()
parser.add_argument("-t", "--time", help="", type=int)
args = parser.parse_args()
# print(args.time)
if args.time != None:
    runtime = args.time

# Get DUT's information
dut_model = subprocess.check_output(
    "adb shell getprop ro.product.product.model", shell=True).decode("utf-8").strip()
dut_name = subprocess.check_output(
    "adb shell getprop ro.product.product.name", shell=True).decode("utf-8").strip()
dut_rom = subprocess.check_output(
    "adb shell getprop ro.product.build.id", shell=True).decode("utf-8").strip()
dut_type = subprocess.check_output(
    "adb shell getprop ro.product.build.type", shell=True).decode("utf-8").strip()  # userdebug
#print(dut_model, dut_name, dut_rom, dut_type)

# check USB speed
speed_type = subprocess.check_output("adb shell cat sys/class/udc/*/current_speed | head -1",
                                     shell=True).decode("utf-8").strip()  # ex: super-speed plus


def Get_Host_PC_IP():
    """Get Host PC IP address"""
    result = subprocess.check_output(
        "ifconfig", shell=True, stderr=subprocess.PIPE)
    host_pc_ip = re.search("192\.168\.\d+\.\d+", str(result)).group()
    # print(f"{host_pc_port}")
    # print(host_pc_ip)
    return host_pc_ip

# Open terminal and execute cmd


def open_terminal_execute(host_pc_ip):
    try:
        # Opne terminal and server
        subprocess.check_output(
            "gnome-terminal -e 'bash -c \"iperf3 -s; exec bash\"'", shell=True, stderr=subprocess.PIPE)

        # Execute TX: server to client
        #subprocess.check_output(f"gnome-terminal -e 'bash -c \"adb shell iperf3 -c {host_pc_ip} -p {host_pc_port} -t{runtime}; exec bash\"'", shell=True, stderr=subprocess.PIPE)

        time.sleep(2)
        tx_result = subprocess.check_output(
            f"adb shell iperf3 -c {host_pc_ip} -p {host_pc_port} -t{runtime}", shell=True, stderr=subprocess.PIPE).decode("utf-8").strip()
        # print(re)
        save_result_to_local_file(tx_result, "TX")
        time.sleep(5)

        # Execute RX: client to server
        #subprocess.check_output(f"gnome-terminal -e 'bash -c \"adb shell iperf3 -c {host_pc_ip} -p {host_pc_port} -t{runtime} --reverse; exec bash\"'", shell=True, stderr=subprocess.PIPE)
        rx_result = subprocess.check_output(
            f"adb shell iperf3 -c {host_pc_ip} -p {host_pc_port} -t{runtime} --reverse", shell=True, stderr=subprocess.PIPE).decode("utf-8").strip()
        save_result_to_local_file(rx_result, "RX")

    except:
        print("iperf fail to execute!")

# Save cmd result to local file


def save_result_to_local_file(content, orientation):
    """Save cmd result to local txt file"""
    try:
        current_time = time.strftime(
            "%Y-%m-%d", time.localtime())  # 2022-12-29
        # 2022-12-29_TX_Pixel 7a_lynx_TD4A.221205.011_userdebug.txt
        with open(f"{current_time}_{orientation}_{dut_model}_{dut_name}_{dut_rom}_{dut_type}", "w") as f:
            f.write(content)
        print("Result saves in " + getcwd())
    except:
        print("Save file fail.")


""" Main Entry """
try:
    subprocess.check_output("adb root", shell=True)
    subprocess.check_output("python3 wifi_connect.py",
                            shell=True)  # connect to wifi
    # switch to tethering
    subprocess.check_output("adb shell svc usb setFunctions ncm", shell=True)
    time.sleep(10)
    print("Speed Type :", speed_type)  # show current speed
    print("Runtime :", runtime)  # show execute time
    open_terminal_execute(Get_Host_PC_IP())
    print("iperf done successfully")
except:
    print("Something goes wrong!")
