# UI KeyError 점검 보고서

**작성일**: 2026-01-19
**작업자**: Claude (test-runner agent)
**작업 유형**: 코드 품질 점검 / 버그 분석

---

## 1. 작업 개요

ui_integration 폴더의 모든 Python 파일에서 발생할 수 있는 KeyError 위험 지점을 분석하고, 수정 방안을 제시하는 점검 작업을 수행했습니다.

---

## 2. 분석 결과 요약

| 항목 | 수치 |
|------|------|
| **검사한 Python 파일** | 5개 |
| **발견된 KeyError 위험** | 23개 |
| **HIGH 우선순위** | 8개 |
| **MEDIUM 우선순위** | 10개 |
| **LOW 우선순위** | 5개 |

### 파일별 위험도

| 파일 | 위험 수 | 비율 |
|------|---------|------|
| app.py | 13개 | 56.5% |
| supabase_data.py | 6개 | 26.1% |
| visualizations.py | 3개 | 13.0% |
| chart_analyzer.py | 1개 | 4.4% |
| utils.py | 0개 | 0% (안전) |

---

## 3. 주요 문제점 (HIGH 우선순위)

### 3.1 app.py:792 - product_options 생성

**현재 코드 (위험)**:
```python
product_options = {f"{v['product']['brand']} {v['product']['name']}": k for k, v in all_data.items()}
```

**문제점**:
- `v['product']`가 None이거나 키가 없을 경우 KeyError 발생
- `brand` 또는 `name` 키가 없을 경우 충돌

**권장 수정**:
```python
product_options = {}
for k, v in all_data.items():
    product = v.get('product', {})
    if product and isinstance(product, dict):
        brand = product.get('brand', 'Unknown')
        name = product.get('name', 'Unknown')
        if brand and name:
            product_options[f"{brand} {name}"] = k
```

---

### 3.2 app.py:1457 - target_data 검색

**현재 코드 (위험)**:
```python
target_data = next(d for d in selected_data if f"{d['product']['brand']} {d['product']['name']}" == target_label)
```

**문제점**:
- `next()`가 일치하는 항목을 찾지 못하면 `StopIteration` 예외 발생
- 직접 dictionary 접근으로 KeyError 가능

**권장 수정**:
```python
target_data = None
for d in selected_data:
    product = d.get('product', {})
    if f"{product.get('brand', '')} {product.get('name', '')}" == target_label:
        target_data = d
        break

if target_data is None:
    st.error("선택한 제품을 찾을 수 없습니다.")
    return
```

---

### 3.3 supabase_data.py:106 - 직접 인덱싱

**현재 코드 (위험)**:
```python
"id": str(p['id']),
```

**권장 수정**:
```python
"id": str(p.get('id', 'unknown')),
```

---

### 3.4 supabase_data.py:403 - 제품 정보 접근

**현재 코드 (위험)**:
```python
summary = f"{product['brand']} {product['name'][:30]}..."
```

**문제점**:
- `product['brand']`, `product['name']` 직접 접근
- `name`이 None일 경우 슬라이싱 불가

**권장 수정**:
```python
brand = product.get('brand', 'Unknown')
name = (product.get('name') or 'Unknown')[:30]
summary = f"{brand} {name}..."
```

---

## 4. MEDIUM 우선순위 문제점

| 위치 | 문제 | 해결방안 |
|------|------|----------|
| app.py:1045 | session_state 키 접근 | `.get()` 사용 |
| app.py:1128 | 분석 결과 중첩 접근 | 안전한 체이닝 |
| app.py:1299 | 차트 데이터 접근 | 타입 검증 추가 |
| app.py:1544-1546 | 체크리스트 중첩 .get() | 기본값 처리 |
| visualizations.py:35 | 레이더 차트 데이터 | 구조 검증 |
| visualizations.py:59 | 가격 비교 차트 | 안전한 접근 |

---

## 5. 공통 패턴별 수정 가이드

### 패턴 1: Dictionary 직접 접근
```python
# 위험
value = data['key']

# 안전
value = data.get('key', default_value)
```

### 패턴 2: 중첩 Dictionary 접근
```python
# 위험
value = data['outer']['inner']

# 안전
outer = data.get('outer', {})
value = outer.get('inner', default_value)
```

### 패턴 3: next() 사용
```python
# 위험
item = next(x for x in items if condition)

# 안전
item = next((x for x in items if condition), None)
if item is None:
    # 에러 처리
```

---

## 6. 영향도 분석

| 항목 | 평가 |
|------|------|
| 프로덕션 배포 가능성 | ❌ 위험 (HIGH) |
| 데이터 무결성 | ⚠️ 중간 위험 |
| 사용자 경험 | ⚠️ 중간 위험 (간헐적 충돌) |
| 시스템 안정성 | ⚠️ 중간 위험 |

---

## 7. 수정 우선순위 및 계획

| Phase | 항목 | 예상 소요시간 | 우선순위 |
|-------|------|---------------|----------|
| Phase 1 | HIGH 4개 | 8-10시간 | 🔴 긴급 |
| Phase 2 | MEDIUM 10개 | 10-15시간 | 🟠 1주일 내 |
| Phase 3 | 타입 힌팅 추가 | 15-20시간 | 🟡 2주일 내 |

---

## 8. 생성된 상세 보고서

```
output/test_reports/
├── KeyError_Analysis_Report.md      (814줄, 상세 분석)
├── KeyError_Executive_Summary.md    (372줄, 임원 요약)
├── KeyError_Fix_Examples.md         (572줄, 수정 샘플)
└── KeyError_Quick_Reference.md      (346줄, 빠른 참조)
```

---

## 9. 권고사항

### 즉시 조치 필요
1. **app.py:792** - product_options 생성 로직 수정
2. **app.py:1457** - target_data 검색 로직 수정
3. **supabase_data.py:106** - 직접 인덱싱 제거
4. **supabase_data.py:403** - 안전한 문자열 생성

### 코딩 가이드라인 추가
- 모든 dictionary 접근에 `.get()` 사용 의무화
- `next()` 사용 시 반드시 기본값 지정
- API 응답 파싱 시 스키마 검증 추가

---

## 10. 다음 단계

1. [ ] Phase 1 HIGH 우선순위 4개 항목 즉시 수정
2. [ ] 수정 후 단위 테스트 작성
3. [ ] Phase 2 MEDIUM 우선순위 항목 수정
4. [ ] 타입 힌팅 및 정적 분석 도입 검토
5. [ ] CI/CD 파이프라인에 정적 분석 추가

---

## 11. 참고 자료

- 상세 분석: `output/test_reports/KeyError_Analysis_Report.md`
- 수정 샘플: `output/test_reports/KeyError_Fix_Examples.md`
- 빠른 참조: `output/test_reports/KeyError_Quick_Reference.md`

---

**최종 평가**: 🔴 **HIGH RISK** - 프로덕션 배포 전 즉시 수정 필요
