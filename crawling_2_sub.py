from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import random

CHROME_DRIVER_PATH = 'C:\\programing\\chromedriver-win64\\chromedriver.exe'

# 2호선 서울역 리스트 반환 함수
def subway():
    return [
        "시청", "을지로입구", "을지로3가", "을지로4가", "동대문역사문화공원", "신당", "상왕십리", "왕십리", "한양대", "뚝섬",
        "성수", "건대입구", "구의", "강변", "잠실나루", "잠실", "잠실새내", "종합운동장", "삼성", "선릉", "역삼",
        "강남", "교대", "서초", "방배", "사당", "서울대입구", "봉천", "신림", "신대방", "구로디지털단지", "대림",
        "신도림", "문래", "영등포구청", "당산", "합정", "홍대입구", "신촌", "이대", "아현", "충정로"
    ]

# Selenium 설정
options = webdriver.ChromeOptions()
# options.add_argument('--headless')  # 필요 시 활성화
options.add_argument("user-agent=Mozilla/5.0")
service = Service(CHROME_DRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 10)

results = []
total_start_time = time.time()

try:
    for station in subway():
        print(f"\n### '{station}' 음식점 검색 시작 ###\n")
        driver.get('https://map.kakao.com/')
        time.sleep(2)

        # 검색창 초기화 및 검색어 입력
        search_box = driver.find_element(By.ID, 'search.keyword.query')
        search_box.clear()
        search_box.send_keys(f'{station}역 음식점')
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)

        # 장소 탭 클릭
        try:
            wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="info.main.options"]/li[2]/a'))).click()
        except:
            print(f"[{station}] 장소 탭 클릭 실패")
            continue

        page_group = 1
        while True:
            for page_in_group in range(1, 6):
                page_num = ((page_group - 1) * 5) + page_in_group
                print(f"[{station}] === {page_num} 페이지 ===")
                time.sleep(random.uniform(2, 4))

                place_items = driver.find_elements(By.CSS_SELECTOR, 'ul#info\\.search\\.place\\.list > li.PlaceItem')
                for item in place_items:
                    try:
                        name = item.find_element(By.CSS_SELECTOR, '.head_item .link_name').text
                        address = item.find_element(By.CSS_SELECTOR, '.info_item .addr p[data-id="address"]').text
                        detail_link = item.find_element(By.CSS_SELECTOR, '.contact .moreview').get_attribute('href')
                    except:
                        continue

                    driver.execute_script("window.open('');")
                    driver.switch_to.window(driver.window_handles[1])
                    driver.get(detail_link)
                    time.sleep(2)

                    menus = []
                    menu_tab = None
                    tabs = driver.find_elements(By.CSS_SELECTOR, 'a.link_tab')
                    for tab in tabs:
                        if tab.text.strip() == '메뉴':
                            menu_tab = tab
                            break

                    if menu_tab:
                        try:
                            menu_tab.click()
                            time.sleep(2)
                            menu_items = driver.find_elements(By.CSS_SELECTOR, '.wrap_goods ul.list_goods > li')
                            for menu in menu_items:
                                try:
                                    menu_name = menu.find_element(By.CSS_SELECTOR, '.info_goods .tit_item').text.strip()
                                    menu_price = menu.find_element(By.CSS_SELECTOR, '.info_goods .desc_item').text.strip()
                                    menus.append(f"{menu_name} ({menu_price})")
                                except:
                                    continue
                            if not menus:
                                menus = ['메뉴 정보 없음']
                        except Exception as e:
                            menus = [f'메뉴탭 클릭 실패: {e}']
                    else:
                        menus = ['메뉴탭 없음']

                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])

                    results.append({
                        '역': station,
                        '이름': name,
                        '주소': address,
                        '상세보기': detail_link,
                        '메뉴': '; '.join(menus)
                    })

                # ✅ 5페이지마다 임시 저장
                if page_num % 5 == 0:
                    temp_df = pd.DataFrame(results)
                    temp_df.to_csv('서울_2호선_음식점_크롤링_temp.csv', index=False, encoding='utf-8-sig')
                    print(f"✅ [임시 저장] {page_num}페이지까지 저장 완료")

                if page_in_group < 5:
                    try:
                        page_btn = driver.find_element(By.CSS_SELECTOR, f'a#info\\.search\\.page\\.no{page_in_group+1}')
                        page_btn.click()
                        time.sleep(2)
                    except:
                        break

            # 다음 페이지 그룹 버튼
            try:
                next_btn = driver.find_element(By.CSS_SELECTOR, 'button#info\\.search\\.page\\.next')
                if 'disabled' in next_btn.get_attribute('class'):
                    break
                next_btn.click()
                time.sleep(2)
                page_group += 1
            except:
                break

finally:
    driver.quit()
    total_end_time = time.time()
    print(f'\n⏱ 전체 크롤링 소요 시간: {total_end_time - total_start_time:.2f}초')

    # ✅ 마지막까지 저장 안 된 데이터 저장
    temp_df = pd.DataFrame(results)
    temp_df.to_csv('서울_2호선_음식점_크롤링_temp.csv', index=False, encoding='utf-8-sig')
    print('✅ 마지막 임시 저장 완료')

# 🔄 최종 저장
df = pd.DataFrame(results)
df.to_csv('서울_2호선_음식점_크롤링.csv', index=False, encoding='utf-8-sig')
print('✅ 최종 CSV 저장 완료: 서울_2호선_음식점_크롤링.csv')
