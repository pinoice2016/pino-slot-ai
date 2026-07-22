from playwright.sync_api import sync_playwright

from bs4 import BeautifulSoup

import gspread

from google.oauth2.service_account import Credentials

import json

import os

SCOPES = [

    "https://www.googleapis.com/auth/spreadsheets",

    "https://www.googleapis.com/auth/drive",

]

creds_info = json.loads(os.environ["GOOGLE_CREDENTIALS"])

creds = Credentials.from_service_account_info(

    creds_info,

    scopes=SCOPES

)

gc = gspread.authorize(creds)

spreadsheet = gc.open_by_key(

    os.environ["SPREADSHEET_ID"]

)

# シート名を自分のスプレッドシートに合わせる

sheet = spreadsheet.worksheet("データ収集")

URL = "https://min-repo.com/tag/%E3%82%AA%E3%83%BC%E3%82%AE%E3%82%B9/"

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    page.goto(

        URL,

        wait_until="domcontentloaded",

        timeout=60000

    )

    html = page.content()

    browser.close()

soup = BeautifulSoup(html, "lxml")

articles = []

for a in soup.select("article"):

    link = a.find("a", href=True)

    if not link:

        continue

    title = link.get_text(strip=True)

    url = link["href"]

    date = ""

    t = a.find("time")

    if t:

        date = t.get_text(strip=True)

    articles.append([date, title, url])

print(f"{len(articles)}件取得")

sheet.clear()

sheet.append_row([

    "日付",

    "タイトル",

    "URL"

])

if articles:

    sheet.append_rows(articles)

print("保存完了")
