import os
import re
import matplotlib.pyplot as plt
from collections import defaultdict

# Define content type groups
MEDIA_TYPES = [
    'image/', 'audio/', 'video/', 'font/', 'application/x-xpinstall', 'application/x-binary', 'application/x-mpegurl', 'application/json+protobuf'
]
APPLICATION_TYPES = [
    'application/javascript', 'application/x-javascript', 'application/json', 'application/octet-stream', 'application/x-protobuf', 'binary/octet-stream']
TEXT_TYPES = [
    'text/', 'javascript charset=utf-8', 'text/vnd.reddit.partial+html']

# Helper to classify content type

def classify_content_type(ctype):
    ctype = ctype.lower()
    if any(ctype.startswith(prefix) for prefix in MEDIA_TYPES):
        return 'Media'
    if any(ctype.startswith(prefix) or ctype == prefix for prefix in APPLICATION_TYPES):
        return 'Application'
    if any(ctype.startswith(prefix) or ctype == prefix for prefix in TEXT_TYPES):
        return 'Text'
    return 'Others'

# Find all files matching IP address pattern
ip_file_pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}\.txt$')
files = [f for f in os.listdir('.') if ip_file_pattern.match(f)]

site_data = defaultdict(lambda: defaultdict(float))

for fname in files:
    with open(fname, encoding='utf-8') as f:
        lines = f.readlines()
    site = None
    for i, line in enumerate(lines):
        if line.startswith('Loaded Webpage:'):
            site = line.split(':', 1)[1].strip()
        if line.startswith('Breakdown by Content-Type:') and site:
            j = i + 1
            while j < len(lines) and lines[j].strip():
                parts = lines[j].strip().split(':')
                if len(parts) == 2:
                    ctype = parts[0].strip()
                    kb = float(parts[1].replace('KB', '').strip())
                    group = classify_content_type(ctype)
                    site_data[site][group] += kb
                j += 1

# Plot for each site
for site, group_data in site_data.items():
    labels = ['Media', 'Application', 'Text', 'Others']
    values = [group_data.get(label, 0) for label in labels]
    plt.figure(figsize=(6,4))
    plt.bar(labels, values, color=['#4e79a7', '#f28e2b', '#59a14f', '#e15759'])
    plt.title(f'Data Breakdown by Content Type\n{site}')
    plt.ylabel('Kilobytes (KB)')
    plt.xlabel('Content Type Group')
    plt.tight_layout()
    plt.show()
