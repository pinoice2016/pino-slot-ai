from playwright.sync_api import sync_playwright

import gspread

from google.oauth2.service_account import Credentials

import json

import os

# -----------------------------

# Google Sheets

# -----------------------------

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

# -----------------------------

# 対象ページ

# -----------------------------

URL = "https://min-repo.com/2958667/"

# -----------------------------

# Playwright

# -----------------------------

with sync_playwright() as p:

    browser = p.chromium.launch(

        headless=True,

        args=[

            "--no-sandbox",

            "--disable-dev-shm-usage",

        ]

    )

    page = browser.new_page()

    print("店舗ページへアクセス")

    page.goto(

        URL,

        wait_until="domcontentloaded",

        timeout=120000

    )

    page.wait_for_timeout(8000)

    print(page.title())

    print("フレーム一覧")

    for frame in page.frames:

        print(frame.url)

    report_url = ""

    print("リンク検索開始")

    for frame in page.frames:

        try:

            links = frame.locator("a").evaluate_all("""

                els => els.map(e => ({

                    text: e.innerText,

                    href: e.href

                }))

            """)

            for link in links:

                text = link["text"].strip()

                href = link["href"]

                if text:

                    print(text)

                if href:

                    print(href)

                if "パチンコレポート一覧" in text:

                    report_url = href

                elif "スロットレポート一覧" in text:

                    report_url = href

        except Exception as e:

            print("フレーム読込失敗:", e)

    browser.close()

print("レポート一覧URL")

print(report_url)

# -----------------------------

# Google Sheetsへ保存

# -----------------------------

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
