# Supabase 연동 가이드

GitHub 저장소와 Supabase 데이터베이스를 연동하는 방법을 안내합니다.

## 1. Supabase 프로젝트 정보

- **프로젝트 URL**: `https://bvowxbpqtfpkkxkzsumf.supabase.co`
- **GitHub 저장소**: [https://github.com/tturupapa-stack/dev2](https://github.com/tturupapa-stack/dev2)

## 2. 환경 변수 설정

### 2.1 .env 파일 생성

프로젝트 루트 디렉토리에 `.env` 파일을 생성하세요:

```bash
# Windows
type nul > .env

# Linux/Mac
touch .env
```

### 2.2 환경 변수 입력

`.env` 파일에 다음 내용을 입력하세요:

```env
# Anthropic Claude API
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Supabase 설정
SUPABASE_URL=https://bvowxbpqtfpkkxkzsumf.supabase.co
SUPABASE_ANON_KEY=sb_publishable_afWmzo_2ypv3liBdpCkJjg_KjS7nqE2
SUPABASE_SERVICE_ROLE_KEY=sb_secret_7colYDry0-0E76v-yrpzFA_ab48cpbo
```

**⚠️ 중요:** 실제 키 값은 Supabase Dashboard에서 확인하세요.

### 2.3 Supabase 키 확인 방법

1. [Supabase Dashboard](https://supabase.com/dashboard) 접속
2. 프로젝트 선택
3. **Settings** → **API** 메뉴로 이동
4. 다음 정보 확인:
   - **Project URL**: `SUPABASE_URL`에 입력
   - **anon/public key**: `SUPABASE_ANON_KEY`에 입력 (클라이언트용)
   - **service_role key**: `SUPABASE_SERVICE_ROLE_KEY`에 입력 (서버/관리자용)

## 3. 패키지 설치

```bash
pip install -r requirements.txt
```

필요한 패키지:
- `supabase>=2.0.0`: Supabase Python 클라이언트
- `python-dotenv>=1.0.0`: 환경 변수 관리

## 4. 연결 테스트

### 4.1 테스트 스크립트 실행

```bash
python database/test_connection.py
```

### 4.2 Python 코드로 테스트

```python
from database import test_connection, get_supabase_client

# 연결 테스트
if test_connection():
    print("✅ Supabase 연결 성공!")
    
    # 클라이언트 가져오기
    supabase = get_supabase_client()
    print(f"Supabase URL: {supabase.supabase_url}")
else:
    print("❌ Supabase 연결 실패!")
```

## 5. 사용 예제

### 5.1 기본 사용

```python
from database import get_supabase_client

# 클라이언트 가져오기
supabase = get_supabase_client()

# 테이블에서 데이터 조회
response = supabase.table('test_table').select('*').execute()
print(response.data)

# 데이터 삽입
data = {'name': 'test', 'value': 123}
response = supabase.table('test_table').insert(data).execute()
```

### 5.2 관리자 권한 사용

```python
from database import get_supabase_service_client

# 서비스 역할 클라이언트 (관리자 권한)
supabase = get_supabase_service_client()

# RLS(Row Level Security)를 우회하는 작업 수행
# 주의: 서비스 역할 키는 서버 사이드에서만 사용하세요
```

## 6. 데이터베이스 스키마 예제

### 6.1 테스트 테이블 생성

Supabase Dashboard → SQL Editor에서 실행:

```sql
-- 테스트 테이블 생성
CREATE TABLE IF NOT EXISTS test_table (
    id SERIAL PRIMARY KEY,
    name TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 샘플 데이터 삽입
INSERT INTO test_table (name) VALUES ('hello supabase');
```

### 6.2 리뷰 데이터 테이블 예제

```sql
-- 리뷰 검증 결과 저장 테이블
CREATE TABLE IF NOT EXISTS review_validations (
    id SERIAL PRIMARY KEY,
    review_text TEXT NOT NULL,
    trust_score FLOAT,
    is_ad BOOLEAN,
    validation_result JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 리뷰 AI 분석 결과 저장 테이블
CREATE TABLE IF NOT EXISTS review_analyses (
    id SERIAL PRIMARY KEY,
    review_id INTEGER REFERENCES review_validations(id),
    summary TEXT,
    efficacy TEXT,
    side_effects TEXT,
    tip TEXT,
    analysis_result JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 7. 보안 주의사항

### 7.1 .gitignore 확인

`.env` 파일이 Git에 커밋되지 않도록 확인:

```bash
# .gitignore에 다음이 포함되어 있는지 확인
.env
.env.local
.env.*.local
```

### 7.2 키 관리

- **ANON_KEY**: 클라이언트 사이드에서 사용 가능 (RLS 적용)
- **SERVICE_ROLE_KEY**: 서버 사이드에서만 사용 (RLS 우회)
- **절대 공개 저장소에 키를 커밋하지 마세요**

## 8. 문제 해결

### 8.1 연결 실패

1. `.env` 파일이 프로젝트 루트에 있는지 확인
2. 환경 변수 이름이 정확한지 확인 (대소문자 구분)
3. Supabase 프로젝트가 활성화되어 있는지 확인

### 8.2 인증 오류

1. API 키가 올바른지 확인
2. 키의 권한(anon vs service_role) 확인
3. RLS 정책이 올바르게 설정되어 있는지 확인

## 9. 참고 자료

- [Supabase 공식 문서](https://supabase.com/docs)
- [Supabase Python 클라이언트](https://github.com/supabase/supabase-py)
- [GitHub 저장소](https://github.com/tturupapa-stack/dev2)

---

**작성일**: 2026-01-05  
**작성자**: Logic Designer

