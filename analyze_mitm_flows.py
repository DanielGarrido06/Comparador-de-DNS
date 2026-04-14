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
            total_bytes += len(flow.response.raw_content)
            # Get content type (MIME)
            ctype = flow.response.headers.get("content-type", "unknown").split(";")[0].strip().lower()
            content_type_bytes[ctype] += len(flow.response.raw_content)
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
else:
    output_lines.append("Observed network window: unavailable")
output_lines.append(f"Total requests: {num_requests}")
output_lines.append(f"Unique URLs: {len(urls)}")
output_lines.append(f"Total Kilobytes downloaded: {total_bytes/1024:.2f}")

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
