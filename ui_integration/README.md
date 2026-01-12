# 건기식 리뷰 팩트체크 시스템 - Streamlit UI

루테인 제품 리뷰 분석 및 비교 대시보드 (상위 3개 제품 중심)

## 프로젝트 구조

```
ui_integration/
├── app.py                  # 메인 Streamlit 앱 (보안 강화, 상위 3개 표시)
├── mock_data.py            # 목업 데이터 (제품 5종 + 리뷰 100개)
├── visualizations.py       # 차트 컴포넌트 (Plotly 기반 7개 함수)
├── utils.py                # 보안 유틸리티 (입력 검증, XSS 방지)
├── requirements.txt        # 의존성
└── README.md               # 이 파일
```

## 설치 방법

### 1. 가상환경 생성 (권장)

```bash
cd ui_integration
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate  # Windows
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

## 실행 방법

```bash
streamlit run app.py
```

브라우저에서 자동으로 http://localhost:8501 이 열립니다.

## 기능 소개

### 1. 제품 개요 (상위 3개 제품 카드)
- 순위 배지 표시 (🥇 🥈 🥉)
- 제품명, 브랜드, 가격
- 신뢰도 게이지 차트 (Plotly)
- 신뢰도 등급 배지 (HIGH/MEDIUM/LOW)
- 신뢰도 점수 기준 내림차순 정렬

### 2. 종합 비교표 (상위 3개)
- 신뢰도 점수
- 광고 의심률
- 재구매율
- 한 달 사용 비율
- 평균 평점

### 3. 시각화 분석 (상위 3개)
- **레이더 차트**: 다차원 비교 (신뢰도, 가격점수, 함유량, 평점, 리뷰다양성)
- **가격 비교 차트**: 브랜드별 가격 (신뢰도 기반 색상)

### 4. 기타 제품 섹션
- 상위 3개 외 나머지 제품 간략 표시
- Expander로 접기/펼치기 지원

### 5. AI 약사 인사이트 (상위 3개)
각 제품별 상세 분석 (`logic_designer.PharmacistAnalyzer` 기반):
- **요약** (summary): 리뷰 한 줄 요약 (사용자 체감 중심, 30자 이내)
- **효능 분석** (efficacy): 원문 근거 효능, 공식 효능과 비교
- **부작용 정보** (side_effects): 리뷰에서 언급된 부작용
- **약사 핵심 조언** (tip): 50자 이내 실질적 조언
- **주의사항** (warnings): 복용 시 주의점
- **성분 검증** (ingredient_validation): 허위 성분 주장 탐지
- **부인 공지** (disclaimer): "의학적 진단이 아닌 실사용자 체감 정보"
- **13단계 체크리스트 결과** (프로그레스 바)

### 6. 리뷰 상세 보기 (상위 3개)
- 제품별 리뷰 목록 (최대 20개)
- 광고 의심 리뷰 하이라이트
- 평점 필터링 (멀티셀렉트)
- 평점 분포 차트
- 인증구매/재구매/1개월+ 배지

---

## 시각화 컴포넌트 (visualizations.py)

| 함수명 | 설명 | 반환값 |
|--------|------|--------|
| `render_gauge_chart(score, title)` | 신뢰도 게이지 차트 (0-100) | `plotly.Figure` |
| `render_trust_badge(level)` | 신뢰도 등급 배지 HTML | `str` (HTML) |
| `render_comparison_table(products_data)` | 제품 비교 테이블 | `pandas.DataFrame` |
| `render_radar_chart(products_data)` | 다차원 비교 레이더 차트 (신뢰도/가격/함유량/평점/다양성) | `plotly.Figure` |
| `render_review_sentiment_chart(reviews)` | 평점 분포 바 차트 | `plotly.Figure` |
| `render_checklist_visual(checklist_results)` | 13단계 체크리스트 시각화 | `None` (직접 렌더링) |
| `render_price_comparison_chart(products_data)` | 가격 비교 바 차트 | `plotly.Figure` |

### 차트 색상 체계
- **HIGH (70점+)**: `#22c55e` (green)
- **MEDIUM (50-70점)**: `#f59e0b` (amber)
- **LOW (50점 미만)**: `#ef4444` (red)

---

## 보안 유틸리티 (utils.py)

| 함수명 | 설명 |
|--------|------|
| `sanitize_html_string(text)` | HTML 특수문자 이스케이프 (XSS 방지) |
| `sanitize_user_input(text)` | 사용자 입력 검증 및 이스케이프 (최대 1000자) |
| `validate_score(score, min, max)` | 점수 값 유효성 검증 |
| `validate_product_data(product)` | 제품 데이터 필수 필드 검증 |
| `validate_review_data(review)` | 리뷰 데이터 필수 필드 및 평점 검증 |
| `safe_render_html(html_content)` | 안전한 HTML 렌더링 (스크립트/이벤트 핸들러 제거) |

---

## 데이터 구조

### 제품 정보 (5종)
- NOW Foods Lutein 20mg
- Doctor's Best Lutein with Lutemax 2020
- Jarrow Formulas Lutein 20mg
- Life Extension MacuGuard Ocular Support
- California Gold Nutrition Lutein with Zeaxanthin

### 리뷰 정보 (각 제품당 20개, 총 100개)
- 텍스트, 평점, 작성일
- 재구매 여부, 한 달 사용 여부
- 리뷰어, 인증 구매 여부
- 다양한 리뷰 타입 (긍정/부정/중립/광고성)

### 분석 결과 (`logic_designer` 모듈 연동)
- 신뢰도 점수 (0-100)
- 신뢰도 등급 (HIGH/MEDIUM/LOW)
- 13단계 광고 판별 체크리스트 결과
- AI 약사 분석 (summary, efficacy, side_effects, tip, warnings, disclaimer)
- 성분 검증 결과 (ingredient_validation)

---

## 기술 스택

- **Streamlit**: 웹 UI 프레임워크 (캐싱 적용)
- **Plotly**: 인터랙티브 차트 (7개 시각화 함수)
- **Pandas**: 데이터 처리 및 테이블 생성
- **HTML/CSS**: 커스텀 스타일링 (XSS 방지 적용)
- **Claude API (Anthropic)**: AI 약사 분석 엔진

---

## logic_designer 모듈 연동

### PharmacistAnalyzer (AI 약사 분석기)

> 15년 경력 임상 약사 페르소나 기반 AI 분석 엔진

```python
from logic_designer import PharmacistAnalyzer

analyzer = PharmacistAnalyzer(api_key="ANTHROPIC_API_KEY")
result = analyzer.analyze(
    review_text="리뷰 텍스트",
    product_id=1,  # 영양성분 DB 조회용
    model="claude-sonnet-4-5-20250929"
)
```

**분석 결과 구조:**
```python
{
    "summary": "리뷰 한 줄 요약 (30자 이내)",
    "efficacy": "효능 관련 내용 (원문 근거, 공식 효능 비교)",
    "side_effects": "부작용 관련 내용",
    "tip": "약사의 핵심 조언 (50자 이내)",
    "disclaimer": "의학적 진단이 아닌 실사용자 체감 정보 기반",
    "ingredient_validation": {
        "mentioned_ingredients": ["리뷰에서 언급된 성분"],
        "valid_ingredients": ["실제 제품에 포함된 성분"],
        "invalid_ingredients": ["허위 주장 성분"],
        "has_invalid_claims": False
    }
}
```

**페르소나 특징:**
- 전문적이고 객관적인 관점
- 보수적 태도로 과장 표현 경계
- 영양성분 DB 기반 허위 주장 탐지
- 공식 효능 범위 내 주장만 인정

### AdChecklist (광고 판별 체크리스트)

```python
from logic_designer import AdChecklist

checklist = AdChecklist()
detected = checklist.check_ad_patterns(
    review_text="리뷰 텍스트",
    product_id=1  # 영양성분 DB 검증용
)
# 결과: {1: "대가성 문구 존재", 5: "원료 특징 나열 (허위 성분 주장)"}
```

### TrustScoreCalculator (신뢰도 점수 계산기)

```python
from logic_designer import TrustScoreCalculator

calculator = TrustScoreCalculator()
result = calculator.calculate_final_score(
    length_score=80,
    repurchase_score=100,
    monthly_use_score=100,
    photo_score=50,
    consistency_score=70,
    penalty_count=2,
    review_text="리뷰 텍스트",
    product_id=1
)
# 결과: {"base_score": 78.5, "nutrition_score": 85.0, "final_score": 58.5, ...}
```

---

## 광고 판별 기준 (13단계 체크리스트)

> `logic_designer.AdChecklist` 클래스 기반

| # | 항목명 | 탐지 방식 |
|---|--------|----------|
| 1 | 대가성 문구 존재 | "무상 제공", "협찬", "선물 받" 등 패턴 |
| 2 | 감탄사 남발 | `!!!!`, `~~~~`, 하트 3개 이상 |
| 3 | 정돈된 문단 구조 | 번호 목록, 불릿 포인트 등 |
| 4 | 개인 경험 부재 | 1인칭 표현 미존재 |
| 5 | 원료 특징 나열 | 성분/함량 반복 언급 + 허위 성분 주장 검증 |
| 6 | 키워드 반복 | 동일 단어 7회 이상 반복 |
| 7 | 단점 회피 | 부정적 표현 부재 (다른 광고 패턴과 함께일 때만) |
| 8 | 찬사 위주 구성 | "최고", "강추", "대박" 등 반복 |
| 9 | 전문 용어 오남용 | "항산화", "생체이용률" 등 반복 + 허위 의학적 주장 |
| 10 | 비현실적 효과 강조 | "즉시", "하루만에" 등 + 효과 시점 과장 검증 |
| 11 | 타사 제품 비교 | "다른 제품보다 좋다" 등 비교 표현 |
| 12 | 홍보성 블로그 문체 | "~했답니다", "~해드립니다" 등 |
| 13 | 이모티콘 과다 사용 | 이모지 5개 이상 연속 |

### 영양성분 DB 통합 검증 (5, 9, 10번 항목)
- **허위 성분 주장**: 리뷰에서 언급한 성분이 실제 제품에 없는 경우
- **허위 의학적 주장**: 공식 효능 범위를 벗어난 주장
- **효과 시점 과장**: 일반적 효과 발현 기간보다 빠른 주장

---

## 신뢰도 점수 계산 (`logic_designer.TrustScoreCalculator`)

### 점수 공식 (영양성분 점수 포함)
```
S = (L × 0.15) + (R × 0.15) + (M × 0.25) + (P × 0.1) + (C × 0.15) + (N × 0.2)
```

| 변수 | 설명 | 가중치 |
|------|------|--------|
| L | 리뷰 길이 점수 | 15% |
| R | 재구매 여부 점수 | 15% |
| M | 한달 사용 여부 점수 | 25% |
| P | 사진 첨부 점수 | 10% |
| C | 내용 일치도 점수 | 15% |
| N | 영양성분 일치도 점수 | 20% |

### 감점 적용
- 13단계 체크리스트에서 감지된 항목당 **-10점**
- 최종 점수 = 기본 점수 - (감점 항목 수 × 10)

### 광고 판별 기준
- **최종 점수 40점 미만** 또는 **감점 항목 3개 이상** → 광고로 판별

---

## 주요 특징

- **상위 3개 집중 분석**: 신뢰도 기준 상위 3개 제품 중심 표시
- **순위 배지 시스템**: 🥇 🥈 🥉 시각적 순위 표시
- **실시간 제품 검색**: 브랜드/제품명 검색
- **보안 강화**: XSS 방지, 입력 검증, 스크립트 제거
- **캐싱 적용**: `@st.cache_data`로 성능 최적화
- **예외 처리 강화**: try-except로 안정성 확보
- **인터랙티브 차트**: 확대/축소/호버 정보
- **광고성 리뷰 탐지**: 자동 하이라이트

---

## app.py 주요 기능

### Import 구조
```python
from mock_data import (
    get_all_products, get_all_analysis_results,
    search_products, get_analysis_result
)
from visualizations import (
    render_gauge_chart, render_trust_badge,
    render_comparison_table, render_radar_chart,
    render_review_sentiment_chart, render_checklist_visual,
    render_price_comparison_chart
)
from utils import (
    sanitize_user_input, validate_score,
    validate_product_data, validate_review_data, safe_render_html
)
```

### 데이터 흐름
1. `load_analysis_data()` - 캐싱된 분석 데이터 로드
2. `search_products()` - 검색어 기반 필터링
3. 신뢰도 점수 기준 정렬 (내림차순)
4. 상위 3개 (`top3_products`) / 나머지 (`other_products`) 분리
5. 각 섹션별 렌더링

### UI 레이아웃
```
┌─────────────────────────────────────────────┐
│              🔍 건기식 리뷰 팩트체크         │
│         루테인 제품 상위 3종 비교 분석       │
├─────────────────────────────────────────────┤
│  🥇 제품1   │  🥈 제품2   │  🥉 제품3      │
│  [게이지]   │  [게이지]   │  [게이지]      │
│  [배지]     │  [배지]     │  [배지]        │
├─────────────────────────────────────────────┤
│              📊 종합 비교표                  │
├─────────────────────────────────────────────┤
│  🕸️ 레이더차트   │   💰 가격비교           │
├─────────────────────────────────────────────┤
│              📋 기타 제품 (접기)             │
├─────────────────────────────────────────────┤
│              💊 AI 약사 인사이트             │
├─────────────────────────────────────────────┤
│              💬 리뷰 상세 보기               │
└─────────────────────────────────────────────┘
```

---

## 향후 개선 사항

- [ ] 데이터베이스 연동 (Supabase PostgreSQL)
- [ ] 실시간 크롤링 기능
- [ ] 더 많은 제품 카테고리 추가
- [ ] 사용자 로그인 및 즐겨찾기 기능
- [ ] PDF 리포트 내보내기
- [ ] 제품 비교 기능 강화
- [x] 보안 강화 (XSS 방지, 입력 검증)
- [x] 상위 N개 제품 집중 표시
- [x] 순위 배지 시스템
- [x] logic_designer 모듈 연동 (13단계 체크리스트)
- [x] AI 약사 페르소나 분석 (Claude API)
- [x] 영양성분 DB 통합 검증
