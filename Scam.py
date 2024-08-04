
!pip install selenium opencv-python pytesseract pillow


import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import cv2
import pytesseract
from PIL import Image

# بارگذاری تنظیمات از فایل JSON
with open('config.json') as config_file:
    config = json.load(config_file)

TELEGRAM_TOKEN = config['telegram_token']

# پیکربندی Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")  # اجرای بدون رابط گرافیکی
chrome_service = ChromeService(executable_path='/path/to/chromedriver')  # مسیر به chromedriver

def take_screenshot(url, output_path):
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    try:
        driver.get(url)
        screenshot = driver.get_screenshot_as_base64()
        with open(output_path, 'wb') as f:
            f.write(screenshot.decode('base64'))
    finally:
        driver.quit()

def split_image(image_path):
    image = cv2.imread(image_path)
    height, width, _ = image.shape
    section_height = height // 4

    top_section = image[0:section_height, 0:width]
    upper_middle_section = image[section_height:section_height*2, 0:width]
    lower_middle_section = image[section_height*2:section_height*3, 0:width]
    bottom_section = image[section_height*3:, 0:width]

    cv2.imwrite('top_section.png', top_section)
    cv2.imwrite('upper_middle_section.png', upper_middle_section)
    cv2.imwrite('lower_middle_section.png', lower_middle_section)
    cv2.imwrite('bottom_section.png', bottom_section)

# استفاده از پایتون برای پردازش تصویر
def process_image_with_ocr(image_path):
    text = pytesseract.image_to_string(Image.open(image_path))
    return text
