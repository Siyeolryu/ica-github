# Streamlit IndentationError 발생 보고서

**작성일**: 2026-01-12  
**작성자**: 개발팀  
**오류 유형**: Python IndentationError  
**영향 범위**: Streamlit Cloud 배포 실패

---

## 📋 개요

Streamlit Cloud에 배포된 애플리케이션에서 `IndentationError`가 발생하여 앱 실행이 완전히 중단되었습니다. 오류는 `ui_integration/app.py` 파일의 여러 위치에서 발생했습니다.

---

## 🐛 발생한 오류

### 오류 메시지
```
IndentationError: expected an indented block after 'with' statement on line 138
File: /mount/src/ica-github/dev2-2Hour/dev2-main/ui_integration/app.py
Line: 139
```

### 오류 발생 위치

1. **138-139번째 줄**: `with st.sidebar:` 블록
   ```python
   with st.sidebar:
   st.markdown("### 🔎 제품 검색")  # ❌ 들여쓰기 없음
   ```

2. **181번째 줄**: `try:` 문 잘못된 들여쓰기
   ```python
   # 검색 처리
   try:  # ❌ 잘못된 들여쓰기 레벨
   ```

3. **228번째 줄**: `for` 문 잘못된 들여쓰기
   ```python
   cols = st.columns(3)
   
   for idx, data in enumerate(top3_products):  # ❌ 잘못된 들여쓰기 레벨
   ```

---

## 🔍 문제 발생 요인

### 1. 파일 정리 과정에서 발생한 들여쓰기 손실

**원인 분석**:
- GitHub 저장소 파일 정리 작업 중 `app.py` 파일이 이동되거나 수정됨
- 파일 편집 과정에서 들여쓰기가 일부 손실됨
- 특히 `with` 문 블록 내부의 들여쓰기가 제대로 유지되지 않음

**구체적 원인**:
1. **138번째 줄**: `with st.sidebar:` 문 다음에 들여쓰기된 코드 블록이 없음
   - Python은 `with` 문 다음에 반드시 들여쓰기된 코드가 필요함
   - 139번째 줄 `st.markdown()`이 `with` 블록 밖에 위치함

2. **181번째 줄**: `try:` 문이 잘못된 들여쓰기 레벨에 위치
   - `with st.sidebar:` 블록이 제대로 닫히지 않은 상태에서 `try:` 문이 시작됨
   - 이로 인해 코드 구조가 깨짐

3. **228번째 줄**: `for` 문이 잘못된 들여쓰기 레벨에 위치
   - 앞선 들여쓰기 오류로 인해 전체 코드 구조가 영향을 받음

### 2. 코드 편집 도구의 들여쓰기 처리 문제

**가능한 원인**:
- 여러 파일을 한 번에 정리하는 과정에서 자동 포맷팅이 제대로 적용되지 않음
- 탭과 스페이스가 혼용되어 일부 에디터에서 들여쓰기가 깨짐
- 파일 복사/이동 과정에서 들여쓰기 정보 손실

### 3. 배포 전 검증 부족

**문제점**:
- 로컬에서 문법 검사를 실행하지 않음
- Streamlit Cloud 배포 전 코드 검증 단계 누락
- CI/CD 파이프라인에 문법 검사 단계가 없음

---

## 🔄 이전과 다른 점

### 이전 상태 (정상 작동)
- `app.py` 파일이 올바른 들여쓰기로 작성되어 있었음
- Streamlit Cloud에서 정상적으로 배포 및 실행됨
- 모든 `with` 블록이 올바르게 들여쓰기되어 있음

### 현재 상태 (오류 발생)
- **파일 위치 변경**: 저장소 정리 과정에서 파일이 이동됨
- **들여쓰기 손실**: 여러 위치에서 들여쓰기가 깨짐
- **코드 구조 파괴**: `with` 블록이 제대로 닫히지 않음
- **배포 실패**: Streamlit Cloud에서 앱 실행 불가

### 주요 차이점

| 항목 | 이전 | 현재 |
|------|------|------|
| 들여쓰기 일관성 | ✅ 정상 | ❌ 깨짐 |
| `with` 블록 구조 | ✅ 올바름 | ❌ 손상됨 |
| 배포 상태 | ✅ 성공 | ❌ 실패 |
| 코드 검증 | ⚠️ 수동 | ❌ 없음 |

---

## ✅ 개선책

### 1. 즉시 수정 사항

#### 1.1 `with st.sidebar:` 블록 수정
```python
# 수정 전 (138-171줄)
with st.sidebar:
st.markdown("### 🔎 제품 검색")  # ❌ 들여쓰기 없음

# 수정 후
with st.sidebar:
    st.markdown("### 🔎 제품 검색")  # ✅ 4칸 들여쓰기
    
    search_query_raw = st.text_input(
        "제품명 또는 브랜드 검색",
        placeholder="예: NOW Foods, Lutein...",
        key="search"
    )
    
    # 사용자 입력 검증 및 이스케이프
    search_query = sanitize_user_input(search_query_raw) if search_query_raw else ""
    
    st.markdown("---")
    
    st.markdown("### ℹ️ 신뢰도 등급 안내")
    st.markdown("""
    - **HIGH (70점 이상)**: 신뢰할 수 있는 제품
    - **MEDIUM (50-70점)**: 보통 수준
    - **LOW (50점 미만)**: 주의 필요
    """)
    
    st.markdown("---")
    
    st.markdown("### 📊 분석 기준")
    st.markdown("""
    1. 인증 구매 비율
    2. 재구매율
    3. 장기 사용 비율
    4. 평점 분포 적절성
    5. 리뷰 길이
    6. 시간 분포 자연성
    7. 광고성 리뷰 탐지
    8. 리뷰어 다양성
    """)
```

#### 1.2 `try:` 블록 수정
```python
# 수정 전 (180-198줄)
# 검색 처리
try:  # ❌ 잘못된 들여쓰기
    if search_query:
        ...

# 수정 후
# 검색 처리
try:
    if search_query:
        filtered_products = search_products(search_query)
        products_data = []
        
        for p in filtered_products:
            product_id = p.get("id")
            if product_id and product_id in all_analysis:
                products_data.append(all_analysis[product_id])
        
        if not products_data:
            st.warning(f"'{search_query}'에 대한 검색 결과가 없습니다.")
            return
    else:
        products_data = list(all_analysis.values())
except Exception as e:
    st.error(f"검색 처리 중 오류 발생: {str(e)}")
    products_data = list(all_analysis.values())
```

#### 1.3 `for` 문 수정
```python
# 수정 전 (228줄)
cols = st.columns(3)

for idx, data in enumerate(top3_products):  # ❌ 잘못된 들여쓰기

# 수정 후
cols = st.columns(3)

for idx, data in enumerate(top3_products):  # ✅ 올바른 들여쓰기
    try:
        product = data.get("product", {})
        ...
```

### 2. 코드 품질 관리 개선

#### 2.1 배포 전 검증 스크립트 추가
```bash
#!/bin/bash
# scripts/validate_before_deploy.sh

echo "🔍 Python 문법 검사 중..."
python -m py_compile ui_integration/app.py
if [ $? -ne 0 ]; then
    echo "❌ 문법 오류 발견!"
    exit 1
fi

echo "✅ 문법 검사 통과"
echo "🔍 들여쓰기 검사 중..."
python -m flake8 ui_integration/app.py --select=E,W --max-line-length=120
if [ $? -ne 0 ]; then
    echo "⚠️  코드 스타일 경고 발견 (계속 진행)"
fi

echo "✅ 검증 완료"
```

#### 2.2 자동 코드 포맷팅 적용
```bash
# Black 포맷터 사용
black ui_integration/app.py

# 또는 autopep8
autopep8 --in-place --aggressive --aggressive ui_integration/app.py
```

#### 2.3 Git Pre-commit Hook 설정
```bash
# .git/hooks/pre-commit
#!/bin/bash
python -m py_compile ui_integration/app.py
if [ $? -ne 0 ]; then
    echo "❌ 커밋 전 문법 검사 실패!"
    exit 1
fi
```

### 3. 개발 프로세스 개선

#### 3.1 코드 리뷰 체크리스트
- [ ] Python 문법 검사 통과
- [ ] 들여쓰기 일관성 확인 (4칸 공백)
- [ ] `with` 블록 구조 검증
- [ ] 로컬에서 Streamlit 실행 테스트
- [ ] 배포 전 최종 검증

#### 3.2 CI/CD 파이프라인 강화
```yaml
# .github/workflows/validate.yml
name: Code Validation
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Python 문법 검사
        run: python -m py_compile ui_integration/app.py
      - name: 코드 스타일 검사
        run: |
          pip install flake8
          flake8 ui_integration/app.py --select=E,W
```

### 4. 문서화 개선

#### 4.1 개발 가이드 작성
- Python 들여쓰기 규칙 명시
- 코드 포맷팅 표준 정의
- 배포 전 체크리스트 문서화

#### 4.2 에러 대응 매뉴얼
- 일반적인 IndentationError 해결 방법
- Streamlit Cloud 배포 문제 해결 가이드
- 코드 검증 도구 사용법

---

## 🧪 수정 후 검증 방법

### 1. 로컬 검증
```bash
# 문법 검사
python -m py_compile ui_integration/app.py

# Streamlit 실행 테스트
cd ui_integration
streamlit run app.py
```

### 2. 배포 전 최종 확인
- [ ] Python 문법 검사 통과
- [ ] 로컬에서 앱 정상 실행 확인
- [ ] 모든 기능 동작 확인
- [ ] 에러 메시지 없음 확인

### 3. 배포 후 모니터링
- Streamlit Cloud 로그 확인
- 사용자 접근 테스트
- 에러 발생 시 즉시 롤백

---

## 📊 예상 효과

### 즉시 효과
- ✅ Streamlit Cloud 배포 성공
- ✅ 앱 정상 실행
- ✅ 사용자 접근 가능

### 장기 효과
- ✅ 코드 품질 향상
- ✅ 배포 실패율 감소
- ✅ 개발 생산성 향상
- ✅ 유지보수 용이성 증가

---

## 📝 결론

이번 IndentationError는 파일 정리 과정에서 들여쓰기가 손실되어 발생한 문제였습니다. Python의 기본 문법 규칙을 준수하지 않아 발생했으며, 특히 `with` 문 블록의 들여쓰기가 누락된 것이 주요 원인이었습니다.

**즉시 조치**:
1. `app.py` 파일의 들여쓰기 수정
2. 배포 전 문법 검사 실행
3. Streamlit Cloud 재배포

**장기 개선**:
1. 자동 코드 검증 도구 도입
2. CI/CD 파이프라인 강화
3. 개발 프로세스 표준화

---

**보고서 작성 시간**: 2026-01-12  
**다음 조치**: 코드 수정 및 재배포
