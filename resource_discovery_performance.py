import subprocess
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from pysnmp.hlapi import *
import multiprocessing
import csv
import threading
from datetime import datetime

with open('15common_ports.txt', 'r') as file:
    # Read the lines of the file and store them as elements in a list
    common_ports = file.readlines()
str_common_ports = [ports.strip() for ports in common_ports]

str_common_ports = ', '.join(str_common_ports)
target = '192.168.3.1'

def masscan_perf():

	time_begin = time.time()
	masscan_scan = subprocess.Popen(['sudo', 'masscan','--rate=1000','-p' + str_common_ports, target], bufsize=100000, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	for output in masscan_scan.stdout:
		if output:
			time_now = time.time()
			time_elapsed = time_now - time_begin
			print(output.decode("utf-8")[:-1], str(time_elapsed))

def nmap_perf():
    time_begin = time.time()
    global filename

    stdout_filename = filename[:-4] + 'out.csv'

    with open(stdout_filename, 'w') as file:
        scanproc = subprocess.Popen(['nmap','-n','-PS'+str_common_ports, target], bufsize=100000, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for output in scanproc.stdout:
            if output:
                time_now = time.time()
                time_elapsed = time_now - time_begin
                line = f"{output.decode('utf-8').strip()} {time_elapsed:.2f}s\n"

                file.write(line)

                # Optional: print to console as well
                print(line, end='')

def write_throughput_to_csv(list1, list2, list3, list4):

    if not (len(list1) == len(list2) == len(list3) == len(list4)):
        raise ValueError("All lists must have the same length.")
    
    global filename

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["FE00", "FE20", "FE30", "TOTAL_TH"])  # Header

        for i in range(len(list1)):
            writer.writerow([list1[i], list2[i], list3[i], list4[i]])

# SNMP settings
ROUTER_IP = "10.10.10.1"
COMMUNITY = "public"
#IF_INDEX = 4  # Change this to the correct interface index

# OIDs for interface traffic (bytes out)
OID_OUT_FE00 = f"1.3.6.1.2.1.2.2.1.16.1"
OID_OUT_FE20 = f"1.3.6.1.2.1.2.2.1.16.3"
OID_OUT_FE30 = f"1.3.6.1.2.1.2.2.1.16.4"

# Data storage
timestamps = []
out_rates_FE00 = []
out_rates_FE20 = []
out_rates_FE30 = []
out_total = []
start_time = time.time()

def get_snmp_value(ip, community, oid):
    """Fetch SNMP value using SNMP GET."""
    iterator = getCmd(
        SnmpEngine(),
        CommunityData(community, mpModel=0),
        UdpTransportTarget((ip, 161)),
        ContextData(),
        ObjectType(ObjectIdentity(oid))
    )

    errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

    if errorIndication:
        print(f"SNMP Error: {errorIndication}")
        return None
    elif errorStatus:
        print(f"SNMP Error: {errorStatus.prettyPrint()}")
        return None
    else:
        for varBind in varBinds:
            return int(varBind[1])

# Initial values for throughput calculation
prev_out_FE00 = get_snmp_value(ROUTER_IP, COMMUNITY, OID_OUT_FE00)
prev_out_FE20 = get_snmp_value(ROUTER_IP, COMMUNITY, OID_OUT_FE20)
prev_out_FE30 = get_snmp_value(ROUTER_IP, COMMUNITY, OID_OUT_FE30)

def update_graph(frame):
    """Fetch SNMP data, calculate throughput, and update the plot in real-time."""
    global prev_out_FE00, prev_out_FE20, prev_out_FE30
    current_time = time.time() - start_time
    new_out_FE00 = get_snmp_value(ROUTER_IP, COMMUNITY, OID_OUT_FE00)
    new_out_FE20 = get_snmp_value(ROUTER_IP, COMMUNITY, OID_OUT_FE20)
    new_out_FE30 = get_snmp_value(ROUTER_IP, COMMUNITY, OID_OUT_FE30)

    if new_out_FE20 is None or new_out_FE00 is None or new_out_FE30 is None:
        print("SNMP data retrieval failed, skipping this interval.")
        return

    interval = 1  # 1-second update interval
    #in_rate = (new_in - prev_in) * 8 / interval  # Convert bytes to bits per second
    out_rate_FE00 = (new_out_FE00 - prev_out_FE00) * 8 / interval
    out_rate_FE20 = (new_out_FE20 - prev_out_FE20) * 8 / interval
    out_rate_FE30 = (new_out_FE30 - prev_out_FE30) * 8 / interval

    # Update previous values
    prev_out_FE00, prev_out_FE20, prev_out_FE30 = new_out_FE00, new_out_FE20, new_out_FE30

    # Store data
    timestamps.append(current_time)
    #in_rates.append(in_rate)
    out_rates_FE00.append(out_rate_FE00)
    out_rates_FE20.append(out_rate_FE20)
    out_rates_FE30.append(out_rate_FE30)
    out_total.append(out_rate_FE00+out_rate_FE20+out_rate_FE30)

    # Keep only the last 60 data points for better visualization
    if len(timestamps) > 60:
        timestamps.pop(0)
        #in_rates.pop(0)
        out_rates_FE00.pop(0)
        out_rates_FE20.pop(0)
        out_rates_FE30.pop(0)
        out_total.pop(0)


    # Clear and re-draw plot
 
    ax.clear()
    #ax.plot(timestamps, in_rates, label="Inbound (bps)", marker="o", linestyle="-", color="blue")
    ax.plot(timestamps, out_rates_FE00, label="Outbound (bps)", marker="s", linestyle="--", color="red")
    ax.plot(timestamps, out_rates_FE20, label="Outbound (bps)", marker="s", linestyle="--", color="green")
    ax.plot(timestamps, out_rates_FE30, label="Outbound (bps)", marker="s", linestyle="--", color="blue")
    ax.plot(timestamps, out_total, label="Total Outbound (bps)", marker="s", linestyle="-", color="black")

    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Throughput (bps)")
    ax.set_title("Real-time Network Throughput")
    ax.legend()
    ax.grid(True)

def collect_th(start_time, duration=20):
    if time.time() - start_time >= duration:
        print("SNMP collection finished. Saving to CSV...")
        write_throughput_to_csv(out_rates_FE00, out_rates_FE20, out_rates_FE30, out_total)
        return
    #print("wjatt")
        
    """Fetch SNMP data, calculate throughput, and update the plot in real-time."""
    global prev_out_FE00, prev_out_FE20, prev_out_FE30
    current_time = time.time() - start_time
    new_out_FE00 = get_snmp_value(ROUTER_IP, COMMUNITY, OID_OUT_FE00)
    new_out_FE20 = get_snmp_value(ROUTER_IP, COMMUNITY, OID_OUT_FE20)
    new_out_FE30 = get_snmp_value(ROUTER_IP, COMMUNITY, OID_OUT_FE30)

    if new_out_FE20 is None or new_out_FE00 is None or new_out_FE30 is None:
        print("SNMP data retrieval failed, skipping this interval.")
        return

    interval = 2  # 1-second update interval
    #in_rate = (new_in - prev_in) * 8 / interval  # Convert bytes to bits per second
    out_rate_FE00 = (new_out_FE00 - prev_out_FE00) * 8 / interval
    out_rate_FE20 = (new_out_FE20 - prev_out_FE20) * 8 / interval
    out_rate_FE30 = (new_out_FE30 - prev_out_FE30) * 8 / interval

    # Update previous values
    prev_out_FE00, prev_out_FE20, prev_out_FE30 = new_out_FE00, new_out_FE20, new_out_FE30

    # Store data
    timestamps.append(current_time)
    #in_rates.append(in_rate)
    out_rates_FE00.append(out_rate_FE00)
    out_rates_FE20.append(out_rate_FE20)
    out_rates_FE30.append(out_rate_FE30)
    out_total.append(out_rate_FE00+out_rate_FE20+out_rate_FE30)

    

    threading.Timer(2, collect_th, [start_time, duration]).start()

def plot():	
	

	# Run real-time animation (updates every 1 second)
	ani = animation.FuncAnimation(fig, update_graph, interval=1000)

	plt.show()

    
if __name__ == "__main__":
    for _ in range(5):
        date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{date_str}_nmap_pingsyn-th.csv"                                                           ##  NAME TOOLS HERE
        processes = []

        # Set up the Matplotlib figure
        fig, ax = plt.subplots(figsize=(10, 5))

        start_time = time.time()

        p = multiprocessing.Process(target=collect_th, args=(start_time, 12))
        p.start()
        processes.append(p)

        time.sleep(5)

        #scan = multiprocessing.Process(target=masscan_perf, args=())
        scan = multiprocessing.Process(target=nmap_perf, args=())
        scan.start()
        processes.append(scan)
        
        for work in processes:
        	work.join()
