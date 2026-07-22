from playwright.sync_api import sync_playwright

import gspread

from google.oauth2.service_account import Credentials

import json

import os

# -------------------------------

# Google Sheets

# -------------------------------

SCOPES = [

    "https://www.googleapis.com/auth/spreadsheets",

    "https://www.googleapis.com/auth/drive",

]

creds = Credentials.from_service_account_info(

    json.loads(os.environ["GOOGLE_CREDENTIALS"]),

    scopes=SCOPES

)

gc = gspread.authorize(creds)

sheet = gc.open_by_key(

    os.environ["SPREADSHEET_ID"]

).worksheet("データ収集")

# -------------------------------

# 店舗ページ

# -------------------------------

URL = "https://min-repo.com/2958667/"

# -------------------------------

# Playwright

# -------------------------------

with sync_playwright() as p:

    browser = p.chromium.launch(

        headless=True,

        args=[

            "--no-sandbox",

            "--disable-dev-shm-usage",

        ],

    )

    page = browser.new_page(

        viewport={"width": 1400, "height": 3000},

        user_agent="Mozilla/5.0"

    )

    print("店舗ページへアクセス")

    page.goto(

        URL,

        wait_until="domcontentloaded",

        timeout=120000

    )

    page.wait_for_timeout(5000)

    print(page.title())

    print("リンク検索開始")

    report_url = ""

    links = page.locator("a").all()

    for link in links:

        try:

            text = link.inner_text().strip()

            href = link.get_attribute("href")

            if text:

                print(text)

            if href:

                print("  →", href)

            if "レポート一覧" in text:

                report_url = href

                break

        except:

            pass

    print("")

    print("レポート一覧URL")

    print(report_url)

    browser.close()

# -------------------------------

# 保存

# -------------------------------

sheet.clear()

sheet.append_row([

    "店舗",

    "レポート一覧URL"

])

sheet.append_row([

    "オーギヤDO",

    report_url

])

print("保存完了")
