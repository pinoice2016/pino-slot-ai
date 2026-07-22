from playwright.sync_api import sync_playwright

from bs4 import BeautifulSoup

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

# 対象店舗

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

            "--disable-dev-shm-usage"

        ]

    )

    page = browser.new_page(

        viewport={"width": 1400, "height": 3000},

        user_agent="Mozilla/5.0"

    )

    print("店舗ページへアクセス")

    page.goto(URL, wait_until="networkidle", timeout=60000)

    page.wait_for_timeout(5000)

    print("タイトル")

    print(page.title())

    html = page.content()

    browser.close()

# -------------------------------

# HTML解析

# -------------------------------

soup = BeautifulSoup(html, "lxml")

print("=" * 60)

print("ページ内リンク一覧")

print("=" * 60)

links = []

for a in soup.find_all("a", href=True):

    text = a.get_text(" ", strip=True)

    href = a["href"]

    print(text)

    print(href)

    print("--------------------")

    links.append([text, href])

# -------------------------------

# スプレッドシート保存

# -------------------------------

sheet.clear()

sheet.append_row([

    "リンク名",

    "URL"

])

if links:

    sheet.append_rows(links)

print(f"{len(links)}件保存完了")
