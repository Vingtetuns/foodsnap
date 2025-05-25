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
WAIT_TIME = 10  # 충분히 넉넉하게

def init_driver():
    opts = webdriver.ChromeOptions()
    opts.add_argument("--headless=new")  # 최신 크롬에서 headless 모드 권장 옵션
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)

def parse_foodstore():
    driver = init_driver()
    driver.get(START_URL)
    time.sleep(WAIT_TIME)

    # 1) 첫 번째 iframe(검색 결과 영역) 진입
    WebDriverWait(driver, WAIT_TIME).until(
        lambda d: len(d.find_elements(By.TAG_NAME, "iframe")) >= 1
    )
    frs = driver.find_elements(By.TAG_NAME, "iframe")
    driver.switch_to.frame(frs[0])

    # 2) 검색 결과 로딩 대기 (클래스명 최신화 필요)
    # 아래 셀렉터는 반드시 개발자도구로 확인 후 수정!
    try:
        WebDriverWait(driver, WAIT_TIME).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.place_bluelink span.TYaxT"))
        )
    except Exception as e:
        print("검색 결과 요소를 찾지 못했습니다. 클래스명이 변경되었을 수 있습니다.")
        driver.quit()
        return [], []

    # 3) 가게명 클릭
    found = False
    for span in driver.find_elements(By.CSS_SELECTOR, "a.place_bluelink span.TYaxT"):
        if span.text.strip() == TARGET_STORE:
            span.click()
            found = True
            break
    if not found:
        print("타겟 가게를 찾지 못했습니다.")
        driver.quit()
        return [], []

    # 4) 상세페이지 iframe 전환 (entry 프레임)
    driver.switch_to.default_content()
    WebDriverWait(driver, WAIT_TIME).until(
        lambda d: len(d.find_elements(By.TAG_NAME, "iframe")) >= 2
    )
    frs = driver.find_elements(By.TAG_NAME, "iframe")
    entry = next((f for f in frs if "entry" in (f.get_attribute("src") or "")), frs[1])
    driver.switch_to.frame(entry)
    time.sleep(1)

    # 5) 가게명 추출 (클래스명 최신화 필요)
    try:
        store_name = driver.find_element(By.CSS_SELECTOR, "span.GHAhO").text.strip()
    except Exception:
        print("가게명을 찾지 못했습니다. 클래스명을 확인하세요.")
        driver.quit()
        return [], []

    # 6) 메뉴 탭 클릭
    try:
        driver.find_element(By.LINK_TEXT, "메뉴").click()
        time.sleep(1)
    except Exception:
        print("메뉴 탭이 없습니다. 메뉴 정보가 없을 수 있습니다.")

    # 7) 메뉴 추출 (클래스명 최신화 필요)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    menu_items = soup.select("li.E2jtL span.lPzHi")  # 클래스명 최신화 필요
    menus = [item.get_text(strip=True) for item in menu_items]

    driver.quit()
    return [store_name], [menus]

if __name__ == "__main__":
    stores, all_menus = parse_foodstore()
    print("가게명 리스트:", stores)
    print("메뉴 리스트:", all_menus)
