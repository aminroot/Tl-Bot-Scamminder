import telebot
import imgkit
import nest_asyncio
from google.colab import files
import cv2  # OpenCV برای پردازش تصویر
import pytesseract
from pytesseract import Output

# تنظیم حلقه رویداد برای رفع خطای RuntimeError
nest_asyncio.apply()

# تنظیمات تلگرام
TELEGRAM_TOKEN = '7375087926:AAEFvme2mywrVfY7HHxA_qSoPY6CdFA4Erg'  # توکن ربات تلگرام خود را وارد کنید
bot = telebot.TeleBot(TELEGRAM_TOKEN)

def take_screenshot(url, path):
    options = {'format': 'png'}
    imgkit.from_url(url, path, options=options)

def split_image(image_path):
    # بارگذاری تصویر با استفاده از OpenCV
    image = cv2.imread(image_path)
    height, width, _ = image.shape

    # تقسیم تصویر به چهار قسمت افقی
    section_height = height // 4
    top_section = image[:section_height, :]
    upper_middle_section = image[section_height:2*section_height, :]
    lower_middle_section = image[2*section_height:3*section_height, :]
    bottom_section = image[3*section_height:, :]

    # مسیر ذخیره تصاویر
    top_section_path = 'top_section.png'
    upper_middle_section_path = 'upper_middle_section.png'
    lower_middle_section_path = 'lower_middle_section.png'
    bottom_section_path = 'bottom_section.png'

    # ذخیره تصاویر به فایل‌های جداگانه با فرمت PNG
    cv2.imwrite(top_section_path, top_section, [cv2.IMWRITE_PNG_COMPRESSION, 0])
    cv2.imwrite(upper_middle_section_path, upper_middle_section, [cv2.IMWRITE_PNG_COMPRESSION, 0])
    cv2.imwrite(lower_middle_section_path, lower_middle_section, [cv2.IMWRITE_PNG_COMPRESSION, 0])
    cv2.imwrite(bottom_section_path, bottom_section, [cv2.IMWRITE_PNG_COMPRESSION, 0])

    return top_section_path, upper_middle_section_path, lower_middle_section_path, bottom_section_path

def extract_text_from_image(image_path):
    # بارگذاری تصویر
    image = cv2.imread(image_path)
    # استفاده از Tesseract برای استخراج متن
    text = pytesseract.image_to_string(image, lang='eng')
    return text

# دستور /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "سلام! برای چک کردن سایت، دستور /check <نام سایت> را ارسال کنید.")

# دستور /check با ورودی از کاربر
@bot.message_handler(commands=['check'])
def check_website(message):
    try:
        website = message.text.split()[1]  # گرفتن ورودی کاربر
        url = f'https://scamminder.com/websites/{website}/'
        screenshot_path = f'{website}_screenshot.png'
        take_screenshot(url, screenshot_path)
        
        # تقسیم تصویر به چهار قسمت افقی
        top_section_path, upper_middle_section_path, lower_middle_section_path, bottom_section_path = split_image(screenshot_path)
        
        # ارسال تکه‌های تصویر به تلگرام همراه با متن استخراج شده
        for section_path, caption in zip(
            [top_section_path, upper_middle_section_path, lower_middle_section_path, bottom_section_path],
            ["قسمت بالایی 1", "قسمت بالایی 2", "قسمت پایینی 1", "قسمت پایینی 2"]
        ):
            with open(section_path, 'rb') as section_photo:
                bot.send_photo(message.chat.id, section_photo, caption=caption)
            
            # استخراج و ارسال متن زیر تصویر
            text = extract_text_from_image(section_path)
            bot.send_message(message.chat.id, f"متن استخراج شده: {text}")
        
        # آپلود فایل به Google Colab
        files.download(screenshot_path)
    except IndexError:
        bot.reply_to(message, "لطفاً نام سایت را بعد از دستور /check وارد کنید.")
    except Exception as e:
        bot.reply_to(message, f"خطایی رخ داده است: {e}")

# راه‌اندازی ربات
bot.polling()
