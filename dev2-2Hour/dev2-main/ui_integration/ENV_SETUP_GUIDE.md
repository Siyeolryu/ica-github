# 환경 변수 설정 가이드 (Environment Variables Setup Guide)

## ✅ .env 파일 생성 완료!

`.env` 파일이 생성되었습니다. 이제 실제 API 키를 입력하세요.

## 📝 설정 방법

### 1. .env 파일 열기

**VS Code 사용 시:**
```bash
code ui_integration\.env
```

**메모장 사용 시:**
```bash
notepad ui_integration\.env
```

**다른 에디터:**
- `ui_integration` 폴더에서 `.env` 파일을 찾아서 열기

### 2. Claude API 키 발급받기

1. https://console.anthropic.com/ 접속
2. 로그인 (계정이 없으면 회원가입)
3. 좌측 메뉴에서 **"API Keys"** 선택
4. **"Create Key"** 버튼 클릭
5. 키 이름 입력 후 생성
6. **생성된 키를 복사** (한 번만 표시됩니다!)

### 3. .env 파일에 키 입력

`.env` 파일을 열고 다음 줄을 수정하세요:

```env
ANTHROPIC_API_KEY=sk-ant-api03-여기에실제키입력
```

**예시:**
```env
ANTHROPIC_API_KEY=sk-ant-api03-abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
```

### 4. Supabase 설정 (이미 설정되어 있다면 건너뛰기)

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key-here
```

## ✅ 설정 확인

### 방법 1: Python 스크립트로 확인

```bash
cd ui_integration
python setup_env.py verify
```

### 방법 2: 직접 확인

```python
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")

if api_key and api_key != "your-anthropic-api-key-here":
    print(f"✅ API 키가 설정되었습니다: {api_key[:20]}...")
else:
    print("❌ API 키를 설정해주세요.")
```

## 🚀 사용하기

설정이 완료되면:

```bash
# Streamlit 앱 실행
streamlit run app.py

# 또는 API 서버 실행
python -m api.main
```

## ⚠️ 보안 주의사항

1. **절대 Git에 커밋하지 마세요**
   - `.env` 파일은 `.gitignore`에 포함되어 있습니다
   - API 키를 코드에 하드코딩하지 마세요

2. **키 관리**
   - API 키는 비밀번호처럼 관리하세요
   - 키가 노출되면 즉시 재생성하세요

3. **파일 위치**
   - `.env` 파일은 `ui_integration/` 폴더에 있어야 합니다

## 📚 추가 도움말

- 상세 가이드: `API_KEY_SETUP.md` 참조
- Anthropic API 문서: https://docs.anthropic.com/
