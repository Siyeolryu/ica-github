# KeyError 수정 코드 샘플

**작성 날짜**: 2026-01-19
**목적**: 즉시 수정이 필요한 4개 항목의 상세 수정 방안 제시

---

## 1. app.py Line 792 - product_options 생성 안전화

### 현재 코드 (위험)
```python
product_options = {f"{v['product']['brand']} {v['product']['name']}": k for k, v in all_data.items()}
```

### 문제점
- `v['product']`가 None이거나 존재하지 않으면 KeyError
- 'brand' 또는 'name' 키가 없으면 KeyError
- 예외 처리 없음

### 수정된 코드
```python
# 방법 1: 일반적인 안전한 방식
product_options = {}
for k, v in all_data.items():
    try:
        product = v.get('product', {})
        if product and isinstance(product, dict):
            brand = product.get('brand', 'Unknown')
            name = product.get('name', 'Unknown')
            if brand and name:
                product_options[f"{brand} {name}"] = k
    except (KeyError, TypeError, AttributeError) as e:
        print(f"경고: 제품 옵션 생성 중 오류 - 제품ID: {k}, 오류: {str(e)}")
        continue

# 유효한 옵션이 없으면 경고
if not product_options:
    st.warning("분석할 수 있는 제품이 없습니다. Supabase 연결을 확인하세요.")
    return
```

### 방법 2: 헬퍼 함수 활용 (추천)
```python
def extract_product_label(product_data):
    """제품 라벨 추출 (안전한 방식)"""
    product = product_data.get('product', {})
    if not isinstance(product, dict):
        return None

    brand = product.get('brand', '').strip()
    name = product.get('name', '').strip()

    if brand and name:
        return f"{brand} {name}"
    return None

# 사용
product_options = {}
for k, v in all_data.items():
    label = extract_product_label(v)
    if label:
        product_options[label] = k

if not product_options:
    st.warning("분석할 수 있는 제품이 없습니다.")
    return
```

### 테스트 케이스
```python
def test_product_options_safety():
    """product_options 생성 안전성 테스트"""

    # 테스트 1: 정상 데이터
    all_data = {
        "id1": {"product": {"brand": "NOW Foods", "name": "Lutein"}}
    }
    assert len(product_options) == 1

    # 테스트 2: None product
    all_data = {
        "id1": {"product": None}
    }
    assert len(product_options) == 0

    # 테스트 3: 누락된 키
    all_data = {
        "id1": {"product": {"brand": "NOW Foods"}}  # name 누락
    }
    assert len(product_options) == 0

    # 테스트 4: 빈 데이터
    all_data = {}
    assert len(product_options) == 0
```

---

## 2. app.py Line 1457 - target_data 검색 안전화

### 현재 코드 (위험)
```python
target_data = next(
    d for d in selected_data
    if f"{d['product']['brand']} {d['product']['name']}" == target_label
)
```

### 문제점
- 'product' 키가 없으면 KeyError
- 'brand', 'name' 키가 없으면 KeyError
- 일치하는 항목이 없으면 StopIteration 예외
- 예외 처리 없음

### 수정된 코드 (추천)
```python
# 안전한 버전
def find_target_data(selected_data, target_label):
    """대상 제품 데이터 찾기 (안전한 방식)"""
    for d in selected_data:
        product = d.get('product')
        if not product or not isinstance(product, dict):
            continue

        brand = product.get('brand', '')
        name = product.get('name', '')

        if f"{brand} {name}" == target_label:
            return d

    return None

# 메인 코드에서 사용
target_data = find_target_data(selected_data, target_label)

if not target_data:
    st.error(f"선택한 제품 '{target_label}'을 찾을 수 없습니다.")
    st.info("제품 선택을 다시 확인해주세요.")
    return

# 이후 정상적으로 target_data 사용
reviews = target_data.get("reviews", [])
product = target_data.get("product", {})
```

### 대체 방법: 인덱싱 방식 사용
```python
# 선택된 제품 인덱스를 사용하는 방식
selected_index = st.selectbox(
    "리뷰를 확인할 제품 선택",
    options=range(len(selected_data)),
    format_func=lambda i: selected_labels[i],
    key="review_product_select"
)

target_data = selected_data[selected_index]
reviews = target_data.get("reviews", [])
product = target_data.get("product", {})
```

### 테스트 케이스
```python
def test_find_target_data_safety():
    """대상 데이터 찾기 안전성 테스트"""

    selected_data = [
        {"product": {"brand": "NOW Foods", "name": "Lutein"}},
        {"product": {"brand": "Doctor's Best", "name": "Lutein with Lutemax"}}
    ]

    # 테스트 1: 정상 찾기
    target = find_target_data(selected_data, "NOW Foods Lutein")
    assert target is not None

    # 테스트 2: 없는 제품 찾기
    target = find_target_data(selected_data, "Non-existent Product")
    assert target is None

    # 테스트 3: None product
    selected_data_with_none = [{"product": None}]
    target = find_target_data(selected_data_with_none, "Any Product")
    assert target is None

    # 테스트 4: 빈 selected_data
    target = find_target_data([], "Any Product")
    assert target is None
```

---

## 3. supabase_data.py Line 106 - 제품 포맷팅 안전화

### 현재 코드 (위험)
```python
def get_products_by_category(category: str) -> List[Dict]:
    """카테고리별 제품 조회"""
    if not category:
        return get_all_products()
    products = _fetch_from_supabase('products', f'select=*&category=eq.{category}&order=rating_count.desc')
    formatted = []
    for p in products:
        price = p.get('price') or 0
        formatted.append({
            "id": str(p['id']),  # KeyError 가능
            "name": p.get('title', ''),
            "brand": p.get('brand', ''),
            ...
        })
    return formatted
```

### 문제점
- `p['id']`는 직접 접근하므로 'id' 키 없으면 KeyError
- 다른 필드들은 .get()을 사용하는 불일관성

### 수정된 코드
```python
def _format_product(p: Dict) -> Optional[Dict]:
    """제품 데이터 포맷팅 (안전한 방식)"""
    try:
        # 필수 필드 검증
        product_id = p.get('id')
        if product_id is None:
            print(f"경고: id 필드 누락 - {p}")
            return None

        # 가격 변환
        price = p.get('price') or 0
        if isinstance(price, str):
            try:
                price = float(price)
            except ValueError:
                price = 0

        # 포맷팅된 제품 반환
        return {
            "id": str(product_id),
            "name": (p.get('title') or p.get('name') or '').strip(),
            "brand": (p.get('brand') or '').strip(),
            "price": price / 100 if price > 1000 else price,
            "serving_size": p.get('serving_size', '1 Softgel'),
            "servings_per_container": p.get('servings_per_container', 60),
            "ingredients": p.get('ingredients', {
                "lutein": "20mg",
                "zeaxanthin": "4mg"
            }),
            "product_url": (p.get('url') or p.get('product_url') or '').strip(),
            "rating_avg": p.get('rating_avg') or 0,
            "rating_count": p.get('rating_count') or 0,
            "category": (p.get('category') or '').strip()
        }
    except Exception as e:
        print(f"제품 포맷팅 오류: {str(e)}, 제품: {p}")
        return None

def get_products_by_category(category: str) -> List[Dict]:
    """카테고리별 제품 조회"""
    if not category:
        return get_all_products()

    products = _fetch_from_supabase(
        'products',
        f'select=*&category=eq.{category}&order=rating_count.desc'
    )

    formatted = []
    for p in products:
        formatted_product = _format_product(p)
        if formatted_product:
            formatted.append(formatted_product)

    if not formatted:
        print(f"경고: 카테고리 '{category}'에 포맷팅된 제품이 없습니다")

    return formatted
```

### 다른 함수들에도 적용
```python
def get_all_products() -> List[Dict]:
    """모든 제품 정보 반환"""
    products = _fetch_from_supabase('products', 'select=*&order=rating_count.desc')
    formatted = []

    for p in products:
        formatted_product = _format_product(p)
        if formatted_product:
            formatted.append(formatted_product)

    return formatted

def get_product_by_id(product_id: str) -> Optional[Dict]:
    """특정 제품 정보 반환"""
    products = _fetch_from_supabase('products', f'select=*&id=eq.{product_id}')

    if not products:
        return None

    return _format_product(products[0])
```

### 테스트 케이스
```python
def test_format_product_safety():
    """제품 포맷팅 안전성 테스트"""

    # 테스트 1: 정상 제품
    normal_product = {
        'id': 1,
        'title': 'Lutein',
        'brand': 'NOW Foods',
        'price': 1499,
        'rating_avg': 4.5,
        'rating_count': 100
    }
    result = _format_product(normal_product)
    assert result is not None
    assert result['id'] == '1'
    assert result['price'] == 14.99

    # 테스트 2: id 누락
    missing_id = {'title': 'Lutein', 'brand': 'NOW Foods'}
    result = _format_product(missing_id)
    assert result is None

    # 테스트 3: 빈 딕셔너리
    empty = {}
    result = _format_product(empty)
    assert result is None

    # 테스트 4: None 제품
    result = _format_product(None)
    assert result is None

    # 테스트 5: 가격 문자열
    string_price = {
        'id': 1,
        'title': 'Lutein',
        'price': '1499'  # 문자열
    }
    result = _format_product(string_price)
    assert result is not None
    assert result['price'] == 14.99
```

---

## 4. supabase_data.py Line 403 - AI 분석 생성 안전화

### 현재 코드 (위험)
```python
def generate_ai_analysis(product: Dict, checklist: Dict) -> Dict:
    """AI 약사의 분석 결과 생성"""
    trust_score = sum(c["rate"] for c in checklist.values()) / len(checklist) * 100

    if trust_score >= 70:
        trust_level = "high"
        summary = f"{product['brand']} {product['name'][:30]}...는 신뢰도 높은 제품입니다."
    elif trust_score >= 50:
        trust_level = "medium"
        summary = f"{product['brand']} {product['name'][:30]}...는 중간 수준의 신뢰도를 보입니다."
    else:
        trust_level = "low"
        summary = f"{product['brand']} {product['name'][:30]}...는 신뢰도가 낮은 편입니다."

    return {
        "trust_score": round(trust_score, 1),
        "trust_level": trust_level,
        "summary": summary,
        "efficacy": f"루테인 {product['ingredients'].get('lutein', '20mg')} 함유...",
        ...
    }
```

### 문제점
- `product['brand']`, `product['name']` 직접 접근 → KeyError
- `product['ingredients']` 직접 접근 → KeyError, AttributeError
- checklist 데이터 검증 부족

### 수정된 코드
```python
def generate_ai_analysis(product: Dict, checklist: Dict) -> Dict:
    """AI 약사의 분석 결과 생성 (안전한 방식)"""

    # 입력 검증
    if not product or not isinstance(product, dict):
        print("경고: product 데이터가 유효하지 않습니다")
        return _empty_ai_analysis()

    if not checklist or not isinstance(checklist, dict):
        print("경고: checklist 데이터가 유효하지 않습니다")
        checklist = {}

    # 체크리스트 점수 계산
    try:
        valid_rates = []
        for key, item in checklist.items():
            if isinstance(item, dict):
                rate = item.get("rate")
                if isinstance(rate, (int, float)):
                    valid_rates.append(rate)

        if valid_rates:
            trust_score = sum(valid_rates) / len(valid_rates) * 100
        else:
            trust_score = 0
    except Exception as e:
        print(f"체크리스트 계산 오류: {str(e)}")
        trust_score = 0

    # 신뢰도 등급 결정
    if trust_score >= 70:
        trust_level = "high"
    elif trust_score >= 50:
        trust_level = "medium"
    else:
        trust_level = "low"

    # 요약 생성
    brand = product.get('brand', 'Unknown').strip()
    name = (product.get('name') or product.get('title') or 'Unknown').strip()
    name_short = name[:30]

    if trust_level == "high":
        summary = f"{brand} {name_short}는 신뢰도 높은 제품입니다. 리뷰 분석 결과 인증 구매 비율이 높고, 광고성 리뷰 비율이 낮습니다."
    elif trust_level == "medium":
        summary = f"{brand} {name_short}는 중간 수준의 신뢰도를 보입니다. 일부 지표에서 개선이 필요하지만 전반적으로 무난한 제품입니다."
    else:
        summary = f"{brand} {name_short}는 신뢰도가 낮은 편입니다. 광고성 리뷰 비율이 높거나 검증된 구매 비율이 낮습니다."

    # 영양소 정보 추출
    ingredients = product.get('ingredients', {})
    if not isinstance(ingredients, dict):
        ingredients = {}

    lutein = ingredients.get('lutein', '20mg')
    zeaxanthin = ingredients.get('zeaxanthin', '4mg')

    return {
        "trust_score": round(trust_score, 1),
        "trust_level": trust_level,
        "summary": summary,
        "efficacy": f"루테인 {lutein} 함유. 눈 건강 유지 및 황반색소 밀도 개선에 도움을 줄 수 있습니다. 제아잔틴 {zeaxanthin} 추가 함유로 시너지 효과 기대.",
        "side_effects": "일반적으로 안전하나, 드물게 소화불량이나 알레르기 반응이 나타날 수 있습니다. 과량 섭취 시 피부가 노랗게 변할 수 있으니 권장량을 준수하세요.",
        "recommendations": "하루 1회, 식사와 함께 복용하면 흡수율이 높아집니다. 최소 3개월 이상 꾸준히 복용해야 효과를 체감할 수 있습니다.",
        "warnings": "임신부, 수유부는 복용 전 의사와 상담하세요. 다른 눈 건강 보조제와 중복 복용 시 과량 섭취에 주의하세요."
    }

def _empty_ai_analysis() -> Dict:
    """빈 AI 분석 결과 반환"""
    return {
        "trust_score": 0,
        "trust_level": "low",
        "summary": "분석 불가능한 제품입니다.",
        "efficacy": "정보 없음",
        "side_effects": "정보 없음",
        "recommendations": "정보 없음",
        "warnings": "정보 없음"
    }
```

### 호출 함수도 수정
```python
def get_analysis_result(product_id: str) -> Optional[Dict]:
    """특정 제품의 분석 결과 반환"""
    product = get_product_by_id(product_id)
    if not product:
        print(f"경고: 제품을 찾을 수 없습니다 - ID: {product_id}")
        return None

    reviews = get_reviews_by_product(product_id)
    checklist = generate_checklist_results(reviews)
    ai_analysis = generate_ai_analysis(product, checklist)

    return {
        "product": product,
        "reviews": reviews,
        "checklist_results": checklist,
        "ai_result": ai_analysis
    }

def get_all_analysis_results() -> Dict[str, Dict]:
    """모든 제품의 분석 결과 반환"""
    products = get_all_products()
    results = {}

    for product in products[:5]:  # 상위 5개 제품만
        try:
            product_id = product.get("id")
            if not product_id:
                print(f"경고: 제품 ID 누락")
                continue

            reviews = get_reviews_by_product(product_id)
            checklist = generate_checklist_results(reviews)
            ai_analysis = generate_ai_analysis(product, checklist)

            results[product_id] = {
                "product": product,
                "reviews": reviews,
                "checklist_results": checklist,
                "ai_result": ai_analysis
            }
        except Exception as e:
            print(f"분석 결과 생성 오류 - 제품: {product}, 오류: {str(e)}")
            continue

    return results
```

### 테스트 케이스
```python
def test_generate_ai_analysis_safety():
    """AI 분석 생성 안전성 테스트"""

    # 테스트 1: 정상 데이터
    product = {
        'brand': 'NOW Foods',
        'name': 'Lutein',
        'ingredients': {'lutein': '20mg', 'zeaxanthin': '4mg'}
    }
    checklist = {
        '1_verified_purchase': {'rate': 0.7},
        '2_reorder_rate': {'rate': 0.8}
    }
    result = generate_ai_analysis(product, checklist)
    assert result is not None
    assert 'trust_score' in result

    # 테스트 2: None product
    result = generate_ai_analysis(None, checklist)
    assert result['trust_score'] == 0

    # 테스트 3: 빈 checklist
    result = generate_ai_analysis(product, {})
    assert result['trust_score'] == 0

    # 테스트 4: 누락된 필드
    incomplete_product = {'brand': 'NOW Foods'}  # name 누락
    result = generate_ai_analysis(incomplete_product, checklist)
    assert result is not None

    # 테스트 5: 유효하지 않은 ingredients
    product_bad_ingredients = {
        'brand': 'NOW Foods',
        'name': 'Lutein',
        'ingredients': None
    }
    result = generate_ai_analysis(product_bad_ingredients, checklist)
    assert result is not None
```

---

## 요약

| 항목 | 현재 상태 | 수정 후 |
|------|---------|--------|
| app.py:792 | KeyError 위험 | 안전한 처리 |
| app.py:1457 | KeyError + StopIteration | 명확한 오류 메시지 |
| supabase_data.py:106 | 일관성 없는 .get() | 헬퍼 함수로 통일 |
| supabase_data.py:403 | 직접 접근으로 KeyError | 검증과 기본값 추가 |

---

## 다음 단계

1. ✅ 위의 4개 항목을 우선 수정
2. ⏳ 다른 MEDIUM 우선순위 아이템 수정
3. ⏳ 전체 통합 테스트 실행
4. ⏳ 개발일지 작성

