# 빠른 시작 가이드 (Quick Start Guide)

## ✅ .env 파일이 생성되었습니다!

이제 실제 API 키를 입력하면 됩니다.

## 📝 설정 방법 (3단계)

### 1단계: .env 파일 열기

**VS Code 사용:**
```bash
cd ui_integration
code .env
```

**메모장 사용:**
```bash
cd ui_integration
notepad .env
```

**또는 직접 탐색:**
- `ui_integration` 폴더에서 `.env` 파일 찾기
- 텍스트 에디터로 열기

### 2단계: Claude API 키 발급받기

1. 브라우저에서 https://console.anthropic.com/ 접속
2. 로그인 (없으면 회원가입)
3. 좌측 메뉴에서 **"API Keys"** 클릭
4. **"Create Key"** 버튼 클릭
5. 키 이름 입력 (예: "dev2-project")
6. 생성된 키 복사 (한 번만 표시됨!)

### 3단계: .env 파일에 키 입력

`.env` 파일에서 다음 줄을 찾아서:

```env
ANTHROPIC_API_KEY=your-anthropic-api-key-here
```

실제 키로 변경:

```env
ANTHROPIC_API_KEY=sk-ant-api03-실제키값여기에입력
```

**예시:**
```env
ANTHROPIC_API_KEY=sk-ant-api03-abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
```

## ✅ 확인하기

설정이 완료되었는지 확인:

```bash
cd ui_integration
python setup_env.py verify
```

또는 Python에서:

```python
from dotenv import load_dotenv
import os

load_dotenv()
key = os.getenv("ANTHROPIC_API_KEY")
if key and key != "your-anthropic-api-key-here":
    print("✅ API 키가 설정되었습니다!")
else:
    print("❌ API 키를 설정해주세요.")
```

## 🚀 실행하기

설정 완료 후:

```bash
# Streamlit 앱 실행
streamlit run app.py

# 또는 API 서버 실행
python -m api.main
```

## ⚠️ 중요 사항

- ✅ `.env` 파일은 Git에 업로드되지 않습니다 (안전함)
- ❌ API 키를 코드에 직접 입력하지 마세요
- 🔒 키가 노출되면 즉시 재생성하세요

## 📚 더 자세한 정보

- 상세 가이드: `API_KEY_SETUP.md` 또는 `ENV_SETUP_GUIDE.md` 참조
- Anthropic API 문서: https://docs.anthropic.com/
