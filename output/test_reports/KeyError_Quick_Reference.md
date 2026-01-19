# KeyError 위험도 분석 - 빠른 참조 가이드

**작성일**: 2026-01-19 | **버전**: 1.0

---

## 한눈에 보기

### 위험 지점 분포

```
파일명                    | 위험 개수 | 우선순위 | 상태
------------------------+-----------|----------|-------
app.py                  |    13개   |  HIGH   | 🔴 긴급
supabase_data.py        |     6개   |  HIGH   | 🔴 긴급
visualizations.py       |     3개   |  MEDIUM | 🟠 우선
chart_analyzer.py       |     1개   |  LOW    | 🟡 보완
API routes (*.py)       |     2개   |  MEDIUM | 🟠 우선
------------------------+-----------|----------|-------
total                   |    23개   |         |
```

---

## 즉시 조치 4개 항목

### ✅ 1. app.py:792 - product_options

```python
# ❌ 위험
product_options = {f"{v['product']['brand']} {v['product']['name']}": k for k, v in all_data.items()}

# ✅ 수정
product_options = {}
for k, v in all_data.items():
    product = v.get('product', {})
    if product and isinstance(product, dict):
        brand = product.get('brand', 'Unknown')
        name = product.get('name', 'Unknown')
        if brand and name:
            product_options[f"{brand} {name}"] = k
```

**위험 요소**: KeyError (product, brand, name)

---

### ✅ 2. app.py:1457 - target_data

```python
# ❌ 위험
target_data = next(d for d in selected_data if f"{d['product']['brand']} {d['product']['name']}" == target_label)

# ✅ 수정
target_data = None
for d in selected_data:
    product = d.get('product', {})
    if f"{product.get('brand', '')} {product.get('name', '')}" == target_label:
        target_data = d
        break

if not target_data:
    st.error(f"선택한 제품 '{target_label}'을 찾을 수 없습니다.")
    return
```

**위험 요소**: KeyError + StopIteration

---

### ✅ 3. supabase_data.py:106 - product 포맷팅

```python
# ❌ 위험
"id": str(p['id']),  # KeyError 가능

# ✅ 수정
"id": str(p.get('id', 'unknown')),

# 또는 더 강력한 방식:
def _format_product(p):
    if not p or not isinstance(p, dict) or p.get('id') is None:
        return None
    # ... 포맷팅
```

**위험 요소**: KeyError (id)

---

### ✅ 4. supabase_data.py:403 - ai_analysis

```python
# ❌ 위험
summary = f"{product['brand']} {product['name'][:30]}..."
"efficacy": f"루테인 {product['ingredients'].get('lutein', '20mg')} ..."

# ✅ 수정
brand = product.get('brand', 'Unknown')
name = (product.get('name') or 'Unknown')[:30]
ingredients = product.get('ingredients', {})
if isinstance(ingredients, dict):
    lutein = ingredients.get('lutein', '20mg')
else:
    lutein = '20mg'

summary = f"{brand} {name}..."
"efficacy": f"루테인 {lutein}..."
```

**위험 요소**: KeyError + AttributeError

---

## 패턴별 빠른 수정법

### Pattern 1: 체인 .get() 호출
```python
# ❌ 위험
value = data.get('a', {}).get('b').get('c')

# ✅ 수정
a = data.get('a') or {}
b = a.get('b') or {}
c = b.get('c')
```

### Pattern 2: 직접 인덱싱
```python
# ❌ 위험
value = data['key']

# ✅ 수정
value = data.get('key', default_value)
```

### Pattern 3: 리스트 접근
```python
# ❌ 위험
first = data[0]

# ✅ 수정
first = data[0] if data and len(data) > 0 else None
# 또는
first = next(iter(data), None)
```

### Pattern 4: 함수 결과 사용
```python
# ❌ 위험
for item in func_returning_list():
    pass

# ✅ 수정
result = func_returning_list() or []
if isinstance(result, list):
    for item in result:
        pass
```

---

## 테스트 확인 리스트

### Unit Tests
- [ ] 빈 딕셔너리 입력 처리
- [ ] None 값 처리
- [ ] 누락된 키 처리
- [ ] 잘못된 타입 처리
- [ ] 대문자/소문자 불일치 처리

### Integration Tests
- [ ] Supabase 응답 형식 검증
- [ ] API 응답 형식 검증
- [ ] 전체 데이터 흐름 확인
- [ ] 에러 메시지 검증

### Regression Tests
- [ ] 기존 기능 동작 확인
- [ ] 성능 저하 없음 확인
- [ ] 메모리 누수 없음 확인

---

## 디버깅 팁

### 1. KeyError 디버그
```python
try:
    value = data[key]
except KeyError:
    print(f"Missing key: {key}")
    print(f"Available keys: {list(data.keys())}")
    print(f"Data type: {type(data)}")
    print(f"Data: {data}")

# 또는 더 안전하게
value = data.get(key)
if value is None:
    logging.warning(f"Key '{key}' not found in data: {data}")
```

### 2. None 값 디버그
```python
value = obj.get('key')
if value is None:
    print(f"Null value for key in {type(obj)}")
else:
    print(f"Type of value: {type(value)}")
```

### 3. 타입 확인
```python
def safe_get(obj, key, expected_type=None):
    value = obj.get(key) if isinstance(obj, dict) else None
    if expected_type and value is not None:
        if not isinstance(value, expected_type):
            print(f"Type mismatch: expected {expected_type}, got {type(value)}")
            return None
    return value
```

---

## 도구 및 리소스

### 정적 분석 도구
```bash
# 1. mypy - 타입 검사
pip install mypy
mypy ui_integration/

# 2. pylint - 코드 품질
pip install pylint
pylint ui_integration/

# 3. flake8 - 스타일 검사
pip install flake8
flake8 ui_integration/
```

### 테스트 도구
```bash
# pytest 실행
pytest ui_integration/tests/ -v

# 커버리지 확인
pytest ui_integration/tests/ --cov=ui_integration
```

---

## 작업 체크리스트

### Day 1-2 (Phase 1)
```
[ ] app.py:792 수정 및 테스트
[ ] app.py:1457 수정 및 테스트
[ ] supabase_data.py:106 수정 및 테스트
[ ] supabase_data.py:403 수정 및 테스트
[ ] 통합 테스트 실행
[ ] 코드 리뷰
```

### Day 3-5 (Phase 2)
```
[ ] app.py 나머지 8개 위험 수정
[ ] supabase_data.py 나머지 2개 위험 수정
[ ] visualizations.py 3개 위험 수정
[ ] API routes 2개 위험 수정
[ ] 회귀 테스트
[ ] 성능 테스트
```

### Day 6-7 (Phase 3)
```
[ ] 타입 힌팅 추가
[ ] 글로벌 검증 함수 추가
[ ] CI/CD 파이프라인 강화
[ ] 최종 테스트
[ ] 배포 준비
```

---

## FAQ

### Q: KeyError와 AttributeError의 차이?
A:
- **KeyError**: 딕셔너리 키가 없을 때 (예: `d['missing_key']`)
- **AttributeError**: 객체 속성이 없을 때 (예: `None.method()`)

### Q: .get()은 항상 안전한가?
A:
- 기본적으로는 안전하지만, 체인 호출에서 None을 반환할 수 있음
- 항상 None 체크 필요

### Q: 성능에 영향이 있나?
A:
- 미미함 (< 1ms 차이)
- 예외 처리의 오버헤드가 미미함
- 조기 반환으로 오히려 성능 개선 가능

### Q: 어디서 시작해야 하나?
A:
1. 즉시 4개 항목 수정
2. 단위 테스트 작성
3. 통합 테스트 실행
4. 코드 리뷰

### Q: 전체 완료까지 얼마나 걸리나?
A:
- Phase 1 (긴급): 8-10시간
- Phase 2 (단기): 10-15시간
- Phase 3 (중기): 15-20시간
- **총계**: 40-50시간

---

## 연락처

### 담당자
- **개발**: Frontend & Backend Developer
- **테스트**: Test Runner
- **코드 리뷰**: Code Reviewer

### 문서
- 상세 분석: `KeyError_Analysis_Report.md`
- 수정 샘플: `KeyError_Fix_Examples.md`
- 임원 요약: `KeyError_Executive_Summary.md`

---

## 버전 히스토리

| 버전 | 날짜 | 변경사항 |
|------|------|---------|
| 1.0 | 2026-01-19 | 초기 작성 |
| | | |

---

**마지막 업데이트**: 2026-01-19
**상태**: ✅ 검토 필요
**우선순위**: 🔴 CRITICAL

