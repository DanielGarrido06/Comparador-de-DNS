from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.proxy import Proxy, ProxyType
import argparse
import time

def measure_page_metrics(url):
    options = Options()
    options.add_argument('--width=1920')
    options.add_argument('--height=1080')
    # Disable all cache for fair comparison
    options.set_preference("browser.cache.disk.enable", False)
    options.set_preference("browser.cache.memory.enable", False)
    options.set_preference("browser.cache.offline.enable", False)
    options.set_preference("network.http.use-cache", False)

    # Set up mitmproxy as a proxy (assumes mitmproxy is running on localhost:8080)
    proxy = Proxy()
    proxy.proxy_type = ProxyType.MANUAL
    proxy.http_proxy = "localhost:8080"
    proxy.ssl_proxy = "localhost:8080"
    options.proxy = proxy
    driver = webdriver.Firefox(options=options)
    try:
        driver.get(url)
        # Wait for page to load
        time.sleep(15)
        print(f"Visited: {url}")
    finally:
        driver.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Measure page load metrics with Firefox.")
    parser.add_argument('--url', type=str, required=True, help="URL to visit and measure")
    args = parser.parse_args()
    measure_page_metrics(args.url)
