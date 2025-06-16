import os
import requests
from bs4 import BeautifulSoup
import time
import re
import random
import pandas as pd

headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.jobkorea.co.kr/recruit/joblist?menucode=duty",
    "Content-Type": "application/json",
    "X-Requested-With": "XMLHttpRequest",
    "Accept-Encoding": "gzip, deflate, br"
}

dutyCtgr = "10039"
duty = "1000317"

payload = {
    "condition": {
        "dutyCtgr": 0,
        "duty": duty,
        "dutyArr": [duty],
        "dutyCtgrSelect": [dutyCtgr],
        "dutySelect": [duty],
        "isAllDutySearch": False
    },
    "TotalCount": 455,
    "Page": 1,
    "PageSize": 455
}

url = "https://www.jobkorea.co.kr/Recruit/Home/_GI_List/"

session = requests.Session()
session.get("https://www.jobkorea.co.kr/")
session.headers.update(headers)
response = session.post(url, json=payload)
print(f"응답 상태 코드: {response.status_code}")

data_list = []

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "lxml")
    jobs = soup.select(".devTplTabBx table .tplTit > .titBx")

    print(f"공고 수: {len(jobs)}")

    for idx, job in enumerate(jobs, start=1):
        print(f"[{idx}/{len(jobs)}] 공고 수집 중...")
        a_tag = job.select_one("a")
        href = a_tag["href"] if a_tag else None
        if href:
            match = re.search(r'/Recruit/GI_Read/(\d+)', href)
            if match:
                gno = match.group(1)
                detail_url = f"https://www.jobkorea.co.kr/Recruit/GI_Read/{gno}"

                try:
                    detail_res = session.get(detail_url, timeout=10)
                    time.sleep(random.uniform(1, 3))

                    if detail_res.status_code == 200:
                        detail_soup = BeautifulSoup(detail_res.text, "lxml")

                        # 기업명 먼저 추출
                        company_el = detail_soup.select_one("h3.hd_3 > div.header > span.coName")
                        company_name = company_el.text.strip() if company_el else ""

                        # 전체 텍스트에서 기업명 제거한 후 공고제목만 추출
                        title_text = "없음"
                        hd_3 = detail_soup.select_one("h3.hd_3")
                        if hd_3:
                            full_text = hd_3.get_text(strip=True)
                            # 기업명 제거
                            full_text = full_text.replace(company_name, "").strip()
                            # “따옴표 안”만 추출 시도
                            match_title = re.search(r'“(.+?)”', full_text)
                            title_text = match_title.group(1) if match_title else full_text

                        # 날짜 추출
                        start_date_text = "없음"
                        deadline_text = "없음"

                        dl_date = detail_soup.select_one("dl.date")
                        if dl_date:
                            dt_list = dl_date.find_all("dt")
                            dd_list = dl_date.find_all("dd")

                            # 시작일
                            if len(dt_list) >= 1 and "시작일" in dt_list[0].text and len(dd_list) >= 1:
                                start_span = dd_list[0].select_one("span.tahoma")
                                if start_span:
                                    weekday = dd_list[0].get_text(strip=True).replace(start_span.text.strip(), "")
                                    start_date_text = f"{start_span.text.strip()} {weekday.strip()}"

                            # 마감일
                            if len(dt_list) >= 3 and "마감일" in dt_list[2].text and len(dd_list) >= 4:
                                deadline_span = dd_list[3].select_one("span.tahoma")
                                if deadline_span:
                                    weekday = dd_list[3].get_text(strip=True).replace(deadline_span.text.strip(), "")
                                    deadline_text = f"{deadline_span.text.strip()} {weekday.strip()}"

                        # 우대 자격증
                        cert_list = []
                        popup_pref = detail_soup.select_one("#popupPref")
                        dt_elements = popup_pref.select(".tbAdd dt") if popup_pref else detail_soup.select(".artReadJobSum .tbList dt")
                        for dt in dt_elements:
                            if '자격' in dt.text:
                                dd = dt.find_next_sibling("dd")
                                if dd:
                                    certs = dd.text.strip().rstrip(',').split(',')
                                    cert_list = [c.strip() for c in certs if c.strip()]
                                break

                        data_list.append({
                            "공고제목": title_text,
                            "회사명": company_name,
                            "시작일": start_date_text,
                            "마감일": deadline_text,
                            "우대 자격증": ', '.join(cert_list) if cert_list else "없음"
                        })

                except Exception as e:
                    print(f"[예외] 공고 {gno} 처리 중 오류 발생:", e)
else:
    print("[오류] 리스트 페이지 요청 실패:", response.status_code)

# pandas 사용 -> 엑셀 저장
df = pd.DataFrame(data_list)
file_path = "jobkorea_requirements.xlsx"

if os.path.exists(file_path):
    existing_df = pd.read_excel(file_path)
    combined_df = pd.concat([existing_df, df], ignore_index=True)
else:
    combined_df = df

combined_df.to_excel(file_path, index=False)
print("✔ 종료")
