from playwright.sync_api import sync_playwright

from bs4 import BeautifulSoup

import gspread

from google.oauth2.service_account import Credentials

import json

import os

# =========================

# Google Sheets

# =========================

SCOPES = [

    "https://www.googleapis.com/auth/spreadsheets",

    "https://www.googleapis.com/auth/drive",

]

creds = Credentials.from_service_account_info(

    json.loads(os.environ["GOOGLE_CREDENTIALS"]),

    scopes=SCOPES,

)

gc = gspread.authorize(creds)

spreadsheet = gc.open_by_key(os.environ["SPREADSHEET_ID"])

sheet = spreadsheet.worksheet("データ収集")

# =========================

# 対象URL

# =========================

URL = "https://min-repo.com/2958667/"

# =========================

# Playwright

# =========================

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

        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",

    )

    print("アクセス開始")

    page.goto(

        URL,

        wait_until="networkidle",

        timeout=60000,

    )

    page.wait_for_timeout(5000)

    print("URL =", page.url)

    print("TITLE =", page.title())

    html = page.content()

    print("HTMLサイズ =", len(html))

    page.screenshot(path="page.png", full_page=True)

    browser.close()

# =========================

# HTML保存

# =========================

with open("page.html", "w", encoding="utf-8") as f:

    f.write(html)

# =========================

# HTML解析

# =========================

soup = BeautifulSoup(html, "lxml")

rows = []

for a in soup.find_all("a", href=True):

    text = a.get_text(strip=True)

    href = a.get("href")

    if not href:

        continue

    rows.append([

        text,

        href,

    ])

print("リンク数 =", len(rows))

# =========================

# スプレッドシート保存

# =========================

sheet.clear()

sheet.append_row([

    "タイトル",

    "URL",

])

if rows:

    sheet.append_rows(rows)

print("保存完了")
