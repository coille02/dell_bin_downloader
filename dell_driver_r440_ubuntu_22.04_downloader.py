from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time, os, requests, re
from urllib.parse import urljoin, urlparse

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    return webdriver.Chrome(options=options)

def find_search_input(driver):
    """Try multiple selectors to find the search input"""
    possible_selectors = [
        (By.ID, "mh-search-input"),
        (By.ID, "inpEntry"),
        (By.CSS_SELECTOR, "input[placeholder*='search']"),
        (By.CSS_SELECTOR, "input[type='search']"),
        (By.CSS_SELECTOR, "input[data-testid*='search']"),
        (By.CSS_SELECTOR, ".search-input input"),
        (By.CSS_SELECTOR, "[role='searchbox']"),
        (By.XPATH, "//input[contains(@placeholder, 'Search') or contains(@placeholder, '검색')]")
    ]
    
    for by_type, selector in possible_selectors:
        try:
            element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((by_type, selector))
            )
            print(f"Found search input with selector: {by_type} = '{selector}'")
            return element
        except:
            continue
    
    return None

def select_ubuntu_os(driver):
    """Force select Ubuntu Server 20.04 LTS using direct data-value click"""
    print("Looking for Ubuntu Server 20.04 LTS option...")
    
    try:
        # Wait for page to fully load
        time.sleep(3)
        
        print(f"Current page: {driver.current_url}")
        
        # First, try to open any dropdown to make options visible
        try:
            # Look for dropdown buttons by class
            dropdown_buttons = driver.find_elements(By.CSS_SELECTOR, "button[aria-haspopup='listbox']")
            for btn in dropdown_buttons:
                if btn.is_displayed():
                    print("Opening dropdown...")
                    btn.click()
                    time.sleep(3)
                    break
        except:
            print("Could not open dropdown, trying direct element access...")
        
        # Try multiple approaches to find and click Ubuntu option
        ubuntu_selectors = [
            "button[data-value='US008']",  # Ubuntu Server 20.04 LTS
            "button[data-index='9']",      # Based on the log, US008 was at index 9
            "*[data-value='US008']",       # Any element with this data-value
        ]
        
        for selector in ubuntu_selectors:
            try:
                ubuntu_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"Found {len(ubuntu_elements)} elements with selector: {selector}")
                
                for ubuntu_element in ubuntu_elements:
                    if ubuntu_element.is_displayed() or ubuntu_element.is_enabled():
                        print(f"Attempting to click Ubuntu option: {selector}")
                        
                        # Scroll to element
                        driver.execute_script("arguments[0].scrollIntoView(true);", ubuntu_element)
                        time.sleep(1)
                        
                        # Try regular click first
                        try:
                            ubuntu_element.click()
                            print("Successfully clicked with regular click")
                        except:
                            # Try JavaScript click
                            print("Regular click failed, trying JavaScript click...")
                            driver.execute_script("arguments[0].click();", ubuntu_element)
                            print("Successfully clicked with JavaScript")
                        
                        time.sleep(7)  # Wait for page reload
                        
                        # Check if page has changed
                        new_url = driver.current_url
                        if "US008" in new_url or "ubuntu" in driver.page_source.lower():
                            print("Successfully selected Ubuntu Server 20.04 LTS")
                            return True
                        
                        print("Click didn't seem to change the page, trying next method...")
                        
            except Exception as e:
                print(f"Failed with selector {selector}: {e}")
                continue
        
        # If direct clicking didn't work, try other Ubuntu versions as fallback
        fallback_ubuntu_options = ['US001', 'US004']
        for data_value in fallback_ubuntu_options:
            try:
                ubuntu_element = driver.find_element(By.CSS_SELECTOR, f"button[data-value='{data_value}']")
                if ubuntu_element.is_displayed():
                    print(f"Trying fallback Ubuntu option: {data_value}")
                    driver.execute_script("arguments[0].click();", ubuntu_element)
                    time.sleep(7)
                    return True
            except:
                continue
        
        # Final fallback: try RHEL
        rhel_options = ['RHEL9', 'RHEL8']
        for data_value in rhel_options:
            try:
                rhel_element = driver.find_element(By.CSS_SELECTOR, f"button[data-value='{data_value}']")
                if rhel_element.is_displayed():
                    print(f"Trying RHEL option as final fallback: {data_value}")
                    driver.execute_script("arguments[0].click();", rhel_element)
                    time.sleep(7)
                    return True
            except:
                continue
        
        print("Could not select any Linux OS option")
        return False
        
    except Exception as e:
        print(f"Error selecting Ubuntu OS: {e}")
        import traceback
        traceback.print_exc()
        return False

def download_file(url, filepath):
    """Download a file with progress indication"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\r  Progress: {percent:.1f}%", end='', flush=True)
        
        print(f"\n  Successfully downloaded: {os.path.basename(filepath)}")
        return True
    except Exception as e:
        print(f"\n  Error downloading {url}: {e}")
        return False

def find_bin_files(driver):
    """Enhanced search for .bin files using multiple methods"""
    print("Searching for .bin/.BIN files using multiple methods...")
    
    bin_links = []
    
    # Method 1: Direct href links
    all_links = driver.find_elements(By.TAG_NAME, "a")
    for link in all_links:
        href = link.get_attribute("href")
        if href and (href.lower().endswith(".bin") or href.endswith(".BIN")):
            bin_links.append(href)
    
    print(f"Method 1 - Direct href links: Found {len(bin_links)} .bin files")
    
    # Method 2: Search in page source with regex
    if len(bin_links) == 0:
        print("Method 2 - Searching page source with regex...")
        page_source = driver.page_source
        
        # Look for URLs ending in .bin or .BIN
        bin_urls = re.findall(r'https?://[^\s"\'<>]+\.BIN|https?://[^\s"\'<>]+\.bin', page_source)
        for url in bin_urls:
            if url not in bin_links:
                bin_links.append(url)
                
        # Look for relative paths or filenames
        bin_filenames = re.findall(r'[A-Za-z0-9_.-]+\.BIN|[A-Za-z0-9_.-]+\.bin', page_source)
        print(f"Found {len(bin_filenames)} .bin filename references in page source:")
        for filename in bin_filenames[:10]:  # Show first 10
            print(f"  - {filename}")
        
        print(f"Method 2 - Page source regex: Found {len(bin_links)} total .bin files")
    
    # Method 3: Look for download buttons and extract URLs
    if len(bin_links) == 0:
        print("Method 3 - Checking download buttons...")
        download_elements = driver.find_elements(By.XPATH, 
            "//button[contains(@class, 'download') or contains(text(), '다운로드') or contains(text(), 'Download')] | "
            "//a[contains(@class, 'download') or contains(text(), '다운로드') or contains(text(), 'Download')]"
        )
        
        for element in download_elements:
            # Check various attributes for download URLs
            for attr in ['href', 'onclick', 'data-href', 'data-url', 'data-download-url']:
                attr_value = element.get_attribute(attr)
                if attr_value and ('.bin' in attr_value.lower() or '.BIN' in attr_value):
                    bin_links.append(attr_value)
        
        print(f"Method 3 - Download buttons: Found {len(bin_links)} total .bin files")
    
    # Method 4: Look for any elements containing .bin references
    if len(bin_links) == 0:
        print("Method 4 - Searching all elements for .bin references...")
        all_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '.bin') or contains(text(), '.BIN')]")
        print(f"Found {len(all_elements)} elements containing .bin references")
        
        for element in all_elements[:5]:  # Check first 5
            try:
                text = element.text
                print(f"Element text: {text[:100]}...")  # Show first 100 chars
            except:
                pass
    
    # Method 5: Check for data attributes on table rows or containers
    if len(bin_links) == 0:
        print("Method 5 - Checking data attributes on table elements...")
        table_elements = driver.find_elements(By.XPATH, "//tr[@data-*] | //td[@data-*] | //div[@data-download*]")
        
        for element in table_elements:
            for attr_name in element.get_property('attributes').keys() if element.get_property('attributes') else []:
                if 'data-' in attr_name:
                    attr_value = element.get_attribute(attr_name)
                    if attr_value and ('.bin' in attr_value.lower() or '.BIN' in attr_value):
                        bin_links.append(attr_value)
    
    # Remove duplicates
    bin_links = list(set(bin_links))
    
    print(f"Final result: Found {len(bin_links)} unique .bin/.BIN files")
    if bin_links:
        print("Found .bin files:")
        for i, link in enumerate(bin_links[:10]):  # Show first 10
            print(f"  {i+1}: {link}")
    
    return bin_links

def main():
    driver = setup_driver()
    
    try:
        print("Opening Dell Support page...")
        driver.get("https://www.dell.com/support/home/ko-kr")
        
        # Wait for page to load
        time.sleep(3)
        
        # Try to find search input
        search_input = find_search_input(driver)
        
        if search_input is None:
            print("Could not find search input. Trying direct navigation to PowerEdge R440 page...")
            driver.get("https://www.dell.com/support/home/ko-kr/product-support/product/poweredge-r440/drivers")
        else:
            print("Found search input, searching for PowerEdge R440...")
            search_input.clear()
            search_input.send_keys("PowerEdge R440")
            search_input.send_keys(Keys.RETURN)
            time.sleep(5)
            print("Navigating to drivers page...")
            # Try to load the page with Ubuntu filter directly first
            ubuntu_url = "https://www.dell.com/support/home/ko-kr/product-support/product/poweredge-r440/drivers?os=US008"
            print(f"Trying to load Ubuntu filtered page: {ubuntu_url}")
            driver.get(ubuntu_url)
            time.sleep(5)
            
            # Check if Ubuntu filtering worked
            if "ubuntu" not in driver.page_source.lower():
                print("Ubuntu filter didn't work via URL, loading regular page...")
                driver.get("https://www.dell.com/support/home/ko-kr/product-support/product/poweredge-r440/drivers")
        
        # Wait for drivers page to load
        print("Loading drivers page...")
        time.sleep(5)
        
        print(f"Current page URL: {driver.current_url}")
        
        # Try to select Ubuntu OS
        print("\n=== Attempting to select Ubuntu Server 20.04 LTS ===")
        ubuntu_selected = select_ubuntu_os(driver)
        
        if ubuntu_selected:
            print("Ubuntu OS selected successfully, waiting for page to update...")
            time.sleep(5)
        else:
            print("Could not select Ubuntu OS, proceeding with current page...")
        
        # Search for .bin files using enhanced methods
        bin_links = find_bin_files(driver)
        
        if len(bin_links) == 0:
            print("No .bin files found. Showing all available download types for reference...")
            all_links = driver.find_elements(By.TAG_NAME, "a")
            download_links = []
            file_types = {}
            
            for link in all_links:
                href = link.get_attribute("href")
                if href and any(ext in href.lower() for ext in ['.exe', '.bin', '.zip', '.msi']):
                    download_links.append(href)
                    ext = href.split('.')[-1].lower()
                    file_types[ext] = file_types.get(ext, 0) + 1
            
            print(f"\nFile type summary:")
            for ext, count in sorted(file_types.items()):
                print(f"  .{ext}: {count} files")
            
            print(f"\nTotal files found: {len(download_links)}")
            choice = input("\nNo .bin files found. Would you like to:\n1. Download all files anyway\n2. Exit\nChoice (1/2): ").strip()
            
            if choice != "1":
                print("Exiting...")
                return
            
            # Use all download links if no .bin files found
            bin_links = download_links
        
        # Create downloads directory
        os.makedirs("downloads", exist_ok=True)
        
        # Download files
        successful_downloads = 0
        for i, url in enumerate(bin_links):
            # Clean up URL if needed
            if url.startswith('javascript:') or 'onclick' in url:
                print(f"Skipping JavaScript URL: {url[:50]}...")
                continue
                
            filename = os.path.basename(urlparse(url).path)
            if not filename or '.' not in filename:
                filename = f"download_{i}.bin"
            
            filepath = os.path.join("downloads", filename)
            print(f"\nDownloading {i+1}/{len(bin_links)}: {filename}")
            
            if download_file(url, filepath):
                successful_downloads += 1
        
        print(f"\n=== Download Summary ===")
        print(f"Total files found: {len(bin_links)}")
        print(f"Successfully downloaded: {successful_downloads}")
        print(f"Failed downloads: {len(bin_links) - successful_downloads}")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        driver.quit()
        print("Browser closed.")

if __name__ == "__main__":
    main()