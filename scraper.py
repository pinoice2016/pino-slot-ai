from playwright.sync_api import sync_playwright

from bs4 import BeautifulSoup

import gspread

from google.oauth2.service_account import Credentials

import json

import os

# ===============================

# Google Sheets

# ===============================

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

# ===============================

# 店舗URL

# ===============================

STORE_URL = "https://min-repo.com/2958667/"

# ===============================

# Playwright

# ===============================

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

    page.goto(

        STORE_URL,

        wait_until="networkidle",

        timeout=60000

    )

    page.wait_for_timeout(5000)

    print(page.title())

    html = page.content()

    soup = BeautifulSoup(html, "lxml")

    report_url = ""

    print("リンク検索開始")

    for a in soup.find_all("a", href=True):

        text = a.get_text(" ", strip=True)

        href = a["href"]

        if "過去レポート一覧" in text:

            report_url = href

            if report_url.startswith("/"):

                report_url = "https://min-repo.com" + report_url

            break

    print("レポート一覧URL")

    print(report_url)

    if report_url == "":

        print("レポート一覧が見つかりません")

        browser.close()

        exit()

    # ==========================

    # レポート一覧へ移動

    # ==========================

    print("レポート一覧へアクセス")

    page.goto(

        report_url,

        wait_until="networkidle",

        timeout=60000

    )

    page.wait_for_timeout(5000)

    print(page.title())

    html = page.content()

    browser.close()

# ===============================

# HTML解析

# ===============================

soup = BeautifulSoup(html, "lxml")

reports = []

print("営業日一覧取得")

for a in soup.find_all("a", href=True):

    text = a.get_text(" ", strip=True)

    href = a["href"]

    if "オーギヤDO" in text:

        if href.startswith("/"):

            href = "https://min-repo.com" + href

        reports.append([

            text,

            href

        ])

print("取得件数:", len(reports))

# ===============================

# Google Sheets保存

# ===============================

sheet.clear()

sheet.append_row([

    "営業日",

    "URL"

])

if reports:

    sheet.append_rows(reports)

print("保存完了")
