# Frontend 충돌 점검 보고서

**분석 대상**: ui_integration 디렉토리 사이드바 탭 재구성 (4탭 → 3탭)
**분석 일시**: 2026-01-19
**분석 범위**: app.py, utils.py, visualizations.py, supabase_data.py

---

## 요약

사이드바 탭 재구성 변경 사항과 다른 frontend 코드 간 충돌을 점검했습니다.

**결론: 충돌 없음 (안전함)** ✅

다만, **5개의 주의사항**과 **3개의 개선 권고사항**이 있습니다.

---

## 1. Session State 키 충돌 분석

### 1.1 사이드바에서 사용하는 session_state 키

| 키 이름 | 사용 위치 | 타입 | 초기값 | 현황 |
|---------|---------|------|-------|------|
| `product_select` | 탭1: 제품 선택 | list | `[]` | ✅ 안전 |
| `search_query` | 탭1: 검색 | str | `""` | ✅ 안전 |
| `category_filter` | 탭1: 기본필터 | list | `[]` | ✅ 안전 |
| `brand_filter` | 탭1: 기본필터 | list | `[]` | ✅ 안전 |
| `trust_filter` | 탭1: 기본필터 | list | `["HIGH", "MEDIUM", "LOW"]` | ✅ 안전 |
| `price_range` | 탭1: 고급필터 | tuple | `(min, max)` | ✅ 안전 |
| `rating_range` | 탭1: 고급필터 | tuple | `(min, max)` | ✅ 안전 |
| `review_count_range` | 탭1: 고급필터 | tuple | `(min, max)` | ✅ 안전 |
| `review_start_date` | 탭1: 고급필터 | date | `None` | ✅ 안전 |
| `review_end_date` | 탭1: 고급필터 | date | `None` | ✅ 안전 |
| `language_filter` | 탭1: 고급필터 | list | `["all"]` | ✅ 안전 |
| `filter_history` | 탭1: 필터관리 | list | `[]` | ✅ 안전 |
| `filter_preset` | 탭3: 설정 | str | `"선택 안함"` | ✅ 안전 |
| `table_sort` | 메인: 탭1 정렬 | str | 기본값 | ✅ 안전 |
| `rating_filter` | 메인: 탭3 | list | `[1,2,3,4,5]` | ✅ 안전 |
| `highlight_ads` | 메인: 탭3 | bool | `True` | ✅ 안전 |
| `verified_only` | 메인: 탭3 | bool | `False` | ✅ 안전 |
| `review_product_select` | 메인: 탭3 | str | 기본값 | ✅ 안전 |
| `stat_table_sort` | 메인: 탭4 정렬 | str | 기본값 | ✅ 안전 |

**결론**: 모든 키가 고유하며 다른 컴포넌트와 충돌하지 않음. ✅

---

## 2. 변수명 충돌 분석

### 2.1 로컬 변수 스코프 확인

**주의**: `category_filter`, `brand_filter`, `trust_filter` 등의 이름이 여러 곳에서 사용되지만, **Python 로컬 변수이므로 충돌 없음**.

```python
# 사이드바 탭1 (라인 870-898)
with st.expander("📂 기본 필터", expanded=True):
    category_filter = st.multiselect(...)  # 로컬 변수
    brand_filter = st.multiselect(...)     # 로컬 변수
    trust_filter = st.multiselect(...)     # 로컬 변수

# 메인 영역 필터 적용 (라인 1182-1227)
category_filter = filters_dict.get('category_filter', [])  # 다른 로컬 변수
if category_filter:
    ...

brand_filter = filters_dict.get('brand_filter', [])  # 다른 로컬 변수
if brand_filter:
    ...

trust_filter = filters_dict.get('trust_filter', [])  # 다른 로컬 변수
if trust_filter:
    ...
```

**상세 분석**:

1. **사이드바 내 로컬 변수** (라인 870-898):
   - `category_filter` (라인 870)
   - `brand_filter` (라인 883)
   - `trust_filter` (라인 893)
   - 생성 후 즉시 사용되지 않음 (session_state에 저장됨)

2. **메인 영역 로컬 변수** (라인 1182-1227):
   - `category_filter` (라인 1182)
   - `brand_filter` (라인 1190)
   - `trust_filter` (라인 1222)
   - 필터 적용 로직에서 사용

**결론**: 각각 다른 함수 스코프이므로 충돌 없음. ✅

**주의사항 #1**: 코드 가독성 개선을 위해 변수명을 다르게 할 수 있음
```python
# 권장안
sidebar_category_filter = st.multiselect(...)
main_category_filter = filters_dict.get('category_filter', [])
```

---

## 3. 함수 호출 충돌 분석

### 3.1 사이드바에서 호출하는 함수

| 함수명 | 위치 | 호출 구간 | 현황 |
|--------|------|---------|------|
| `reset_all_filters()` | 라인 987 | 사이드바 탭1 리셋 버튼 | ✅ 안전 |
| `save_filter_state_to_history()` | 라인 1004, 1297 | 필터 저장 | ✅ 안전 |
| `restore_filter_state_from_history()` | 라인 1010 | 필터 되돌리기 | ✅ 안전 |
| `get_active_filters_summary()` | 라인 1170 | 활성 필터 표시 | ✅ 안전 |

#### 3.1.1 reset_all_filters() 함수

**정의**: 라인 256-297
**호출 위치**:
- 사이드바 탭1 리셋 버튼 (라인 987)

**분석**:
```python
# 호출
if st.button("🔄", help="초기화", use_container_width=True, key="reset_filters"):
    safe_categories = categories if (categories is not None and isinstance(categories, list)) else []
    safe_brands = brands if (brands is not None and isinstance(brands, list)) else []
    safe_products = all_products_list if (all_products_list is not None and isinstance(all_products_list, list)) else []
    reset_all_filters(safe_products, safe_categories, safe_brands)
    st.rerun()

# 함수 내용
def reset_all_filters(all_products_list: List[Dict], categories: Optional[List[str]], brands: Optional[List[str]]):
    if categories is not None and isinstance(categories, list) and len(categories) > 0:
        st.session_state.category_filter = categories.copy()
    else:
        st.session_state.category_filter = []
    # ... 더 많은 session_state 설정
```

**결론**: ✅ 안전
- 매개변수 타입과 실제 전달 데이터 타입 일치
- session_state 키 중복 없음

#### 3.1.2 save_filter_state_to_history() 함수

**정의**: 라인 183-195
**호출 위치**:
- 사이드바 탭1 필터 저장 버튼 (라인 1004)
- 메인 영역 필터 적용 후 (라인 1297)

**분석**:
```python
# 호출 1: 명시적 저장 (라인 1004)
if st.button("💾", help="저장", use_container_width=True, key="save_filters"):
    current_filters = {
        'category_filter': st.session_state.get('category_filter', []),
        'brand_filter': st.session_state.get('brand_filter', []),
        # ... 10개 필터
    }
    save_filter_state_to_history(current_filters)
    st.toast("필터 저장 완료!", icon="✅")

# 호출 2: 자동 저장 (라인 1297)
save_filter_state_to_history(filters_dict)
```

**결론**: ✅ 안전
- 두 호출 모두 동일한 딕셔너리 구조 사용
- `filter_history` session_state는 고유함

#### 3.1.3 restore_filter_state_from_history() 함수

**정의**: 라인 197-202
**호출 위치**:
- 사이드바 탭1 되돌리기 버튼 (라인 1010)

**분석**:
```python
if 'filter_history' in st.session_state and len(st.session_state.filter_history) > 0:
    if st.button("↩️", help="되돌리기", use_container_width=True, key="undo_filters"):
        previous_state = restore_filter_state_from_history()
        if previous_state:
            for key, value in previous_state.items():
                st.session_state[key] = value
            st.rerun()
```

**결론**: ✅ 안전
- 동적 session_state 업데이트로 유연한 필터 복원
- 키 검증 없음 (주의사항 참고)

#### 3.1.4 get_active_filters_summary() 함수

**정의**: 라인 204-254
**호출 위치**:
- 사이드바 활성 필터 표시 (라인 1170)

**분석**:
```python
# 라인 1170
active_filters = get_active_filters_summary(filters_dict, all_products_list)
```

**결론**: ✅ 안전
- 필터링된 데이터만 처리
- 다른 코드와 상호작용 없음

---

## 4. UI 컴포넌트 Key 중복 분석

### 4.1 st.button key 분석

**중요**: Streamlit에서 같은 페이지 내 `key`가 중복되면 에러 발생

#### 4.1.1 사이드바 탭1 버튼

| key | 위치 | 용도 | 중복 여부 |
|-----|------|------|---------|
| `quick_top3` | 라인 856 | 상위 3개 선택 | ✅ 고유 |
| `quick_all` | 라인 860 | 전체 선택 | ✅ 고유 |
| `reset_filters` | 라인 983 | 필터 초기화 | ✅ 고유 |
| `save_filters` | 라인 991 | 필터 저장 | ✅ 고유 |
| `undo_filters` | 라인 1009 | 필터 되돌리기 | ✅ 고유 |
| `apply_preset_high` | 라인 1087 | 고신뢰도 프리셋 | ✅ 고유 |
| `apply_preset_value` | 라인 1092 | 가성비 프리셋 | ✅ 고유 |
| `apply_preset_reviews` | 라인 1101 | 리뷰 많은 제품 프리셋 | ✅ 고유 |

#### 4.1.2 메인 영역 버튼

| key | 위치 | 용도 | 중복 여부 |
|-----|------|------|---------|
| `table_sort` | 라인 1408 | 테이블 정렬 | ✅ 고유 |
| `analyze_radar_main` | 라인 1375 (함수 내) | 레이더 차트 AI 분석 | ✅ 고유 |
| `analyze_price_main` | 라인 1385 (함수 내) | 가격 비교 차트 AI 분석 | ✅ 고유 |
| `rating_filter` | 라인 681 | 평점 필터 | ✅ 고유 |
| `highlight_ads` | 라인 684 | 광고 의심 하이라이트 | ✅ 고유 |
| `verified_only` | 라인 686 | 인증 구매만 | ✅ 고유 |
| `review_product_select` | 라인 1517 | 리뷰 제품 선택 | ✅ 고유 |
| `stat_table_sort` | 라인 1603 | 통계 테이블 정렬 | ✅ 고유 |

**결론**: ✅ 모든 버튼 key 고유함

### 4.2 st.multiselect key 분석

| key | 위치 | 용도 | 중복 여부 |
|-----|------|------|---------|
| `search_query` | 라인 838 | 제품 검색 | ✅ 고유 |
| `product_select` | 라인 850 | 제품 선택 | ✅ 고유 |
| `category_filter` | 라인 874 | 카테고리 필터 | ✅ 고유 |
| `brand_filter` | 라인 887 | 브랜드 필터 | ✅ 고유 |
| `trust_filter` | 라인 897 | 신뢰도 필터 | ✅ 고유 |
| `language_filter` | 라인 952 | 언어 필터 | ✅ 고유 |

**결론**: ✅ 모든 multiselect key 고유함

### 4.3 st.slider key 분석

| key | 위치 | 용도 | 중복 여부 |
|-----|------|------|---------|
| `price_range` | 라인 911 | 가격 범위 | ✅ 고유 |
| `rating_range` | 라인 924 | 평점 범위 | ✅ 고유 |
| `review_count_range` | 라인 936 | 리뷰 수 범위 | ✅ 고유 |

**결론**: ✅ 모든 slider key 고유함

### 4.4 st.selectbox key 분석

| key | 위치 | 용도 | 중복 여부 |
|-----|------|------|---------|
| `filter_preset` | 라인 1082 | 필터 프리셋 | ✅ 고유 |

**결론**: ✅ selectbox key 고유함

---

## 5. 데이터 흐름 검증

### 5.1 필터 설정 → 적용 흐름

```
사이드바 탭1 (필터 설정)
    ↓
st.session_state에 저장
    ↓
메인 영역 (라인 1148-1159) filters_dict 생성
    ↓
필터링 로직 적용 (라인 1177-1289)
    ↓
selected_data 반환
    ↓
메인 탭들에서 사용
```

**상세 검증**:

#### 5.1.1 사이드바 → session_state

```python
# 사이드바 탭1 (라인 835-953)
search_query = st.text_input(..., key="search_query")
selected_labels = st.multiselect(..., key="product_select")
category_filter = st.multiselect(..., key="category_filter")
brand_filter = st.multiselect(..., key="brand_filter")
trust_filter = st.multiselect(..., key="trust_filter")
price_range = st.slider(..., key="price_range")
rating_range = st.slider(..., key="rating_range")
review_count_range = st.slider(..., key="review_count_range")
start_date = st.date_input(..., key="review_start_date")
end_date = st.date_input(..., key="review_end_date")
language_filter = st.multiselect(..., key="language_filter")
```

✅ **모든 필터 컴포넌트가 session_state에 저장됨**

#### 5.1.2 session_state → filters_dict

```python
# 메인 영역 (라인 1148-1159)
filters_dict = {
    'category_filter': st.session_state.get('category_filter', []),
    'brand_filter': st.session_state.get('brand_filter', []),
    'price_range': st.session_state.get('price_range', None),
    'rating_range': st.session_state.get('rating_range', None),
    'review_count_range': st.session_state.get('review_count_range', None),
    'trust_filter': st.session_state.get('trust_filter', []),
    'search_query': st.session_state.get('search_query', ''),
    'start_date': st.session_state.get('review_start_date', None),  # ← 주의: key 이름 변경
    'end_date': st.session_state.get('review_end_date', None),      # ← 주의: key 이름 변경
    'language_filter': st.session_state.get('language_filter', ['all'])
}
```

✅ **모든 필터가 정상적으로 수집됨** (key 이름 변경 주의)

#### 5.1.3 filters_dict → 필터링 로직

필터링 순서 (라인 1182-1289):
1. 카테고리 필터 적용 (라인 1182-1187) ✅
2. 브랜드 필터 적용 (라인 1190-1195) ✅
3. 가격 필터 적용 (라인 1198-1203) ✅
4. 평점 범위 필터 적용 (라인 1206-1211) ✅
5. 리뷰 수 범위 필터 적용 (라인 1214-1219) ✅
6. 신뢰도 필터 적용 (라인 1222-1227) ✅
7. 검색 필터 적용 (라인 1230-1237) ✅
8. 날짜 범위 필터 적용 (라인 1240-1272) ✅
9. 언어 필터 적용 (라인 1275-1289) ✅

**결론**: ✅ 데이터 흐름 정상

### 5.2 visualizations.py 통합 확인

**함수 호출**:
```python
# 라인 299-307: import
from visualizations import (
    render_gauge_chart,
    render_trust_badge,
    render_comparison_table,
    render_radar_chart,
    render_review_sentiment_chart,
    render_checklist_visual,
    render_price_comparison_chart
)

# 라인 1370-1386: 차트 렌더링
render_chart_with_ai_analysis(
    render_radar_chart,
    selected_data,
    "radar",
    "레이더 차트",
    "radar_main"
)

render_chart_with_ai_analysis(
    render_price_comparison_chart,
    selected_data,
    "bar",
    "가격 비교 차트",
    "price_main"
)
```

**visualizations.py 함수 검토**:

| 함수명 | 입력 타입 | 필수 필드 | app.py 호출 일치 |
|--------|---------|---------|-----------------|
| `render_gauge_chart` | (score, title) | - | ✅ 일치 |
| `render_radar_chart` | list | product, ai_result, reviews | ✅ 일치 |
| `render_price_comparison_chart` | list | product, ai_result | ✅ 일치 |
| `render_trust_badge` | str | - | ✅ 일치 |
| `render_comparison_table` | list | product, ai_result, reviews, checklist_results | ✅ 일치 |
| `render_review_sentiment_chart` | list | rating | ✅ 일치 |
| `render_checklist_visual` | dict | - | ✅ 일치 |

**결론**: ✅ visualizations.py와 호환성 완벽

### 5.3 supabase_data.py 통합 확인

**함수 호출**:
```python
# 라인 22-32: import
from supabase_data import (
    get_all_analysis_results,
    get_all_products,
    search_products,
    get_products_by_category,
    get_products_by_rating_range,
    get_reviews_by_date_range,
    get_reviews_by_language,
    get_all_categories,
    get_statistics_summary
)

# 라인 37-50: 캐싱
@st.cache_data(ttl=300)
def get_cached_products():
    return get_all_products()

# 라인 765: 데이터 로드
all_data = get_cached_analysis_results()

# 라인 812-814: 제품 목록
all_products_list = get_cached_products() or []
categories = get_cached_categories() or []
```

**supabase_data.py 함수 검토**:

| 함수명 | 반환 타입 | 필드 | app.py 호출 일치 |
|--------|---------|------|-----------------|
| `get_all_products()` | List[Dict] | id, name, brand, price, rating_avg, rating_count, category | ✅ 일치 |
| `get_all_categories()` | List[str] | - | ✅ 일치 |
| `get_all_analysis_results()` | Dict[str, Dict] | product, reviews, checklist_results, ai_result | ✅ 일치 |
| `search_products()` | List[Dict] | 상동 | ✅ 일치 |

**결론**: ✅ supabase_data.py와 호환성 완벽

### 5.4 utils.py 통합 확인

**함수 호출**:
```python
# 라인 33: import
from utils import safe_get_product_label, safe_find_item, safe_parse_value

# 라인 1429: 정렬용
comparison_df["_sort_key"] = comparison_df[sort_column].apply(safe_parse_value)
```

**utils.py 함수 검토**:

| 함수명 | 입력 | 출력 | app.py 호출 일치 |
|--------|-----|------|-----------------|
| `safe_parse_value()` | Any | float | ✅ 일치 (테이블 정렬) |
| `safe_get_product_label()` | Dict | str | ✅ 사용 가능 (현재 미사용) |
| `safe_find_item()` | list, predicate | Any | ✅ 사용 가능 (현재 미사용) |

**결론**: ✅ utils.py와 호환성 완벽

---

## 주의사항 (5개)

### ⚠️ 주의사항 #1: 로컬 변수 네이밍 중복

**위치**: 라인 870-898 (사이드바) vs 라인 1182-1227 (메인)

**문제**: 같은 이름의 로컬 변수가 여러 곳에서 사용됨
- `category_filter`
- `brand_filter`
- `trust_filter`

**영향**:
- 현재는 서로 다른 스코프이므로 **기술적 충돌 없음**
- 코드 가독성 저하 가능

**권장 해결**:
```python
# 사이드바 내
sidebar_category_filter = st.multiselect(...)
sidebar_brand_filter = st.multiselect(...)
sidebar_trust_filter = st.multiselect(...)

# 메인 영역
applied_category_filter = filters_dict.get('category_filter', [])
applied_brand_filter = filters_dict.get('brand_filter', [])
applied_trust_filter = filters_dict.get('trust_filter', [])
```

**심각도**: 🟡 낮음 (가독성 문제만)

---

### ⚠️ 주의사항 #2: 필터 키 이름 불일치

**위치**: 라인 1156-1157

**문제**:
```python
# 사이드바 session_state 키
key="review_start_date"  # 라인 943
key="review_end_date"    # 라인 945

# 메인 영역 filters_dict 키
'start_date': st.session_state.get('review_start_date', None)  # 라인 1156
'end_date': st.session_state.get('review_end_date', None)      # 라인 1157

# 필터링 로직
start_date = filters_dict.get('start_date')  # 라인 1240
end_date = filters_dict.get('end_date')      # 라인 1241
```

**영향**:
- 가독성 저하
- 유지보수 시 혼동 가능
- **기능상 문제 없음** (일관성 있게 변환됨)

**권장 해결**:
```python
# 옵션 1: 사이드바 키를 변경
key="start_date"    # 라인 943
key="end_date"      # 라인 945

# 옵션 2: 딕셔너리 생성 시 키를 통일
'start_date': st.session_state.get('start_date', None)
'end_date': st.session_state.get('end_date', None)
```

**심각도**: 🟡 낮음 (가독성 + 유지보수 문제)

---

### ⚠️ 주의사항 #3: selected_labels 변수 미리 정의 부재

**위치**: 라인 846-851 vs 라인 1036-1037, 1143

**문제**:
```python
# 사이드바 탭1 (라인 846-851)
selected_labels = st.multiselect(
    "분석할 제품을 선택하세요",
    options=list(product_options.keys()),
    default=list(product_options.keys())[:3],
    key="product_select"
)

# 사이드바 탭2에서 사용 (라인 1036-1037)
if selected_labels:  # ← selected_labels는 탭1 내에서만 정의됨
    st.info(f"**{len(selected_labels)}개 제품** 선택됨")

# 메인 영역에서 사용 (라인 1143)
if not selected_labels:  # ← 전역 변수 필요
    st.warning("분석할 제품을 하나 이상 선택해주세요.")
    return
```

**현재 동작**:
- Streamlit의 재렌더링 특성상 `selected_labels`는 매번 새로 생성됨
- session_state의 `product_select`를 사용하면 상태 유지 가능

**개선안**:
```python
# 라인 1036-1037 수정
if st.session_state.get('product_select'):
    st.info(f"**{len(st.session_state.product_select)}개 제품** 선택됨")

# 라인 1143-1145 수정
selected_labels = st.session_state.get('product_select', [])
if not selected_labels:
    st.warning("분석할 제품을 하나 이상 선택해주세요.")
    return
```

**심각도**: 🟡 낮음 (현재는 동작하지만 불안정할 수 있음)

---

### ⚠️ 주의사항 #4: restore_filter_state_from_history() 동적 키 업데이트

**위치**: 라인 1010-1014

**문제**:
```python
previous_state = restore_filter_state_from_history()
if previous_state:
    for key, value in previous_state.items():
        st.session_state[key] = value  # ← 검증 없음
    st.rerun()
```

**위험성**:
- 히스토리에 저장된 키가 현재 앱에 없으면 새 키가 생성됨
- 미사용 키들이 session_state에 쌓일 수 있음
- 예: `old_key_name` → `new_key_name`으로 변경 후 되돌리기 사용 시 충돌

**개선안**:
```python
# 라인 1010-1014 수정
previous_state = restore_filter_state_from_history()
if previous_state:
    # 유효한 키만 업데이트
    valid_keys = {
        'category_filter', 'brand_filter', 'price_range', 'rating_range',
        'review_count_range', 'trust_filter', 'search_query',
        'review_start_date', 'review_end_date', 'language_filter'
    }
    for key, value in previous_state.items():
        if key in valid_keys:
            st.session_state[key] = value
    st.rerun()
```

**심각도**: 🟡 낮음 (장기 사용 시 session_state 오염 가능)

---

### ⚠️ 주의사항 #5: 메인 영역 selected_data 필터링 성능

**위치**: 라인 1177-1289

**문제**: 필터링 로직이 순차적이고 반복문이 많음
```python
# 9개의 필터 적용 단계
selected_data = [...]  # 라인 1179

# 각 필터마다 새로운 리스트 생성
if category_filter:
    selected_data = [...]  # 1단계

if brand_filter:
    selected_data = [...]  # 2단계

# ... (7단계 추가)
```

**영향**:
- 제품 수가 많을 경우 성능 저하 가능
- 각 필터 단계에서 O(n) 복잡도

**권장 해결**:
```python
# 필터 함수 통합
def apply_all_filters(data, filters_dict):
    filtered = []
    for d in data:
        # 모든 조건을 한 번에 검사
        if all_conditions_met(d, filters_dict):
            filtered.append(d)
    return filtered

selected_data = apply_all_filters(all_data.values(), filters_dict)
```

**심각도**: 🟡 낮음 (현재 제품 수가 적어서 문제 없음)

---

## 개선 권고사항 (3개)

### 권고 #1: 탭별 변수 네이밍 규칙 정립

**현재**: 사이드바와 메인 영역에서 같은 이름의 변수 사용

**권고**:
```python
# 명확한 네이밍 규칙 도입
# 사이드바 필터: sidebar_<component>
# 메인 영역 필터: main_<component>
# session_state: ss_<component> (타입_이름)

# 예시
sidebar_category_filter = st.multiselect(...)  # 사이드바에서 보여주기용
ss_category_filter_value = st.session_state.get('category_filter', [])  # 저장된 값
main_filtered_data = [d for d in data if meets_criteria(d)]  # 필터링된 결과
```

**효과**:
- 코드 가독성 향상
- 디버깅 용이성 증가
- 변수 타입 명확화

---

### 권고 #2: 필터 검증 함수 강화

**현재**: `validate_filters()` (라인 58-91) 사용하지만 미흡

**권고**:
```python
def validate_filter_consistency(filters_dict: Dict) -> Dict[str, List[str]]:
    """필터 일관성 검증"""
    errors = {}
    warnings = {}

    # 가격 범위 검증
    if 'price_range' in filters_dict and filters_dict['price_range']:
        if filters_dict['price_range'][0] > filters_dict['price_range'][1]:
            errors['price_range'] = ["최소 가격이 최대 가격보다 큼"]

    # 날짜 범위 검증
    if filters_dict.get('start_date') and filters_dict.get('end_date'):
        if filters_dict['start_date'] > filters_dict['end_date']:
            errors['date_range'] = ["시작일이 종료일보다 큼"]

    # 카테고리/브랜드 검증
    if not filters_dict.get('category_filter'):
        warnings['empty_category'] = ["카테고리 필터가 비어있음"]

    return {'errors': errors, 'warnings': warnings}

# 사용 예
validation_result = validate_filter_consistency(filters_dict)
if validation_result['errors']:
    for field, msgs in validation_result['errors'].items():
        st.error(f"{field}: {msgs[0]}")
if validation_result['warnings']:
    for field, msgs in validation_result['warnings'].items():
        st.warning(f"{field}: {msgs[0]}")
```

**효과**:
- 사용자 실수 조기 감지
- UX 개선

---

### 권고 #3: 필터 상태 영속성 추가

**현재**: session_state만 사용 (브라우저 새로고침 시 초기화)

**권고**:
```python
import json
import streamlit as st
from pathlib import Path

# 필터 상태를 파일에 저장
def save_filter_state_to_file(filters_dict: Dict, user_id: str):
    """필터 상태를 로컬 파일에 저장"""
    state_file = Path(f"./.streamlit/filter_states/{user_id}.json")
    state_file.parent.mkdir(parents=True, exist_ok=True)

    with open(state_file, 'w') as f:
        json.dump(filters_dict, f, default=str)

# 필터 상태를 파일에서 로드
def load_filter_state_from_file(user_id: str) -> Dict:
    """필터 상태를 로컬 파일에서 로드"""
    state_file = Path(f"./.streamlit/filter_states/{user_id}.json")

    if state_file.exists():
        with open(state_file, 'r') as f:
            return json.load(f)
    return {}

# 앱 시작 시 사용
if 'initialized' not in st.session_state:
    user_id = st.session_state.get('user_id', 'default')
    saved_filters = load_filter_state_from_file(user_id)
    for key, value in saved_filters.items():
        if key not in st.session_state:
            st.session_state[key] = value
    st.session_state.initialized = True

# 필터 변경 시
if st.button("💾", help="저장", use_container_width=True, key="save_filters"):
    save_filter_state_to_file(filters_dict, user_id)
    st.toast("필터 상태가 저장되었습니다", icon="✅")
```

**효과**:
- 사용자 경험 개선
- 자주 쓰는 필터 조합 유지
- 멀티 유저 지원 가능

---

## 종합 결론

### 충돌 분석 최종 결과

| 검사 항목 | 상태 | 심각도 | 조치 |
|---------|------|-------|------|
| Session State 키 충돌 | ✅ 없음 | - | 불필요 |
| 로컬 변수 충돌 | ✅ 없음 | - | 불필요 |
| 함수 호출 충돌 | ✅ 없음 | - | 불필요 |
| UI 컴포넌트 key 중복 | ✅ 없음 | - | 불필요 |
| 데이터 흐름 | ✅ 정상 | - | 불필요 |
| 모듈 호환성 | ✅ 완벽 | - | 불필요 |

### 주의사항 우선순위

| 우선순위 | 항목 | 조치 |
|---------|------|------|
| 1순위 | #3: selected_labels 상태 관리 | 권고 - 안정성 개선 |
| 2순위 | #2: 필터 키 이름 통일 | 권고 - 가독성 개선 |
| 3순위 | #1: 로컬 변수 네이밍 | 권고 - 유지보수 개선 |
| 4순위 | #4: 히스토리 동적 키 | 권고 - 방어 로직 추가 |
| 5순위 | #5: 필터링 성능 | 권고 - 향후 최적화 |

### 최종 평가

**사이드바 탭 재구성 (4탭 → 3탭) 변경사항은 다른 frontend 코드와 충돌하지 않습니다.** ✅

모든 필터 값이 올바르게 session_state에 저장되고, 메인 영역에서 정확히 사용되며, 외부 모듈(visualizations.py, supabase_data.py, utils.py)과도 완벽하게 호환됩니다.

다만, **코드 가독성과 유지보수성 향상을 위해 위의 주의사항과 개선 권고사항을 고려할 것을 권장합니다.**

---

## 부록: 데이터 흐름 다이어그램

```
┌─────────────────────────────────────────────────────────────────┐
│                        Streamlit 앱 시작                         │
└────────────────────────────────────┬────────────────────────────┘
                                     │
                    ┌────────────────▼────────────────┐
                    │   메인 함수 main() 실행         │
                    └────────────────┬────────────────┘
                                     │
        ┌────────────────────────────┼────────────────────────────┐
        │                            │                            │
        ▼                            ▼                            ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  데이터 로드     │    │  사이드바 렌더링  │    │  메인 영역 렌더링 │
│ (supabase_data) │    │  (3개 탭)        │    │  (4개 탭)        │
└────────┬─────────┘    └─────────┬────────┘    └────────┬─────────┘
         │                       │                        │
         │ all_data            │                        │
         │ all_products_list    │                        │
         │ categories          │                        │
         │ brands              │                        │
         │                      │ (탭1: 검색&필터)      │
         │              ┌───────▼────────┐              │
         │              │ st.multiselect │              │
         │              │ st.slider      │──────────┐   │
         │              │ st.date_input  │          │   │
         │              │ st.text_input  │          │   │
         │              └────────────────┘          │   │
         │                                          │   │
         │              (탭2: 통계&인사이트)        │   │
         │              ┌───────────────┐          │   │
         │              │ 통계 메트릭   │          │   │
         │              └───────────────┘          │   │
         │                                         │   │
         │              (탭3: 설정)                │   │
         │              ┌───────────────┐          │   │
         │              │ 필터 프리셋   │          │   │
         │              └───────────────┘          │   │
         │                                         │   │
         └─────────────────────────────────────────┼───┼──────┐
                                      session_state  │   │
                                                     │   │
                       ┌─────────────────────────────┘   │
                       │                                  │
        ┌──────────────▼───────────────┐                 │
        │  filters_dict 생성           │                 │
        │ (모든 필터값 수집)           │                 │
        └──────────────┬───────────────┘                 │
                       │                                  │
        ┌──────────────▼───────────────┐                 │
        │  필터링 로직 적용            │                 │
        │ (9단계 순차 필터)            │                 │
        └──────────────┬───────────────┘                 │
                       │                                  │
        ┌──────────────▼───────────────┐                 │
        │  selected_data 반환          │                 │
        │ (필터링된 제품 데이터)       │                 │
        └──────────────┬───────────────┘                 │
                       │ selected_data                    │
                       │                                  │
                       ├──────────────────────────────────┤
                       │                                  │
        ┌──────────────▼────────┐    ┌──────────────────▼──────┐
        │  메인 탭1: 종합 비교   │    │  메인 탭2: AI 정밀진단  │
        │  (render_*_chart)     │    │  (render_gauge_chart)  │
        └───────────────────────┘    └─────────────────────────┘
                       │                     │
        ┌──────────────▼────────┐    ┌──────────────────▼──────┐
        │  메인 탭3: 리뷰딥다이  │    │  메인 탭4: 통계분석     │
        │  (render_*_chart)     │    │  (statistics_df)       │
        └───────────────────────┘    └─────────────────────────┘
```

---

## 검사 명령어 기록

```bash
# Session state 키 검색
grep -r "st\.session_state\." ui_integration/

# 변수명 사용 현황
grep -r "selected_labels\|category_filter\|brand_filter" ui_integration/app.py

# 함수 호출 확인
grep -r "reset_all_filters\|save_filter_state\|restore_filter_state" ui_integration/app.py

# UI key 검색
grep -r "key=" ui_integration/app.py | grep -E "st\.button|st\.multiselect|st\.slider"
```

---

**보고서 작성**: 2026-01-19
**분석 도구**: Grep, Read, Bash
**상세도**: 5단계 (최상)
