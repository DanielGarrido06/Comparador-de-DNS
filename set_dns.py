import subprocess
import re
import sys
import ctypes


def is_admin():
	try:
		return ctypes.windll.shell32.IsUserAnAdmin()
	except:
		return False
	

def get_active_interface():
	# Get the list of interfaces and their status
	result = subprocess.run(["netsh", "interface", "show", "interface"], capture_output=True, text=True)
	if result.returncode != 0:
		raise RuntimeError("Failed to get network interfaces")
	# Find the first 'Connected' interface that is not a loopback or tunnel
	for line in result.stdout.splitlines():
		# Example line: 'Enabled    Connected     Dedicated    Wi-Fi'
		if 'Connected' in line and not ('Loopback' in line or 'Tunnel' in line):
			parts = re.split(r'\s{2,}', line.strip())
			if len(parts) == 4:
				return parts[3]
	raise RuntimeError("No active network interface found")


def set_dns(interface_name, dns_address):
	# Set the DNS server for the specified interface
	command = [
		"netsh", "interface", "ip", "set", "dns",
		f'name={interface_name}', f'source=static', f'addr={dns_address}', 'register=primary']
	result = subprocess.run(command, capture_output=True, text=True)
	if result.returncode == 0:
		print(f"DNS set to {dns_address} on {interface_name}")
	else:
		print(f"Error setting DNS: {result.stderr}")


def get_current_dns(interface_name):
	# Get the current DNS server for the specified interface
	command = [
		"netsh", "interface", "ip", "show", "dns", f'name={interface_name}'
	]
	result = subprocess.run(command, capture_output=True, text=True)
	if result.returncode != 0:
		print(f"Error reading DNS: {result.stderr}")
		return None
	# Parse the output for DNS addresses
	dns_addresses = []
	for line in result.stdout.splitlines():
		if re.search(r'DNS Servers', line):
			# The DNS address is on this line or the next lines
			addr = line.split(':')[-1].strip()
			if addr:
				dns_addresses.append(addr)
		elif dns_addresses and line.strip():
			# Additional DNS addresses
			dns_addresses.append(line.strip())
		elif dns_addresses and not line.strip():
			break
	return dns_addresses


def flush_dns_cache():
	# Flush the DNS cache
	command = ["ipconfig", "/flushdns"]
	result = subprocess.run(command, capture_output=True, text=True)
	if result.returncode == 0:
		print("DNS cache flushed.")
	else:
		print(f"Error flushing DNS cache: {result.stderr}")


def main(new_dns = "8.8.8.8"):
	if not is_admin():
		print("Error: This script must be run as administrator to change DNS settings.")
		sys.exit(1)
		
	try:
		interface = get_active_interface()
		print(f"Active interface: {interface}")
		current_dns = get_current_dns(interface)
		print(f"Current DNS addresses: {current_dns}")
		set_dns(interface, new_dns)
		flush_dns_cache()
	except Exception as e:
		print(f"Error: {e}")

if __name__ == "__main__":
	main()