import os
import re
import matplotlib.pyplot as plt
from collections import defaultdict

# Define content type groups
MEDIA_TYPES = [
    'image/', 'audio/', 'video/', 'font/']
APPLICATION_TYPES = [
    'application/', 'javascript/', 'binary/']
TEXT_TYPES = [
    'text/']

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
files = [f for f in os.listdir('.') if ip_file_pattern.match(f)]
graphics_dir = 'charts'
os.makedirs(graphics_dir, exist_ok=True)

DNS_DISPLAY_NAMES = {
    '192.168.0.69': 'pihole',
}

# site_data[site][dns][group] -> KB
site_data = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))

for fname in files:
    with open(fname, encoding='utf-8') as f:
        lines = f.readlines()

    current_dns = None
    current_site = None

    for i, line in enumerate(lines):
        if line.startswith('DNS used:'):
            current_dns = line.split(':', 1)[1].strip()

        if line.startswith('Loaded Webpage:'):
            current_site = line.split(':', 1)[1].strip()

        if line.startswith('Breakdown by Content-Type:') and current_site and current_dns:
            j = i + 1
            while j < len(lines) and lines[j].strip():
                parts = lines[j].strip().split(':')
                if len(parts) == 2:
                    ctype = parts[0].strip()
                    kb = float(parts[1].replace('KB', '').strip())
                    group = classify_content_type(ctype)
                    site_data[current_site][current_dns][group] += kb
                j += 1

# Plot one graph per site, with grouped bars per DNS inside each content type
for site, dns_data in site_data.items():
    labels = ['Mídia', 'Aplicação', 'Texto', 'Outros']
    dns_servers = sorted(dns_data.keys())
    x_positions = list(range(len(labels)))

    num_dns = len(dns_servers)
    group_width = 0.8
    bar_width = group_width / num_dns if num_dns else group_width

    plt.figure(figsize=(9, 5))

    for idx, dns_server in enumerate(dns_servers):
        offset = (idx - (num_dns - 1) / 2) * bar_width
        dns_values = [dns_data[dns_server].get(label, 0) for label in labels]
        bar_positions = [x + offset for x in x_positions]
        legend_label = DNS_DISPLAY_NAMES.get(dns_server, dns_server)
        plt.bar(bar_positions, dns_values, width=bar_width, label=legend_label)

    plt.xticks(x_positions, labels)
    plt.title(f'Distribuição de Dados por Tipo de Conteudo\n{site}')
    plt.ylabel('Kilobytes (KB)')
    plt.xlabel('Tipo de Conteúdo')
    plt.legend(title='Servidor DNS')
    plt.tight_layout()

    safe_site = re.sub(r'[^a-zA-Z0-9._-]+', '_', site)
    plt.savefig(os.path.join(graphics_dir, f'{safe_site}.png'), dpi=150)
