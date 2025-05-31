ResourceDiscovery or ZTScan is a network discovery tool developed to support Zero Trust Architecture (ZTA) implementation, particularly in the context assessment phase. It combines the power of masscan and nmap to identify active hosts and their exposed services, serving as a foundational step in Zero Trust enforcement such as microsegmentation and access control policies.

    🛡️ Developed for research purposes, ZTScan is introduced as part of this research https://ejournal.nusamandiri.ac.id/index.php/jitk/article/view/6628

🔍 Purpose

ZTScan was built to automate asset and service discovery in a network, providing the situational awareness required for implementing Zero Trust security strategies. This tool assists network administrators in mapping out reachable hosts and open ports, which are essential for:

    Identifying trusted vs untrusted communication

    Planning segmentation policies

    Creating granular access rules

⚙️ Requirements

ZTScan is designed to run on Linux, preferably Kali Linux, with the following tools installed:

    masscan

    nmap

    Python 3.x

    Ensure both masscan and nmap are accessible via your system's PATH.

📁 File Structure

    proposed.py: Main script where you define the target subnet/IPs directly in the code.

    20common_ports.txt: External text file where you list the ports to scan using masscan.

🚀 Usage

    Edit the target
    Open proposed.py and set the target host(s) manually:

target = "192.168.1.0/24"

Set the ports
Edit the ports.txt file and list ports separated by enter, e.g.:

22
80
etc,,

Run the tool

    python3 proposed.py

    The tool will:

        Run masscan to discover active hosts and open ports

        Follow up with nmap for deeper service enumeration

        Output results for further Zero Trust analysis

📌 Notes

    The current version requires manual editing of the target IP in the .py script and ports in ports.txt.

    Root privileges may be required depending on your Linux configuration for raw socket scanning.

    Future improvements may include argument parsing and configuration files for better usability.

📄 Citation

If you're using ZTScan for academic work, please cite the accompanying paper published in JITK:

https://ejournal.nusamandiri.ac.id/index.php/jitk/article/view/6628

📬 Contact

For questions or contributions, please reach out via GitHub Issues or contact [numburanggata@gmail.com].
