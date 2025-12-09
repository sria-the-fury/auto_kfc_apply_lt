import datetime
import time
import os
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager

# --- USER DATA ---
TARGET_URL = 'https://apollolt.teamdash.com/p/jobs/17/prisijunk-prie-musu-komandos#QLwk'
MY_NAME = "Md Jakaria Mashud Shahria"
MY_EMAIL = "jakariamsria@gmail.com"
MY_PHONE = "69096326"
CV_FILENAME = "Jakaria-LT_2111.pdf" 
POSITIONS_POOL = ["Burgerių gaminimas", "Vištienos paniravimas"]
TARGET_CITY_ID = "985" 

def apply_to_job():
    current_folder = os.path.dirname(os.path.abspath(__file__))
    cv_full_path = os.path.join(current_folder, CV_FILENAME)

    if not os.path.exists(cv_full_path):
        print(f"❌ ERROR: CV file not found at {cv_full_path}")
        return

    # --- FIREFOX SETUP ---
    print("🚀 Setting up Firefox...")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox") 
    options.add_argument("--width=1920")
    options.add_argument("--height=1080")
    
    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 20)

    try:
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
        print("🔀 looking for Iframe...")
        try:
            iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#QLwk iframe")))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", iframe)
            driver.switch_to.frame(iframe)
            print("✅ Successfully switched inside the Form Iframe!")
            time.sleep(2)
        except Exception as e:
            print(f"❌ Could not switch to iframe: {e}")
            raise

        # 3. FILL NAME
        print(f"✍️  Filling Name...")
        name_field = wait.until(EC.visibility_of_element_located((By.ID, "vardas-pavard")))
        name_field.clear()
        name_field.send_keys(MY_NAME)

        # 4. FILL EMAIL
        print(f"📧 Filling Email...")
        driver.find_element(By.ID, "el-patas").send_keys(MY_EMAIL)

        # 5. FILL PHONE
        print(f"📱 Filling Phone...")
        driver.find_element(By.NAME, "telephone").send_keys(MY_PHONE)
        
        # 6. POSITION
        print(f"🎲 Selecting Position...")
        today = datetime.datetime.now().day
        print(f"ℹ️ Today is day: {today}")
        
        if today % 2 == 0: 
            chosen = POSITIONS_POOL[0] # Even days
        else: 
            chosen = POSITIONS_POOL[1] # Odd days
            
        print(f"ℹ️ Applying for: {chosen}")
        select_elem = driver.find_element(By.ID, "kokioje-pozicijoje-nori-ibandyti-savo-jgas")
        Select(select_elem).select_by_value(chosen)
        print(f"✅ Selected: {chosen}")

        # 7. CITY
        print("🏙️ Selecting City...")
        city_id = f"miestas-{TARGET_CITY_ID}"
        try:
            city_box = driver.find_element(By.ID, city_id)
            driver.execute_script("arguments[0].click();", city_box)
            print("✅ City checked (ID method)")
        except:
            city_box = driver.find_element(By.CSS_SELECTOR, f"input[value='{TARGET_CITY_ID}']")
            driver.execute_script("arguments[0].click();", city_box)
            print("✅ City checked (Value method)")

        # 8. UPLOAD CV
        print(f"📂 Uploading CV...")
        file_input = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
        file_input.send_keys(cv_full_path)

        # 9. CONSENT CHECKBOXES
        print("☑️ Checking Consents...")
        try:
            age_box = driver.find_element(By.NAME, "ar-esi-pilnametis")
            driver.execute_script("arguments[0].click();", age_box)
        except:
            print("⚠️ Age box not found")

        try:
            gdpr_box = driver.find_element(By.NAME, "sutinku-jog-mano-cv-bt-saugomas-36-mn-po-pateikimo")
            driver.execute_script("arguments[0].click();", gdpr_box)
        except:
            print("⚠️ GDPR box not found")

        # 10. SUBMIT (UPDATED WITH FORCE CLICK)
        print("🚀 Submitting...")
        try:
            # 1. Wait for button
            submit_btn = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.btn-primary")))
            
            # 2. Scroll button into view (align to bottom to avoid headers blocking it)
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_btn)
            time.sleep(1) # Give it a moment to settle
            
            # 3. FORCE CLICK via JavaScript (Bypasses overlays/not-clickable errors)
            driver.execute_script("arguments[0].click();", submit_btn)
            print("✅ Button clicked via JavaScript execution.")
            
        except Exception as e:
            print(f"❌ Failed to click button: {e}")

        
        print("⏳ Waiting for success confirmation (attribute check)...")
        
        try:
            # Check for success="true"
            success_element = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "form[success='true']")
            ))
            
            print("\n🎉 SUCCESS CONFIRMED!")
            print("✅ Found <form success='true'> in the HTML.")
            print("Application has been strictly verified.")
            
        except Exception as e:
            print("\n⚠️ VERIFICATION FAILED or TIMED OUT.")
            print("The form tag did not get 'success=true'.")
            
            # Save debug info
            driver.save_screenshot("verification_failed.png")
            print("📸 Saved 'verification_failed.png'")
            
            # Check for errors
            errors = driver.find_elements(By.CSS_SELECTOR, ".has-error, .is-invalid")
            if len(errors) > 0:
                print("❌ Found validation errors on the form (Red fields).")

        time.sleep(2)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        driver.save_screenshot("iframe_error.png")
        print("📸 Screenshot saved as 'iframe_error.png'")

    finally:
        driver.quit()

if __name__ == "__main__":
    apply_to_job()