from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

# 크롬 옵션 설정
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
driver = webdriver.Chrome(options=options)

query = "경호"
num_pages = 3
news_data = []

for page in range(1, num_pages + 1):
    start = (page - 1) * 10 + 1
    url = f"https://search.naver.com/search.naver?where=news&query={query}&start={start}"
    driver.get(url)

    # 로딩 대기: 뉴스 전체 목록 컨테이너 기준
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, 'div.fds-news-item-list-tab')
    ))

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    container = soup.select_one('div.fds-news-item-list-tab')
    if not container:
        print(f"[{page}] 뉴스 컨테이너가 없습니다.")
        continue

    news_items = container.select('div.sds-comps-vertical-layout')

    for item in news_items:
        # 제목
        title_tag = item.select_one('a[href] > span.sds-comps-text-type-headline1')
        if not title_tag:
            continue  # 제목이 없으면 건너뜀

        title = title_tag.get_text(strip=True)
        link_tag = title_tag.find_parent('a')
        link = link_tag.get('href', '') if link_tag else '링크 없음'

        # 요약
        summary_tag = item.select_one('a[href] > span.sds-comps-text-type-body1')
        summary = summary_tag.get_text(strip=True) if summary_tag else ''

        # 언론사
        press_tag = item.select_one('a[href] > span.sds-comps-text-type-body2.sds-comps-text-weight-sm')
        press = press_tag.get_text(strip=True) if press_tag else '언론사 없음'

        # 날짜
        date_tag = item.select_one(
            'span.sds-comps-profile-info-subtext span.sds-comps-text-type-body2.sds-comps-text-weight-sm'
        )
        date = date_tag.get_text(strip=True) if date_tag else '날짜 없음'

        news_data.append((title, link, summary, press, date))

    time.sleep(1)

driver.quit()

# 출력
print("===== 뉴스 정보 모음 =====")
for idx, (title, link, summary, press, date) in enumerate(news_data, 1):
    print(f"{idx}. {title}")
    print(f"   링크: {link}")
    print(f"   언론사: {press} / 날짜: {date}")
    print(f"   요약: {summary}")
    print("-" * 80)
