import pandas as pd
from rapidfuzz import process, fuzz

# CSV 파일 로드 (경로는 실제 파일 위치에 맞게 수정)
df = pd.read_csv('광진구 건대입구역 음식점 크롤링.csv')

# 메뉴명 전처리 함수
def preprocess_menu(menu_str):
    if pd.isna(menu_str):
        return []
    items = []
    for part in menu_str.split(';'):
        # 괄호, 가격, 옵션 제거
        name = part.split('(')[0].split('（')[0].strip()
        # +로 연결된 메뉴 분리
        for n in name.split('+'):
            n = n.strip()
            if len(n) > 1:
                items.append(n)
    return items

# 전체 (가게명, 메뉴명) 리스트 생성
menu_data = []  # (가게명, 메뉴명) 튜플 저장

for idx, row in df.iterrows():
    store_name = row['이름']
    menus = preprocess_menu(row['메뉴'])
    for menu in menus:
        menu_data.append((store_name, menu))

# 입력 음식명과 유사도 50 이상인 메뉴+가게 리스트 반환 함수
def find_similar_menus(query, menu_data, score_threshold=50):
    # 메뉴명 리스트만 추출
    menu_names = [m[1] for m in menu_data]
    # Rapidfuzz로 유사도 계산
    matches = process.extract(query, menu_names, scorer=fuzz.ratio, score_cutoff=score_threshold)
    # matches: [(매칭된 메뉴명, 점수, 인덱스), ...]
    
    # 결과에 가게명 추가
    results = []
    for match_name, score, idx in matches:
        store_name = menu_data[idx][0]
        results.append((store_name, match_name, score))
    return results

# 사용자 입력
query = input("음식명을 입력하세요: ")
results = find_similar_menus(query, menu_data)

print(f"'{query}'와 유사도 50 이상인 메뉴 및 가게 리스트:")
for store, menu, score in results:
    print(f"- 가게명: {store}, 메뉴명: {menu}, 유사도: {score}")
