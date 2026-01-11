README 
==========

Project Name: WiFi Deauthentication Tool
Author: Mandeep
Profession: Cyber Security Professional
Language: Python
Platform: Linux
Run Level: Requires root privileges

------------------------------------------------------------
DESCRIPTION
------------------------------------------------------------

This project is a Python-based WiFi deauthentication tool developed for
cybersecurity learning, research, and authorized testing purposes.

The tool automatically scans all wireless networks within range,
detects access points and connected clients, and performs continuous
deauthentication attacks. Once started, the attack runs repeatedly
and indefinitely until manually stopped by the user.

This tool demonstrates how deauthentication attacks work in real-world
wireless environments and helps security professionals understand,
test, and improve WiFi network defenses.

------------------------------------------------------------
FEATURES
------------------------------------------------------------

- Automatic scanning of nearby WiFi networks
- Automatic detection of connected clients
- Continuous (infinite) deauthentication attack
- No manual interaction required after launch
- Clean termination using Ctrl + C
- Written entirely in Python

------------------------------------------------------------
REQUIREMENTS
------------------------------------------------------------

- Linux operating system
- Python 3
- Root (sudo) privileges
- Wireless adapter supporting monitor mode and packet injection

------------------------------------------------------------
USAGE
------------------------------------------------------------

Run the tool using the following command:

sudo python3 wifi_deauth.py

After execution:
- The tool automatically scans nearby WiFi networks
- Detected networks and clients are targeted automatically
- Deauthentication attacks run continuously
- Press Ctrl + C to stop the attack and exit the tool

------------------------------------------------------------
TERMINATION
------------------------------------------------------------

To stop the tool and cancel the ongoing deauthentication process:

Press Ctrl + C

This immediately stops the attack loop and exits the program safely.

------------------------------------------------------------
LEGAL AND ETHICAL DISCLAIMER
------------------------------------------------------------

WARNING:

This tool is intended ONLY for:
- Educational purposes
- Cybersecurity research
- Authorized penetration testing
- Testing networks you own or have explicit permission to test

Unauthorized deauthentication attacks are illegal in many countries
and may violate local, national, or international laws.

The author is NOT responsible for:
- Misuse of this tool
- Illegal activities performed using this software
- Any damage, disruption, or legal consequences caused by misuse

By using this tool, you agree that you understand and accept full
responsibility for your actions.

------------------------------------------------------------
AUTHOR
------------------------------------------------------------

Name: Mandeep
Field: Cyber Security

------------------------------------------------------------
END OF FILE
------------------------------------------------------------
