from playwright.sync_api import sync_playwright

from bs4 import BeautifulSoup

import gspread

from google.oauth2.service_account import Credentials

import json

import os

# ----------------------------

# Google Sheets

# ----------------------------

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

# ----------------------------

# 対象店舗

# ----------------------------

STORE_NAME = "オーギヤDO"

STORE_URL = "https://min-repo.com/2958667/"

# ----------------------------

# Playwright開始

# ----------------------------

with sync_playwright() as p:

    browser = p.chromium.launch(

        headless=True,

        args=[

            "--no-sandbox",

            "--disable-dev-shm-usage",

        ],

    )

    page = browser.new_page(

        viewport={"width": 1400, "height": 5000},

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

    html = page.content()

    with open("page.html", "w", encoding="utf-8") as f:

        f.write(html)

    page.screenshot(

        path="page.png",

        full_page=True,

    )

    print("店舗ページ保存完了")

    browser.close()

# ----------------------------

# HTML解析

# ----------------------------

soup = BeautifulSoup(html, "lxml")

print("リンク検索開始")

report_url = ""

for a in soup.find_all("a", href=True):

    text = a.get_text(" ", strip=True)

    if "パチンコレポート一覧" in text:

        report_url = a["href"]

        if report_url.startswith("/"):

            report_url = "https://min-repo.com" + report_url

        break

print("レポート一覧URL")

print(report_url)

# ----------------------------

# レポート一覧取得

# ----------------------------

days = []

if report_url != "":

    with sync_playwright() as p:

        browser = p.chromium.launch(

            headless=True,

            args=[

                "--no-sandbox",

                "--disable-dev-shm-usage",

            ],

        )

        page = browser.new_page(

            viewport={"width": 1400, "height": 5000},

        )

        print("レポート一覧へアクセス")

        page.goto(

            report_url,

            wait_until="networkidle",

            timeout=60000,

        )

        page.wait_for_timeout(5000)

        print(page.title())

        html = page.content()

        browser.close()

    soup = BeautifulSoup(html, "lxml")

    print("営業日一覧取得")

    for a in soup.find_all("a", href=True):

        text = a.get_text(" ", strip=True)

        if "/" in text and "(" in text:

            if text not in days:

                days.append(text)

print("取得件数:", len(days))

# ----------------------------

# Google Sheets保存

# ----------------------------

sheet.clear()

sheet.append_row([

    "店舗",

    "営業日"

])

for d in days:

    sheet.append_row([

        STORE_NAME,

        d,

    ])

print("保存完了")
