import csv
import os
import re

def read_csv(file_path):
    """Reads a CSV file and returns a dictionary where the first column is the key and the second and third columns are stored as a list."""
    data = {}
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) < 3:
                continue  # Skip invalid rows
            key = row[1]
            value = row[2]
            if key in data:
                data[key].append(value)
            else:
                data[key] = [value]
    return data

def check_csv_files(directory, reference_dict):
    """Reads every file with '-thout.csv' in its name and checks if its content matches reference_dict."""
    for filename in os.listdir(directory):
        #if '-thout.csv' in filename:
        if '-th.csv' in filename:
            file_path = os.path.join(directory, filename)
            print(filename)
            with open(file_path, mode='r', newline='', encoding='utf-8') as file:
                content = list(csv.reader(file))
            
            allstring = ''
            hosts = {}
            for x in content[3:42]:
                print(x[-1])


            ##   NMAP
            # allstring = ''
            # hosts = {}
            # for x in content:
            #     contentstring = ''.join(x) + '\n'
            #     allstring = allstring + contentstring

            # print(allstring[-8:-2])
            # hosts = re.findall(r'(Nmap scan report for .*?)(?=\nNmap scan report for|\Z)', allstring, re.DOTALL)

            # for key in reference_dict:
            #     for port in reference_dict[key]:
            #         #print(key,port)

            #         if port == 'none':
            #             port = 'is up'
            #             port_pattern = re.compile(re.escape(port))
            #         else:
            #             port_pattern = re.compile(re.escape(port)+'/')

            #         key_pattern = re.compile(re.escape(key))

                    
                    

                    
            #         found = 0
            #         #print(key_pattern, port_pattern)
            #         for host in hosts:
            #             #print(rowstrinig)
            #             if key_pattern.search(host) and port_pattern.search(host):
            #                found = 1
                           
            #                #print(host)
            #                break
            #         # print(found)
            ### NMAP


            # for key in reference_dict:
            #     for port in reference_dict[key]:
            #         #print(key,port)
            #         key_pattern = re.compile(re.escape(key))
            #         port_pattern = re.compile(re.escape(port))
                    
            #         found = 0
                    
            #         for row in content:
            #             rowstring = ', '.join(row)

            #             #print(rowstrinig)
            #             if key_pattern.search(rowstring) and port_pattern.search(rowstring):
            #                 found = 1
            #                 #print(row)
            #                 break



# Example usage:
reference_dict = read_csv('expected_target.csv')
print(reference_dict)

#check_csv_files('/home/kali/ResourceDiscovery/nmap-pingsyn', reference_dict)
#check_csv_files('/home/kali/ResourceDiscovery/nmap-basic', reference_dict)
check_csv_files('/home/kali/ResourceDiscovery/rustscan-basic', reference_dict)
#check_csv_files('/home/kali/ResourceDiscovery/zmap-basic-100ports', reference_dict)
#check_csv_files('/home/kali/ResourceDiscovery/masscan-basic-100ports', reference_dict)
