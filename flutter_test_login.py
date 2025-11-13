from appium import webdriver
from appium.options.common import AppiumOptions
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import mysql.connector
from datetime import datetime

# ============================
# 🔧 KONFIGURASI DATABASE
# ============================
DB_CONFIG = {
    "host": "localhost",
    "user": "root",            # ubah sesuai user MySQL kamu
    "password": "",            # isi password MySQL kamu
    "database": "automation_db"  # pastikan DB ini sudah dibuat
}

# Buat tabel kalau belum ada
def setup_database():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS test_results (
            id INT AUTO_INCREMENT PRIMARY KEY,
            test_time DATETIME,
            status VARCHAR(20),
            error_message TEXT,
            duration FLOAT
        )
    """)
    conn.commit()
    conn.close()

# Simpan hasil test
def save_test_result(status, error_message, duration):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    query = "INSERT INTO test_results (test_time, status, error_message, duration) VALUES (%s, %s, %s, %s)"
    values = (datetime.now(), status, error_message, duration)
    cursor.execute(query, values)
    conn.commit()
    conn.close()
    print(f"💾 Hasil test disimpan ke MySQL (status: {status})")


# ============================
# 🚀 MULAI TEST APPIUM
# ============================
setup_database()
start_time = time.time()
status = "SUCCESS"
error_message = None

print("🚀 Memulai sesi Appium Flutter (pakai UiAutomator2)...")

# --- KONFIGURASI KAPABILITAS ---
options = AppiumOptions()
options.set_capability("platformName", "Android")
options.set_capability("automationName", "UiAutomator2")
options.set_capability("deviceName", "emulator-5554")  # ubah sesuai hasil adb devices
options.set_capability("app", "C:\\Users\\LENOVO\\Downloads\\app-debug.apk")
options.set_capability("appPackage", "com.example.automation_testing")
options.set_capability("appActivity", ".MainActivity")
options.set_capability("noReset", True)
options.set_capability("newCommandTimeout", 300)

# --- HUBUNGKAN KE SERVER APPIUM ---
driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
print("✅ Appium berhasil terhubung ke aplikasi!")

time.sleep(5)

try:
    print("📱 Contexts:", driver.contexts)
    driver.switch_to.context("NATIVE_APP")
    print("🔁 Berhasil switch ke NATIVE_APP context")

    # --- LOGIN FLOW ---
    print("⏳ Menunggu halaman login...")
    found = False
    for i in range(60):
        src = driver.page_source
        if "login_email_input" in src:
            found = True
            print(f"✅ Elemen email ditemukan di detik ke-{i}")
            break
        time.sleep(1)
    if not found:
        raise Exception("Elemen login_email_input tidak muncul dalam 60 detik.")

    email_field = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("login_email_input")')
        )
    )
    email_field.click()
    email_field.send_keys("user@test.com")

    password_field = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("login_password_input")')
        )
    )
    password_field.click()
    password_field.send_keys("user123")

    login_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "Login"))
    )
    login_button.click()
    print("🚀 Login berhasil diklik!")

    # --- DASHBOARD ---
    dashboard = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable(
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("bottom_nav_dashboard")')
        )
    )
    dashboard.click()
    print("✅ Klik Dashboard.")

    # --- PROFILE ---
    profile_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable(
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("bottom_nav_profile")')
        )
    )
    time.sleep(1)
    profile_button.click()
    print("✅ Klik Profile.")

    # --- SETTINGS ---
    settings_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable(
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("bottom_nav_settings")')
        )
    )
    time.sleep(1)
    settings_button.click()
    print("✅ Klik Settings.")

    # --- HOME ---
    home_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable(
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("bottom_nav_home")')
        )
    )
    time.sleep(1)
    home_button.click()
    print("✅ Kembali ke Home.")

    # --- LOGOUT ---
    logout_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable(
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().description("Logout")')
        )
    )
    time.sleep(1)
    logout_button.click()
    print("🚪 Logout berhasil dilakukan!")

except Exception as e:
    status = "FAILED"
    error_message = str(e)
    print("❌ Terjadi kesalahan:", e)
    try:
        print(driver.page_source[:2000])
    except Exception:
        print("(Gagal ambil page source)")

finally:
    driver.quit()
    duration = round(time.time() - start_time, 2)
    print(f"🧹 Sesi Appium ditutup. Durasi: {duration} detik")
    save_test_result(status, error_message, duration)
