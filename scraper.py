from playwright.sync_api import sync_playwright

from bs4 import BeautifulSoup

import gspread

from google.oauth2.service_account import Credentials

import json

import os

# ----------------------------------------

# Google Sheets

# ----------------------------------------

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

# ----------------------------------------

# 店舗URL

# ----------------------------------------

STORE_URL = "https://min-repo.com/2958667/"

# ----------------------------------------

# Playwright開始

# ----------------------------------------

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

        wait_until="domcontentloaded",

        timeout=60000,

    )

    page.wait_for_timeout(5000)

    print(page.title())

    html = page.content()

    # ------------------------------------

    # レポート一覧URL取得

    # ------------------------------------

    soup = BeautifulSoup(html, "lxml")

    report_url = ""

    print("リンク検索開始")

    for a in soup.find_all("a", href=True):

        text = a.get_text(" ", strip=True)

        if "パチンコレポート一覧" in text:

            report_url = a["href"]

            break

    print("レポート一覧URL")

    print(report_url)

    # URLが相対パスなら絶対URLへ変換

    if report_url.startswith("/"):

        report_url = "https://min-repo.com" + report_url

    # ------------------------------------

    # レポート一覧ページ

    # ------------------------------------

    rows = []

    if report_url != "":

        print("レポート一覧へアクセス")

        page.goto(

            report_url,

            wait_until="domcontentloaded",

            timeout=60000,

        )

        page.wait_for_timeout(5000)

        print(page.title())

        html = page.content()

        soup = BeautifulSoup(html, "lxml")

        print("営業日一覧取得")

        links = soup.find_all("a", href=True)

        for link in links:

            href = link.get("href", "")

            text = link.get_text(" ", strip=True)

            if "/report/" in href:

                if href.startswith("/"):

                    href = "https://min-repo.com" + href

                rows.append([text, href])

        print("取得件数:", len(rows))

    browser.close()

# ----------------------------------------

# Google Sheets保存

# ----------------------------------------

sheet.clear()

sheet.append_row([

    "営業日",

    "URL",

])

if rows:

    sheet.append_rows(rows)

print("保存完了")
