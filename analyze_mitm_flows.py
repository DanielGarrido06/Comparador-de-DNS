from mitmproxy.io import FlowReader
import argparse
from collections import defaultdict

parser = argparse.ArgumentParser()
parser.add_argument("--dns", type=str, default=None, help="DNS address used for this run")
parser.add_argument("--url", type=str, default=None, help="URL being measured")
args = parser.parse_args()
flows_path = "flows_file"



total_bytes = 0
num_requests = 0
urls = set()
content_type_bytes = defaultdict(int)

with open(flows_path, "rb") as logfile:
    reader = FlowReader(logfile)
    for flow in reader.stream():
        if flow.request:
            num_requests += 1
            urls.add(flow.request.pretty_url)
        if flow.response and flow.response.raw_content:
            total_bytes += len(flow.response.raw_content)
            # Get content type (MIME)
            ctype = flow.response.headers.get("content-type", "unknown").split(";")[0].strip().lower()
            content_type_bytes[ctype] += len(flow.response.raw_content)

output_lines = []

output_lines.append(f"\n\nDNS used: {args.dns}\n")
output_lines.append(f"Loaded Webpage: {args.url.replace('https://', '')}")
output_lines.append(f"Total requests: {num_requests}")
output_lines.append(f"Unique URLs: {len(urls)}")
output_lines.append(f"Total Kylobytes downloaded: {total_bytes/1024:.2f}")

# Add breakdown by content type
output_lines.append("\nBreakdown by Content-Type:")
for ctype, b in sorted(content_type_bytes.items(), key=lambda x: -x[1]):
    output_lines.append(f"  {ctype or 'unknown'}: {b/1024:.2f} KB")

output_text = "\n".join(output_lines)
print(output_text)

# Save to file if DNS argument is provided (append, do not overwrite)
if args.dns:
    filename = f"{args.dns}.txt"
    with open(filename, "a", encoding="utf-8") as f:
        f.write(output_text + "\n")
