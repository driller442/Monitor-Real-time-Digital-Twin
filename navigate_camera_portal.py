import time
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

# --- Configuration ---
PROFILE_PATH = r"C:\ChromeSeleniumProfile"
CAMERA_URL = "https://ipc-eu.ismartlife.me/#/cameraView?id=your_camera_id_here"

DEFAULT_TILT_CLICKS = 6
DEFAULT_PAN_HOLD_DURATION = 1.5
DEFAULT_TILT_HOLD_DURATION = 1.5

VIDEO_PLAYER_AREA_SELECTOR = "div.camera_mainVideo1__20JW9"
PTZ_HOVER_ACTIVATED_CONTAINER_XPATH = "//div[contains(@class,'camera_shark__3xiHH')]"
TILT_UP_XPATH = "(//div[contains(@class,'camera_click__2Wc0w')]/div[contains(@class,'camera_clickItem__IhuPx')])[1]"
PAN_RIGHT_XPATH = "(//div[contains(@class,'camera_click__2Wc0w')]/div[contains(@class,'camera_clickItem__IhuPx')])[2]"
PAN_LEFT_XPATH = "(//div[contains(@class,'camera_click__2Wc0w')]/div[contains(@class,'camera_clickItem__IhuPx')])[3]"
TILT_DOWN_XPATH = "(//div[contains(@class,'camera_click__2Wc0w')]/div[contains(@class,'camera_clickItem__IhuPx')])[4]"

# --- Movement Queue ---
movement_queue = []

def queue_action(action, *args, **kwargs):
    movement_queue.append((action, args, kwargs))
    print(f"Queued: {action.__name__} args={args} kwargs={kwargs}")

def robust_click(driver, button_element, action_description):
    try:
        button_element.click()
        print(f"Standard click successful for {action_description}.")
    except ElementClickInterceptedException:
        print(f"Standard click intercepted for {action_description}. Trying JavaScript click.")
        try:
            driver.execute_script("arguments[0].click();", button_element)
            print(f"JavaScript click successful for {action_description}.")
        except Exception as js_e:
            print(f"JavaScript click ALSO FAILED for {action_description}: {js_e}")
            raise 

def ensure_ptz_controls_visible(driver, video_player_element_selector, ptz_container_xpath):
    print("Ensuring PTZ controls are visible...")
    video_player_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, video_player_element_selector))
    )
    hover_action = ActionChains(driver)
    hover_action.move_to_element(video_player_element).perform()
    time.sleep(0.7)
    try:
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, ptz_container_xpath))
        )
        time.sleep(0.5)
        return True
    except TimeoutException:
        print("ERROR: PTZ control container DID NOT become visible after hover.")
        return False

def get_clickable_element(driver, xpath_locator, description):
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath_locator)))
    button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, xpath_locator))
    )
    time.sleep(0.2)
    return button

def perform_tilt_up(driver, clicks=DEFAULT_TILT_CLICKS):
    print(f"--- ACTION: Tilting UP ({clicks} clicks) ---")
    if not ensure_ptz_controls_visible(driver, VIDEO_PLAYER_AREA_SELECTOR, PTZ_HOVER_ACTIVATED_CONTAINER_XPATH):
        return
    button = get_clickable_element(driver, TILT_UP_XPATH, "Tilt UP button")
    for i in range(clicks):
        print(f"Tilt UP: Click {i+1} of {clicks}")
        robust_click(driver, button, f"Tilt UP (Click {i+1})")
        time.sleep(0.3)
    print("Tilt UP action completed.")

def perform_tilt_down(driver, duration=DEFAULT_TILT_HOLD_DURATION):
    print(f"--- ACTION: Tilting DOWN (hold {duration}s) ---")
    if not ensure_ptz_controls_visible(driver, VIDEO_PLAYER_AREA_SELECTOR, PTZ_HOVER_ACTIVATED_CONTAINER_XPATH):
        return
    button = get_clickable_element(driver, TILT_DOWN_XPATH, "Tilt DOWN button")
    actions = ActionChains(driver)
    print(f"Pressing and holding Tilt DOWN for {duration}s...")
    actions.click_and_hold(button).perform()
    time.sleep(duration)
    print("Releasing Tilt DOWN...")
    actions.release(button).perform()
    print("Tilt DOWN action completed.")

def perform_pan_left(driver, duration=DEFAULT_PAN_HOLD_DURATION):
    print(f"--- ACTION: Panning LEFT (hold {duration}s) ---")
    if not ensure_ptz_controls_visible(driver, VIDEO_PLAYER_AREA_SELECTOR, PTZ_HOVER_ACTIVATED_CONTAINER_XPATH):
        return
    button = get_clickable_element(driver, PAN_LEFT_XPATH, "Pan LEFT button")
    actions = ActionChains(driver)
    print(f"Pressing and holding Pan LEFT for {duration}s...")
    actions.click_and_hold(button).perform()
    time.sleep(duration)
    print("Releasing Pan LEFT...")
    actions.release(button).perform()
    print("Pan LEFT action completed.")

def perform_pan_right(driver, duration=DEFAULT_PAN_HOLD_DURATION):
    print(f"--- ACTION: Panning RIGHT (hold {duration}s) ---")
    if not ensure_ptz_controls_visible(driver, VIDEO_PLAYER_AREA_SELECTOR, PTZ_HOVER_ACTIVATED_CONTAINER_XPATH):
        return
    button = get_clickable_element(driver, PAN_RIGHT_XPATH, "Pan RIGHT button")
    actions = ActionChains(driver)
    print(f"Pressing and holding Pan RIGHT for {duration}s...")
    actions.click_and_hold(button).perform()
    time.sleep(duration)
    print("Releasing Pan RIGHT...")
    actions.release(button).perform()
    print("Pan RIGHT action completed.")

def record_movements():
    """Queue up a set of movements. Modify this as needed."""
    queue_action(perform_tilt_up, clicks=DEFAULT_TILT_CLICKS)
    queue_action(perform_pan_right, duration=DEFAULT_PAN_HOLD_DURATION)
    queue_action(perform_tilt_down, duration=DEFAULT_TILT_HOLD_DURATION)
    queue_action(perform_pan_left, duration=DEFAULT_PAN_HOLD_DURATION)
    print("\nMovement sequence recorded (but not executed).")

def execute_movements(driver):
    """Execute all queued movements."""
    print("\nExecuting queued movements...")
    for idx, (func, args, kwargs) in enumerate(movement_queue, 1):
        print(f"Step {idx}: {func.__name__} args={args} kwargs={kwargs}")
        func(driver, *args, **kwargs)
        time.sleep(2)

def main():
    print(f"Starting camera portal navigation (PTZ queue mode)...")
    chrome_options = Options()
    chrome_options.add_argument(f"user-data-dir={PROFILE_PATH}")

    service = ChromeService(executable_path=ChromeDriverManager().install())
    driver = None

    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print(f"Navigating to camera portal: {CAMERA_URL}")
        driver.get(CAMERA_URL)

        print("Waiting for the video player area to be present (max 20 seconds)...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, VIDEO_PLAYER_AREA_SELECTOR))
        )
        print("Video player area found. Giving page 2s to fully settle...")
        time.sleep(2)

        # Record (but do not perform) the movements
        record_movements()

        print("\nQueued movements:")
        for idx, (func, args, kwargs) in enumerate(movement_queue, 1):
            print(f"  {idx}. {func.__name__} args={args} kwargs={kwargs}")

        print("Auto-skip: No movements will be executed.")

    except Exception as e:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(f"AN ERROR OCCURRED: {e}")
        print("-----------------------------------------------")
        print("FULL PYTHON TRACEBACK:")
        traceback.print_exc()
        print("-----------------------------------------------")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    finally:
        input("Press Enter to close browser and terminate script...")
        if driver:
            driver.quit()
        print("Browser closed, script terminated.")

if __name__ == "__main__":
    main()
