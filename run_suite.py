import subprocess
import time
import os
import dns_utils

# CONFIGURABLE PATHS
PAGES_FILE = "pages.txt"  # List of URLs, one per line
MITM_FLOWS = "flows_file"
MITM_ANALYZER = "analyze_mitm_flows.py"
MEASURE_SCRIPT = "measure_page.py"

# DNS addresses to test
DNS_LIST = ["192.168.0.69", "1.1.1.1"]


def run_suite(dns_addr, pages):
    # Start mitmdump
    mitm = subprocess.Popen(["mitmdump", "-w", MITM_FLOWS])
    time.sleep(2)  # Give mitmdump time to start
    for url in pages:
        print(f"Testing: {url}")
        subprocess.run(["python", MEASURE_SCRIPT, "--url", url.strip()])
        time.sleep(2)
    mitm.terminate()
    mitm.wait()
    # Analyze flows
    print(f"Results for DNS {dns_addr}:")
    subprocess.run(["python", MITM_ANALYZER])
    # Save results
    os.rename(MITM_FLOWS, f"flows_{dns_addr.replace('.', '_')}.dump")

if __name__ == "__main__":
    dns_utils.exit_if_not_admin()
    network_interface = dns_utils.get_active_interface()
    with open(PAGES_FILE) as f:
        pages = [line.strip() for line in f if line.strip()]
    for dns in DNS_LIST:
        dns_utils.flush_dns_cache()
        dns_utils.set_dns(network_interface, dns)
        run_suite(dns, pages)
    print("All tests complete.")
