# selenium_bs_crawl_indexed.py

"""
광진구 음식점 메뉴 크롤러 – 인덱스 방식 안정화
1) search page iframe[0] 에서 place 링크만 수집
2) 각 링크 driver.get → iframe[?] 전환 → 메뉴 수집
3) 엑셀 저장

필요: pip install selenium webdriver-manager beautifulsoup4 pandas openpyxl
"""

import time, os
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ─────────────────────────────────────────
START_URL   = "https://map.naver.com/p/search/광진구%20음식점"
OUTPUT_FILE = "광진구_음식점_메뉴.xlsx"
WAIT_TIME   = 5
MAX_PLACES  = 10   # 테스트용
# ─────────────────────────────────────────

def init_driver():
    opts = webdriver.ChromeOptions()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)

def parse_menu(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    menu = {}
    for li in soup.select("li.E2jtL"):
        name = li.select_one("span.lPzHi")
        price = li.select_one("div.GXS1X em")
        if name and price:
            n = name.get_text(strip=True)
            p = price.get_text(strip=True).replace(",", "")
            if p.isdigit():
                menu[n] = int(p)
    return menu

def main():
    driver = init_driver()
    driver.get(START_URL)
    time.sleep(WAIT_TIME)

    # 1) 검색 결과 프레임[0] 전환
    WebDriverWait(driver, WAIT_TIME).until(
        lambda d: len(d.find_elements(By.TAG_NAME, "iframe")) >= 1
    )
    frames = driver.find_elements(By.TAG_NAME, "iframe")
    driver.switch_to.frame(frames[0])
    # place 링크 수집
    WebDriverWait(driver, WAIT_TIME).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.place_bluelink"))
    )
    links = []
    for a in driver.find_elements(By.CSS_SELECTOR, "a.place_bluelink"):
        href = a.get_attribute("href")
        if href and "/place/" in href:
            links.append(href)
        if len(links) >= MAX_PLACES:
            break
    driver.quit()
    print("▶ 수집된 place URL:", len(links))

    # 2) 각 링크로 직접 진입해 메뉴 크롤링
    driver = init_driver()
    data = []
    for idx, url in enumerate(links, 1):
        print(f"[{idx}/{len(links)}] {url}")
        driver.get(url)
        time.sleep(WAIT_TIME)

        # 상세페이지 프레임 검색 (entryIframe 보통 두 번째)
        WebDriverWait(driver, WAIT_TIME).until(
            lambda d: len(d.find_elements(By.TAG_NAME, "iframe")) >= 2
        )
        frs = driver.find_elements(By.TAG_NAME, "iframe")
        # 가능한 entryIframe을 src로 찾거나, 두 번째 인덱스
        entry = None
        for f in frs:
            src = f.get_attribute("src") or ""
            if "entry" in src:
                entry = f
                break
        if not entry:
            entry = frs[1]
        driver.switch_to.frame(entry)
        time.sleep(1)

        # 가게 이름
        try:
            store_name = driver.find_element(By.CSS_SELECTOR, "span.GHAhO").text.strip()
        except:
            store_name = "이름없음"

        # 메뉴 탭 클릭 (존재 시)
        try:
            driver.find_element(By.LINK_TEXT, "메뉴").click()
            time.sleep(1)
        except:
            pass

        # 메뉴 파싱
        html = driver.page_source
        menus = parse_menu(html)
        if not menus:
            menus = {"메뉴없음": 0}

        # 행 추가
        row = {"매장명": store_name}
        row.update(menus)
        data.append(row)

    driver.quit()

    # 3) DataFrame → 엑셀 저장
    df = pd.DataFrame(data).fillna("")
    df.to_excel(OUTPUT_FILE, index=False)
    print("✅ 저장 완료:", os.path.abspath(OUTPUT_FILE))

if __name__ == "__main__":
    main()
