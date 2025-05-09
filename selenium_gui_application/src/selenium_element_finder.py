# selenium_element_finder.py (v2 - With Command-Line Arguments)
# A reusable tool to scan a web page using Selenium and log details of found elements.

import time
import os
import argparse # For command-line arguments
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException, StaleElementReferenceException
import subprocess
import json
import sys

# Import webdriver-manager for automatic ChromeDriver management
from webdriver_manager.chrome import ChromeDriverManager

# --- Default Configuration (can be overridden by command-line args) ---
DEFAULT_PAGE_LOAD_WAIT_SECONDS = 20
DEFAULT_HOVER_WAIT_SECONDS = 3
DEFAULT_ELEMENT_TAGS_TO_SCAN = ["div", "span", "svg", "i", "img", "button", "a", "input", "textarea", "select", "form"]
# --- End of Default Configuration ---

def kill_chrome_processes():
    # (Function remains the same as before)
    print("Attempting to terminate existing Chrome processes...")
    try:
        if sys.platform.startswith('win'):
            subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        elif sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
            subprocess.run(["pkill", "-f", "chrome"], check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        print("  Command to kill Chrome processes not found. Skipping.")
    except Exception as e:
        print(f"  Error terminating Chrome processes: {e}")

def get_element_attributes_as_dict(driver_instance, element_to_query):
    # (Function remains the same as before)
    try:
        return driver_instance.execute_script(
            'var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) { items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;',
            element_to_query
        )
    except Exception:
        return {"error_getting_attributes_js": "Could not execute JS for attributes"}

def log_element_details(driver_instance, element_to_log, strategy_name, file_handle):
    # (Function remains largely the same, minor error handling improvements possible)
    try:
        tag = "N/A (stale or error)"
        try:
            tag = element_to_log.tag_name
            element_to_log.is_displayed() 
        except StaleElementReferenceException:
            print(f"  Element ({strategy_name}, tag: {tag if tag != 'N/A (stale or error)' else 'unknown'}) is stale. Skipping.")
            file_handle.write(f"Element Searched: {strategy_name}\n  Result: STALE\n------------------------------------\n")
            return
        except Exception as initial_access_error:
            print(f"  Error initially accessing element ({strategy_name}): {initial_access_error}. Skipping.")
            file_handle.write(f"Element Searched: {strategy_name}\n  Result: ERROR ON INITIAL ACCESS - {initial_access_error}\n------------------------------------\n")
            return

        all_attrs = get_element_attributes_as_dict(driver_instance, element_to_log)
        
        element_id = all_attrs.get("id", "N/A")
        element_class = all_attrs.get("class", "N/A")
        title = all_attrs.get("title", "N/A")
        aria_label = all_attrs.get("aria-label", "N/A")
        role = all_attrs.get("role", "N/A")
        
        xlink_href = "N/A"
        if tag.lower() == 'use':
            xlink_href = all_attrs.get("xlink:href", all_attrs.get("href", "N/A"))
        elif tag.lower() == 'svg':
            try:
                use_elements_in_svg = element_to_log.find_elements(By.TAG_NAME, "use")
                if use_elements_in_svg:
                    use_attrs = get_element_attributes_as_dict(driver_instance, use_elements_in_svg[0])
                    xlink_href = use_attrs.get("xlink:href", use_attrs.get("href", "N/A"))
            except Exception: xlink_href = "N/A (error finding/parsing <use>)"

        data_attributes = {k: v for k, v in all_attrs.items() if k.startswith('data-')}
        
        text_content = ""; is_displayed = False; is_enabled = False; size = {}; location = {}; outer_html_snippet = ""
        try: text_content = element_to_log.text.strip()
        except: pass 
        try: is_displayed = element_to_log.is_displayed()
        except: pass
        try: is_enabled = element_to_log.is_enabled()
        except: pass
        try: size = element_to_log.size
        except: pass
        try: location = element_to_log.location
        except: pass
        try: outer_html_snippet = element_to_log.get_attribute('outerHTML')[:350]
        except: pass

        details = (
            f"Source Tag Searched: {strategy_name}\n"
            f"  Tag Found: {tag}\n"
            f"  ID: {element_id}\n"
            f"  Class: {element_class}\n"
            f"  Title: {title}\n"
            f"  Aria-Label: {aria_label}\n"
            f"  Role: {role}\n"
            f"  xlink:href/href (for SVG/use): {xlink_href}\n"
            f"  Data Attributes: {json.dumps(data_attributes) if data_attributes else 'N/A'}\n"
            f"  Text Content: {text_content[:150] if text_content else 'N/A'}\n"
            f"  Displayed: {is_displayed}\n"
            f"  Enabled: {is_enabled}\n"
            f"  Size: {size}\n"
            f"  Location: {location}\n"
            f"  All Attributes (JSON): {json.dumps(all_attrs)}\n"
            f"  Outer HTML (first 350 chars): {outer_html_snippet}...\n"
            f"------------------------------------\n"
        )
        file_handle.write(details)
    except Exception as e_log: 
        file_handle.write(f"Error logging element ({strategy_name}): {e_log}\n------------------------------------\n")

def main(args):
    kill_chrome_processes()

    print(f"Target URL: {args.url}")
    if args.profile_path:
        print(f"Using Chrome Profile: {args.profile_path}")
    else:
        print("Not using a Chrome Profile (default behavior).")

    chrome_options = ChromeOptions()
    if args.profile_path:
        chrome_options.add_argument(f"user-data-dir={args.profile_path}")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--start-maximized")
    if args.headless:
        print("Running in headless mode.")
        chrome_options.add_argument("--headless")

    print("Initializing WebDriver...")
    driver = None
    try:
        # Use ChromeDriver path from environment variable if available, otherwise use webdriver-manager
        chromedriver_path = os.environ.get("CHROMEDRIVER_PATH")
        if chromedriver_path and os.path.exists(chromedriver_path):
            print(f"Using ChromeDriver from path: {chromedriver_path}")
            service = ChromeService(executable_path=chromedriver_path)
        else:
            print("No ChromeDriver path provided or path invalid. Using webdriver-manager to install ChromeDriver.")
            service = ChromeService(ChromeDriverManager().install())
        
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("WebDriver initialized.")
        actions = ActionChains(driver)

        driver.get(args.url)
        print(f"Navigated to {args.url}. Waiting {args.load_wait}s for page to load...")
        time.sleep(args.load_wait)
        print("Initial page load wait complete.")

        if args.enable_hover and args.hover_selector:
            hover_target_element = None
            try:
                print(f"Attempting to find hover target area by CSS selector: '{args.hover_selector}'")
                hover_target_element = driver.find_element(By.CSS_SELECTOR, args.hover_selector)
                
                if hover_target_element and hover_target_element.is_displayed():
                    print(f"Found displayed hover target: {hover_target_element.tag_name} (Selector: '{args.hover_selector}')")
                    print("Moving mouse to hover over target area...")
                    actions.move_to_element(hover_target_element).perform()
                    print(f"Hover simulated. Waiting {args.hover_wait}s for dynamic elements...")
                    time.sleep(args.hover_wait)
                    print("Hover wait complete.")
                else:
                    print(f"Hover target not found or not displayed (Selector: '{args.hover_selector}'). Proceeding without hover.")
            except NoSuchElementException:
                print(f"Hover target ('{args.hover_selector}') not found. Proceeding without hover.")
            except Exception as e_hover_setup:
                print(f"Error during hover setup: {e_hover_setup}. Proceeding without hover.")
        else:
            print("Hover simulation is disabled or no hover target specified.")

        print("Performing scan for elements...")
        output_file = args.output_file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"Element Scan for: {args.url} at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            if args.enable_hover and args.hover_selector:
                f.write(f"Scan performed after attempting hover on '{args.hover_selector}'.\n\n")
            else:
                f.write(f"Scan performed without hover simulation.\n\n")
            
            tags_to_scan = args.tags_to_scan.split(',') if args.tags_to_scan else DEFAULT_ELEMENT_TAGS_TO_SCAN
            print(f"Will scan for tags: {tags_to_scan}")

            for tag_name in tags_to_scan:
                tag_name = tag_name.strip()
                if not tag_name: continue
                print(f"Scanning for all <{tag_name}> elements...")
                try:
                    elements = driver.find_elements(By.TAG_NAME, tag_name)
                    print(f"Found {len(elements)} <{tag_name}> element(s).")
                    f.write(f"\nScan Results for <{tag_name}> elements:\n")
                    if elements:
                        for el_count, el in enumerate(elements):
                            if el_count > 0 and el_count % 25 == 0: 
                                print(f"  ...logged {el_count} of {len(elements)} <{tag_name}> elements...")
                            log_element_details(driver, el, f"All <{tag_name}>", f)
                    else:
                        f.write(f"No <{tag_name}> elements found.\n")
                    print(f"Finished scanning for <{tag_name}> elements.")
                except Exception as e_scan_tag:
                    print(f"Error scanning for <{tag_name}> elements: {e_scan_tag}")
                    f.write(f"Error scanning for <{tag_name}> elements: {e_scan_tag}\n------------------------------------\n")
            
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            if iframes:
                f.write(f"\nFound {len(iframes)} iframe(s). Details NOT extracted by this basic scan.\n")
            else:
                f.write("\nNo iframes found on the page.\n")

        print(f"Element scan details saved to {output_file}")

    except WebDriverException as e:
        print(f"A WebDriver error occurred: {e}")
        if "Chrome failed to start" in str(e):
            print("\nPossible causes:")
            print("1. Chrome is not installed correctly")
            print("2. Missing dependencies")
            print("3. Sandbox issues (try adding --no-sandbox flag)")
            
            # Suggest installing Chrome dependencies on Linux
            if sys.platform.startswith('linux'):
                print("\nOn Linux, try installing Chrome dependencies:")
                print("sudo apt-get install libnss3 libasound2 libatk-bridge2.0-0 libatk1.0-0 libcups2 libdbus-1-3 libgdk-pixbuf2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libxss1 libx11-xcb1 libxcomposite1 libxcursor1 libxdamage1 libxfixes3 libxi6 libxrandr2 libxrender1 libxtst6")
        import traceback; traceback.print_exc()
    except Exception as e:
        print(f"A general error occurred: {e}")
        import traceback; traceback.print_exc()
    finally:
        if driver:
            print("Closing WebDriver.")
            driver.quit()
        print(f"--- Element Finder Script Finished. Output: {args.output_file if 'args' in locals() and args.output_file else 'N/A'} ---")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Selenium Element Finder Tool")
    parser.add_argument("url", help="The target URL to scan.")
    parser.add_argument("-o", "--output_file", default="discovered_elements.txt", help="Name of the output file for results.")
    parser.add_argument("-p", "--profile_path", default=None, help="Path to Chrome user profile directory. (Optional)")
    parser.add_argument("--enable_hover", action="store_true", help="Enable hover simulation before scanning.")
    parser.add_argument("--hover_selector", default="body", help="CSS selector for the element to hover over if --enable_hover is used.")
    parser.add_argument("--load_wait", type=int, default=DEFAULT_PAGE_LOAD_WAIT_SECONDS, help="Seconds to wait for initial page load.")
    parser.add_argument("--hover_wait", type=int, default=DEFAULT_HOVER_WAIT_SECONDS, help="Seconds to wait after hover simulation.")
    parser.add_argument("--tags_to_scan", default=",".join(DEFAULT_ELEMENT_TAGS_TO_SCAN), help="Comma-separated list of HTML tags to scan (e.g., div,span,svg).")
    parser.add_argument("--headless", action="store_true", help="Run Chrome in headless mode.")
    
    parsed_args = parser.parse_args()
    main(parsed_args)