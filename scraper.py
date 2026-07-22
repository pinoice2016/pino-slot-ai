from playwright.sync_api import sync_playwright

from bs4 import BeautifulSoup

import gspread

from google.oauth2.service_account import Credentials

import json

import os

# ==================================

# Google Sheets

# ==================================

SCOPES = [

    "https://www.googleapis.com/auth/spreadsheets",

    "https://www.googleapis.com/auth/drive",

]

creds = Credentials.from_service_account_info(

    json.loads(os.environ["GOOGLE_CREDENTIALS"]),

    scopes=SCOPES,

)

gc = gspread.authorize(creds)

sheet = gc.open_by_key(

    os.environ["SPREADSHEET_ID"]

).worksheet("データ収集")

# ==================================

# 店舗URL

# ==================================

STORE_URL = "https://min-repo.com/2958667/"

# ==================================

# Playwright

# ==================================

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

        user_agent="Mozilla/5.0",

    )

    print("店舗ページへアクセス")

    page.goto(

        STORE_URL,

        wait_until="networkidle",

        timeout=60000,

    )

    page.wait_for_timeout(5000)

    print(page.title())

    # ==================================

    # 店舗ページ保存

    # ==================================

    html = page.content()

    with open("store.html", "w", encoding="utf-8") as f:

        f.write(html)

    page.screenshot(

        path="store.png",

        full_page=True,

    )

    print("店舗ページ保存完了")

    # ==================================

    # HTML解析

    # ==================================

    soup = BeautifulSoup(html, "lxml")

    print("ページ内リンク一覧")

    for a in soup.find_all("a", href=True):

        text = a.get_text(" ", strip=True)

        href = a["href"]

        print("----------------------------")

        print("TEXT =", text)

        print("HREF =", href)

    browser.close()

# ==================================

# Google Sheets

# ==================================

sheet.clear()

sheet.append_row([

    "確認",

])

sheet.append_row([

    "store.html を保存しました",

])

print("保存完了")
