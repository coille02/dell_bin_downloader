from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time, os, requests, re, platform, sys
from urllib.parse import urljoin, urlparse

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins")
    options.add_argument("--disable-images")
    options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Platform-specific configurations
    current_platform = platform.system().lower()
    print(f"Detected platform: {current_platform}")
    
    if current_platform == "linux":
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--remote-debugging-port=9222")
    elif current_platform == "darwin":  # macOS
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
    
    try:
        driver = webdriver.Chrome(options=options)
        print("Chrome driver initialized successfully")
        return driver
    except Exception as e:
        print(f"Error initializing Chrome driver: {e}")
        print("Please ensure Chrome and chromedriver are installed:")
        if current_platform == "linux":
            print("  Ubuntu/Debian: sudo apt install chromium-browser chromium-chromedriver")
            print("  CentOS/RHEL: sudo yum install chromium chromedriver")
        elif current_platform == "darwin":
            print("  macOS: brew install --cask google-chrome && brew install chromedriver")
        else:
            print("  Windows: Install Chrome and download chromedriver")
        sys.exit(1)

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

def select_os_by_data_value(driver, os_data_value, os_name):
    """Select specific OS by data-value with enhanced clicking"""
    print(f"Attempting to select {os_name} (data-value: {os_data_value})...")
    
    try:
        # Wait for page to load
        time.sleep(5)
        
        # Method 1: Try to find and open OS dropdown
        dropdown_selectors = [
            "button[aria-haspopup='listbox']",
            "select[name*='os']",
            "select[id*='os']",
            ".dropdown-toggle",
            "[role='combobox']",
            "button[aria-expanded='false']",
            "button[data-toggle='dropdown']"
        ]
        
        dropdown_opened = False
        for selector in dropdown_selectors:
            try:
                dropdowns = driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"Found {len(dropdowns)} elements with selector: {selector}")
                
                for dropdown in dropdowns:
                    if dropdown.is_displayed() and dropdown.is_enabled():
                        print(f"Clicking dropdown with selector: {selector}")
                        
                        # Scroll into view
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", dropdown)
                        time.sleep(1)
                        
                        # Try to click
                        try:
                            dropdown.click()
                        except:
                            driver.execute_script("arguments[0].click();", dropdown)
                        
                        time.sleep(3)
                        dropdown_opened = True
                        break
                        
                if dropdown_opened:
                    break
                    
            except Exception as e:
                print(f"Error with selector {selector}: {e}")
                continue
        
        if not dropdown_opened:
            print("Could not open any dropdown, trying direct OS element access...")
        else:
            print("Dropdown opened successfully")
        
        # Method 2: Try multiple approaches to find and click OS option
        os_selectors = [
            (f"button[data-value='{os_data_value}']", f"{os_name} - data-value"),
            (f"*[data-value='{os_data_value}']", f"{os_name} - any element"),
            (f"option[value='{os_data_value}']", f"{os_name} - option"),
            (f"li[data-value='{os_data_value}']", f"{os_name} - list item"),
        ]
        
        # Try CSS selectors first
        for selector, description in os_selectors:
            try:
                os_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"Found {len(os_elements)} elements for {description}")
                
                for os_element in os_elements:
                    try:
                        # Debug element visibility and state
                        is_displayed = os_element.is_displayed()
                        is_enabled = os_element.is_enabled()
                        text = os_element.text
                        print(f"Element state - Displayed: {is_displayed}, Enabled: {is_enabled}, Text: '{text[:30]}'")
                        
                        # Try clicking even if not perfectly visible/enabled
                        if is_displayed or is_enabled or text:  # More lenient check
                            print(f"Attempting to click: {description}")
                            
                            # Scroll to element
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", os_element)
                            time.sleep(2)
                            
                            # Multiple click attempts
                            click_success = False
                            
                            # Method 1: Regular click
                            try:
                                os_element.click()
                                click_success = True
                                print("Regular click successful")
                            except Exception as e:
                                print(f"Regular click failed: {e}")
                            
                            # Method 2: JavaScript click
                            if not click_success:
                                try:
                                    driver.execute_script("arguments[0].click();", os_element)
                                    click_success = True
                                    print("JavaScript click successful")
                                except Exception as e:
                                    print(f"JavaScript click failed: {e}")
                            
                            # Method 3: Action chains
                            if not click_success:
                                try:
                                    from selenium.webdriver.common.action_chains import ActionChains
                                    ActionChains(driver).move_to_element(os_element).click().perform()
                                    click_success = True
                                    print("ActionChains click successful")
                                except Exception as e:
                                    print(f"ActionChains click failed: {e}")
                            
                            # Method 4: Force click with coordinates
                            if not click_success:
                                try:
                                    driver.execute_script("arguments[0].click(); arguments[0].dispatchEvent(new Event('change'));", os_element)
                                    click_success = True
                                    print("Force click with event successful")
                                except Exception as e:
                                    print(f"Force click failed: {e}")
                            
                            if click_success:
                                print("Click executed, waiting for page update...")
                                time.sleep(8)  # Wait longer for page to update
                                
                                # Check if selection worked
                                new_url = driver.current_url
                                page_source = driver.page_source.lower()
                                
                                print(f"After click - URL: {new_url}")
                                print(f"Checking for {os_name} content in page...")
                                
                                # Check for .bin files immediately
                                bin_check = driver.find_elements(By.XPATH, "//a[contains(@href, '.bin') or contains(@href, '.BIN')]")
                                print(f"Found {len(bin_check)} .bin files after selection")
                                
                                if len(bin_check) > 5 or os_data_value.lower() in new_url.lower():
                                    print(f"Successfully selected {os_name}!")
                                    return True
                                else:
                                    print("Selection didn't seem to work, trying next method...")
                            else:
                                print("All click methods failed for this element")
                            
                    except Exception as e:
                        print(f"Error with element: {e}")
                        continue
                        
            except Exception as e:
                print(f"Error with selector {selector}: {e}")
                continue
        
        print(f"Could not select {os_name}")
        return False
        
    except Exception as e:
        print(f"Error selecting {os_name}: {e}")
        import traceback
        traceback.print_exc()
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
    
    # Method 2: Search in page source with regex (only if no direct links found)
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
        for filename in bin_filenames[:5]:  # Show first 5
            print(f"  - {filename}")
        
        print(f"Method 2 - Page source regex: Found {len(bin_links)} total .bin files")
    
    # Remove duplicates
    bin_links = list(set(bin_links))
    
    print(f"Final result: Found {len(bin_links)} unique .bin/.BIN files")
    if bin_links:
        print("Sample .bin files found:")
        for i, link in enumerate(bin_links[:5]):  # Show first 5
            print(f"  {i+1}: {os.path.basename(urlparse(link).path)}")
    
    return bin_links

def download_file(url, filepath):
    """Download a file with progress indication"""
    try:
        response = requests.get(url, stream=True, timeout=30)
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

def main():
    # Define OS options to check (data-value: name)
    os_options = {
        'BIOSA': 'BIOS',
        'RHEL9': 'Red Hat Enterprise Linux 9',
        'RHEL8': 'Red Hat Enterprise Linux 8',
        'RHE70': 'Red Hat Enterprise Linux 7',
        'RH60': 'Red Hat Enterprise Linux 6',
        'US008': 'Ubuntu Server 20.04 LTS',
        'US004': 'Ubuntu Server 18.04 LTS',
        'US001': 'Ubuntu Server 16.04 LTS',
        'SLE15': 'SUSE Linux ES 15',
        'SLE12': 'SUSE Linux ES 12',
        'XI80': 'VMware ESXi 8.0',
        'XI70': 'VMware ESXi 7.0',
        'XI67': 'VMware ESXi 6.7',
        'XI65': 'VMware ESXi 6.5',
        'XI60': 'VMware ESXi 6.0',
        'CXS09': 'Citrix XenServer 7.1',
        'WS22L': 'Windows Server 2022 LTSC',
        'WS19L': 'Windows Server 2019 LTSC',
        'WST14': 'Windows Server 2016',
        'W12R2': 'Windows Server 2012 R2',
        'NAA': '해당 없음'
    }
    
    try:
        driver = setup_driver()
    except Exception as e:
        print(f"Failed to initialize Chrome driver: {e}")
        return
        
    all_bin_files = {}  # Dictionary to store OS -> [bin_files]
    download_summary = {}
    
    try:
        print("Starting comprehensive Dell PowerEdge R440 driver collection...")
        print(f"Will check {len(os_options)} different operating systems")
        
        for i, (os_data_value, os_name) in enumerate(os_options.items(), 1):
            print(f"\n{'='*60}")
            print(f"Processing OS {i}/{len(os_options)}: {os_name}")
            print(f"{'='*60}")
            
            # First load the base drivers page
            base_url = "https://www.dell.com/support/home/ko-kr/product-support/product/poweredge-r440/drivers"
            print(f"Loading base drivers page: {base_url}")
            
            try:
                driver.get(base_url)
                time.sleep(5)  # Wait for page to load
                
                current_url = driver.current_url
                print(f"Current URL: {current_url}")
                
                # Check if we got redirected to login
                if any(login_indicator in current_url for login_indicator in 
                       ["login.microsoftonline.com", "login.dell.com", "oauth", "saml"]):
                    print(f"Got redirected to login page, skipping {os_name}...")
                    continue
                
                # Check if the page loaded successfully
                if "poweredge-r440" not in current_url and "dell.com" not in current_url:
                    print(f"Failed to load drivers page, skipping {os_name}...")
                    continue
                
                # Now select the specific OS
                print(f"Selecting {os_name}...")
                os_selected = select_os_by_data_value(driver, os_data_value, os_name)
                
                if not os_selected:
                    print(f"Failed to select {os_name}, skipping...")
                    continue
                
                # Find .bin files for this OS
                print(f"Searching for .bin files for {os_name}...")
                bin_files = find_bin_files(driver)
                
                print(f"Found {len(bin_files)} .bin files for {os_name}")
                
                if bin_files:
                    all_bin_files[os_name] = bin_files
                    
                    # Create OS-specific directory
                    os_safe_name = re.sub(r'[<>:"/\\|?*]', '_', os_name)
                    os_dir = os.path.join("downloads", os_safe_name)
                    os.makedirs(os_dir, exist_ok=True)
                    
                    # Show first few files found
                    print(f"Sample files found for {os_name}:")
                    for j, url in enumerate(bin_files[:5]):
                        filename = os.path.basename(urlparse(url).path)
                        print(f"  {j+1}: {filename}")
                    
                    # Download files for this OS
                    successful_downloads = 0
                    print(f"Downloading files to: {os_dir}")
                    
                    for j, url in enumerate(bin_files):
                        filename = os.path.basename(urlparse(url).path)
                        if not filename or '.' not in filename:
                            filename = f"driver_{j}.bin"
                        
                        filepath = os.path.join(os_dir, filename)
                        
                        # Skip if file already exists
                        if os.path.exists(filepath):
                            print(f"Skipping {filename} (already exists)")
                            successful_downloads += 1
                            continue
                        
                        print(f"Downloading {j+1}/{len(bin_files)}: {filename}")
                        if download_file(url, filepath):
                            successful_downloads += 1
                    
                    download_summary[os_name] = {
                        'total_files': len(bin_files),
                        'successful_downloads': successful_downloads
                    }
                    
                    print(f"Completed {os_name}: {successful_downloads}/{len(bin_files)} files downloaded")
                else:
                    print(f"No .bin files found for {os_name}")
                
                # Small delay before next OS
                time.sleep(3)
                
            except Exception as e:
                print(f"Error processing {os_name}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        # Final summary
        print(f"\n{'='*80}")
        print("FINAL DOWNLOAD SUMMARY")
        print(f"{'='*80}")
        
        total_files = 0
        total_successful = 0
        
        for os_name, summary in download_summary.items():
            files = summary['total_files']
            success = summary['successful_downloads']
            total_files += files
            total_successful += success
            
            print(f"{os_name}: {success}/{files} files downloaded")
        
        print(f"\nOverall Summary:")
        print(f"Total .bin files found: {total_files}")
        print(f"Successfully downloaded: {total_successful}")
        print(f"Failed downloads: {total_files - total_successful}")
        print(f"Operating systems with .bin files: {len(download_summary)}")
        
        # Show which OS had the most files
        if download_summary:
            max_files_os = max(download_summary.items(), key=lambda x: x[1]['total_files'])
            print(f"OS with most .bin files: {max_files_os[0]} ({max_files_os[1]['total_files']} files)")
        
    except Exception as e:
        print(f"Critical error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        driver.quit()
        print("Browser closed.")

if __name__ == "__main__":
    main()