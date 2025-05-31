from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

options = Options()
driver = webdriver.Chrome(options=options)

query = "경호"

# 원하는 페이지 수
num_pages = 3

titles = []

for page in range(1, num_pages + 1):
    start = (page - 1) * 10 + 1
    url = f"https://search.naver.com/search.naver?where=news&query={query}&start={start}"
    driver.get(url)

    # 로딩 기다리기
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, 'a > span.sds-comps-text-type-headline1')
    ))

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    spans = soup.select('a > span.sds-comps-text-type-headline1')

    for span in spans:
        titles.append(span.get_text(strip=True))

    # 너무 빠르면 차단될 수 있으니 약간 대기
    time.sleep(1)

driver.quit()

# 출력
print("===== 뉴스 제목 모음 =====")
for idx, title in enumerate(titles, 1):
    print(f"{idx}. {title}")