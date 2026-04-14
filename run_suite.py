import subprocess
import time
import dns_utils


# CONFIGURABLE PATHS
INPUT_FILE = "input.txt"  # Formato: primeira linha DNS, demais URLs
MITM_FLOWS = "flows_file"
MITM_ANALYZER = "analyze_mitm_flows.py"
MEASURE_SCRIPT = "measure_page.py"
GRAPHIC_SCRIPT = "graphing.py"


def run_suite(dns_addr, pages):
    for url in pages:
        # Start mitmdump
        mitm = subprocess.Popen(["mitmdump", "-w", MITM_FLOWS])
        time.sleep(2)  # Give mitmdump time to start
        print(f"Testing: {url}")
        subprocess.run(["python", MEASURE_SCRIPT, "--url", url.strip()])
        mitm.terminate()
        mitm.wait()
        time.sleep(1)
        # Analyze flows
        print(f"Results for DNS {dns_addr} at URL {url}:")
        subprocess.run(["python", MITM_ANALYZER, "--dns", dns_addr, "--url", url.strip()])

def parse_input_file(input_path):
    dns_list = []
    pages = []
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.lower().startswith("dns:"):
                dns_list = [x.strip() for x in line[4:].split(",") if x.strip()]
            else:
                pages.append(line)
    return dns_list, pages

if __name__ == "__main__":
    dns_utils.exit_if_not_admin()
    network_interface = dns_utils.get_active_interface()
    DNS_LIST, pages = parse_input_file(INPUT_FILE)
    for dns in DNS_LIST:
        dns_utils.flush_dns_cache()
        dns_utils.set_dns(network_interface, dns)
        run_suite(dns, pages)
    subprocess.run(["python", GRAPHIC_SCRIPT])
    print("All tests complete.")
