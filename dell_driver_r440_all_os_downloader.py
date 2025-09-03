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

def select_os_by_data_value(driver, os_data_value, os_name):
    """Select specific OS by data-value"""
    print(f"Attempting to select {os_name} (data-value: {os_data_value})...")
    
    try:
        # Wait for page to load
        time.sleep(3)
        
        # Try to open dropdown first
        try:
            dropdown_buttons = driver.find_elements(By.CSS_SELECTOR, "button[aria-haspopup='listbox']")
            for btn in dropdown_buttons:
                if btn.is_displayed():
                    btn.click()
                    time.sleep(2)
                    break
        except:
            pass
        
        # Find and click the specific OS option
        try:
            os_element = driver.find_element(By.CSS_SELECTOR, f"button[data-value='{os_data_value}']")
            if os_element.is_displayed() or os_element.is_enabled():
                driver.execute_script("arguments[0].scrollIntoView(true);", os_element)
                time.sleep(1)
                
                try:
                    os_element.click()
                except:
                    driver.execute_script("arguments[0].click();", os_element)
                
                print(f"Successfully selected {os_name}")
                time.sleep(7)  # Wait for page reload
                return True
        except Exception as e:
            print(f"Failed to select {os_name}: {e}")
            return False
        
    except Exception as e:
        print(f"Error selecting {os_name}: {e}")
        return False

def find_bin_files(driver):
    """Search for .bin files"""
    bin_links = []
    
    # Direct href links
    all_links = driver.find_elements(By.TAG_NAME, "a")
    for link in all_links:
        href = link.get_attribute("href")
        if href and (href.lower().endswith(".bin") or href.endswith(".BIN")):
            bin_links.append(href)
    
    # Remove duplicates
    bin_links = list(set(bin_links))
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
    
    driver = setup_driver()
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
                
                print(f"Current URL: {driver.current_url}")
                
                # Check if the page loaded successfully
                if "poweredge-r440" not in driver.current_url:
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