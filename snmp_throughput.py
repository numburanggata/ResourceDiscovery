import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from pysnmp.hlapi import *

# SNMP settings
ROUTER_IP = "192.168.1.1"
COMMUNITY = "public"
IF_INDEX = 1  # Change this to the correct interface index

# OIDs for interface traffic (bytes in and out)
OID_IN = f"1.3.6.1.2.1.2.2.1.10.{IF_INDEX}"
OID_OUT = f"1.3.6.1.2.1.2.2.1.16.{IF_INDEX}"

# Data storage
timestamps = []
in_rates = []
out_rates = []
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
prev_in = get_snmp_value(ROUTER_IP, COMMUNITY, OID_IN)
prev_out = get_snmp_value(ROUTER_IP, COMMUNITY, OID_OUT)

def update_graph(frame):
    """Fetch SNMP data, calculate throughput, and update the plot in real-time."""
    global prev_in, prev_out
    current_time = time.time() - start_time
    new_in = get_snmp_value(ROUTER_IP, COMMUNITY, OID_IN)
    new_out = get_snmp_value(ROUTER_IP, COMMUNITY, OID_OUT)

    if new_in is None or new_out is None:
        print("SNMP data retrieval failed, skipping this interval.")
        return

    interval = 1  # 1-second update interval
    in_rate = (new_in - prev_in) * 8 / interval  # Convert bytes to bits per second
    out_rate = (new_out - prev_out) * 8 / interval

    # Update previous values
    prev_in, prev_out = new_in, new_out

    # Store data
    timestamps.append(current_time)
    in_rates.append(in_rate)
    out_rates.append(out_rate)

    # Keep only the last 60 data points for better visualization
    if len(timestamps) > 60:
        timestamps.pop(0)
        in_rates.pop(0)
        out_rates.pop(0)

    # Clear and re-draw plot
    ax.clear()
    ax.plot(timestamps, in_rates, label="Inbound (bps)", marker="o", linestyle="-", color="blue")
    ax.plot(timestamps, out_rates, label="Outbound (bps)", marker="s", linestyle="--", color="red")

    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Throughput (bps)")
    ax.set_title("Real-time Network Throughput")
    ax.legend()
    ax.grid(True)

# Set up the Matplotlib figure
fig, ax = plt.subplots(figsize=(10, 5))

# Run real-time animation (updates every 1 second)
ani = animation.FuncAnimation(fig, update_graph, interval=1000)

plt.show()
