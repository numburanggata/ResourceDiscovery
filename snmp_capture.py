import time
import matplotlib.pyplot as plt
from pysnmp.hlapi import *

# SNMP Settings
ROUTER_IP = "192.168.1.1"  # Change to your router IP
COMMUNITY_STRING = "public"
SNMP_PORT = 161
CPU_OID = "1.3.6.1.4.1.9.2.1.56.0"  # CPU Load (5s avg)
MEM_USED_OID = ".1.3.6.1.4.1.9.9.48.1.1.6.1"  # Used memory
MEM_FREE_OID = ".1.3.6.1.4.1.9.9.48.1.1.5.1"  # Free memory

# Function to query SNMP data
def get_snmp_data(oid):
    try:
        iterator = getCmd(
            SnmpEngine(),
            CommunityData(COMMUNITY_STRING, mpModel=0),
            UdpTransportTarget((ROUTER_IP, SNMP_PORT)),
            ContextData(),
            ObjectType(ObjectIdentity(oid))
        )
        errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
        if errorIndication:
            print(f"SNMP Error: {errorIndication}")
            return None
        else:
            for varBind in varBinds:
                return int(varBind[1])  # Return SNMP value as integer
    except Exception as e:
        print(f"Error fetching SNMP data: {e}")
        return None

# Initialize data storage
time_values = []
cpu_usage = []
memory_usage = []

# Live Graph
plt.ion()  # Interactive mode ON
fig, ax = plt.subplots()

# Data Collection Loop
for i in range(300):  # Collect data for 30 iterations (~5 minutes)
    cpu = get_snmp_data(CPU_OID)
    #mem_used = get_snmp_data(MEM_USED_OID)
    #mem_free = get_snmp_data(MEM_FREE_OID)
    
    if cpu is not None:
        #total_mem = mem_used + mem_free
        #mem_usage_percent = (mem_used / total_mem) * 100

        time_values.append(i * 1)  # Time in seconds
        cpu_usage.append(cpu)

        print(time_values[-1], cpu_usage[-1])
        #memory_usage.append(mem_usage_percent)

        # Clear and update graph
        ax.clear()
        ax.plot(time_values, cpu_usage, label="CPU Usage (%)", color='r')
        #ax.plot(time_values, memory_usage, label="Memory Usage (%)", color='b')
        ax.set_xlabel("Time (seconds)")
        ax.set_ylabel("Usage (%)")
        ax.set_title("Cisco Router CPU Usage")
        ax.legend()
        plt.pause(1)  # Wait 1 seconds before next poll
    else:
        print("Failed to fetch SNMP data.")

plt.ioff()  # Turn off interactive mode
plt.show()  # Show final graph
