from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

options = webdriver.ChromeOptions()
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    driver.get('https://map.kakao.com/')
    time.sleep(3)  # 페이지 로딩 대기

    # iframe 목록 출력
    iframes = driver.find_elements('tag name', 'iframe')
    for idx, iframe in enumerate(iframes):
        print(f"{idx}: id={iframe.get_attribute('id')}, name={iframe.get_attribute('name')}")
finally:
    driver.quit()
