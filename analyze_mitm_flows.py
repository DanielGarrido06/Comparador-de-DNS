from mitmproxy.io import FlowReader

# Path to the mitmproxy dump file (e.g., 'flows_file')
flows_path = "flows_192_168_0_69.dump"

total_bytes = 0
num_requests = 0
urls = set()

with open(flows_path, "rb") as logfile:
    reader = FlowReader(logfile)
    for flow in reader.stream():
        if flow.request:
            num_requests += 1
            urls.add(flow.request.pretty_url)
        if flow.response and flow.response.raw_content:
            total_bytes += len(flow.response.raw_content)

print(f"Total requests: {num_requests}")
print(f"Unique URLs: {len(urls)}")
print(f"Total bytes downloaded: {total_bytes/1024:.2f} KB")
