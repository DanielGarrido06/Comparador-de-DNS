import os
import re
import matplotlib.pyplot as plt
from collections import defaultdict


LABELS = ['Mídia', 'Aplicação', 'Texto', 'Outros']


DNS_DISPLAY_NAMES = {
    '192.168.0.69': 'pihole',
    '1.1.1.1': 'Cloudflare',
    '8.8.8.8': 'Google',
}

BASELINE_DNS = '8.8.8.8'


# Define content type groups
MEDIA_TYPES = [
    'image/', 'audio/', 'video/', 'font/']
APPLICATION_TYPES = [
    'application/', 'javascript/', 'binary/']
TEXT_TYPES = [
    'text/']

class SiteData:
    def __init__(self, site, dns, timestamp):
        self.site = site
        self.dns = dns
        self.timestamp = timestamp
        self.groups = dict.fromkeys(LABELS, 0.0)

    def add_kb(self, group, kb):
        self.groups[group] = self.groups.get(group, 0.0) + kb




# Helper to classify content type

def classify_content_type(ctype):
    ctype = ctype.lower()
    if any(ctype.startswith(prefix) for prefix in MEDIA_TYPES):
        return 'Mídia'
    if any(ctype.startswith(prefix) or ctype == prefix for prefix in APPLICATION_TYPES):
        return 'Aplicação'
    if any(ctype.startswith(prefix) or ctype == prefix for prefix in TEXT_TYPES):
        return 'Texto'
    return 'Outros'

# Find all files matching IP address pattern
ip_file_pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}\.txt$')
content_type_line_pattern = re.compile(r'^(.+?):\s*(\d+(?:\.\d+)?)\s*KB$')
files = [f for f in os.listdir('.') if ip_file_pattern.match(f)]
graphics_dir = 'charts'
os.makedirs(graphics_dir, exist_ok=True)

# List of Site_Data instances.
site_data = []


def get_or_create_site_data(site, dns, timestamp):
    for entry in site_data:
        if entry.site == site and entry.dns == dns and entry.timestamp == timestamp:
            return entry

    entry = SiteData(site, dns, timestamp)
    site_data.append(entry)
    return entry

for fname in files:
    with open(fname, encoding='utf-8') as f:
        lines = f.readlines()

    current_dns = None
    current_site = None
    current_timestamp = None

    for i, line in enumerate(lines):
        if line.startswith('DNS used:'):
            current_dns = line.split(':', 1)[1].strip()

        if line.startswith('Loaded Webpage:'):
            current_site = line.split(':', 1)[1].strip()

        if line.startswith('Timestamp of first request:'):
            current_timestamp = line.split(':', 1)[1].strip()


        if line.startswith('Breakdown by Content-Type:') and current_site and current_dns and current_timestamp:
            j = i + 1
            while j < len(lines):
                stripped = lines[j].strip()
                if not stripped:
                    break
                # Stop when a new report block begins.
                if stripped.startswith('DNS used:') or stripped.startswith('Loaded Webpage:') or stripped.startswith('Breakdown by Content-Type:'):
                    break

                match = content_type_line_pattern.match(stripped)
                if match:
                    ctype = match.group(1).strip()
                    kb = float(match.group(2))
                    group = classify_content_type(ctype)
                    entry = get_or_create_site_data(current_site, current_dns, current_timestamp)
                    entry.add_kb(group, kb)
                j += 1

# Plot one graph per site, with grouped bars per DNS inside each content type
labels = LABELS
sites = sorted({entry.site for entry in site_data})

for site in sites:
    site_entries = [entry for entry in site_data if entry.site == site]
    dns_servers = sorted(entry.dns for entry in site_entries)
    x_positions = list(range(len(labels)))
    timestamp_label = site_entries[0].timestamp[:-4] if site_entries else 'N/A'

    num_dns = len(dns_servers)
    group_width = 0.8
    bar_width = group_width / num_dns if num_dns else group_width

    plt.figure(figsize=(9, 5))

    for idx, dns_server in enumerate(dns_servers):
        offset = (idx - (num_dns - 1) / 2) * bar_width
        dns_entries = [entry for entry in site_entries if entry.dns == dns_server]
        dns_values = [sum(entry.groups.get(label, 0) for entry in dns_entries) for label in labels]
        bar_positions = [x + offset for x in x_positions]
        legend_label = DNS_DISPLAY_NAMES.get(dns_server, dns_server)
        plt.bar(bar_positions, dns_values, width=bar_width, label=legend_label)

    plt.xticks(x_positions, labels)
    plt.title(f'Distribuição de Dados por Tipo de Conteudo\n{site}\nMedição em: {timestamp_label}')
    plt.ylabel('Kilobytes (KB)')
    plt.xlabel('Tipo de Conteúdo')
    plt.legend(title='Servidor DNS')
    plt.tight_layout()

    safe_site = re.sub(r'[^a-zA-Z0-9._-]+', '_', site)
    site_dir = os.path.join(graphics_dir, safe_site)
    os.makedirs(site_dir, exist_ok=True)
    safe_timestamp = re.sub(r'[^a-zA-Z0-9._-]+', '_', timestamp_label)
    plt.savefig(os.path.join(site_dir, f'{safe_timestamp}.png'), dpi=150)

# Plot one summary chart with percentage change in total downloaded data per site and DNS.
totals_by_site_dns = defaultdict(lambda: defaultdict(float))
for entry in site_data:
    totals_by_site_dns[entry.site][entry.dns] += sum(entry.groups.values())

comparison_sites = sorted(totals_by_site_dns.keys())
all_dns_servers = sorted({dns for dns_totals in totals_by_site_dns.values() for dns in dns_totals.keys()})

if comparison_sites and all_dns_servers:
    baseline_dns = BASELINE_DNS if BASELINE_DNS in all_dns_servers else all_dns_servers[0]
    x_positions = list(range(len(comparison_sites)))
    num_dns = len(all_dns_servers)
    group_width = 0.8
    bar_width = group_width / num_dns if num_dns else group_width

    plt.figure(figsize=(12, 6))

    for idx, dns_server in enumerate(all_dns_servers):
        offset = (idx - (num_dns - 1) / 2) * bar_width
        percent_values = []

        for site in comparison_sites:
            baseline_total = totals_by_site_dns[site].get(baseline_dns)
            current_total = totals_by_site_dns[site].get(dns_server)

            if baseline_total is None or baseline_total == 0 or current_total is None:
                percent_change = float('nan')
            elif dns_server == baseline_dns:
                percent_change = 0.0
            else:
                percent_change = ((current_total - baseline_total) / baseline_total) * 100

            percent_values.append(percent_change)

        bar_positions = [x + offset for x in x_positions]
        legend_label = DNS_DISPLAY_NAMES.get(dns_server, dns_server)
        plt.bar(bar_positions, percent_values, width=bar_width, label=legend_label)

    plt.axhline(0, color='black', linewidth=1)
    plt.xticks(x_positions, comparison_sites, rotation=25, ha='right')
    baseline_label = DNS_DISPLAY_NAMES.get(baseline_dns, baseline_dns)
    plt.title(f'Variação Percentual de Dados Baixados por Site\nComparado ao DNS: {baseline_label}')
    plt.ylabel('Variação Percentual (%)')
    plt.xlabel('Site')
    plt.legend(title='Servidor DNS')
    plt.tight_layout()
    plt.savefig(os.path.join(graphics_dir, 'comparativo_percentual_dns.png'), dpi=150)
