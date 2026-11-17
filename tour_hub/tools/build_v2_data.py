#!/usr/bin/env python3
"""트립픽 v2 데이터 생성: 고단가 15개 + 필수품 12건 + 추천 코스 3개를 tour_hub/data 로 병합.

입력: tmp_bc/high_ticket_products.json, tmp_bc/high_ticket_raw.json,
      tmp_bc/essentials_products.json, tour_hub/data/tours.json
출력: tour_hub/data/tours.json (30 → 45개, 도시 10 → 18곳)
      tour_hub/data/essentials.json
      tour_hub/data/courses.json
      tour_hub/images/n_<id>.jpg / _sm.jpg (신규 15개)
"""
import json
import subprocess
from pathlib import Path
from PIL import Image

ROOT = Path('/workspace')
DATA = ROOT / 'tour_hub' / 'data'
IMG = ROOT / 'tour_hub' / 'images'

high = json.loads((ROOT / 'tmp_bc/high_ticket_products.json').read_text(encoding='utf-8'))
raw = json.loads((ROOT / 'tmp_bc/high_ticket_raw.json').read_text(encoding='utf-8'))
ess = json.loads((ROOT / 'tmp_bc/essentials_products.json').read_text(encoding='utf-8'))
tours = json.loads((DATA / 'tours.json').read_text(encoding='utf-8'))

H = {p['id']: p for p in high['products']}

# ---------------------------------------------------------------- 도시(섹션)
NEW_CITIES = [
    dict(id='vietnam_golf', country='vn', name='다낭·푸꾸옥 골프', title='다낭·푸꾸옥 골프',
         tagline='다낭 54홀과 푸꾸옥 36홀, 5성 호텔 3박에 마사지·식사가 붙은 골프 패키지입니다. 그린피·캐디피·카트 포함 여부와 캐디팁·주말 서차지가 상품마다 달라 표로 나눠 적었습니다.',
         cardRel=None, duration_note='3박 5일'),
    dict(id='italy', country='it', name='이탈리아·스위스', title='이탈리아·스위스', tagline=None, cardRel=None, duration_note=None),  # 기존 값 유지용 자리
    dict(id='eu_west', country='eu', name='서유럽 4개국', title='서유럽 4개국',
         tagline='융프라우와 파리 베르사유를 넣은 9박 10일. 쇼핑 6회와 가이드 경비 €100은 가격표에 없어서 표에 그대로 적었습니다.',
         cardRel=None, duration_note='9박 10일'),
    dict(id='eu_iberia', country='eu', name='스페인·포르투갈', title='스페인·포르투갈',
         tagline='8박 9일과 10박 11일, 1급 호텔 기준 두 상품입니다. 가이드 경비가 행사 인원에 따라 €90~120으로 달라집니다.',
         cardRel=None, duration_note='8박 9일~10박 11일'),
    dict(id='us_east', country='us', name='미동부·캐나다', title='미동부·캐나다',
         tagline='힐튼 폭포뷰 1박과 자유의 여신상·우드버리 아울렛을 넣은 8박 10일. 항공사(아시아나/대한항공)만 다른 두 상품을 나란히 놓았습니다.',
         cardRel=None, duration_note='8박 10일'),
    dict(id='us_west', country='us', name='미서부', title='미서부 내셔널파크',
         tagline='4대 캐년과 자이언, 온천욕까지 넣은 7박 9일 노쇼핑 상품입니다. 기사·가이드 경비 $196가 현장에서 따로 붙습니다.',
         cardRel=None, duration_note='7박 9일'),
    dict(id='hawaii', country='us', name='하와이', title='하와이',
         tagline='와이키키 오션뷰 숙소에 관광 2일을 넣은 세미패키지입니다. 하얏트 6박과 쉐라톤 허니문 5박, 취소 규정이 다른 두 상품을 비교했습니다.',
         cardRel=None, duration_note='5박 7일~6박 8일'),
    dict(id='oceania', country='oc', name='호주·뉴질랜드', title='호주·뉴질랜드',
         tagline='시드니와 뉴질랜드 남북섬을 잇는 8박 10일. 마운트쿡 트래킹과 밀포드 사운드 크루즈가 포함됩니다.',
         cardRel=None, duration_note='8박 10일'),
    dict(id='zhangjiajie', country='cn', name='장가계·원가계', title='장가계·원가계',
         tagline='대한항공 3박 5일, 노팁·노옵션·노쇼핑 상품입니다. 예약금이 출발일과 무관하게 환불되지 않는 특별약관이라 취소 규정을 먼저 보세요.',
         cardRel=None, duration_note='3박 5일'),
]

# 기존 도시 순서 유지 + 신규 삽입
old_cities = {c['id']: c for c in tours['cities']}
order = ['osaka', 'tokyo', 'fukuoka', 'sapporo', 'danang', 'nhatrang', 'bangkok', 'taipei',
         'italy', 'guam']
new_city_map = {c['id']: c for c in NEW_CITIES}

cities = []
for cid in order:
    c = dict(old_cities[cid])
    if cid == 'italy':
        c['country'] = 'eu'
        c['tagline'] = ('이탈리아·스위스 2국 9일과 이탈리아 일주 9일을 함께 담았습니다. 노쇼핑 상품과 쇼핑 포함 상품, '
                        '자유시간 횟수, 가이드 경비(€90)를 같은 표에서 비교하세요.')
        c['duration_note'] = '8박 9일~7박 9일'
    cities.append(c)
    if cid == 'nhatrang':
        cities.append({k: v for k, v in new_city_map['vietnam_golf'].items() if k != 'cardRel'})
    if cid == 'italy':
        cities.append({k: v for k, v in new_city_map['eu_west'].items()})
        cities.append({k: v for k, v in new_city_map['eu_iberia'].items()})
    if cid == 'guam':
        for k in ('us_east', 'us_west', 'hawaii', 'oceania'):
            cities.append({k2: v for k2, v in new_city_map[k].items()})
cities.append({k: v for k, v in new_city_map['zhangjiajie'].items()})
for c in cities:
    c.pop('cardRel', None)

# ---------------------------------------------------------------- 15개 상품
IMG_SRC = {}
NEW = [
    dict(id='use_ca10_oz', city='us_east', country='us', type='풀패키지', fee=3, label='프리미엄',
         theme='미동부·나이아가라·토론토 8박 10일',
         title='미동부+캐나다 10일 (힐튼 폭포뷰·아시아나)',
         includes='왕복항공(아시아나)·힐튼 폭포뷰 1박·일정 내 식사·입장료·제세금',
         excludes='기사·가이드 경비 $180, ESTA $40, 선택관광·개인경비, 식사 2회',
         extraFees=['기사·가이드 경비+식사팁 $180', 'ESTA $40 (대행 8만원)', '식사 2회 불포함'],
         perks='힐튼 폭포뷰 · 자유의 여신상 · 우드버리 아울렛',
         ticket='입장료 포함', guide='한국어',
         meeting='인천국제공항 제2터미널 노랑풍선 카운터', meetingTime='출발 3시간 전', meetShort='인천공항 T2 미팅',
         minPax='상세페이지 확인 필요', maxPax='상세페이지 확인 필요',
         cancel='30일 전까지 계약금 환급 · 29일 전 10% · 19일 전 15% · 9일 전 20% · 7일 전 30% · 당일 50% (항공권 취소료 별도)',
         cancelShort='29일 전부터 위약금 10%', cancelDays=0,
         tags=['미동부', '캐나다', '힐튼폭포뷰'], duration='8박 10일'),
    dict(id='sw_it9_noshop', city='italy', country='it', type='풀패키지', fee=3, label='노쇼핑',
         theme='스위스·이탈리아 2국 7박 9일',
         title='스위스/이탈리아 2국 9일 (노팁·노쇼핑·융프라우·수네가)',
         includes='왕복항공·전 일정 교통·4성 호텔 7박·식사·입장료·기사/가이드 경비',
         excludes='개인 경비, 불포함 식사, 매너팁(자율)',
         extraFees=['일정표 외 식사', '개인 경비·매너팁(자율)'],
         perks='노팁·노쇼핑 · 융프라우 · 수네가 전망대 · 자유시간 3회',
         ticket='입장료 포함', guide='한국어',
         meeting='인천국제공항 출발', meetingTime='항공 스케줄에 따라 상이', meetShort='인천공항 출발',
         minPax='상세페이지 확인 필요', maxPax='상세페이지 확인 필요',
         cancel='30일 전까지 계약금 환급 · 29일 전 10% · 19일 전 15% · 9일 전 20% · 7일 전 30% · 당일 50%',
         cancelShort='30일 전까지 계약금만 환급', cancelDays=0,
         tags=['노쇼핑', '노팁', '스위스', '융프라우'], duration='7박 9일'),
    dict(id='use_ca10_ke', city='us_east', country='us', type='풀패키지', fee=3, label='프리미엄',
         theme='미동부·나이아가라·토론토 8박 10일',
         title='미동부+캐나다 10일 (힐튼 폭포뷰·대한항공)',
         includes='왕복항공(대한항공)·힐튼 폭포뷰 1박·일정 내 식사·입장료·제세금',
         excludes='기사·가이드 경비 $180, ESTA $40, 선택관광·개인경비, 식사 2회',
         extraFees=['기사·가이드 경비+식사팁 $180', 'ESTA $40 (대행 8만원)', '식사 2회 불포함'],
         perks='힐튼 폭포뷰 · 대한항공 · 예약 성사율 96%',
         ticket='입장료 포함', guide='한국어',
         meeting='인천국제공항 제2터미널 노랑풍선 카운터', meetingTime='출발 3시간 전', meetShort='인천공항 T2 미팅',
         minPax='상세페이지 확인 필요', maxPax='상세페이지 확인 필요',
         cancel='30일 전까지 계약금 환급 · 29일 전 10% · 19일 전 15% · 9일 전 20% · 7일 전 30% · 당일 50% (항공권 취소료 별도)',
         cancelShort='29일 전부터 위약금 10%', cancelDays=0,
         tags=['미동부', '캐나다', '힐튼폭포뷰'], duration='8박 10일'),
    dict(id='au_nz10', city='oceania', country='oc', type='풀패키지', fee=3, label='베스트',
         theme='호주·뉴질랜드 남북섬 8박 10일',
         title='호주+뉴질랜드 남북섬 10일 (마운트쿡 트래킹)',
         includes='왕복+중간항공 2회·숙박(2인 1실)·전 일정 식사·1억원 보험',
         excludes='가이드·기사 경비, 선택관광·개인비용, 호주 ETA AUD20·뉴질랜드 NZeTA NZD117~123',
         extraFees=['가이드·기사 경비 현지 지불', '호주 ETA AUD20 · 뉴질랜드 NZeTA NZD117~123', '선택관광·매너팁'],
         perks='마운트쿡 트래킹 · 밀포드 사운드 크루즈',
         ticket='입장료 별도', guide='한국어',
         meeting='인천국제공항 제2터미널 참좋은여행 카운터', meetingTime='출발 3시간 전(15:00 미팅)', meetShort='인천공항 T2 미팅',
         minPax='8명', maxPax='상세페이지 확인 필요',
         cancel='30일 전까지 전액 환불 · 20일 전 10% · 10일 전 15% · 8일 전 20% · 1일 전 30% · 당일 50%',
         cancelShort='30일 전까지 전액 환불', cancelDays=30,
         tags=['호주', '뉴질랜드', '마운트쿡'], duration='8박 10일'),
    dict(id='hi_hyatt8', city='hawaii', country='us', type='세미패키지', fee=3, label='프리미엄',
         theme='하와이 와이키키 6박 8일',
         title='하와이 하얏트 리젠시 와이키키 8일 (오션뷰→오션프론트)',
         includes='왕복항공·하얏트 리젠시 6박·관광 2일+자유 4일·조식',
         excludes='ESTA 8만원(개별 $40), 현지가이드·기사 경비 $70, 자유일정 식사·팁',
         extraFees=['현지가이드·기사 경비 $70', 'ESTA 8만원 (개별 $40)', '자유일정 식사·테이블팁'],
         perks='오션뷰→오션프론트 · 관광 2일+자유 4일',
         ticket='입장료 포함', guide='한국어',
         meeting='인천국제공항 출발', meetingTime='항공 스케줄에 따라 상이', meetShort='인천공항 출발',
         minPax='상세페이지 확인 필요', maxPax='상세페이지 확인 필요',
         cancel='30일 전까지 계약금 환급 · 29일 전 10% · 19일 전 15% · 9일 전 20% · 7일 전 30% · 당일 50% (발권 후 항공권 취소료 별도)',
         cancelShort='30일 전까지 계약금만 환급', cancelDays=0,
         tags=['하와이', '와이키키', '하얏트'], duration='6박 8일'),
    dict(id='hi_sheraton7', city='hawaii', country='us', type='세미패키지', fee=3, label='허니문',
         theme='하와이 허니문 5박 7일',
         title='[허니문] 하와이 쉐라톤 와이키키 오션프론트 5박 7일',
         includes='왕복항공·쉐라톤 와이키키 5박·섬일주·별빛투어',
         excludes='ESTA 8만원, 자유일정 식사·매너팁, 개인 경비',
         extraFees=['ESTA 8만원 (개별 $40)', '자유일정 식사·매너팁', '개인 경비'],
         perks='허니문 · 오션프론트 · 섬일주·별빛투어',
         ticket='입장료 포함', guide='한국어',
         meeting='인천국제공항 출발', meetingTime='항공 스케줄에 따라 상이', meetShort='인천공항 출발',
         minPax='상세페이지 확인 필요', maxPax='상세페이지 확인 필요',
         cancel='30일 전까지 계약금 환급 · 29~21일 전 10% · 20~15일 전 50% · 14~1일 전 80% · 당일 100% (발권 후 항공권 취소료 별도)',
         cancelShort='30일 전까지 계약금만 환급', cancelDays=0,
         tags=['하와이', '허니문', '쉐라톤'], duration='5박 7일'),
    dict(id='eu4_10', city='eu_west', country='eu', type='풀패키지', fee=3, label='프리미엄',
         theme='서유럽 4개국 9박 10일',
         title='서유럽 4개국 10일 (융프라우+파리 베르사유)',
         includes='왕복항공·1급 호텔 9박·일정 내 식사·입장료·제세금',
         excludes='가이드·기사 경비 €100, 영국 ETA, 선택관광·개인비용, 1일차 석식',
         extraFees=['가이드·기사 경비 €100', '영국 ETA 20파운드 (대행 7만원)', '식사 1회(1일차 석식)'],
         perks='융프라우 · 파리 베르사유 · 4개국',
         ticket='입장료 포함', guide='한국어',
         meeting='인천국제공항 제2터미널 12번 출입구', meetingTime='06:30 미팅(예정)', meetShort='인천공항 T2 미팅',
         minPax='20명', maxPax='상세페이지 확인 필요',
         cancel='30일 전까지 전액 환불 · 20일 전 10% · 10일 전 15% · 8일 전 20% · 1일 전 30% · 당일 50%',
         cancelShort='30일 전까지 전액 환불', cancelDays=30,
         tags=['서유럽', '융프라우', '파리'], duration='9박 10일'),
    dict(id='sp_pt11', city='eu_iberia', country='eu', type='풀패키지', fee=3, label='프리미엄',
         theme='스페인·포르투갈 10박 11일',
         title='스페인+포르투갈 11일 (전 일정 1급 호텔·포르티망)',
         includes='왕복항공·1급 호텔 10박·일정 내 식사·입장료·제세금',
         excludes='가이드·기사 경비 €120, 선택관광·개인비용, 자유식 1회',
         extraFees=['가이드·기사 경비 €120', '자유식 1회', '선택관광·개인 비용'],
         perks='1급 호텔 · 포르티망 · 10박 11일',
         ticket='입장료 포함', guide='한국어',
         meeting='인천국제공항 제2터미널 1번 출입구 카운터', meetingTime='09:30 미팅(예정)', meetShort='인천공항 T2 미팅',
         minPax='20명', maxPax='상세페이지 확인 필요',
         cancel='30일 전까지 전액 환불 · 20일 전 10% · 10일 전 15% · 8일 전 20% · 1일 전 30% · 당일 50%',
         cancelShort='30일 전까지 전액 환불', cancelDays=30,
         tags=['스페인', '포르투갈', '포르티망'], duration='10박 11일'),
    dict(id='usw9', city='us_west', country='us', type='풀패키지', fee=3, label='노쇼핑',
         theme='미서부 캐년 7박 9일',
         title='미서부 9일 (4대캐년·자이언캐년·온천욕)',
         includes='왕복항공·숙박 7박·일정 내 식사·입장료·제세금',
         excludes='기사·가이드 경비 $196, ESTA $40, 자유식 2회',
         extraFees=['기사·가이드 경비 $196 (식사팁 포함)', 'ESTA $40 (대행 8만원)', '자유식 2회'],
         perks='4대 캐년 · 자이언 · 온천욕 · 노쇼핑',
         ticket='입장료 포함', guide='한국어',
         meeting='인천국제공항 출발', meetingTime='항공 스케줄에 따라 상이', meetShort='인천공항 출발',
         minPax='상세페이지 확인 필요', maxPax='상세페이지 확인 필요',
         cancel='30일 전까지 전액 환불 · 29일 전 10% · 19일 전 15% · 9일 전 20% · 7일 전 30% · 당일 50%',
         cancelShort='30일 전까지 전액 환불', cancelDays=30,
         tags=['노쇼핑', '미서부', '캐년'], duration='7박 9일'),
    dict(id='sp_pt9_bob', city='eu_iberia', country='eu', type='풀패키지', fee=3, label='베스트',
         theme='스페인·포르투갈 8박 9일',
         title='스페인+포르투갈 9일 (베스트 오브 베스트·1급 호텔 2박 UP)',
         includes='왕복항공·1급 호텔 8박·식사·입장료(론다 티타임)',
         excludes='가이드·기사 경비 €90~120(인원별), 선택관광·개인 비용',
         extraFees=['가이드·기사 경비 €90~120 (행사 인원별)', '선택관광·개인 비용'],
         perks='1급 호텔 2박 UP · 론다 티타임',
         ticket='입장료 포함', guide='한국어',
         meeting='인천국제공항 제2터미널 1번 출입구 카운터', meetingTime='08:00 미팅', meetShort='인천공항 T2 미팅',
         minPax='20명', maxPax='상세페이지 확인 필요',
         cancel='30일 전까지 전액 환불 · 20일 전 10% · 10일 전 15% · 8일 전 20% · 1일 전 30% · 당일 50%',
         cancelShort='30일 전까지 전액 환불', cancelDays=30,
         tags=['스페인', '포르투갈', '론다'], duration='8박 9일'),
    dict(id='it9_classic', city='italy', country='it', type='풀패키지', fee=3, label='베스트',
         theme='이탈리아 일주 8박 9일',
         title='이탈리아 클래식 일주 9일 (피사·아시시·친퀘테레)',
         includes='왕복항공·숙박 8박·식사·입장료·현지 쓰루가이드',
         excludes='가이드·기사 경비 €90, 8일차 중식, 선택관광',
         extraFees=['가이드·기사 경비 €90', '8일차 중식 불포함', '선택관광'],
         perks='피사·아시시·친퀘테레 · 현지 가이드 진행',
         ticket='입장료 포함', guide='한국어',
         meeting='인천국제공항 제2터미널 1번 출입구 카운터', meetingTime='10:30 미팅(예정)', meetShort='인천공항 T2 미팅',
         minPax='20명', maxPax='상세페이지 확인 필요',
         cancel='30일 전까지 전액 환불 · 20일 전 10% · 10일 전 15% · 8일 전 20% · 1일 전 30% · 당일 50%',
         cancelShort='30일 전까지 전액 환불', cancelDays=30,
         tags=['이탈리아', '친퀘테레', '피사'], duration='8박 9일'),
    dict(id='hk4_cju', city='sapporo', country='jp', type='풀패키지', fee=3, label='노쇼핑',
         theme='홋카이도 온천 3박 4일',
         title='청주 출발 홋카이도 4일 (비에이·아오이이케·3대 온천)',
         includes='왕복항공(청주)·온천 2곳 3박·식사·입장료·기사/가이드 경비',
         excludes='개인 여행경비, 매너팁(자율)',
         extraFees=['매너팁 (자율)', '개인 여행경비'],
         perks='청주 출발 · 비에이·아오이이케 · 3대 온천마을',
         ticket='입장료 포함', guide='한국어',
         meeting='청주국제공항 출발', meetingTime='항공 스케줄에 따라 상이', meetShort='청주공항 출발',
         minPax='상세페이지 확인 필요', maxPax='상세페이지 확인 필요',
         cancel='30일 전까지 전액 환불 · 20일 전 10% · 10일 전 15% · 8일 전 20% · 1일 전 30% · 당일 50%',
         cancelShort='30일 전까지 전액 환불', cancelDays=30,
         tags=['노쇼핑', '홋카이도', '청주출발'], duration='3박 4일'),
    dict(id='dn_golf54', city='vietnam_golf', country='vn', type='골프패키지', fee=3, label='골프',
         theme='다낭 골프 3박 5일',
         title='다낭 황제 골프 54홀 3박 5일 (진에어·오션뷰)',
         includes='왕복항공·5성 호텔 3박·그린피 54홀·캐디피·카트·1일 1마사지',
         excludes='중식, 캐디팁 $15/18홀, 가이드팁 $50, 주말 서차지 $20',
         extraFees=['캐디팁 $15/18홀', '가이드팁 1인 $50 (4인 미달 시 총 $200)', '중식·주말 서차지 $20'],
         perks='54홀 · 오션뷰 5성 · 1일 1마사지',
         ticket='입장료 포함', guide='한국어',
         meeting='인천국제공항 항공사 카운터 (개별 수속)', meetingTime='출발 3시간 전', meetShort='개별 수속',
         minPax='2명', maxPax='상세페이지 확인 필요',
         cancel='50일 전까지 무료 취소 · 49~20일 전 30% · 20일 전부터 100% (예약금은 별도 환불 불가)',
         cancelShort='50일 전까지 무료 취소', cancelDays=50,
         tags=['골프', '다낭', '54홀'], duration='3박 5일'),
    dict(id='pqc_golf36', city='vietnam_golf', country='vn', type='골프패키지', fee=3, label='골프',
         theme='푸꾸옥 골프 3박 5일',
         title='푸꾸옥 VVIP 골프 36홀 3박 5일 (5성호텔)',
         includes='왕복항공·5성 호텔 3박·그린피 36홀·캐디피·카트·관광',
         excludes='중식, 캐디팁 $15/18홀, 가이드팁 $50, 주말 서차지 $20',
         extraFees=['캐디팁 $15/18홀', '가이드팁 1인 $50 (4인 미달 시 총 $200)', '중식·주말 서차지 $20'],
         perks='36홀+관광 · 5성호텔 · 시푸드 SET',
         ticket='입장료 포함', guide='한국어',
         meeting='인천국제공항 항공사 카운터 (개별 수속)', meetingTime='출발 3시간 전', meetShort='개별 수속',
         minPax='4명', maxPax='상세페이지 확인 필요',
         cancel='50일 전까지 무료 취소 · 49~20일 전 30% · 20일 전부터 100% (예약금은 별도 환불 불가)',
         cancelShort='50일 전까지 무료 취소', cancelDays=50,
         tags=['골프', '푸꾸옥', '36홀'], duration='3박 5일'),
    dict(id='zgj5', city='zhangjiajie', country='cn', type='풀패키지', fee=3, label='노쇼핑',
         theme='장가계·원가계 3박 5일',
         title='장가계/원가계 5일 (대한항공·노팁·노옵션·노쇼핑)',
         includes='왕복항공(대한항공)·숙박 3박·식사·입장료·기사/가이드 경비',
         excludes='매너팁(자율), 외국 국적 7만원 추가',
         extraFees=['매너팁 (자율)', '외국 국적 1인 7만원 추가'],
         perks='대한항공 · 노팁·노옵션·노쇼핑 · 효도 여행',
         ticket='입장료 포함', guide='한국어',
         meeting='인천국제공항 제2터미널 (문자 안내)', meetingTime='출발 전 문자 안내', meetShort='인천공항 T2 미팅',
         minPax='10명', maxPax='상세페이지 확인 필요',
         cancel='특별약관: 예약금 입금 후 출발일과 무관하게 예약금 전액 환불 불가 · 이후 기간별 환불규정 적용',
         cancelShort='예약금 환불 불가 (특별약관)', cancelDays=0,
         tags=['노쇼핑', '노팁', '장가계', '효도'], duration='3박 5일'),
]

existing_ids = {t['id'] for t in tours['tours']}
assert len({n['id'] for n in NEW}) == 15
for n in NEW:
    assert n['id'] in H, n['id']
    assert n['id'] not in existing_ids, n['id']
    h = H[n['id']]
    n['seller'] = h['seller']
    n['price'] = h['listPrice']
    n['sale'] = h['salePrice']
    n['discount'] = f"{h['discountRate']}%" if h['discountRate'] else ''
    n['rating'] = None
    n['reviews'] = 0
    n['booked'] = f"예약 성사율 {h['confirmRatio']}%"
    n['url'] = h['naverMe']
    n['private'] = False
    n['affiliate'] = 'travel-connect'
    n['img'] = f"images/n_{n['id']}_sm.jpg"
    n['imgLg'] = f"images/n_{n['id']}.jpg"
    n['note'] = '표시가는 여행 커넥트 목록의 출발일 최저가이며, 좌석·출발일에 따라 달라집니다.'

# tk_p1 취소 규정 상충 정리 (상세페이지: 30일 전까지 취소마감일 → 29일 전부터 10% 차감)
for t in tours['tours']:
    if t['id'] == 'tk_p1':
        t['cancel'] = ('30일 전까지 무료 취소 · 29일 전 10% · 19일 전 15% · 9일 전 20% · 7일 전 30% · 당일 50%')
        t['cancelShort'] = '30일 전까지 무료 취소'
        t['cancelDays'] = 30

tours['tours'].extend(NEW)

# 기존 이탈리아 상품 country 를 eu 로 (탭 통합)
for t in tours['tours']:
    if t['city'] == 'italy':
        t['country'] = 'eu'
    if t['city'] == 'sapporo':
        t['country'] = 'jp'

tours['cities'] = cities
tours['meta'] = {
    'count': len(tours['tours']),
    'cities': len(cities),
    'countries': sorted({t['country'] for t in tours['tours']}),
    'updated': '2026-11-16',
    'note': '가격은 여행 커넥트 상품 목록 기준 출발일 최저가. 상세 조건은 각 상세페이지 확인.',
}

(DATA / 'tours.json').write_text(json.dumps(tours, ensure_ascii=False, indent=1), encoding='utf-8')
print('tours.json:', len(tours['tours']), 'products /', len(cities), 'cities')

# ---------------------------------------------------------------- 이미지
def grab(url, out):
    subprocess.run(['curl', '-sL', '-A', 'Mozilla/5.0', '-o', out, url], check=False)
    try:
        return Image.open(out).convert('RGB')
    except Exception:
        return None

for n in NEW:
    imgs = raw.get(n['id'], {}).get('images') or []
    ok = False
    for idx, url in enumerate(imgs[:6]):
        tmp = f"/tmp/v2_{n['id']}_{idx}.jpg"
        im = grab(url, tmp)
        if not im:
            continue
        w, h = im.size
        if w < 700:
            continue
        if w / h > 1.5:
            nw = int(h * 1.5)
            im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
        else:
            nh = int(w / 1.5)
            im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
        im = im.resize((1200, 800), Image.LANCZOS)
        im.save(IMG / f"n_{n['id']}.jpg", quality=86, optimize=True)
        im.resize((660, 440), Image.LANCZOS).save(IMG / f"n_{n['id']}_sm.jpg", quality=84, optimize=True)
        IMG_SRC[n['id']] = url
        print('img', n['id'], 'ok', idx, f'{w}x{h}')
        ok = True
        break
    if not ok:
        print('img', n['id'], 'FAILED', imgs[:1])

# 이미지 경로가 생성되지 않은 상품은 기존 대표 이미지로 대체하지 않고 실패로 남긴다
missing = [n['id'] for n in NEW if not (IMG / f"n_{n['id']}.jpg").exists()]
print('missing images:', missing)

# ---------------------------------------------------------------- 필수품
ess_out = dict(
    source=ess['verification'],
    disclosure=ess['disclosureNote'],
    changePolicy=ess['changePolicy'],
    products=ess['products'],
)
(DATA / 'essentials.json').write_text(json.dumps(ess_out, ensure_ascii=False, indent=1), encoding='utf-8')
print('essentials.json:', len(ess['products']), 'items')

# ---------------------------------------------------------------- 추천 코스
courses = {
    'note': '일차별 추천 구성. 가이드투어는 여행 커넥트, 교통·입장권·eSIM은 쇼핑 커넥트 제휴 링크입니다.',
    'courses': [
        dict(
            id='osaka', title='오사카·교토 3박 4일', country='jp', city='osaka',
            lead='3일차에 어디를 넣느냐로 갈립니다. 교토를 하루 가이드투어로 돌면 이동시간을 아끼고, USJ를 넣으면 이동을 단독차량으로 붙이세요.',
            days=[
                dict(no=1, title='인천 → 간사이 → 난바', memo='도착 후 라피트로 난바까지 38분. 체크인 후 도톤보리 야경.',
                     items=[dict(kind='essence', ref='jp-esim-usimsa-1d', note='도착 즉시 켜는 1일 데이터'),
                            dict(kind='essence', ref='osaka-nankai-rapit', note='공항→난바 38분 지정석')]),
                dict(no=2, title='교토 하루 — 후시미이나리 → 아라시야마 → 청수사',
                     memo='버스로만 도는 동선이라 하루 가이드투어가 가장 빠릅니다. 입장료는 별도인 곳이 많습니다.',
                     items=[dict(kind='tour', ref='os_g', note='한국어 가이드 일일 버스투어'),
                            dict(kind='essence', ref='osaka-amazing-pass', note='2일권으로 2~3일차 지하철+명소 입장',
                                 warn='상세문구에 교환기한이 2024년으로 남아 있습니다. 구매 전 판매처에 기한을 확인하고, 리뷰 0건이라 대표 카드로 쓰지 않았습니다.')]),
                dict(no=3, title='오사카 시내 · USJ', memo='USJ 방문이면 이동을 미리 잡아두세요. 4인 동반이면 단독차량 1건으로 왕복이 해결됩니다.',
                     items=[dict(kind='essence', ref='osaka-usj-pickup', note='공항·시내↔USJ 편도 단독차량'),
                            dict(kind='essence', ref='osaka-usj-shuttle-existing', note='예산형 셔틀버스'),
                            dict(kind='essence', ref='jp-esim-usimsa-3d', note='3일 완전무제한 메인 eSIM')]),
                dict(no=4, title='난바 → 간사이 → 인천', memo='라피트나 공항버스로 복귀. 남은 데이터는 3일권으로 커버됩니다.',
                     items=[dict(kind='essence', ref='jp-esim-lingsim-1d', note='1일 500MB 가성비 16%'),
                            dict(kind='essence', ref='osaka-nankai-rapit', note='복귀편도')]),
            ],
            lodge=dict(area='난바·신사이바시 역세권 (우메다도 가능)',
                       note='3박 모두 같은 숙소를 잡으면 이동이 줄어듭니다. 트립닷컴·아고다 제휴 승인 전이라 호텔 요금 비교표는 넣지 않았습니다.'),
            package=dict(ref='os_p2', note='2박 3일 상품 — 이 코스보다 1박 짧습니다 (호텔 3박은 직접 예약)'),
        ),
        dict(
            id='tokyo', title='도쿄·후지 3박 4일', country='jp', city='tokyo',
            lead='후지산은 날씨가 전부라 2일차를 비워두는 편이 안전합니다. 3일차는 메트로 패스 하나로 시내 이동이 정리됩니다.',
            days=[
                dict(no=1, title='나리타 → 우에노', memo='스카이라이너 41분 직통. 우에노·아사쿠사 숙소면 이동이 짧습니다.',
                     items=[dict(kind='essence', ref='tokyo-skyliner', note='나리타→우에노 41분 (편도 기준)'),
                            dict(kind='essence', ref='jp-esim-usimsa-1d', note='도착일 1일 데이터')]),
                dict(no=2, title='후지산 하루 — 센겐공원 → 오시노핫카이 → 가와구치호',
                     memo='도쿄역·신주쿠 출발 버스투어. 맑은 날을 골라야 오층탑 앞 후지산이 보입니다.',
                     items=[dict(kind='tour', ref='tk_g', note='한국인 가이드 일일 버스투어'),
                            dict(kind='essence', ref='tokyo-metro-pass', note='시내 이동용 (24/48/72시간 중 선택)')]),
                dict(no=3, title='도쿄 시내 자유 — 시부야·긴자·아사쿠사', memo='메트로 패스 24~72시간으로 이동을 묶고, 쇼핑은 저녁에.',
                     items=[dict(kind='essence', ref='tokyo-metro-pass', note='24시간권 최저 5,600원~'),
                            dict(kind='essence', ref='jp-esim-lingsim-1d', note='590원 1일 500MB')]),
                dict(no=4, title='우에노 → 나리타', memo='출국 3시간 전 도착 기준으로 스카이라이너 시간을 역산하세요.',
                     items=[dict(kind='essence', ref='tokyo-skyliner', note='우에노→나리타')]),
            ],
            lodge=dict(area='우에노·아사쿠사 또는 신주쿠 역세권',
                       note='나리타 왕복이면 우에노 쪽이 편하고, 후지 투어 출발지가 신주쿠면 신주쿠가 낫습니다. 호텔 제휴 연동 준비 중.'),
            package=dict(ref='tk_p1', note='시내호텔 3연박 + 1일 자유 or 하코네 — 이 코스와 일수·숙박이 같습니다'),
        ),
        dict(
            id='danang', title='다낭·호이안 3박 5일', country='vn', city='danang',
            lead='5일 중 2일은 이동·휴식입니다. 바나힐과 호이안 야경만 미리 잡아두면 나머지는 자유일정으로 충분합니다.',
            days=[
                dict(no=1, title='인천 → 다낭', memo='심야 도착도 추가금 없는 단독차량을 잡으면 새벽 도착이 편합니다.',
                     items=[dict(kind='essence', ref='danang-airport-pickup', note='야간 추가금 없는 단독차량'),
                            dict(kind='essence', ref='vn-esim-usimsa-1d', note='200원 1일 데이터')]),
                dict(no=2, title='바나힐 — 케이블카·골든브릿지', memo='입장권과 케이블카가 한 상품입니다. 차량 포함 옵션은 금액이 올라갑니다.',
                     items=[dict(kind='essence', ref='danang-bana-hills', note='4,890원은 최저 옵션가 (차량 포함 시 상승)',
                                 warn='4,890원은 입장권 단독 기준 최저 옵션가입니다. 2인·차량 포함 옵션을 고르면 금액이 올라갑니다.'),
                            dict(kind='essence', ref='vn-esim-usimsa-3d', note='3일 완전무제한')]),
                dict(no=3, title='호이안 올드타운 · 야경', memo='해 질 무렵 도착해 등불 야경까지 보는 동선. 쇼핑 커넥트에 호이안 단독 투어 상품은 없어 패키지로 붙였습니다.',
                     items=[dict(kind='tour', ref='dn_p3', note='호이안 야경투어 포함 3박 5일 패키지 (노옵션·노팁)')]),
                dict(no=4, title='미케비치 자유일정', memo='마사지·카페·해변. 별도 예약 없이 숙소 근처에서 정리하는 날로 두었습니다.',
                     items=[dict(kind='tour', ref='dn_p2', note='바나힐·스윗룸·전신마사지 포함 패키지')]),
                dict(no=5, title='다낭 → 인천', memo='공항 샌딩은 같은 픽업 상품의 반대 방향 — 판매처에 샌딩 가능 여부를 확인하세요.',
                     items=[dict(kind='essence', ref='danang-airport-pickup', note='공항 이동 (편도 기준)')]),
            ],
            lodge=dict(area='미케비치·한시장 인근 5성급',
                       note='이 코스의 패키지 상품들은 5성 호텔 3박을 포함합니다. 호텔 단독 예약은 제휴 연동 준비 중.'),
            package=dict(ref='dn_p1', note='노팁·노옵션·5성급 3박 5일 — 바나힐·호이안이 모두 포함됩니다'),
        ),
    ],
}
(DATA / 'courses.json').write_text(json.dumps(courses, ensure_ascii=False, indent=1), encoding='utf-8')
print('courses.json:', len(courses['courses']), 'courses')
