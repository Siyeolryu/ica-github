# Cursor AI에 Claude Code MCP 연결 가이드

이 가이드는 Cursor AI IDE에 Claude Code MCP 서버를 단계별로 연결하는 방법을 설명합니다.

## 1단계: 프로젝트 준비

### 1.1 저장소 클론 (이미 완료된 경우 건너뛰기)

```bash
git clone <repository-url>
cd ica-github
```

### 1.2 의존성 설치

```bash
npm install
```

### 1.3 프로젝트 빌드

```bash
npm run build
```

빌드가 성공하면 `dist/` 폴더에 컴파일된 JavaScript 파일이 생성됩니다.

## 2단계: Anthropic API 키 받기

### 2.1 Anthropic 계정 생성

1. [https://console.anthropic.com/](https://console.anthropic.com/) 접속
2. 계정이 없다면 회원가입
3. 로그인

### 2.2 API 키 생성

1. 왼쪽 메뉴에서 "API Keys" 클릭
2. "Create Key" 버튼 클릭
3. 키 이름 입력 (예: "cursor-mcp")
4. 생성된 키를 안전한 곳에 복사 (한 번만 표시됩니다!)

### 2.3 API 키 저장

프로젝트 루트에 `.env` 파일 생성:

```bash
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**중요:** `.env` 파일은 `.gitignore`에 포함되어 있어 Git에 커밋되지 않습니다.

## 3단계: Cursor AI 설정

### 방법 A: 프로젝트 단위 설정 (권장)

이 방법은 현재 프로젝트에만 MCP 서버를 적용합니다.

#### A.1 환경 변수 설정

**macOS/Linux:**

`~/.zshrc` 또는 `~/.bashrc`에 추가:

```bash
export ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

그 다음 터미널 재시작 또는:

```bash
source ~/.zshrc  # 또는 source ~/.bashrc
```

**Windows:**

시스템 환경 변수 설정:
1. 시스템 속성 > 환경 변수
2. 사용자 변수에 새로 만들기
3. 변수 이름: `ANTHROPIC_API_KEY`
4. 변수 값: `sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

#### A.2 Cursor에서 프로젝트 열기

1. Cursor 실행
2. File > Open Folder
3. `ica-github` 폴더 선택

`.cursor/mcp-config.json` 파일이 이미 설정되어 있습니다.

### 방법 B: 전역 설정

이 방법은 모든 Cursor 프로젝트에서 MCP 서버를 사용할 수 있게 합니다.

#### B.1 Cursor 설정 파일 찾기

**macOS:**
```
~/.cursor/mcp_settings.json
```

**Linux:**
```
~/.cursor/mcp_settings.json
```

**Windows:**
```
%APPDATA%\Cursor\User\mcp_settings.json
```

#### B.2 설정 파일 편집

파일이 없다면 새로 생성하고, 다음 내용을 추가:

```json
{
  "mcpServers": {
    "claude-code": {
      "command": "node",
      "args": ["/Users/yourname/projects/ica-github/dist/index.js"],
      "env": {
        "ANTHROPIC_API_KEY": "sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
      }
    }
  }
}
```

**주의사항:**
- `/Users/yourname/projects/ica-github`를 실제 프로젝트의 절대 경로로 변경
- Windows의 경우 경로를 `C:\\Users\\yourname\\projects\\ica-github\\dist\\index.js` 형식으로 변경
- API 키를 실제 키로 변경

## 4단계: Cursor 재시작

MCP 설정을 적용하려면 **Cursor를 완전히 종료**하고 다시 시작해야 합니다.

1. Cursor 종료 (Cmd+Q on Mac, Alt+F4 on Windows)
2. Cursor 다시 실행

## 5단계: 연결 확인

### 5.1 MCP 서버 상태 확인

Cursor에서:

1. Command Palette 열기 (Cmd+Shift+P on Mac, Ctrl+Shift+P on Windows)
2. "MCP" 입력
3. "MCP: Show Status" 또는 유사한 명령 실행

`claude-code` 서버가 "Connected" 상태로 표시되어야 합니다.

### 5.2 테스트 실행

Cursor의 AI Chat 창에서 다음을 시도:

```
Claude를 통해 Hello World를 출력하는 Python 함수를 만들어줘
```

MCP 서버가 정상적으로 작동하면 Claude가 응답합니다.

## 트러블슈팅

### 문제 1: MCP 서버가 연결되지 않음

**해결 방법:**

1. 빌드 확인:
```bash
cd /path/to/ica-github
npm run build
```

2. 환경 변수 확인:
```bash
# macOS/Linux
echo $ANTHROPIC_API_KEY

# Windows
echo %ANTHROPIC_API_KEY%
```

3. Cursor 개발자 도구 확인:
   - Help > Toggle Developer Tools
   - Console 탭에서 에러 메시지 확인

### 문제 2: "ANTHROPIC_API_KEY not found" 에러

**해결 방법:**

1. `.env` 파일이 프로젝트 루트에 있는지 확인
2. API 키가 올바른지 확인
3. 환경 변수가 시스템에 설정되었는지 확인
4. Cursor를 완전히 재시작

### 문제 3: Node.js 버전 에러

**해결 방법:**

```bash
node --version
```

Node.js 18 이상이 필요합니다. 업데이트:

```bash
# macOS (Homebrew)
brew install node

# Windows (nvm-windows)
nvm install latest
nvm use latest

# Linux (nvm)
nvm install --lts
nvm use --lts
```

### 문제 4: TypeScript 컴파일 에러

**해결 방법:**

```bash
# 의존성 재설치
rm -rf node_modules package-lock.json
npm install

# 다시 빌드
npm run build
```

### 문제 5: 경로 에러 (Windows)

Windows에서 경로 문제가 있다면:

```json
{
  "mcpServers": {
    "claude-code": {
      "command": "node",
      "args": ["C:\\Users\\YourName\\projects\\ica-github\\dist\\index.js"],
      "env": {
        "ANTHROPIC_API_KEY": "your-key-here"
      }
    }
  }
}
```

백슬래시를 이중으로 사용하거나 슬래시로 변경:

```json
"args": ["C:/Users/YourName/projects/ica-github/dist/index.js"]
```

## 추가 설정

### 로그 활성화

디버깅을 위해 로그를 활성화하려면:

```json
{
  "mcpServers": {
    "claude-code": {
      "command": "node",
      "args": ["/path/to/ica-github/dist/index.js"],
      "env": {
        "ANTHROPIC_API_KEY": "your-key-here",
        "DEBUG": "*"
      }
    }
  }
}
```

### 여러 MCP 서버 사용

다른 MCP 서버와 함께 사용하려면:

```json
{
  "mcpServers": {
    "claude-code": {
      "command": "node",
      "args": ["/path/to/ica-github/dist/index.js"],
      "env": {
        "ANTHROPIC_API_KEY": "your-key-here"
      }
    },
    "other-mcp-server": {
      "command": "python",
      "args": ["/path/to/other-server.py"]
    }
  }
}
```

## 다음 단계

MCP 서버가 정상적으로 연결되면:

1. Cursor의 AI Chat에서 코드 생성 요청
2. 코드 분석 및 리뷰 요청
3. 버그 찾기 및 최적화 제안 받기

자세한 사용 예제는 [README.md](README.md)를 참고하세요.

## 도움이 필요하신가요?

- GitHub Issues: 문제 보고 및 기능 요청
- [Anthropic Documentation](https://docs.anthropic.com/)
- [Cursor Documentation](https://cursor.sh/docs)
- [MCP Protocol](https://modelcontextprotocol.io/)
