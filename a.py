import subprocess
import re

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
		f'name={interface_name}', f'source=static', f'addr={dns_address}', 'register=primary'
	result = subprocess.run(command, capture_output=True, text=True)
	if result.returncode == 0:
		print(f"DNS set to {dns_address} on {interface_name}")
	else:
		print(f"Error setting DNS: {result.stderr}")

if __name__ == "__main__":
	dns = "8.8.8.8"  # Example DNS address
	try:
		iface = get_active_interface()
		print(f"Active interface: {iface}")
		set_dns(iface, dns)
	except Exception as e:
        print(f"Error: {e}")
