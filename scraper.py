from playwright.sync_api import sync_playwright

from bs4 import BeautifulSoup

import gspread

from google.oauth2.service_account import Credentials

import json

import os

# ==========================

# Google認証

# ==========================

SCOPES = [

    "https://www.googleapis.com/auth/spreadsheets",

    "https://www.googleapis.com/auth/drive",

]

creds = Credentials.from_service_account_info(

    json.loads(os.environ["GOOGLE_CREDENTIALS"]),

    scopes=SCOPES,

)

gc = gspread.authorize(creds)

spreadsheet = gc.open_by_key(

    os.environ["SPREADSHEET_ID"]

)

sheet = spreadsheet.worksheet("データ収集")

# ==========================

# 対象URL

# ==========================

URL = "https://min-repo.com/tag/%E3%82%AA%E3%83%BC%E3%82%AE%E3%83%A4do/"

# ==========================

# Playwright

# ==========================

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    page = browser.new_page(

        viewport={"width": 1400, "height": 2000},

        user_agent="Mozilla/5.0"

    )

    page.goto(URL, wait_until="networkidle", timeout=60000)

    page.wait_for_timeout(5000)

    html = page.content()

    print("取得URL :", page.url)

    print("タイトル :", page.title())

    print("HTMLサイズ :", len(html))

    browser.close()

# ==========================

# HTML解析

# ==========================

soup = BeautifulSoup(html, "lxml")

rows = []

# 全リンクを調査

for a in soup.find_all("a", href=True):

    href = a["href"]

    text = a.get_text(strip=True)

    # min-repoの記事だけ取得

    if href.startswith("https://min-repo.com/"):

        # タグやカテゴリ除外

        if "/tag/" in href:

            continue

        if "/category/" in href:

            continue

        if text == "":

            continue

        rows.append([

            text,

            href

        ])

# 重複削除

unique = []

seen = set()

for r in rows:

    if r[1] not in seen:

        seen.add(r[1])

        unique.append(r)

print("取得件数:", len(unique))

# ==========================

# スプレッドシート保存

# ==========================

sheet.clear()

sheet.append_row([

    "店舗名",

    "URL"

])

if unique:

    sheet.append_rows(unique)

print("保存完了")
