const fs = require('fs');
const path = require('path');
const Telegraf = require('telegraf');
const cv = require('opencv4nodejs');
const Tesseract = require('tesseract.js');
const { Builder, By, until } = require('selenium-webdriver');
require('chromedriver');

// بارگذاری تنظیمات از فایل JSON
const config = require('./config.json');

const TELEGRAM_TOKEN = config.telegram_token; // توکن ربات تلگرام از فایل JSON
const bot = new Telegraf(TELEGRAM_TOKEN);

const takeScreenshot = async (url, outputPath) => {
  let driver = await new Builder().forBrowser('chrome').build();
  try {
    await driver.get(url);
    let screenshot = await driver.takeScreenshot();
    fs.writeFileSync(outputPath, screenshot, 'base64');
  } finally {
    await driver.quit();
  }
};

const splitImage = async (imagePath) => {
  const image = await cv.imreadAsync(imagePath);
  const height = image.rows;
  const sectionHeight = Math.floor(height / 4);

  const topSection = image.getRegion(new cv.Rect(0, 0, image.cols, sectionHeight));
  const upperMiddleSection = image.getRegion(new cv.Rect(0, sectionHeight, image.cols, sectionHeight));
  const lowerMiddleSection = image.getRegion(new cv.Rect(0, sectionHeight * 2, image.cols, sectionHeight));
  const bottomSection = image.getRegion(new cv.Rect(0, sectionHeight * 3, image.cols, height - sectionHeight * 3));

  const topSectionPath = 'top_section.png';
  const upperMiddleSectionPath = 'upper_middle_section.png';
  const lowerMiddleSectionPath = 'lower_middle_section.png';
  const bottomSectionPath = 'bottom_section.png';

  await Promise.all([
    cv.imwriteAsync(topSectionPath, topSection),
    cv.imwriteAsync(upperMiddleSectionPath, upperMiddleSection),
    cv.imwriteAsync(lowerMiddleSectionPath, lowerMiddleSection),
    cv.imwriteAsync(bottomSectionPath, bottomSection)
  ]);

  return [topSectionPath, upperMiddleSectionPath, lowerMiddleSectionPath, bottomSectionPath];
};

const extractTextFromImage = async (imagePath) => {
  const { data: { text } } = await Tesseract.recognize(imagePath, 'eng');
  return text;
};

bot.start((ctx) => ctx.reply('سلام! برای چک کردن سایت، دستور /check <نام سایت> را ارسال کنید.'));

bot.command('check', async (ctx) => {
  try {
    const website = ctx.message.text.split(' ')[1];
    if (!website) {
      return ctx.reply('لطفاً نام سایت را بعد از دستور /check وارد کنید.');
    }
    const url = `https://scamminder.com/websites/${website}/`;
    const screenshotPath = `${website}_screenshot.png`;
    await takeScreenshot(url, screenshotPath);

    const [topSectionPath, upperMiddleSectionPath, lowerMiddleSectionPath, bottomSectionPath] = await splitImage(screenshotPath);

    const sections = [
      { path: topSectionPath, caption: 'قسمت بالایی 1' },
      { path: upperMiddleSectionPath, caption: 'قسمت بالایی 2' },
      { path: lowerMiddleSectionPath, caption: 'قسمت پایینی 1' },
      { path: bottomSectionPath, caption: 'قسمت پایینی 2' }
    ];

    for (const { path, caption } of sections) {
      await ctx.replyWithPhoto({ source: path }, { caption });
      const text = await extractTextFromImage(path);
      await ctx.reply(`متن استخراج شده: ${text}`);
    }
  } catch (error) {
    ctx.reply(`خطایی رخ داده است: ${error.message}`);
  }
});

bot.launch();
