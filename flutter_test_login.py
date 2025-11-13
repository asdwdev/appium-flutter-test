from appium import webdriver
from appium.options.common import AppiumOptions
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

print("🚀 Memulai sesi Appium Flutter (pakai UiAutomator2)...")

options = AppiumOptions()
options.set_capability("platformName", "Android")
options.set_capability("automationName", "UiAutomator2")
options.set_capability("deviceName", "emulator-5554")  # ubah sesuai hasil `adb devices`
options.set_capability("app", "C:\\Users\\LENOVO\\Downloads\\app-debug.apk")
options.set_capability("appPackage", "com.example.automation_testing")
options.set_capability("appActivity", ".MainActivity")
options.set_capability("noReset", True)
options.set_capability("newCommandTimeout", 300)

driver = webdriver.Remote("http://127.0.0.1:4723", options=options)

print("✅ Appium berhasil terhubung ke aplikasi!")
time.sleep(5)  # tunggu app boot

try:
    print("📱 Contexts:", driver.contexts)
    driver.switch_to.context("NATIVE_APP")
    print("🔁 Berhasil switch ke NATIVE_APP context")

    # 🔄 Tunggu sampai elemen email benar-benar muncul di source
    print("⏳ Menunggu halaman login muncul (max 60 detik)...")
    found = False
    for i in range(60):
        src = driver.page_source
        if "login_email_input" in src:
            found = True
            print(f"✅ Elemen email ditemukan di detik ke-{i}")
            break
        time.sleep(1)

    if not found:
        raise Exception("Elemen login_email_input tidak muncul di page source dalam 60 detik.")

    # --- LOGIN FLOW ---
    print("🔍 Cari field email (pakai resource-id)...")
    email_field = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().resourceId("login_email_input")'))
    )
    email_field.click()
    email_field.send_keys("user@test.com")
    print("✅ Email diisi.")

    print("🔍 Cari field password...")
    password_field = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().resourceId("login_password_input")'))
    )
    password_field.click()
    password_field.send_keys("user123")
    print("✅ Password diisi.")

    print("🔍 Klik tombol Login...")
    login_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "Login"))
    )
    login_button.click()
    print("🚀 Tombol login diklik!")

    time.sleep(5)

    try:
        dashboard = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "menu_dashboard_button")
        if dashboard.is_displayed():
            print("🎉 Login sukses, dashboard terlihat!")
        else:
            print("⚠️ Dashboard tidak tampil walau login diklik.")
    except Exception:
        print("⚠️ Tidak menemukan dashboard button, mungkin login gagal.")

except Exception as e:
    print("❌ Terjadi kesalahan selama login:", e)
    try:
        print("\n===== 🧩 PAGE SOURCE SAAT ERROR =====\n")
        print(driver.page_source[:2000])
        print("\n=====================================\n")
    except Exception:
        print("(Gagal ambil page source untuk debug)")

finally:
    driver.quit()
    print("🧹 Sesi Appium ditutup.")
