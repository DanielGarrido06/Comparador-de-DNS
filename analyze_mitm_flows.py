from mitmproxy.io import FlowReader
import argparse
from collections import defaultdict
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument("--dns", type=str, default=None, help="DNS address used for this run")
parser.add_argument("--url", type=str, default=None, help="URL being measured")
args = parser.parse_args()
flows_path = "flows_file"

def format_human_timestamp(epoch_seconds):
    if epoch_seconds is None:
        return "unavailable"
    return datetime.fromtimestamp(epoch_seconds).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

total_bytes = 0
num_requests = 0
urls = set()
content_type_bytes = defaultdict(int)
content_type_origin_ips = defaultdict(lambda: defaultdict(int))
content_type_origin_ip_bytes = defaultdict(lambda: defaultdict(int))
first_request_start = None
last_response_end = None
main_document_start = None
main_document_end = None

with open(flows_path, "rb") as logfile:
    reader = FlowReader(logfile)
    for flow in reader.stream():
        if flow.request:
            num_requests += 1
            urls.add(flow.request.pretty_url)
            request_start = getattr(flow.request, "timestamp_start", None)
            if request_start is not None:
                if first_request_start is None or request_start < first_request_start:
                    first_request_start = request_start
        if flow.response and flow.response.raw_content:
            response_bytes = len(flow.response.raw_content)
            total_bytes += response_bytes
            # Get content type (MIME)
            ctype = flow.response.headers.get("content-type", "unknown").split(";")[0].strip().lower()
            content_type_bytes[ctype] += response_bytes

            # Track origin IP occurrences per content type.
            origin_ip = "unknown"
            server_conn = getattr(flow, "server_conn", None)
            if server_conn is not None:
                ip_address = getattr(server_conn, "ip_address", None)
                if ip_address:
                    if isinstance(ip_address, tuple) and len(ip_address) > 0 and ip_address[0]:
                        origin_ip = str(ip_address[0])
                    else:
                        origin_ip = str(ip_address)
                else:
                    address = getattr(server_conn, "address", None)
                    if isinstance(address, tuple) and len(address) > 0 and address[0]:
                        origin_ip = str(address[0])
            content_type_origin_ips[ctype][origin_ip] += 1
            content_type_origin_ip_bytes[ctype][origin_ip] += response_bytes
        if flow.response:
            response_end = getattr(flow.response, "timestamp_end", None)
            if response_end is not None:
                if last_response_end is None or response_end > last_response_end:
                    last_response_end = response_end

        if flow.request and flow.response:
            ctype = flow.response.headers.get("content-type", "unknown").split(";")[0].strip().lower()
            request_start = getattr(flow.request, "timestamp_start", None)
            response_end = getattr(flow.response, "timestamp_end", None)
            if request_start is not None and response_end is not None and ctype == "text/html":
                if main_document_start is None or request_start < main_document_start:
                    main_document_start = request_start
                    main_document_end = response_end

observed_window_seconds = None
if first_request_start is not None and last_response_end is not None:
    observed_window_seconds = max(0.0, last_response_end - first_request_start)

main_document_seconds = None
if main_document_start is not None and main_document_end is not None:
    main_document_seconds = max(0.0, main_document_end - main_document_start)

output_lines = []

output_lines.append(f"\n\nDNS used: {args.dns}\n")
output_lines.append(f"Loaded Webpage: {args.url.replace('https://', '')}")
if main_document_seconds is not None:
    output_lines.append(f"Main document load time: {main_document_seconds:.2f} s")
else:
    output_lines.append("Main document load time: unavailable")
if observed_window_seconds is not None:
    output_lines.append(f"Observed network window: {observed_window_seconds:.2f} s")
    output_lines.append(f"Timestamp of first request: {format_human_timestamp(first_request_start)}")
else:
    output_lines.append("Observed network window: unavailable")
output_lines.append(f"Total requests: {num_requests}")
output_lines.append(f"Unique URLs: {len(urls)}")
output_lines.append(f"Total Kilobytes downloaded: {total_bytes/1024:.2f}")

# Add breakdown by content type
output_lines.append("\nBreakdown by Content-Type:")
for ctype, b in sorted(content_type_bytes.items(), key=lambda x: -x[1]):
    output_lines.append(f"  {ctype or 'unknown'}: {b/1024:.2f} KB")
    top_origins = sorted(
        content_type_origin_ip_bytes[ctype].items(),
        key=lambda x: -x[1]
    )[:5]
    if top_origins:
        output_lines.append("    Top 5 origin IPs:")
        for ip, bytes_transferred in top_origins:
            count = content_type_origin_ips[ctype][ip]
            ip_kb = bytes_transferred / 1024
            output_lines.append(f"      {ip}: {count} responses, {ip_kb:.2f} KB")
    else:
        output_lines.append("    Top 5 origin IPs: unavailable")

output_text = "\n".join(output_lines)
print(output_text)

# Save to file if DNS argument is provided (append, do not overwrite)
if args.dns:
    filename = f"{args.dns}.txt"
    with open(filename, "a", encoding="utf-8") as f:
        f.write(output_text + "\n")
