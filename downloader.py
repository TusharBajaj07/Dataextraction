from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, NoSuchElementException
import time
import random
import os

# Function to wait for element and return fresh reference
def wait_for_element(driver, element_id, timeout=10):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.ID, element_id))
    )

# Function to wait for element to be clickable
def wait_for_clickable(driver, element_id, timeout=10):
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.ID, element_id))
    )

# Function to check if element exists
def element_exists(driver, by, value, timeout=5):
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return True
    except:
        return False

# Function to retry dropdown selection with fresh references
def select_from_dropdown(driver, dropdown_id, skip_first=True, max_retries=3):
    for attempt in range(max_retries):
        try:
            # Always get a fresh reference to the dropdown
            dropdown_element = wait_for_clickable(driver, dropdown_id)
            dropdown = Select(dropdown_element)
            
            # Get fresh options
            options = dropdown.options
            if len(options) <= 1:
                print(f"Dropdown {dropdown_id} has no valid options. Refreshing page...")
                driver.refresh()
                time.sleep(3)
                continue
                
            # Select a random option (skipping first if needed)
            start_index = 1 if skip_first else 0
            if len(options) > start_index:
                random_option = random.choice(options[start_index:])
                option_text = random_option.text
                
                # Get fresh dropdown reference again before selecting
                dropdown = Select(wait_for_clickable(driver, dropdown_id))
                dropdown.select_by_visible_text(option_text)
                print(f"Selected '{option_text}' from {dropdown_id}")
                return True
            else:
                print(f"No valid options in {dropdown_id}")
                return False
                
        except StaleElementReferenceException:
            print(f"Stale element in {dropdown_id}, retrying... (attempt {attempt+1}/{max_retries})")
            time.sleep(1)
        except Exception as e:
            print(f"Error selecting from {dropdown_id}: {e}")
            time.sleep(1)
    
    return False

def select_district(driver, district_name):
    try:
        # Get the district dropdown
        district_dropdown = wait_for_clickable(driver, "ContentPlaceHolder1_ddlDistrict")
        district_select = Select(district_dropdown)
        
        # Select the specified district
        district_select.select_by_visible_text(district_name)
        print(f"Selected district: {district_name}")
        return True
    except Exception as e:
        print(f"Error selecting district {district_name}: {e}")
        return False

# Function to select a specific police station by name
def select_police_station(driver, ps_name):
    try:
        # Wait for police station dropdown to be populated after district selection
        time.sleep(2)
        
        # Get the police station dropdown
        ps_dropdown = wait_for_clickable(driver, "ContentPlaceHolder1_ddlPoliceStation")
        ps_select = Select(ps_dropdown)
        
        # Select the specified police station
        ps_select.select_by_visible_text(ps_name)
        print(f"Selected police station: {ps_name}")
        return True
    except Exception as e:
        print(f"Error selecting police station {ps_name}: {e}")
        return False

# Function to handle download buttons
def download_fir_pdfs(driver, download_folder="downloads"):
    # Create download directory if it doesn't exist
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
        print(f"Created download directory: {download_folder}")
    
    # Try to find download buttons using different patterns
    download_patterns = [
        "[id^='ContentPlaceHolder1_gdvDeadBody_btnDownload_']",  # Pattern you provided
        "[id^='ContentPlaceHolder1_gvFIRs_btnDownload_']",       # Possible alternative pattern
        "a[href*='ViewFIR']",                                    # Links containing ViewFIR
        "a[target='_blank']",                                    # Links opening in new tab
        "input[type='button'][value*='Download']",               # Input buttons with Download text
        "button[id*='Download']"                                 # Any button with Download in ID
    ]
    
    downloads_found = False
    
    for pattern in download_patterns:
        try:
            print(f"Searching for download elements using pattern: {pattern}")
            download_elements = driver.find_elements(By.CSS_SELECTOR, pattern)
            
            if download_elements:
                downloads_found = True
                print(f"Found {len(download_elements)} download elements with pattern: {pattern}")
                
                # Click each download button
                for i, button in enumerate(download_elements):
                    try:
                        print(f"Clicking download element {i+1}/{len(download_elements)}")
                        
                        # Store the current window handles before clicking
                        original_window = driver.current_window_handle
                        original_handles = driver.window_handles
                        
                        # Click the button/link
                        button.click()
                        time.sleep(2)  # Wait for download to initiate or new tab to open
                        
                        # Check if a new window/tab was opened
                        new_handles = driver.window_handles
                        if len(new_handles) > len(original_handles):
                            # Switch to the new window
                            new_window = [handle for handle in new_handles if handle != original_window][0]
                            driver.switch_to.window(new_window)
                            print(f"Switched to new tab with URL: {driver.current_url}")
                            
                            # Look for download links in the new window
                            try:
                                # Wait for page to load
                                time.sleep(2)
                                
                                # Try to find PDF viewer or direct download links
                                pdf_links = driver.find_elements(By.CSS_SELECTOR, "a[href$='.pdf'], embed[type='application/pdf']")
                                if pdf_links:
                                    print(f"Found PDF content in new tab")
                                else:
                                    print(f"No PDF content found in new tab")
                                
                                # Close the new tab and switch back to original
                                driver.close()
                                driver.switch_to.window(original_window)
                                
                            except Exception as tab_error:
                                print(f"Error processing new tab: {tab_error}")
                                # Make sure we get back to the original window
                                driver.switch_to.window(original_window)
                        
                    except Exception as click_error:
                        print(f"Error clicking element {i+1}: {click_error}")
        
        except Exception as pattern_error:
            print(f"Error with pattern {pattern}: {pattern_error}")
    
    return downloads_found

# Initialize WebDriver with download preferences
options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": os.path.join(os.getcwd(), "downloads"),
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True  # Automatically download PDFs instead of opening in browser
}
options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(options=options)
driver.maximize_window()  # Maximize to ensure all elements are visible

try:
    max_attempts = 5
    for attempt in range(max_attempts):
        try:
            print(f"\n==== Starting attempt {attempt+1}/{max_attempts} ====")
            
            # Navigate to the page (fresh load for each attempt)
            driver.get("https://citizen.mahapolice.gov.in/Citizen/MH/PublishedFIRs.aspx")
            time.sleep(2)  # Allow page to fully load
            
            # 1. Enter dates first (always get fresh references)
            print("Entering date range...")
            from_date = wait_for_element(driver, "ContentPlaceHolder1_txtDateOfRegistrationFrom")
            from_date.clear()
            from_date.send_keys("/01022025")
            
            to_date = wait_for_element(driver, "ContentPlaceHolder1_txtDateOfRegistrationTo")
            to_date.clear()
            to_date.send_keys("/01032025")
            
            # 2. Wait and then handle district dropdown
            time.sleep(2)
            # 2. Select specific district
            print("Selecting district...")
            district_name = "THANE CITY"  # Change to your desired district
            district_selected = select_district(driver, district_name)
            if not district_selected:
                print("Could not select district, refreshing...")
                continue
                
            # 3. Wait for police station dropdown to populate
            time.sleep(3)
            print("Selecting police station...")
            ps_name = "NAUPADA"  # Change to your desired police station
            ps_selected = select_police_station(driver, ps_name)
            if not ps_selected:
                print("Could not select police station, refreshing...")
                continue
            
            # 4. Click search button (get fresh reference)
            print("Clicking search button...")
            search_button = wait_for_clickable(driver, "ContentPlaceHolder1_btnSearch")
            search_button.click()
            time.sleep(5)  

            print("Setting records per page to 50...")
            try:
                # Look for the dropdown or button to select number of records per page
                records_dropdown = Select(driver.find_element(By.ID, "ContentPlaceHolder1_ucRecordView_ddlPageSize"))
                records_dropdown.select_by_value("50")  # Select 50 records per page
                print("Successfully set to display 50 records per page")
            except Exception as e:
                print(f"Could not set records per page: {e}")
                # Alternative approach - try clicking the "50" link directly
                try:
                    records_link = driver.find_element(By.XPATH, "//a[text()='50']")
                    records_link.click()
                    print("Clicked on '50' records link")
                except:
                    print("Could not find records per page selector")
            # 5. Wait for results or download buttons
            print("Waiting for results or download buttons...")
            time.sleep(5)  # Give page time to load results
            
            # Check for success - either results table or download buttons
            results_found = False
            
            # First check if the results table exists
            if element_exists(driver, By.ID, "ContentPlaceHolder1_gvFIRs"):
                print("Results table found!")
                results_found = True
                
                # Process results table
                table = driver.find_element(By.ID, "ContentPlaceHolder1_gvFIRs")
                rows = table.find_elements(By.TAG_NAME, "tr")
                
                if len(rows) <= 1:
                    print("No results found or only header row present.")
                else:
                    # Extract data from each row (skip header)
                    for row in rows[1:]:
                        columns = row.find_elements(By.TAG_NAME, "td")
                        fir_number = columns[0].text.strip()
                        fir_date = columns[1].text.strip()
                        police_station = columns[2].text.strip()
                        section = columns[3].text.strip()
                        print(f"FIR: {fir_number}, Date: {fir_date}, PS: {police_station}, Section: {section}")
            
            # Now attempt to find and click download buttons regardless of table presence
            print("\nAttempting to download FIR PDFs...")
            downloads_found = download_fir_pdfs(driver)
            
            # If either results or downloads were found, consider it a success
            if results_found or downloads_found:
                print("Search successful - found results or downloads!")
                break
            else:
                print("No results or download buttons found. Retrying...")
                continue
            
        except Exception as e:
            print(f"Error during attempt {attempt+1}: {e}")
            time.sleep(2)
            
except Exception as e:
    print(f"Fatal error: {e}")
    
finally:
    print("\nScraping complete. Browser will remain open.")
    input("Press Enter to close browser...")
    # Uncomment to close browser automatically:
    # driver.quit()
