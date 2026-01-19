# 권고사항 구현 가이드

**문서 목적**: 위 충돌 점검 보고서의 권고사항을 실제 코드로 구현하는 방법

---

## 개선안 1: selected_labels 상태 관리 개선

### 문제 상황

```python
# 현재 코드 (app.py 라인 846-851)
with st.tabs(["🔍 검색 & 필터", "📊 통계", "⚙️ 설정"]):
    with sidebar_tab1:
        selected_labels = st.multiselect(...)  # ← 탭1에서만 정의

        # 탭1에서는 사용 가능
        # but 탭2, 탭3에서 selected_labels 참조 불가능

# 메인 영역 (라인 1036-1037)
# 탭2에서 selected_labels 사용 시도
if selected_labels:  # ← NameError 발생 가능
    st.info(f"**{len(selected_labels)}개 제품** 선택됨")
```

### 해결 방법 1: session_state 활용 (권장)

```python
# === 수정 1: 사이드바 탭1 ===
with sidebar_tab1:
    # 라인 846-851 수정
    st.session_state.product_select = st.multiselect(
        "분석할 제품을 선택하세요",
        options=list(product_options.keys()),
        default=st.session_state.get('product_select', list(product_options.keys())[:3]),
        key="product_select"
    )

# === 수정 2: 사이드바 탭2 ===
with sidebar_tab2:
    # 라인 1036-1037 수정
    selected_count = len(st.session_state.get('product_select', []))
    if selected_count > 0:
        st.info(f"**{selected_count}개 제품** 선택됨")
    else:
        st.caption("제품을 선택하세요")

# === 수정 3: 메인 영역 제품 선택 검증 ===
# 라인 1142-1145 수정
selected_labels = st.session_state.get('product_select', [])
if not selected_labels:
    st.warning("분석할 제품을 하나 이상 선택해주세요.")
    return
```

### 결과

```python
# 함수 호출 흐름
main()
    ├─ 사이드바: st.session_state.product_select 설정
    ├─ 탭2: st.session_state.product_select 참조
    └─ 메인: st.session_state.product_select 사용 → 필터링 적용

# 장점
✅ 상태 지속성 (재렌더링 후에도 유지)
✅ 다중 탭 간 데이터 공유 가능
✅ 비동기 상태 관리 안정화
```

---

## 개선안 2: 필터 키 이름 통일

### 문제 상황

```python
# 현재 코드의 불일치
# 사이드바 (라인 943-945)
start_date = st.date_input("시작일", value=None, key="review_start_date")
end_date = st.date_input("종료일", value=None, key="review_end_date")

# 메인 영역 filters_dict (라인 1156-1157)
'start_date': st.session_state.get('review_start_date', None),
'end_date': st.session_state.get('review_end_date', None),

# 필터링 로직 (라인 1240-1241)
start_date = filters_dict.get('start_date')
end_date = filters_dict.get('end_date')
```

### 해결 방법: 키 이름 일관성 유지

**옵션 A: 사이드바 키 변경 (권장)**

```python
# === 사이드바 고급필터 수정 (라인 940-945) ===
with st.expander("⚙️ 고급 필터", expanded=False):
    # ... 다른 필터들 ...

    # 날짜 필터 - 키 이름 단순화
    st.markdown("**📅 리뷰 날짜**")
    col_date1, col_date2 = st.columns(2)
    with col_date1:
        # ✓ 변경: "review_start_date" → "start_date"
        start_date = st.date_input("시작일", value=None, key="start_date")
    with col_date2:
        # ✓ 변경: "review_end_date" → "end_date"
        end_date = st.date_input("종료일", value=None, key="end_date")

# === 메인 영역 filters_dict 수정 (라인 1148-1159) ===
filters_dict = {
    'category_filter': st.session_state.get('category_filter', []),
    'brand_filter': st.session_state.get('brand_filter', []),
    'price_range': st.session_state.get('price_range', None),
    'rating_range': st.session_state.get('rating_range', None),
    'review_count_range': st.session_state.get('review_count_range', None),
    'trust_filter': st.session_state.get('trust_filter', []),
    'search_query': st.session_state.get('search_query', ''),
    # ✓ 변경: 키 이름 직접 매핑
    'start_date': st.session_state.get('start_date', None),
    'end_date': st.session_state.get('end_date', None),
    'language_filter': st.session_state.get('language_filter', ['all'])
}

# === 필터링 로직 변수명도 동일하게 ===
# 라인 1240-1241 (변경 불필요 - 이미 'start_date' 사용함)
start_date = filters_dict.get('start_date')
end_date = filters_dict.get('end_date')
if start_date and end_date:
    # ... 필터링 로직
```

**옵션 B: 통합 변환 헬퍼 함수**

```python
def normalize_filter_keys(raw_session_state: Dict) -> Dict:
    """session_state의 키를 정규화된 형식으로 변환"""
    return {
        'category_filter': raw_session_state.get('category_filter', []),
        'brand_filter': raw_session_state.get('brand_filter', []),
        'price_range': raw_session_state.get('price_range', None),
        'rating_range': raw_session_state.get('rating_range', None),
        'review_count_range': raw_session_state.get('review_count_range', None),
        'trust_filter': raw_session_state.get('trust_filter', []),
        'search_query': raw_session_state.get('search_query', ''),
        # 키 이름 정규화
        'start_date': raw_session_state.get('start_date') or raw_session_state.get('review_start_date'),
        'end_date': raw_session_state.get('end_date') or raw_session_state.get('review_end_date'),
        'language_filter': raw_session_state.get('language_filter', ['all'])
    }

# 사용 예
filters_dict = normalize_filter_keys(st.session_state)
```

### 결과

```python
# 일관된 키 네이밍
"start_date" → "start_date" → start_date (필터링 로직)
"end_date"   → "end_date"   → end_date (필터링 로직)

# 장점
✅ 명확한 데이터 흐름
✅ 유지보수 용이
✅ 버그 감소
```

---

## 개선안 3: 로컬 변수 네이밍 규칙

### 문제 상황

```python
# 사이드바 탭1에서 (라인 870-898)
category_filter = st.multiselect(...)  # st.multiselect 반환값
brand_filter = st.multiselect(...)
trust_filter = st.multiselect(...)

# 메인 영역에서 (라인 1182-1227)
category_filter = filters_dict.get('category_filter', [])  # 다른 변수!
if category_filter:
    # 필터링 로직
```

### 해결 방법: 명확한 네이밍 규칙

```python
# ========== 규칙 정의 ==========
# 1. session_state 키: 소문자 + 언더스코어 (카멜케이스 대체)
#    예: category_filter, brand_filter, search_query
#
# 2. 사이드바 입력 변수: [컴포넌트명]_value
#    예: category_value, brand_value, trust_value
#
# 3. 메인 영역 필터 변수: applied_[필터명]
#    예: applied_category, applied_brand, applied_trust
#
# 4. 필터링 결과: filtered_[대상]
#    예: filtered_data, filtered_reviews

# ========== 사이드바 탭1 적용 (라인 867-898) ==========
with st.expander("📂 기본 필터", expanded=True):
    # 카테고리
    if categories:
        category_value = st.multiselect(  # ✓ _value suffix
            "📂 카테고리",
            options=categories,
            default=categories,
            key="category_filter"
        )
    else:
        category_value = []

    # 브랜드
    if not brands and all_products_list:
        brands = sorted(list(set(p.get("brand", "") for p in all_products_list if p.get("brand") and p.get("brand"))))
    if brands:
        brand_value = st.multiselect(  # ✓ _value suffix
            "🏷️ 브랜드",
            options=brands,
            default=brands,
            key="brand_filter"
        )
    else:
        brand_value = []

    # 신뢰도
    trust_value = st.multiselect(  # ✓ _value suffix
        "🎯 신뢰도 등급",
        options=["HIGH", "MEDIUM", "LOW"],
        default=["HIGH", "MEDIUM", "LOW"],
        key="trust_filter"
    )

# ========== 메인 영역 필터링 (라인 1182-1227) ==========
with st.spinner("필터 적용 중..."):
    filtered_data = [all_data[product_options[label]] for label in selected_labels]

    # 카테고리 필터 적용
    applied_category = filters_dict.get('category_filter', [])  # ✓ applied_ prefix
    if applied_category:
        filtered_data = [  # ✓ 변수명 명확화
            d for d in filtered_data
            if d.get("product", {}).get("category", "") in applied_category
        ]

    # 브랜드 필터 적용
    applied_brand = filters_dict.get('brand_filter', [])  # ✓ applied_ prefix
    if applied_brand:
        filtered_data = [
            d for d in filtered_data
            if d.get("product", {}).get("brand", "") in applied_brand
        ]

    # 신뢰도 필터 적용
    applied_trust = filters_dict.get('trust_filter', [])  # ✓ applied_ prefix
    if applied_trust:
        filtered_data = [
            d for d in filtered_data
            if d.get("ai_result", {}).get("trust_level", "").upper() in [f.upper() for f in applied_trust]
        ]

    # 최종 결과
    selected_data = filtered_data  # ✓ 명확한 이름
```

### 네이밍 가이드 표

| 용도 | 패턴 | 예시 | 위치 |
|------|------|------|------|
| session_state 키 | `lowercase_with_underscore` | `category_filter` | Streamlit |
| UI 입력값 (사이드바) | `[name]_value` | `category_value` | 사이드바 |
| 필터링된 데이터 | `filtered_[target]` | `filtered_data` | 메인 |
| 필터 적용값 | `applied_[filter]` | `applied_category` | 메인 |
| 임시 처리 데이터 | `temp_[operation]` | `temp_reviews` | 함수 내부 |
| 최종 결과 | `[operation]_result` | `filter_result` | 반환값 |

### 결과

```python
# 명확한 데이터 흐름 추적
category_value (UI 입력)
    ↓ [session_state에 저장]
st.session_state.category_filter
    ↓ [filters_dict로 수집]
applied_category
    ↓ [필터링 적용]
filtered_data

# 장점
✅ 코드 의도 명확함
✅ 디버깅 용이
✅ 신규 개발자 이해도 향상
```

---

## 개선안 4: 필터 히스토리 검증 로직

### 문제 상황

```python
# 현재 코드 (라인 1010-1014)
previous_state = restore_filter_state_from_history()
if previous_state:
    for key, value in previous_state.items():
        st.session_state[key] = value  # ← 무분별한 키 추가
    st.rerun()

# 문제점
# 1. 더 이상 사용하지 않는 키도 session_state에 추가됨
# 2. 타입 검증 없음
# 3. 오래된 버전의 필터 키 존재 가능
```

### 해결 방법: 필터 키 화이트리스트 적용

```python
# ========== 필터 키 정의 (상수) ==========
# 앱 상단에 추가
VALID_FILTER_KEYS = {
    'product_select',
    'search_query',
    'category_filter',
    'brand_filter',
    'trust_filter',
    'price_range',
    'rating_range',
    'review_count_range',
    'start_date',
    'end_date',
    'language_filter'
}

FILTER_KEY_TYPES = {
    'product_select': list,
    'search_query': str,
    'category_filter': list,
    'brand_filter': list,
    'trust_filter': list,
    'price_range': tuple,
    'rating_range': tuple,
    'review_count_range': tuple,
    'start_date': (type(None), object),  # date 객체
    'end_date': (type(None), object),
    'language_filter': list
}

# ========== 필터 복원 함수 (개선) ==========
def restore_filter_state_from_history_safe() -> Optional[Dict]:
    """히스토리에서 이전 필터 상태 복원 (검증 포함)"""
    if 'filter_history' not in st.session_state or len(st.session_state.filter_history) == 0:
        return None

    previous_state = st.session_state.filter_history.pop()

    # 입력 검증
    if not isinstance(previous_state, dict):
        st.warning("⚠️ 저장된 필터 상태가 손상되었습니다.")
        return None

    # 화이트리스트 기반 필터링
    validated_state = {}
    for key, value in previous_state.items():
        # 유효한 키인지 확인
        if key not in VALID_FILTER_KEYS:
            print(f"경고: 알 수 없는 필터 키 '{key}' 무시됨")
            continue

        # 타입 검증
        expected_type = FILTER_KEY_TYPES.get(key)
        if expected_type is not None:
            if isinstance(expected_type, tuple):  # 여러 타입 허용
                if not isinstance(value, expected_type):
                    print(f"경고: 필터 '{key}'의 타입이 맞지 않습니다. {type(value)} → {expected_type}")
                    continue
            else:
                if not isinstance(value, expected_type):
                    print(f"경고: 필터 '{key}'의 타입이 맞지 않습니다. {type(value)} → {expected_type}")
                    continue

        # 값 검증 (특수 검사)
        if key == 'price_range' and isinstance(value, tuple):
            if not (isinstance(value[0], (int, float)) and isinstance(value[1], (int, float))):
                continue
            if value[0] < 0 or value[1] < 0:
                print(f"경고: 가격 범위가 음수입니다. {value}")
                continue

        validated_state[key] = value

    return validated_state if validated_state else None

# ========== 사용자 인터페이스 업데이트 (라인 1008-1014) ==========
with col_btn3:
    if 'filter_history' in st.session_state and len(st.session_state.filter_history) > 0:
        if st.button("↩️", help="되돌리기", use_container_width=True, key="undo_filters"):
            previous_state = restore_filter_state_from_history_safe()
            if previous_state:
                for key, value in previous_state.items():
                    st.session_state[key] = value
                st.success("✅ 이전 필터 설정으로 복원되었습니다")
                st.rerun()
            else:
                st.error("❌ 필터 복원에 실패했습니다")
```

### 결과

```python
# 필터 히스토리 복원 과정
stored_filters = {'old_key': value, 'category_filter': [...]}
    ↓ [restore_filter_state_from_history_safe()]
validated_filters = {'category_filter': [...]}  # old_key 제거됨
    ↓ [session_state 업데이트]
st.session_state 정상 상태 유지

# 장점
✅ session_state 오염 방지
✅ 타입 안정성 확보
✅ 후방 호환성 지원
✅ 버그 조기 감지
```

---

## 개선안 5: 필터링 성능 최적화

### 현재 구조의 문제점

```python
# 현재 코드: 순차적 필터링 (라인 1182-1289)
selected_data = [all_data[product_options[label]] for label in selected_labels]  # 1단계

# 9개의 필터를 순차적으로 적용
if category_filter:
    selected_data = [...]  # O(n*m) 2단계

if brand_filter:
    selected_data = [...]  # O(n*m) 3단계

# ... 7단계 추가

# 최악의 경우: O(n * 9m) = O(nm) 복잡도에서 9배 오버헤드
```

### 해결 방법: 통합 필터링 함수

```python
# ========== 필터 적용 함수 (통합) ==========
def apply_all_filters_optimized(data_dict: Dict, product_options: Dict, selected_labels: List[str], filters_dict: Dict) -> List[Dict]:
    """
    모든 필터를 한 번에 적용하는 최적화된 함수

    Args:
        data_dict: {product_id: {product, reviews, checklist_results, ai_result}} 형식
        product_options: {product_label: product_id} 형식
        selected_labels: 선택된 제품 라벨 리스트
        filters_dict: 필터 조건 딕셔너리

    Returns:
        필터링된 데이터 리스트
    """
    # 1단계: 초기 제품 선택
    selected_data = []
    for label in selected_labels:
        if label in product_options:
            product_id = product_options[label]
            if product_id in data_dict:
                selected_data.append(data_dict[product_id])

    # 2단계: 통합 필터링 (한 번의 순회)
    filtered_data = []

    for data in selected_data:
        # 모든 필터 조건을 함께 검사
        product = data.get("product", {})
        ai_result = data.get("ai_result", {})
        reviews = data.get("reviews", [])

        # 카테고리 필터
        if filters_dict.get('category_filter'):
            if product.get("category", "") not in filters_dict['category_filter']:
                continue

        # 브랜드 필터
        if filters_dict.get('brand_filter'):
            if product.get("brand", "") not in filters_dict['brand_filter']:
                continue

        # 가격 필터
        if filters_dict.get('price_range'):
            price = product.get("price", 0)
            if not (filters_dict['price_range'][0] <= price <= filters_dict['price_range'][1]):
                continue

        # 평점 필터
        if filters_dict.get('rating_range'):
            rating_avg = product.get("rating_avg", 0)
            if not (filters_dict['rating_range'][0] <= rating_avg <= filters_dict['rating_range'][1]):
                continue

        # 리뷰 수 필터
        if filters_dict.get('review_count_range'):
            review_count = product.get("rating_count", 0)
            if not (filters_dict['review_count_range'][0] <= review_count <= filters_dict['review_count_range'][1]):
                continue

        # 신뢰도 필터
        if filters_dict.get('trust_filter'):
            trust_level = ai_result.get("trust_level", "").upper()
            if trust_level not in [f.upper() for f in filters_dict['trust_filter']]:
                continue

        # 검색 필터
        if filters_dict.get('search_query'):
            query = filters_dict['search_query'].lower()
            product_name = f"{product.get('brand', '')} {product.get('name', '')}".lower()
            if query not in product_name:
                continue

        # 언어 필터
        if filters_dict.get('language_filter') and "all" not in filters_dict['language_filter']:
            lang_filter = filters_dict['language_filter']
            filtered_reviews = [
                r for r in reviews
                if r.get("language", "ko") in lang_filter
            ]
            if not filtered_reviews:
                continue
            data_copy = data.copy()
            data_copy["reviews"] = filtered_reviews
            filtered_data.append(data_copy)
            continue

        # 날짜 필터 (리뷰 기준)
        start_date = filters_dict.get('start_date')
        end_date = filters_dict.get('end_date')
        if start_date and end_date:
            filtered_reviews = []
            for r in reviews:
                review_date_str = r.get("date")
                if review_date_str:
                    try:
                        if isinstance(review_date_str, str):
                            review_date = datetime.strptime(review_date_str, "%Y-%m-%d").date()
                        else:
                            review_date = review_date_str

                        if start_date <= review_date <= end_date:
                            filtered_reviews.append(r)
                    except:
                        filtered_reviews.append(r)
                else:
                    filtered_reviews.append(r)

            if filtered_reviews:
                data_copy = data.copy()
                data_copy["reviews"] = filtered_reviews
                filtered_data.append(data_copy)
            continue

        # 모든 조건을 통과한 데이터만 추가
        filtered_data.append(data)

    return filtered_data

# ========== 메인 영역에서 사용 (라인 1177-1289 대체) ==========
# 필터 적용 (로딩 표시)
with st.spinner("필터 적용 중..."):
    selected_data = apply_all_filters_optimized(
        all_data,
        product_options,
        selected_labels,
        filters_dict
    )
```

### 성능 비교

```
현재 코드:
- 로직: 순차적 필터 적용 (9번 반복)
- 복잡도: O(n * 9m) = O(nm) × 9
- 10개 제품, 100개 리뷰: ~9,000 연산

개선된 코드:
- 로직: 한 번의 순회로 모든 필터 적용
- 복잡도: O(n * m) = O(nm)
- 10개 제품, 100개 리뷰: ~1,000 연산

개선율: 9배 성능 향상! 📈
```

### 결과

```python
# 장점
✅ 성능 9배 향상
✅ 메모리 사용량 감소
✅ 코드 가독성 향상
✅ 유지보수 용이

# 적용 시기
현재 제품 수가 적어서 성능 문제 없음
하지만 향후 데이터 확장 시 즉시 적용 권장
```

---

## 구현 우선순위 및 일정

| 우선순위 | 개선안 | 영향도 | 구현 난이도 | 예상 시간 | 일정 |
|---------|-------|------|----------|---------|------|
| 🔴 높음 | #1: selected_labels | 안정성 | 낮음 | 30분 | 즉시 |
| 🔴 높음 | #2: 필터 키 통일 | 가독성 | 낮음 | 1시간 | 1주일 |
| 🟠 중간 | #3: 네이밍 규칙 | 유지보수 | 중간 | 2시간 | 2주일 |
| 🟠 중간 | #4: 히스토리 검증 | 안정성 | 중간 | 1시간 | 1주일 |
| 🟡 낮음 | #5: 성능 최적화 | 성능 | 높음 | 3시간 | 1개월 |

---

## 테스트 가이드

### 테스트 1: selected_labels 상태 관리

```python
# 테스트 시나리오
1. 제품 선택 → 사이드바 탭2로 이동
   기대: "N개 제품 선택됨" 표시

2. 메인 탭 전환 → 데이터 표시 확인
   기대: 선택된 제품의 데이터만 표시

3. 페이지 새로고침 (F5) → 선택 유지 확인
   기대: 이전 선택이 유지됨 (session_state)
```

### 테스트 2: 필터 키 통일

```python
# 테스트 시나리오
1. 필터 저장 → 히스토리 확인
   기대: 모든 필터 값이 정상 저장

2. 필터 되돌리기 → 이전 상태 복원
   기대: 모든 필터가 정확히 복원됨

3. console 에러 확인
   기대: KeyError 없음
```

### 테스트 3: 성능 측정

```python
# 성능 테스트 코드
import time

# 현재 코드
start = time.time()
# ... 필터링 로직 실행
current_time = time.time() - start

# 개선된 코드
start = time.time()
# ... 개선된 필터링 로직 실행
optimized_time = time.time() - start

print(f"현재 코드: {current_time:.4f}초")
print(f"개선 코드: {optimized_time:.4f}초")
print(f"개선율: {current_time/optimized_time:.1f}배")
```

---

## 마이그레이션 체크리스트

```markdown
### Phase 1: 안정성 개선 (1주일)
- [ ] 개선안 #1 적용 (selected_labels)
- [ ] 테스트: 모든 탭 정상 동작
- [ ] 페이지 새로고침 후 상태 유지 확인
- [ ] console 에러 없음 확인

### Phase 2: 가독성 개선 (2주일)
- [ ] 개선안 #2 적용 (필터 키 통일)
- [ ] 개선안 #3 적용 (네이밍 규칙)
- [ ] 코드 리뷰
- [ ] 테스트: 필터 기능 동작 확인

### Phase 3: 방어 로직 추가 (1주일)
- [ ] 개선안 #4 적용 (히스토리 검증)
- [ ] 엣지 케이스 테스트
- [ ] console 경고 메시지 확인

### Phase 4: 성능 최적화 (향후)
- [ ] 개선안 #5 적용 (필터링 성능)
- [ ] 성능 벤치마크
- [ ] 대용량 데이터 테스트
```

---

**문서 작성**: 2026-01-19
**버전**: 1.0
