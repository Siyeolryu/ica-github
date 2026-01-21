# Streamlit Cloud ImportError 수정

**작업일**: 2026-01-21
**작업명**: Streamlit Cloud 배포 ImportError 해결

## 작업 개요

Streamlit Cloud에 배포된 앱에서 `ImportError`가 발생하여 앱이 실행되지 않는 문제를 해결했습니다. `app.py`에서 import하려는 함수들이 `utils.py`에 정의되어 있지 않아 발생한 문제였습니다.

## 에러 메시지

```
ImportError: This app has encountered an error.
File "/mount/src/ica-github/dev2-2Hour/dev2-main/ui_integration/app.py", line 33, in <module>
    from utils import safe_get_product_label, safe_find_item, safe_parse_value
```

## 주요 작업 내용

### 1. 문제 분석

**파일**: `ica-github/dev2-2Hour/dev2-main/ui_integration/utils.py`

- `app.py`의 33번째 줄에서 다음 함수들을 import 시도:
  - `safe_get_product_label`
  - `safe_find_item`
  - `safe_parse_value`

- 하지만 `utils.py`에는 이 함수들이 정의되어 있지 않음

### 2. 함수 사용 패턴 분석

**app.py에서의 사용 패턴**:

```python
# Line 1461: DataFrame 정렬 시 값 파싱
comparison_df["_sort_key"] = comparison_df[sort_column].apply(safe_parse_value)

# Line 1482-1485: 신뢰도 값 안전하게 추출
trust_val = safe_parse_value(row.get("신뢰도", 0))
trust_val = safe_parse_value(row.loc["신뢰도"])
```

### 3. 함수 구현

**파일**: `ica-github/dev2-2Hour/dev2-main/ui_integration/utils.py`

#### `safe_parse_value(value: Any) -> float`
DataFrame 값을 안전하게 숫자로 파싱하는 함수

**기능**:
- None, 숫자, 문자열 등 다양한 타입 처리
- 특수 문자 제거 ($, %, 쉼표, "점" 등)
- 파싱 실패 시 0.0 반환

```python
def safe_parse_value(value: Any) -> float:
    try:
        if value is None:
            return 0.0
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            cleaned = value.strip().replace('$', '').replace('%', '').replace(',', '').replace('점', '')
            if not cleaned:
                return 0.0
            return float(cleaned)
        return float(str(value))
    except (ValueError, TypeError, AttributeError):
        return 0.0
```

#### `safe_get_product_label(product: Dict[str, Any]) -> str`
제품 데이터에서 안전하게 라벨 문자열 생성

**기능**:
- 제품 딕셔너리에서 브랜드와 이름 추출
- "{브랜드} {제품명}" 형태로 반환
- 실패 시 "Unknown Product" 반환

```python
def safe_get_product_label(product: Dict[str, Any]) -> str:
    try:
        if not product or not isinstance(product, dict):
            return "Unknown Product"
        brand = product.get('brand', '')
        name = product.get('name', '')
        if not brand and not name:
            return "Unknown Product"
        if brand and not name:
            return str(brand)
        if not brand and name:
            return str(name)
        return f"{brand} {name}"
    except (KeyError, TypeError, AttributeError):
        return "Unknown Product"
```

#### `safe_find_item(items: list, key: str, value: Any) -> Optional[Dict[str, Any]]`
리스트에서 특정 키-값을 가진 아이템을 안전하게 검색

**기능**:
- 딕셔너리 리스트에서 특정 조건에 맞는 아이템 찾기
- 타입 검증 및 예외 처리
- 찾지 못하면 None 반환

```python
def safe_find_item(items: list, key: str, value: Any) -> Optional[Dict[str, Any]]:
    try:
        if not items or not isinstance(items, list):
            return None
        for item in items:
            if isinstance(item, dict) and item.get(key) == value:
                return item
        return None
    except (KeyError, TypeError, AttributeError):
        return None
```

## 기술 스택 및 의존성

- **Python 3.x**: 타입 힌트 (typing.Optional, Any, Dict)
- **기존 의존성**: 추가 패키지 설치 불필요

## 테스트 결과

### 1. Import 테스트

```bash
$ python -c "from utils import safe_get_product_label, safe_find_item, safe_parse_value; print('Import success!')"
Import success!
```

### 2. 함수 동작 테스트

```python
# safe_parse_value 테스트
safe_parse_value("100.5")  # 결과: 100.5
safe_parse_value("$1,234.56")  # 결과: 1234.56
safe_parse_value(None)  # 결과: 0.0

# safe_get_product_label 테스트
safe_get_product_label({"brand": "Test", "name": "Product"})  # 결과: "Test Product"
safe_get_product_label({})  # 결과: "Unknown Product"
```

### 3. Python 구문 검증

```bash
$ python -m py_compile app.py
$ python -m py_compile utils.py
Python syntax validation: PASS
```

## Git 커밋 및 배포

### 커밋 정보

```bash
[main def7337] Fix ImportError: Add missing safe helper functions to utils.py
 1 file changed, 101 insertions(+), 4 deletions(-)
```

### 푸시 완료

```bash
To https://github.com/Siyeolryu/ica-github.git
   b70b76c..def7337  main -> main
```

### Streamlit Cloud 배포

- **배포 저장소**: https://github.com/Siyeolryu/ica-github
- **앱 경로**: `dev2-2Hour/dev2-main/ui_integration/app.py`
- **자동 재배포**: Git push 후 Streamlit Cloud에서 자동으로 재배포 시작
- **예상 결과**: ImportError 해결, 앱 정상 실행

## 트러블슈팅

### 문제 1: 함수 미정의 ImportError

**증상**: Streamlit Cloud에서 `ImportError` 발생

**원인**: `app.py`에서 import하는 함수들이 `utils.py`에 정의되지 않음

**해결**:
1. `app.py`에서 함수 사용 패턴 분석
2. 필요한 3개 함수 구현 (`safe_parse_value`, `safe_get_product_label`, `safe_find_item`)
3. 타입 힌트 및 예외 처리 포함
4. 로컬 테스트 통과 확인
5. Git 커밋 및 푸시

### 문제 2: DataFrame 정렬 시 타입 오류

**증상**: DataFrame 정렬 시 문자열/숫자 혼용으로 인한 오류 가능성

**해결**: `safe_parse_value` 함수에서 다양한 타입 처리
- 숫자, 문자열, None 모두 처리
- 특수 문자 ($, %, 쉼표) 자동 제거
- 파싱 실패 시 0.0 반환으로 안전성 확보

## 배운 점

### 1. Streamlit Cloud 배포 시 주의사항

- 로컬 개발 환경에서는 import 오류가 없어도, 클라우드 환경에서 발생할 수 있음
- 모든 import는 실제 파일에 정의되어 있어야 함
- 배포 전 `python -m py_compile` 로 구문 검증 필수

### 2. 안전한 함수 설계 패턴

- 타입 힌트를 명확히 지정
- 다양한 예외 상황 처리 (None, 잘못된 타입, KeyError 등)
- 기본값 반환으로 앱 크래시 방지
- 사용자 친화적인 에러 메시지

### 3. Git 서브모듈 작업

- 서브모듈 내 파일 수정 시 해당 디렉토리에서 직접 commit/push
- 메인 프로젝트와 서브모듈의 Git 히스토리 분리 관리

## 다음 단계

1. **Streamlit Cloud 모니터링**: 재배포 완료 후 앱 정상 동작 확인
2. **에러 로그 확인**: 추가 ImportError 또는 런타임 오류 없는지 체크
3. **기능 테스트**: 테이블 정렬, 필터링 등 주요 기능 동작 확인
4. **성능 최적화**: 캐싱 적용 여부 및 로딩 속도 개선

## 체크리스트

- [x] 문제 분석 완료
- [x] 함수 구현 완료
- [x] 로컬 테스트 통과
- [x] Python 구문 검증 통과
- [x] Git 커밋 및 푸시 완료
- [ ] Streamlit Cloud 재배포 확인 (자동 진행 중)
- [ ] 앱 정상 동작 확인

---

**참고 파일**:
- `ica-github/dev2-2Hour/dev2-main/ui_integration/app.py`
- `ica-github/dev2-2Hour/dev2-main/ui_integration/utils.py`

**관련 커밋**: def7337
