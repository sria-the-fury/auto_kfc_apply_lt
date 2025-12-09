import datetime
import time
import os
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys

# --- USER DATA ---
TARGET_URL = 'https://apollolt.teamdash.com/p/jobs/17/prisijunk-prie-musu-komandos#QLwk'
MY_NAME = "Md Jakaria Mashud Shahria"
MY_EMAIL = "jakariamsria@gmail.com"
MY_PHONE = "69096326"
CV_FILENAME = "Jakaria-LT_2111.pdf" 
POSITIONS_POOL = ["Burgerių gaminimas", "Vištienos paniravimas"]
TARGET_CITY_ID = "985" 

def apply_to_job():
    driver = None
    current_folder = os.path.dirname(os.path.abspath(__file__))
    cv_full_path = os.path.join(current_folder, CV_FILENAME)

    if not os.path.exists(cv_full_path):
        raise FileNotFoundError(f"❌ CV file missing: {cv_full_path}")

    # --- CHROME SETUP (Optimized for GitHub Actions) ---
    print("🚀 Setting up Chrome...")
    options = Options()
    
    # CRITICAL FLAGS FOR SERVER STABILITY
    #options.add_argument("--headless=new") # Must use 'new' headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage") # Prevents memory crashes
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        wait = WebDriverWait(driver, 20)

        print(f"🌍 Navigating...")
        driver.get(TARGET_URL)
        time.sleep(5) 

        # 1. HANDLE COOKIES
        print("🍪 Cookies...")
        try:
            cookie_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Sutinku') or contains(text(), 'Accept') or contains(text(), 'Allow')]")
            cookie_btn.click()
            print("✅ Cookie Banner clicked.")
            time.sleep(1)
        except:
            print("ℹ️ No cookie button found.")

        # 2. SWITCH TO IFRAME
        print("🔀 Looking for Iframe...")
        try:
            iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#QLwk iframe")))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", iframe)
            driver.switch_to.frame(iframe)
            print("✅ Inside Iframe!")
            time.sleep(2)
        except Exception as e:
            print(f"❌ Critical: Could not switch to iframe. {e}")
            raise

        # 3. FILL FORM DATA
        print(f"✍️  Filling Data...")
        wait.until(EC.visibility_of_element_located((By.ID, "vardas-pavard"))).send_keys(MY_NAME)
        driver.find_element(By.ID, "el-patas").send_keys(MY_EMAIL)
        driver.find_element(By.NAME, "telephone").send_keys(MY_PHONE)
        
        # 4. POSITION (Date Logic)
        today = datetime.datetime.now().day
        chosen = POSITIONS_POOL[0] if today % 2 == 0 else POSITIONS_POOL[1]
        print(f"📅 Day {today}: Applying for '{chosen}'")
        
        try:
            select_elem = driver.find_element(By.ID, "kokioje-pozicijoje-nori-ibandyti-savo-jgas")
            Select(select_elem).select_by_value(chosen)
        except:
            # Fallback for weird dropdowns
            sel = driver.find_element(By.TAG_NAME, "select")
            sel.send_keys(Keys.ARROW_DOWN if today % 2 == 0 else Keys.ARROW_DOWN + Keys.ARROW_DOWN)
            sel.send_keys(Keys.ENTER)

        # 5. CITY
        try:
            driver.execute_script("arguments[0].click();", driver.find_element(By.ID, f"miestas-{TARGET_CITY_ID}"))
        except:
            driver.execute_script("arguments[0].click();", driver.find_element(By.CSS_SELECTOR, f"input[value='{TARGET_CITY_ID}']"))

        # 6. UPLOAD CV
        print(f"📂 Uploading CV...")
        driver.find_element(By.CSS_SELECTOR, "input[type='file']").send_keys(cv_full_path)

        # 7. CONSENTS
        try:
            driver.execute_script("arguments[0].click();", driver.find_element(By.NAME, "ar-esi-pilnametis"))
            driver.execute_script("arguments[0].click();", driver.find_element(By.NAME, "sutinku-jog-mano-cv-bt-saugomas-36-mn-po-pateikimo"))
        except:
            pass

        # 8. SUBMIT (Force Click)
        print("🚀 Submitting...")
        try:
            btn = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.btn-primary")))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", btn)
            print("✅ Button clicked.")
        except Exception as e:
            print(f"❌ Click failed: {e}")
            raise

        # 9. VERIFY SUCCESS
        print("⏳ Verifying...")
        try:
            # Wait for success attribute
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "form[success='true']")))
            print("\n🎉 SUCCESS! <form success='true'> detected.")
        except:
            print("⚠️ Attribute check failed. Checking for errors...")
            if len(driver.find_elements(By.CSS_SELECTOR, ".has-error, .is-invalid")) > 0:
                print("❌ Validation Errors detected.")
            driver.save_screenshot("verification_fail.png")
            raise Exception("Verification Failed")

        time.sleep(2)
        driver.save_screenshot("final_success.png")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        if driver: driver.save_screenshot("crash.png")
        raise e

    finally:
        if driver: driver.quit()

if __name__ == "__main__":
    apply_to_job()