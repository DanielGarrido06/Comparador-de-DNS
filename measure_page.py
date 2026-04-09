from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time
import argparse

def measure_page_metrics(url):
    options = Options()
    options.headless = True  # Run in headless mode
    driver = webdriver.Firefox(options=options)
    try:
        start = time.time()
        driver.get(url)
        # Wait for page to load
        time.sleep(2)
        # Use browser performance API to get metrics
        perf_entries = driver.execute_script("return window.performance.getEntries();")
        nav = driver.execute_script("return window.performance.timing;")
        # Calculate load time
        load_time = nav['loadEventEnd'] - nav['navigationStart']
        # Number of requests
        num_requests = len(perf_entries)
        # Total data downloaded (sum of transferSize if available, else 0)
        total_bytes = 0
        for entry in perf_entries:
            if 'transferSize' in entry and entry['transferSize']:
                total_bytes += entry['transferSize']
        print(f"Page: {url}")
        print(f"Load time: {load_time/1000:.2f} seconds")
        print(f"Number of requests: {num_requests}")
        print(f"Total data downloaded: {total_bytes/1024:.2f} KB")
        return {
            'url': url,
            'load_time_ms': load_time,
            'num_requests': num_requests,
            'total_bytes': total_bytes
        }
    finally:
        driver.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Measure page load metrics with Firefox.")
    parser.add_argument('--url', type=str, required=True, help="URL to visit and measure")
    args = parser.parse_args()
    measure_page_metrics(args.url)
