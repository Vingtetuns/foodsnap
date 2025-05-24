from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import csv

url = 'https://map.kakao.com/'
driver = webdriver.Chrome()  # 드라이버 경로
driver.get(url)

searchloc = '광진구 음식점' # 수정 필요 : 서울 구 전부 반복

# 음식점 입력 후 찾기 버튼 클릭 
search_area = driver.find_element(By.XPATH, '//*[@id="search.keyword.query"]')   # 검색창
search_area.send_keys(searchloc)
driver.find_element(By.XPATH, '//*[@id="search.keyword.submit"]').send_keys(Keys.ENTER)
time.sleep(2)

# 장소 버튼 클릭 
driver.find_element(By.XPATH, '//*[@id="info.main.options"]/li[2]/a').send_keys(Keys.ENTER)


def storeNamePrint(page):
    time.sleep(0.2)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    store_lists = soup.select('.placelist > .PlaceItem')
    data_list = []

    # 음식점 이름, 평점, 주소, 메뉴 저장
    for store in store_lists:
        name = store.select('.head_item > .tit_name > .link_name')[0].text
        degree = store.select('.rating > .score > .num')[0].text
        addr = store.select('.info_item > .addr')[0].text.splitlines()[1]  # 도로명주소 
        menu = storeMenuPrint(n)
        # print(name, degree, addr, '-')

        data_list.append([name, degree, addr, menu])

    if page == 1:
        f = open('store_list_1.csv', 'w', encoding='utf-8-sig', newline='')  # 파일명 써주기 
        writercsv = csv.writer(f)
        header = ['name', 'degree', 'address', 'menu']
        writercsv.writerow(header)

        for i in data_list:
            writercsv.writerow(i)
    else:   
    	# 파일이 이미 존재하므로, 존재하는 파일에 이어서 쓰기 
        f = open('store_list_1.csv', 'a', encoding='utf-8-sig', newline='')
        writercsv = csv.writer(f)

        for i in data_list:
            writercsv.writerow(i)

################################수정필요##################################
# 메뉴 찾기 - 상세보기 링크 > 메뉴 클릭 > 메뉴 크롤링 (<strong class="tit_item">)
n = 1
def storeMenuPrint(index) :
    # 상세페이지로 가서 메뉴찾기
    detail_page_xpath = '//*[@id="info.search.place.list"]/li[' + str(i + 1) + ']/div[5]/div[4]/a[1]'
    driver.find_element_by_xpath(detail_page_xpath).send_keys(Keys.ENTER)
    driver.switch_to.window(driver.window_handles[-1])  # 상세정보 탭으로 변환
    time.sleep(1)

    menuInfos = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # 메뉴의 3가지 타입 : 수정필요 : 이거 예외 필요한지 텍스트만 해도 되는지 확인
    menuonlyType = soup.select('.cont_menu > .list_menu > .menuonly_type')
    nophotoType = soup.select('.cont_menu > .list_menu > .nophoto_type')
    photoType = soup.select('.cont_menu > .list_menu > .photo_type')

    if len(menuonlyType) != 0:
        for menu in menuonlyType:
            menuInfos.append(_getMenuInfo(menu))
    elif len(nophotoType) != 0:
        for menu in nophotoType:
            menuInfos.append(_getMenuInfo(menu))
    else:
        for menu in photoType:
            menuInfos.append(_getMenuInfo(menu))

    driver.close()
    driver.switch_to.window(driver.window_handles[0])  # 검색 탭으로 전환

    return menuInfos

def _getMenuInfo(menu):
    menuName = menu.select('.info_menu > .loss_word')[0].text
    menuPrices = menu.select('.info_menu > .price_menu')
    menuPrice = ''

    if len(menuPrices) != 0:
        menuPrice =  menuPrices[0].text.split(' ')[1]

    return [menuName, menuPrice]

storeNamePrint(1)

'''
try:
    # 장소 더보기 버튼 누르기 
    btn = driver.find_element(By.CSS_SELECTOR, '.more')   
    driver.execute_script("arguments[0].click();", btn)

    for i in range(2, 6): # 수정 필요 : 다섯번째 장까지 넘기기 >> 전체 검색할 필요 있음 > 나눠서 해야할 듯듯
        # 페이지 넘기기
        n = i 

        xPath = '//*[@id="info.search.page.no' + str(i) + '"]'
        driver.find_element(By.XPATH, xPath).send_keys(Keys.ENTER)
        time.sleep(1)

        storeNamePrint(i)
except:
    print('ERROR!')
'''

print('**크롤링 완료**')