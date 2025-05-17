# parse_foodstore_example.py

"""
미식광진 본관 한 곳만 크롤링하여
가게명 리스트, 메뉴 리스트를 반환하는 예제
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

START_URL = "https://map.naver.com/p/search/광진구%20음식점"
TARGET_STORE = "미식광진 본관"
WAIT_TIME = 5

def init_driver():
    opts = webdriver.ChromeOptions()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)

def parse_foodstore():
    """
    1) 검색 결과 페이지에서 '미식광진 본관'만 클릭
    2) 상세페이지 진입 → 메뉴 탭 클릭 → HTML 파싱
    3) [가게명 리스트], [메뉴 리스트 리스트] 형태로 반환
    """
    driver = init_driver()
    driver.get(START_URL)
    time.sleep(WAIT_TIME)

    # 1) 검색 결과 iframe 전환 (인덱스 0)
    WebDriverWait(driver, WAIT_TIME).until(
        lambda d: len(d.find_elements(By.TAG_NAME, "iframe")) >= 1
    )
    frs = driver.find_elements(By.TAG_NAME, "iframe")
    driver.switch_to.frame(frs[0])

    # 2) place_bluelink 중 TARGET_STORE 텍스트인 요소 클릭
    WebDriverWait(driver, WAIT_TIME).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.place_bluelink span.TYaxT"))
    )
    for span in driver.find_elements(By.CSS_SELECTOR, "a.place_bluelink span.TYaxT"):
        if span.text.strip() == TARGET_STORE:
            span.click()
            break

    # 3) 상세페이지 iframe 전환 (entry 프레임 찾기)
    driver.switch_to.default_content()
    WebDriverWait(driver, WAIT_TIME).until(
        lambda d: len(d.find_elements(By.TAG_NAME, "iframe")) >= 2
    )
    frs = driver.find_elements(By.TAG_NAME, "iframe")
    # src에 'entry' 포함된 프레임 우선
    entry = next((f for f in frs if "entry" in (f.get_attribute("src") or "")), frs[1])
    driver.switch_to.frame(entry)
    time.sleep(1)

    # 4) 가게명 추출
    store_name = driver.find_element(By.CSS_SELECTOR, "span.GHAhO").text.strip()

    # 5) 메뉴 탭 클릭
    try:
        driver.find_element(By.LINK_TEXT, "메뉴").click()
        time.sleep(1)
    except:
        pass

    # 6) 페이지 소스에서 메뉴명만 추출
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    menu_items = soup.select("li.E2jtL span.lPzHi")
    menus = [item.get_text(strip=True) for item in menu_items]

    driver.quit()

    # 반환 형태
    store_names = [store_name]
    menus_list  = [menus]
    return store_names, menus_list

if __name__ == "__main__":
    stores, all_menus = parse_foodstore()
    print("가게명 리스트:", stores)
    print("메뉴 리스트:", all_menus)
