# API 키 설정 가이드

## Claude API 키 발급 방법

1. **Anthropic 콘솔 접속**
   - https://console.anthropic.com/ 접속
   - 계정 로그인 (없으면 회원가입)

2. **API 키 생성**
   - 좌측 메뉴에서 "API Keys" 선택
   - "Create Key" 버튼 클릭
   - 키 이름 입력 후 생성
   - **생성된 키를 복사해두세요** (한 번만 표시됩니다)

## 환경 변수 설정 방법

### 방법 1: .env 파일 사용 (로컬 개발 권장)

1. **.env 파일 생성**
   ```bash
   cd ui_integration
   cp .env.example .env
   ```

2. **.env 파일 편집**
   텍스트 에디터로 `.env` 파일을 열고 실제 API 키로 변경:
   ```env
   ANTHROPIC_API_KEY=sk-ant-api03-실제키값여기에입력
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=실제키값여기에입력
   ```

3. **확인**
   ```bash
   # Python에서 확인
   python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('API Key:', os.getenv('ANTHROPIC_API_KEY')[:20] + '...')"
   ```

### 방법 2: Streamlit Secrets 사용 (Streamlit Cloud 배포 시)

#### 로컬에서 테스트:
1. **secrets.toml 파일 생성**
   ```bash
   cd ui_integration/.streamlit
   cp secrets.toml.example secrets.toml
   ```

2. **secrets.toml 파일 편집**
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-api03-실제키값여기에입력"
   SUPABASE_URL = "https://your-project.supabase.co"
   SUPABASE_ANON_KEY = "실제키값여기에입력"
   ```

#### Streamlit Cloud에서:
1. Streamlit Cloud 대시보드 접속
2. 앱 선택 > Settings > Secrets
3. 다음 형식으로 입력:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-api03-실제키값"
   SUPABASE_URL = "https://your-project.supabase.co"
   SUPABASE_ANON_KEY = "실제키값"
   ```

### 방법 3: 시스템 환경 변수 사용 (Windows)

#### PowerShell에서:
```powershell
# 현재 세션에만 적용
$env:ANTHROPIC_API_KEY = "sk-ant-api03-실제키값"

# 영구적으로 설정 (사용자 레벨)
[System.Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", "sk-ant-api03-실제키값", "User")
```

#### 명령 프롬프트(CMD)에서:
```cmd
# 현재 세션에만 적용
set ANTHROPIC_API_KEY=sk-ant-api03-실제키값

# 영구적으로 설정
setx ANTHROPIC_API_KEY "sk-ant-api03-실제키값"
```

### 방법 4: 시스템 환경 변수 사용 (Mac/Linux)

```bash
# 현재 세션에만 적용
export ANTHROPIC_API_KEY="sk-ant-api03-실제키값"

# 영구적으로 설정 (~/.bashrc 또는 ~/.zshrc에 추가)
echo 'export ANTHROPIC_API_KEY="sk-ant-api03-실제키값"' >> ~/.bashrc
source ~/.bashrc
```

## 설정 확인

### Python 스크립트로 확인:
```python
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# API 키 확인
api_key = os.getenv("ANTHROPIC_API_KEY")
if api_key:
    print(f"✅ API 키가 설정되었습니다: {api_key[:20]}...")
else:
    print("❌ API 키가 설정되지 않았습니다.")
```

### Streamlit 앱에서 확인:
```python
import streamlit as st
import os

# Streamlit secrets에서 확인
if 'ANTHROPIC_API_KEY' in st.secrets:
    st.success("✅ API 키가 설정되었습니다 (Streamlit Secrets)")
elif os.getenv('ANTHROPIC_API_KEY'):
    st.success("✅ API 키가 설정되었습니다 (환경 변수)")
else:
    st.error("❌ API 키가 설정되지 않았습니다.")
```

## 보안 주의사항

⚠️ **중요:**
1. **절대 Git에 업로드하지 마세요**
   - `.env` 파일은 `.gitignore`에 포함되어 있어야 합니다
   - `secrets.toml`도 Git에 커밋하지 마세요
   - API 키를 코드에 하드코딩하지 마세요

2. **키 관리**
   - API 키는 비밀번호처럼 관리하세요
   - 키가 노출되면 즉시 재생성하세요
   - 팀원과 공유할 때는 안전한 방법을 사용하세요

3. **권한 관리**
   - 필요한 최소 권한만 부여하세요
   - 사용하지 않는 키는 삭제하세요

## 문제 해결

### "API 키가 설정되지 않았습니다" 오류

1. **파일 위치 확인**
   - `.env` 파일이 `ui_integration/` 디렉토리에 있는지 확인
   - `secrets.toml` 파일이 `ui_integration/.streamlit/` 디렉토리에 있는지 확인

2. **파일 이름 확인**
   - `.env.example`이 아닌 `.env` 파일인지 확인
   - `secrets.toml.example`이 아닌 `secrets.toml` 파일인지 확인

3. **키 형식 확인**
   - Claude API 키는 `sk-ant-api03-`로 시작해야 합니다
   - 따옴표 없이 입력했는지 확인

4. **애플리케이션 재시작**
   - 환경 변수를 변경한 후 앱을 재시작하세요

### "Invalid API Key" 오류

1. **키 복사 확인**
   - 공백이나 줄바꿈이 포함되지 않았는지 확인
   - 전체 키가 복사되었는지 확인

2. **키 유효성 확인**
   - Anthropic 콘솔에서 키가 활성화되어 있는지 확인
   - 키가 만료되지 않았는지 확인

3. **계정 확인**
   - API 사용량 한도에 도달하지 않았는지 확인

## 추가 도움말

- [Anthropic API 문서](https://docs.anthropic.com/)
- [Streamlit Secrets 문서](https://docs.streamlit.io/streamlit-cloud/get-started/deploy-an-app/connect-to-data-sources/secrets-management)
- [python-dotenv 문서](https://pypi.org/project/python-dotenv/)
