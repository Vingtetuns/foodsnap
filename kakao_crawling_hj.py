# 카카오맵 크롤링

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

CHROME_DRIVER_PATH = 'C:\programing\chromedriver-win64\chromedriver.exe'

options = webdriver.ChromeOptions()
# options.add_argument('--headless')  # 필요 시 사용
service = Service(CHROME_DRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 10)

results = []

# 전체 시작 시간
total_start_time = time.time()

try:
    driver.get('https://map.kakao.com/')
    time.sleep(2)

    # 검색 수행
    search_box = driver.find_element(By.ID, 'search.keyword.query')
    search_box.send_keys('건대입구역 음식점')
    search_box.send_keys(Keys.RETURN)
    time.sleep(3)

    # 장소 버튼 클릭 
    driver.find_element(By.XPATH, '//*[@id="info.main.options"]/li[2]/a').send_keys(Keys.ENTER)
    '''    # 장소 더보기 버튼 누르기 
    btn = driver.find_element(By.CSS_SELECTOR, '.more')   
    driver.execute_script("arguments[0].click();", btn)'''

    '''# 검색 수행
    search_box = driver.find_element(By.ID, 'search.keyword.query')
    search_box.send_keys('건대입구역 음식점')
    search_box.send_keys(Keys.RETURN)
    time.sleep(3)

    # 사용자 수동 조작 대기
    input('after click 장소 더보기 in terminal, press enter')'''

    page_group = 1
    while True:
        for page_in_group in range(1, 6):
            page_num = ((page_group - 1) * 5) + page_in_group
            print(f'=== {page_num} 페이지 ===')
            # 페이지 시작 시간
            page_start_time = time.time()
            time.sleep(2)

            place_items = driver.find_elements(By.CSS_SELECTOR, 'ul#info\\.search\\.place\\.list > li.PlaceItem')
            for item in place_items:
                try:
                    name = item.find_element(By.CSS_SELECTOR, '.head_item .link_name').text
                    address = item.find_element(By.CSS_SELECTOR, '.info_item .addr p[data-id="address"]').text
                    detail_link = item.find_element(By.CSS_SELECTOR, '.contact .moreview').get_attribute('href')
                except Exception:
                    continue

                # 메뉴탭 탐색
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
                            except Exception:
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
                    '이름': name,
                    '주소': address,
                    '상세보기': detail_link,
                    '메뉴': '; '.join(menus)
                })

            # 페이지 끝 시간
            page_end_time = time.time()
            elapsed = page_end_time - page_start_time
            print(f'[{page_num} 페이지 소요 시간: {elapsed:.2f}초]')

            # 다음 페이지 (1~5 내에서)
            if page_in_group < 5:
                try:
                    page_btn = driver.find_element(By.CSS_SELECTOR, f'a#info\\.search\\.page\\.no{page_in_group+1}')
                    page_btn.click()
                    time.sleep(2)
                except Exception:
                    break

        # 다음 페이지 그룹으로 이동
        try:
            next_btn = driver.find_element(By.CSS_SELECTOR, 'button#info\\.search\\.page\\.next')
            if 'disabled' in next_btn.get_attribute('class'):
                break
            next_btn.click()
            time.sleep(2)
            page_group += 1
        except Exception:
            break

finally:
    driver.quit()
    # 전체 끝 시간
    total_end_time = time.time()
    total_elapsed = total_end_time - total_start_time
    print(f'전체 크롤링 소요 시간: {total_elapsed:.2f}초')

# 결과 저장
df = pd.DataFrame(results)
df.to_csv('광진구 건대입구역 음식점 크롤링.csv', index=False, encoding='utf-8-sig')
print('save as CSV')