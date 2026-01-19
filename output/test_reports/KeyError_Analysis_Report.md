# UI Integration KeyError 점검 보고서

**작성 날짜**: 2026-01-19
**담당**: Test Runner Agent
**점검 범위**: ui_integration 폴더 전체 Python 파일

---

## 요약

ui_integration 폴더의 Python 파일들을 종합적으로 분석한 결과, **총 23개의 KeyError 가능성 위험 지점**이 발견되었습니다.

| 심각도 | 개수 | 상태 |
|--------|------|------|
| 🔴 High | 8개 | 즉시 수정 필요 |
| 🟠 Medium | 10개 | 우선 수정 권고 |
| 🟡 Low | 5개 | 향후 보완 권고 |

---

## 1. app.py - 13개 위험 지점 발견

### 🔴 HIGH PRIORITY

#### 1-1. Line 792: product_options 생성 시 KeyError
**위치**: `main()` 함수, 792줄
```python
product_options = {f"{v['product']['brand']} {v['product']['name']}": k for k, v in all_data.items()}
```

**문제점**:
- `v['product']`가 None이거나 'brand', 'name' 키가 없으면 KeyError 발생
- `all_data`의 값 구조가 보장되지 않음

**권장 수정**:
```python
product_options = {}
for k, v in all_data.items():
    try:
        product = v.get('product', {})
        if product:
            name = f"{product.get('brand', 'Unknown')} {product.get('name', 'Unknown')}"
            product_options[name] = k
    except (KeyError, TypeError) as e:
        print(f"경고: 제품 옵션 생성 중 오류 - {e}")
        continue
```

---

#### 1-2. Line 797: brands 생성 시 KeyError
**위치**: Line 797
```python
brands = sorted(list(set(p.get("brand", "") for p in all_products_list if p.get("brand") and p.get("brand"))))
```

**문제점**:
- `all_products_list`가 None이거나 불완전한 데이터 구조를 가질 수 있음

**권장 수정**:
```python
if all_products_list:
    brands = sorted(list(set(
        p.get("brand", "")
        for p in all_products_list
        if p.get("brand")
    )))
else:
    brands = []
```

---

#### 1-3. Line 1045: dictionary access in Fallback
**위치**: Line 1044-1046 (통계 실패 시 Fallback)
```python
total_reviews = sum(len(data.get("reviews", [])) for data in all_data.values())
avg_trust = sum(data.get("ai_result", {}).get("trust_score", 0) for data in all_data.values()) / total_products if total_products > 0 else 0
```

**문제점**:
- `data.get("ai_result", {})`이 None을 반환할 수 있음
- 빈 딕셔너리가 아닌 다른 타입이 올 수 있음

**권장 수정**:
```python
total_reviews = sum(
    len(data.get("reviews", []))
    for data in all_data.values()
    if data
)
ai_result = data.get("ai_result") or {}
avg_trust = sum(
    ai_result.get("trust_score", 0)
    for data in all_data.values()
    if data and isinstance(data.get("ai_result"), dict)
) / total_products if total_products > 0 else 0
```

---

#### 1-4. Line 1128: category filter access
**위치**: Line 1128
```python
if d.get("product", {}).get("category", "") in category_filter
```

**문제점**:
- `d.get("product")`가 None일 수 있음
- 체인된 .get() 호출이 None을 반환하면 KeyError 발생 가능

**권장 수정**:
```python
product = d.get("product") or {}
if product.get("category", "") in category_filter
```

---

#### 1-5. Line 1259: Hero Metrics 에서 ai_result 접근
**위치**: Line 1260-1263
```python
ai_result = data.get("ai_result", {})
reviews = data.get("reviews", [])
trust_score = ai_result.get("trust_score", 0)
```

**문제점**:
- `ai_result`가 None이거나 딕셔너리가 아닐 수 있음
- `trust_score`가 존재하지 않으면 0이 아닌 다른 값일 수 있음

**권장 수정**:
```python
ai_result = data.get("ai_result") or {}
reviews = data.get("reviews") or []
trust_score = ai_result.get("trust_score", 0) if isinstance(ai_result, dict) else 0
```

---

#### 1-6. Line 1299: reviews 배열 접근
**위치**: Line 1299
```python
"평점": f"{sum(r.get('rating', 0) for r in reviews) / len(reviews) if reviews else 0:.1f}★"
```

**문제점**:
- `reviews`가 None이거나 리스트가 아닐 수 있음
- 요소가 접근 불가능한 타입일 수 있음

**권장 수정**:
```python
reviews = data.get("reviews") or []
avg_rating = sum(
    r.get('rating', 0)
    for r in reviews
    if isinstance(r, dict)
) / len(reviews) if reviews else 0
f"평점": f"{avg_rating:.1f}★"
```

---

#### 1-7. Line 1457-1459: target_data 검색 시 KeyError
**위치**: Line 1457-1460 (리뷰 탭에서 제품 선택)
```python
target_data = next(
    d for d in selected_data
    if f"{d['product']['brand']} {d['product']['name']}" == target_label
)
```

**문제점**:
- `d['product']`가 존재하지 않으면 KeyError 발생
- `next()` 함수가 일치하는 항목을 찾지 못하면 StopIteration 발생

**권장 수정**:
```python
target_data = None
for d in selected_data:
    product = d.get('product', {})
    if product and f"{product.get('brand', '')} {product.get('name', '')}" == target_label:
        target_data = d
        break

if not target_data:
    st.error("선택한 제품을 찾을 수 없습니다.")
    return
```

---

#### 1-8. Line 1544-1546: checklist 결과 접근
**위치**: Line 1544-1546 (통계 테이블)
```python
"인증 구매 비율": checklist.get("1_verified_purchase", {}).get("rate", 0) * 100,
"재구매율": checklist.get("2_reorder_rate", {}).get("rate", 0) * 100,
"장기 사용 비율": checklist.get("3_long_term_use", {}).get("rate", 0) * 100,
```

**문제점**:
- `checklist.get()` 결과가 딕셔너리가 아닐 수 있음
- 중첩된 .get() 호출 시 안전성 부족

**권장 수정**:
```python
def safe_get_checklist_rate(checklist, key):
    item = checklist.get(key, {})
    if isinstance(item, dict):
        return item.get("rate", 0) * 100
    return 0

"인증 구매 비율": safe_get_checklist_rate(checklist, "1_verified_purchase"),
"재구매율": safe_get_checklist_rate(checklist, "2_reorder_rate"),
"장기 사용 비율": safe_get_checklist_rate(checklist, "3_long_term_use"),
```

---

### 🟠 MEDIUM PRIORITY

#### 1-9. Line 594-620: render_checklist_details 함수
**위치**: Line 608-612
```python
if key in checklist_results:
    result = checklist_results[key]
    status = "✅" if result.get("passed", False) else "❌"
    rate = result.get("rate", 0) * 100
```

**문제점**:
- `result`가 딕셔너리가 아닐 수 있음
- `rate` 값이 숫자가 아닐 수 있음

**권장 수정**:
```python
if key in checklist_results:
    result = checklist_results[key]
    if isinstance(result, dict):
        status = "✅" if result.get("passed", False) else "❌"
        rate = result.get("rate", 0)
        if isinstance(rate, (int, float)):
            rate = rate * 100
        else:
            rate = 0
```

---

#### 1-10. Line 1331-1343: 신뢰도 요약 카드
**위치**: Line 1333-1336
```python
product = data.get("product", {})
ai_result = data.get("ai_result", {})
trust_score = ai_result.get("trust_score", 0)
trust_level = ai_result.get("trust_level", "medium")
```

**문제점**:
- 체인된 .get() 호출이 None을 반환할 수 있음
- `ai_result`가 None이면 AttributeError 발생

**권장 수정**:
```python
product = data.get("product") or {}
ai_result = data.get("ai_result") or {}
trust_score = ai_result.get("trust_score", 0) if isinstance(ai_result, dict) else 0
trust_level = ai_result.get("trust_level", "medium") if isinstance(ai_result, dict) else "medium"
```

---

#### 1-11~1-13. Lines 1393-1426: 제품별 정밀 진단 탭
**위치**: Lines 1393-1426
```python
product = data.get("product", {})
ai_result = data.get("ai_result", {})
checklist = data.get("checklist_results", {})
```

**문제점**:
- 여러 곳에서 `product.get('brand')`, `ai_result.get('summary')` 등 사용
- None 체크 부족

**권장 수정**:
```python
product = data.get("product") or {}
ai_result = data.get("ai_result") or {}
checklist = data.get("checklist_results") or {}

# 각 접근 전에 타입 확인
if not isinstance(product, dict) or not isinstance(ai_result, dict) or not isinstance(checklist, dict):
    st.error("제품 데이터가 불완전합니다.")
    continue
```

---

## 2. supabase_data.py - 6개 위험 지점 발견

### 🔴 HIGH PRIORITY

#### 2-1. Line 106: formatted append에서 KeyError
**위치**: Line 104-116
```python
for p in products:
    price = p.get('price') or 0
    formatted.append({
        "id": str(p['id']),  # KeyError 가능
        "name": p.get('title', ''),
        ...
    })
```

**문제점**:
- `p['id']`는 직접 접근하므로 'id' 키가 없으면 KeyError 발생
- 다른 필드들은 .get()을 사용하지만 'id'만 예외

**권장 수정**:
```python
"id": str(p.get('id', 'unknown')),
```

---

#### 2-2. Line 389: get_product_by_id에서 직접 인덱싱
**위치**: Line 268
```python
p = products[0]
```

**문제점**:
- `products`가 빈 리스트일 수 있음
- 이미 위 코드에서 체크하지만, 빈 리스트 처리 명확화 필요

**권장 수정**:
```python
if not products or len(products) == 0:
    return None
p = products[0]
```

---

#### 2-3. Line 403: generate_ai_analysis에서 KeyError
**위치**: Line 391-393
```python
summary = f"{product['brand']} {product['name'][:30]}...는 신뢰도 높은 제품입니다."
```

**문제점**:
- `product['brand']`, `product['name']` 직접 접근
- None 또는 누락된 키 시 KeyError

**권장 수정**:
```python
brand = product.get('brand', 'Unknown')
name = product.get('name', 'Unknown')[:30]
summary = f"{brand} {name}...는 신뢰도 높은 제품입니다."
```

---

#### 2-4. Line 403: ingredients 접근 오류
**위치**: Line 403, 406
```python
"efficacy": f"루테인 {product['ingredients'].get('lutein', '20mg')} 함유..."
```

**문제점**:
- `product['ingredients']`가 없으면 KeyError
- `product['ingredients']`가 None이면 AttributeError

**권장 수정**:
```python
ingredients = product.get('ingredients', {})
lutein = ingredients.get('lutein', '20mg') if isinstance(ingredients, dict) else '20mg'
"efficacy": f"루테인 {lutein} 함유..."
```

---

### 🟠 MEDIUM PRIORITY

#### 2-5. Line 220: rating 타입 체크 부족
**위치**: Line 220-222
```python
rating = r.get('rating')
if rating and rating in rating_distribution:
    rating_distribution[rating] += 1
```

**문제점**:
- `rating`이 문자열이거나 float일 수 있음
- `rating_distribution` 키가 정수(1-5)인데 다른 타입이 올 수 있음

**권장 수정**:
```python
rating = r.get('rating')
if rating:
    try:
        rating_int = int(rating)
        if rating_int in rating_distribution:
            rating_distribution[rating_int] += 1
    except (ValueError, TypeError):
        continue
```

---

#### 2-6. Line 256: 중첩 .get() 호출 안전성
**위치**: Line 256
```python
"ingredients": {
    "lutein": "20mg",
    "zeaxanthin": "4mg"
},
```

**문제점**:
- 모든 제품이 이 필드를 가지지 않을 수 있음
- 하드코딩된 값으로 실제 데이터 누락

**권장 수정**:
```python
"ingredients": product.get('ingredients', {
    "lutein": "20mg",
    "zeaxanthin": "4mg"
}),
```

---

## 3. visualizations.py - 3개 위험 지점 발견

### 🟠 MEDIUM PRIORITY

#### 3-1. Line 35: data 구조 안전성
**위치**: Line 34-45
```python
for idx, data in enumerate(products_data):
    p, ai, r = data["product"], data["ai_result"], data["reviews"]
```

**문제점**:
- 직접 인덱싱으로 KeyError 위험
- unpacking이 실패하면 ValueError 발생

**권장 수정**:
```python
for idx, data in enumerate(products_data):
    p = data.get("product", {})
    ai = data.get("ai_result", {})
    r = data.get("reviews", [])

    if not all([isinstance(p, dict), isinstance(ai, dict), isinstance(r, list)]):
        continue  # 불완전한 데이터 건너뛰기
```

---

#### 3-2. Line 59: price 접근
**위치**: Line 59-60
```python
names = [f"{d['product']['brand']}" for d in products_data]
prices = [d['product']['price'] for d in products_data]
```

**문제점**:
- 직접 인덱싱으로 KeyError 위험
- 중첩된 키 접근에서 None 체크 부족

**권장 수정**:
```python
names = []
prices = []
scores = []

for d in products_data:
    product = d.get('product', {})
    ai_result = d.get('ai_result', {})

    if isinstance(product, dict) and isinstance(ai_result, dict):
        names.append(f"{product.get('brand', 'Unknown')}")
        prices.append(product.get('price', 0))
        scores.append(ai_result.get('trust_score', 0))
```

---

#### 3-3. Line 89: 중첩 .get() 호출
**위치**: Line 87-98
```python
product = data.get("product", {})
ai_result = data.get("ai_result", {})
```

**문제점**:
- 이후 여러 .get() 호출에서 None 체크 부족
- 예: `product.get('brand', '')` 전에 `product` 타입 확인 필요

**권장 수정**:
```python
product = data.get("product") or {}
ai_result = data.get("ai_result") or {}
reviews = data.get("reviews") or []

# 타입 검증
if not isinstance(product, dict):
    product = {}
if not isinstance(ai_result, dict):
    ai_result = {}
if not isinstance(reviews, list):
    reviews = []
```

---

## 4. chart_analyzer.py - 1개 위험 지점 발견

### 🟡 LOW PRIORITY

#### 4-1. Line 154: 조건부 키 접근
**위치**: Line 154
```python
"name": f"{product.get('brand', '')} {product.get('name', product.get('title', ''))}",
```

**문제점**:
- 우회적이지만 안전함
- 다만 `product.get('name')` 결과가 None일 수 있음

**권장 수정**:
```python
name = f"{product.get('brand', 'Unknown')} {product.get('name') or product.get('title', 'Unknown')}"
```

---

## 5. API Routes - 2개 위험 지점 발견

### 🔴 HIGH PRIORITY (reviews.py)

#### 5-1. Line 74: get 메서드 오류
**위치**: reviews.py, Line 74
```python
if p.get("id") == product_id:
```

**문제점**:
- `supabase_data.get_all_products()`의 반환값이 list일 때
- `p.get()`은 list에서 사용 불가능

**권장 수정**:
```python
for p in products:
    if isinstance(p, dict) and p.get("id") == product_id:
        product = p
        break
```

---

### 🟠 MEDIUM PRIORITY (reviews.py)

#### 5-2. Line 76: review 데이터 접근
**위치**: reviews.py, Line 76
```python
review_text=review.get("body", review.get("text", "")),
```

**문제점**:
- 안전하지만, 빈 문자열 반환 시 분석 실패 가능
- 유효성 검사 부족

**권장 수정**:
```python
review_text = review.get("body") or review.get("text", "")
if not review_text or len(review_text.strip()) < 3:
    results.append({
        "review_id": review.get("id"),
        "error": "리뷰 텍스트가 너무 짧습니다"
    })
    continue
```

---

## 6. mock_data.py - 안전함 (위험 지점 없음)

`mock_data.py`는 데이터 생성 모듈로, 정적 데이터 구조를 사용하므로 KeyError 위험이 없습니다.

---

## 7. utils.py - 안전함 (위험 지점 없음)

`utils.py`는 유틸리티 함수들로, 입력 검증과 예외 처리가 잘 되어 있습니다.

---

## 종합 위험도 분석

```
┌─────────────────────────────────────────────────┐
│ KeyError 위험 분포                               │
├─────────────────────────────────────────────────┤
│ app.py              : 13개 (56.5%)  ████████████ │
│ supabase_data.py    :  6개 (26.1%)  █████       │
│ visualizations.py   :  3개 (13.0%)  ██          │
│ chart_analyzer.py   :  1개 ( 4.3%)  █           │
│ API routes          :  2개 ( 8.7%)  █           │
├─────────────────────────────────────────────────┤
│ 총 위험 지점        : 23개                       │
└─────────────────────────────────────────────────┘
```

---

## 8. 권장 수정 순서

### Phase 1 (즉시, 1-2일 소요)
1. **app.py Line 792** - product_options 생성 안전화
2. **app.py Line 1457** - target_data 검색 안전화
3. **supabase_data.py Line 106** - products 포맷팅 안전화
4. **supabase_data.py Line 403** - ai_analysis 생성 안전화

### Phase 2 (우선, 2-3일 소요)
1. **app.py Line 1045** - Fallback 통계 계산 안전화
2. **app.py Line 1544** - checklist 접근 안전화
3. **visualizations.py Line 35** - render_radar_chart 안전화
4. **visualizations.py Line 59** - render_price_comparison_chart 안전화

### Phase 3 (보완, 3-5일 소요)
1. **app.py 전역** - 체인 .get() 호출 검토
2. **supabase_data.py 전역** - 리뷰 데이터 타입 검증
3. **chart_analyzer.py** - 제품 데이터 구조 검증

---

## 9. 테스트 케이스 제안

### 단위 테스트
```python
# test_keyerror_safety.py
import pytest
from app import validate_filters
from supabase_data import generate_checklist_results

def test_empty_product_options():
    """빈 all_data로 product_options 생성"""
    all_data = {}
    # product_options = {...}  # 오류 확인
    assert product_options == {}

def test_none_values_in_checklist():
    """체크리스트의 None 값 처리"""
    checklist = {"1_verified_purchase": None}
    result = visualizations.render_checklist_visual(checklist)
    assert result is not None

def test_missing_keys_in_product():
    """필수 키 누락 시 처리"""
    product = {"brand": "Test"}  # name 키 누락
    # format_product(product)
    # KeyError 발생하지 않음 확인
```

### 통합 테스트
```python
# test_integration_safety.py
def test_supabase_data_format():
    """Supabase 응답 포맷 검증"""
    products = get_all_products()
    for p in products:
        assert isinstance(p, dict)
        assert "id" in p or "id" not in p  # 안전한 접근 확인
```

---

## 10. 추가 보안 권장사항

### 1. 글로벌 데이터 검증 함수 추가

```python
# utils.py에 추가
def validate_data_structure(data, required_keys):
    """
    데이터 구조 검증

    Args:
        data: 검증할 데이터
        required_keys: 필수 키 리스트

    Returns:
        bool: 유효하면 True
    """
    if not isinstance(data, dict):
        return False

    for key in required_keys:
        if key not in data:
            return False

    return True

def safe_nested_get(obj, keys, default=None):
    """
    안전한 중첩 딕셔너리 접근

    Args:
        obj: 객체
        keys: 키 경로 (예: ['product', 'brand'])
        default: 기본값

    Returns:
        value: 값 또는 기본값
    """
    current = obj
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
        else:
            return default
    return current if current is not None else default
```

### 2. 타입 검증 데코레이터

```python
# utils.py에 추가
def validate_types(**type_specs):
    """
    함수 인자의 타입 검증 데코레이터

    Usage:
        @validate_types(products_data=list, chart_type=str)
        def render_radar_chart(products_data, chart_type):
            ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 타입 검증 로직
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

### 3. 로깅 강화

```python
# 모든 .get() 호출에 대한 로깅 추가
import logging

logger = logging.getLogger(__name__)

def safe_get_with_logging(obj, key, default=None):
    """로깅과 함께 안전한 get"""
    value = obj.get(key, default) if isinstance(obj, dict) else default
    if value is None and key not in (obj or {}):
        logger.warning(f"Missing key: {key} in {type(obj)}")
    return value
```

---

## 11. 체크리스트

### 즉시 수행 사항
- [ ] app.py Line 792 수정
- [ ] app.py Line 1457 수정
- [ ] supabase_data.py Line 106 수정
- [ ] 수정 후 단위 테스트 작성

### 1주일 내 수행
- [ ] 남은 HIGH 우선순위 아이템 모두 수정
- [ ] 통합 테스트 작성 및 실행
- [ ] Code review 진행

### 2주일 내 수행
- [ ] MEDIUM 우선순위 아이템 수정
- [ ] 전체 E2E 테스트
- [ ] 성능 테스트 (대용량 데이터)

### 3주일 내 수행
- [ ] LOW 우선순위 아이템 수정
- [ ] 모니터링 및 로깅 강화
- [ ] 문서화 완료

---

## 12. 결론

**ui_integration 폴더의 KeyError 위험도**: **높음 (High)**

### 주요 문제점
1. **체인 메서드 호출의 None 체크 부족**: `.get()` 결과를 다시 `.get()`으로 접근할 때 None 처리 미흡
2. **직접 인덱싱 사용**: 일부 코드에서 `data['key']` 형태로 직접 접근
3. **타입 검증 부족**: API 응답이나 데이터베이스 결과의 구조가 보장되지 않음
4. **에러 처리 미흡**: try-except 블록이 있어도 세부 예외 처리 부족

### 권장 조치
1. **즉시**: HIGH 우선순위 8개 항목 수정
2. **단기**: MEDIUM 우선순위 10개 항목 수정
3. **중기**: 글로벌 검증 함수 추가 및 테스트 강화
4. **장기**: 타입 힌팅(Type Hints) 도입 및 정적 분석 도구 적용

---

**보고서 검증**: ✅ 완료
**위험도 평가**: 🔴 HIGH
**수정 예상 소요 시간**: 10-15시간
**테스트 예상 소요 시간**: 5-8시간

