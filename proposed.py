import nmap
import socket
import argparse
import subprocess
import re
import multiprocessing
import time
import csv
from tabulate import tabulate
import ipaddress
from threading import Event

with open('20common_ports.txt', 'r') as file:
	# Read the lines of the file and store them as elements in a list
	common_ports = file.readlines()
str_common_ports = [ports.strip() for ports in common_ports]

str_common_ports = ','.join(str_common_ports)
target = '192.168.0.0/21'

def nmap_parse(scan_result):

	ip_address_all, ports_all, subnet_all = [], [], []

	hosts = re.findall(r'(Nmap scan report for .*?)(?=\nNmap scan report for|\Z)', scan_result, re.DOTALL)
	if not hosts:
		hosts = re.findall(r'(Nmap scan report for .*?)(?=\nNmap done|\Z)', scan_result, re.DOTALL)

	for host in hosts:
		ip_match = re.search(r"(?<=Nmap scan report for )[\d\.]+", host)
		
		ip_address = ip_match.group() if ip_match else None
		ports = re.findall(r"(\d+)(?=/tcp\s+open)", host)
		if not ports:
			ports = ['None']
		subnet = str(ipaddress.ip_network(ip_address + '/24', strict=False))
		
		ip_address_all.append(ip_address)
		ports_all.append(ports)
		subnet_all.append(subnet)

	return ip_address_all, ports_all, subnet_all

			
def extract_ip(ip_string):
	ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
	# Use re.findall to find all matches in the input string
	matches = re.findall(ip_pattern, ip_string)

	match = re.search(r"(?<=open port )\d+", ip_string)

	# Return the first match (if any)
	if matches and match:
		return matches[0], match.group()

def deep_scan(target_host):
	
	print('DEEP SCAN: ' + target_host)

	nm = subprocess.Popen(['nmap','-n','-F','-PS'+str_common_ports, target_host], bufsize=100000, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	
	allstring = '' 
	hosts = {}
	stdout_data, stderr_data = nm.communicate()
	allstring = stdout_data.decode()

	target, ports, subnet = nmap_parse(allstring)
	

	existing = False
	with open('scan_result.csv', 'r') as f:
		for line in f:
			ip_existing, subnet_existing, ports_existing= line.strip().split(',')
			#print(ip_existing, subnet_existing, ports_existing)
			#print(target[0], subnet[0])
			if ip_existing == target[0] and subnet_existing == subnet[0]:
				#print('match found')
				existing = True
				for x in ports[0]:	
					if x == ports_existing:
						pass
					else:
						with open('scan_result.csv', 'a') as g:
							g.write(f"{''.join(target[0])},{''.join(subnet[0])},{x}\n")
			else:
				pass

	if existing == False:
		if ports[0] == 'None':
			ports_existing = ['None']
		else:
			ports_existing = ports[0]

	for i in ports_existing:
		with open('scan_result.csv', 'a') as f:
			f.write(f"{''.join(target[0])},{''.join(subnet[0])},{i}\n")

def complementing_scan(target_host):
	print('COMPLEMENTING SCAN: ' + target_host)

	nm = subprocess.Popen(['nmap','-n', target_host], bufsize=100000, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	
	allstring = '' 
	hosts = {}
	stdout_data, stderr_data = nm.communicate()
	allstring = stdout_data.decode()

	target, ports, subnet = nmap_parse(allstring)


	
	for i in range(len(target)):
		existing = False
		# print(target[i], ports[i], subnet[i])
		with open('scan_result.csv', 'r') as f:
			content = f.readlines()

		for line in content:
			ip_existing, subnet_existing, ports_existing= line.strip().split(',')
			if ip_existing == target[i] and subnet_existing == subnet[i]:
				existing = True
				for x in ports[i]:	
					if x in ports_existing:
						pass
					else:
						# print(f"{''.join(t/arget[i])},{''.join(subnet[i])},{x}\n")
						with open('scan_result.csv', 'a') as g:
							g.write(f"{''.join(target[i])},{''.join(subnet[i])},{x}\n")
				break
			else:
				pass

		# if existing == False:
			# if len(ports[i]) == 1:
			# 	#print(f"{''.join(target[i])},{''.join(subnet[i])},{ports[i]}\n")
			# 	pass
			# else:
			# for o in ports[]
			# ports_existing = ports[i]

		for l in ports[i]:
			# pass
			# print(f"{''.join(target[i])},{''.join(subnet[i])},{l}\n")
			with open('scan_result.csv', 'a') as f:
				f.write(f"{''.join(target[i])},{''.join(subnet[i])},{l}\n")

def cleansort(target_subnet):
	unique_entries = set()

	with open("scan_result.csv", "r") as f:
		lines = f.readlines()

	# Preserve the header
	header = lines[0]
	data = lines[1:]  # Skip header

	# Process and remove duplicates
	for line in data:
		unique_entries.add(line.strip())  # strip() to remove trailing newlines

	# Write back unique data
	print("\nHASIL PEMINDAIAN: " + target_subnet)
	with open("pretty_result.csv", "w") as f:
		f.write(header)  # Write header first
		for entry in sorted(unique_entries):  # Sort for better readability
			print(entry)
			f.write(entry + "\n")


def probe(target_subnet):

	with open('scan_result.csv', 'w') as f:
		f.write(f"host,subnet,ports\n")
		f.close()

	print("PROBE DENGAN MASSCAN: \t" + target_subnet)
	probe_scan = subprocess.Popen(['sudo', 'masscan','--rate=1000','-p' + str_common_ports, target_subnet], bufsize=100000, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	last_probe_time = time.time()
	processes = []
	ongoing_scan = []
	
	while True:
		output = probe_scan.stdout.readline()
		if output:
			regex_host_ip, regex_host_port = extract_ip(str(output.strip().decode()))
			if regex_host_ip:
				subnet_ip = str(ipaddress.ip_network(regex_host_ip + '/24', strict=False))
				host_exist = False
				with open('scan_result.csv', 'r') as f:
					for line in f:
						ip, _, _= line.strip().split(',')
						if ip == regex_host_ip:
							host_exist = True
				if host_exist or regex_host_ip in ongoing_scan:
					print("HOST DITEMUKAN: " + regex_host_ip + " port " + regex_host_port+" TCP")
					pass
				
				else:
					print("HOST DITEMUKAN: " + regex_host_ip + " port " + regex_host_port+" TCP")
					ongoing_scan.append(regex_host_ip)
					
					
					deep = multiprocessing.Process(target=deep_scan, args=(regex_host_ip,))
					deep.start()
					processes.append(deep)

					if subnet_ip not in ongoing_scan:
						complement = multiprocessing.Process(target=complementing_scan, args=(subnet_ip,))
						complement.start()
						processes.append(complement)
						ongoing_scan.append(subnet_ip)

					# with multiprocessing.Pool(processes=2) as pool:
					# 	results = []

					# 	results.append(pool.apply_async(deep_scan, (regex_host_ip,)))
					# 	#results.append(pool.apply_async(complementing_scan, (subnet_ip,)))

					# 	for r in results:
					# 		r.wait(
		
		if probe_scan.poll() is not None:
			print("PROBING SELESAI")
			break
	
	for p in processes:
		p.join()
	print("SCAN SELESAI")
	cleansort(target_subnet)

if __name__ == "__main__":
	probe(target)