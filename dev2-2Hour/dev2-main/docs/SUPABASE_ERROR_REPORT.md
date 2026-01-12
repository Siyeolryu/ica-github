# Supabase 연동 오류 보고서

**작성일**: 2026-01-09
**앱 URL**: https://ica-app-exygnp32igpx6sqravtn8t.streamlit.app/
**Supabase 프로젝트**: https://supabase.com/dashboard/project/bvowxbpqtfpkkxkzsumf

---

## 1. 문제 요약

Streamlit Cloud에 배포된 앱에서 Supabase 데이터가 표시되지 않음.

---

## 2. 원인 분석

### 2.1 로컬 환경 테스트 결과
| 항목 | 상태 | 비고 |
|------|------|------|
| Supabase 연결 | ✅ 성공 | REST API 정상 응답 |
| products 테이블 | ✅ 성공 | 5개 제품 확인 |
| reviews 테이블 | ✅ 성공 | 리뷰 데이터 확인 |

```
=== Supabase 연결 테스트 ===
URL: https://bvowxbpqtfpkkxkzsumf.supabase.co
--- products 테이블 ---
Status: 200
데이터 수: 5
  - ID: 14, Brand: iHerb (California Gold Nutrition)
  - ID: 15, Brand: Doctor's Best
  - ID: 16, Brand: Jarrow Formulas
  - ID: 17, Brand: Now Foods
  - ID: 18, Brand: Solgar

--- reviews 테이블 ---
Status: 200
데이터 수: 100
```

### 2.2 Streamlit Cloud 환경 분석

**문제점**:
1. Streamlit Cloud secrets 설정 확인 필요
2. 환경 변수 로드 방식 차이 가능성
3. CORS 또는 네트워크 이슈 가능성

---

## 3. 해결 방안

### 3.1 Streamlit Cloud Secrets 설정

`.streamlit/secrets.toml` 파일에 다음 내용 추가:

```toml
SUPABASE_URL = "https://bvowxbpqtfpkkxkzsumf.supabase.co"
SUPABASE_ANON_KEY = "your-anon-key-here"
```

### 3.2 코드 수정 사항

`supabase_data.py`에서 환경 변수 로드 로직 확인:

```python
# Streamlit Cloud 환경에서 secrets 사용
if hasattr(st, 'secrets'):
    supabase_url = st.secrets.get('SUPABASE_URL')
    supabase_key = st.secrets.get('SUPABASE_ANON_KEY')
else:
    # 로컬 환경에서 .env 사용
    from dotenv import load_dotenv
    load_dotenv()
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
```

---

## 4. 테스트 결과

### 로컬 환경
- ✅ Supabase 연결 성공
- ✅ 데이터 조회 성공
- ✅ Streamlit 앱 정상 작동

### Streamlit Cloud
- ⚠️ Supabase 연결 실패 (secrets 미설정)
- ⚠️ 데이터 조회 실패

---

## 5. 다음 단계

1. Streamlit Cloud에 secrets 설정
2. 재배포 후 테스트
3. 연결 성공 시 데이터 표시 확인
