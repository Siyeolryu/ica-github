# Claude Code MCP for Cursor AI

Cursor AI에서 Claude Code를 MCP (Model Context Protocol) 서버로 연결하여 사용할 수 있게 해주는 통합 도구입니다.

## 기능

이 MCP 서버는 Cursor AI에서 다음과 같은 Claude Code 기능을 제공합니다:

- **claude_code_chat**: Claude Code와 대화하며 코딩 질문, 디버깅, 코드 생성 등을 수행
- **claude_code_analyze**: 코드 분석, 버그 찾기, 개선 제안, 복잡한 로직 설명
- **claude_code_generate**: 요구사항에 따라 완전한 프로덕션 수준의 코드 생성

## 필수 요구사항

- Node.js 18 이상
- Cursor AI 편집기
- Anthropic API 키

## 설치 및 설정

### 1. 프로젝트 설정

```bash
# 의존성 설치
npm install

# TypeScript 컴파일
npm run build
```

### 2. API 키 설정

Anthropic API 키를 받으세요:
1. [Anthropic Console](https://console.anthropic.com/)에 접속
2. API Keys 섹션에서 새 키 생성
3. `.env` 파일 생성:

```bash
cp .env.example .env
```

`.env` 파일을 열고 API 키를 입력:

```
ANTHROPIC_API_KEY=your_actual_api_key_here
```

### 3. Cursor AI 설정

#### 방법 1: 프로젝트별 설정

Cursor에서 프로젝트를 열고, `.cursor/mcp-config.json` 파일이 이미 생성되어 있습니다.

환경 변수를 시스템에 설정:

**macOS/Linux:**
```bash
export ANTHROPIC_API_KEY=your_api_key_here
```

**Windows:**
```cmd
set ANTHROPIC_API_KEY=your_api_key_here
```

#### 방법 2: 전역 설정

Cursor 설정 파일에 추가:

**macOS/Linux:**
`~/.cursor/mcp_settings.json`

**Windows:**
`%APPDATA%\Cursor\User\mcp_settings.json`

다음 내용을 추가:

```json
{
  "mcpServers": {
    "claude-code": {
      "command": "node",
      "args": ["/absolute/path/to/ica-github/dist/index.js"],
      "env": {
        "ANTHROPIC_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

**주의:** `/absolute/path/to/ica-github`를 실제 프로젝트 경로로 변경하세요.

### 4. Cursor 재시작

설정을 적용하려면 Cursor를 완전히 종료하고 다시 시작하세요.

## 사용 방법

### Cursor에서 MCP 도구 사용

Cursor AI와 대화할 때, MCP 도구가 자동으로 사용 가능해집니다:

**예제 1: 코드에 대해 질문하기**
```
"이 함수가 무엇을 하는지 설명해줘"
```

**예제 2: 버그 찾기**
```
"이 코드에서 버그를 찾아줘"
```

**예제 3: 코드 생성**
```
"TypeScript로 사용자 인증 시스템을 만들어줘"
```

### MCP 도구 직접 호출

Cursor의 명령 팔레트에서:

1. **Claude Code Chat**
   - 메시지: "어떻게 React에서 상태 관리를 해야 할까?"
   - 모델: claude-sonnet-4-5-20250929 (기본값)

2. **Claude Code Analyze**
   - 코드: `function example() { ... }`
   - 작업: "optimize"
   - 언어: "javascript"

3. **Claude Code Generate**
   - 요구사항: "REST API를 호출하는 비동기 함수 만들기"
   - 언어: "typescript"
   - 컨텍스트: "Express.js 사용"

## 사용 가능한 Claude 모델

- `claude-sonnet-4-5-20250929` (기본값) - 빠르고 강력한 일반 용도
- `claude-opus-4-5-20251101` - 최고 성능의 복잡한 작업용
- `claude-3-5-sonnet-20241022` - 이전 버전 호환성

## 개발

### 로컬에서 테스트

```bash
# 빌드 및 실행
npm run dev

# 또는 빌드 후 실행
npm run build
npm start
```

### 프로젝트 구조

```
ica-github/
├── src/
│   └── index.ts          # MCP 서버 메인 코드
├── dist/                 # 컴파일된 JavaScript 파일
├── .cursor/
│   └── mcp-config.json   # Cursor 프로젝트 설정
├── cursor-mcp-settings.json  # 전역 설정 예제
├── .env.example          # 환경 변수 템플릿
├── package.json
├── tsconfig.json
└── README.md
```

## 트러블슈팅

### MCP 서버가 연결되지 않는 경우

1. Cursor를 완전히 재시작했는지 확인
2. `npm run build`로 최신 코드가 컴파일되었는지 확인
3. API 키가 올바르게 설정되었는지 확인
4. Cursor의 개발자 도구(Help → Toggle Developer Tools)에서 콘솔 로그 확인

### API 키 오류

- `.env` 파일이나 시스템 환경 변수에 `ANTHROPIC_API_KEY`가 설정되었는지 확인
- API 키가 유효한지 [Anthropic Console](https://console.anthropic.com/)에서 확인

### Node.js 버전 오류

```bash
node --version  # v18 이상이어야 함
```

## 라이선스

MIT

## 기여

이슈와 풀 리퀘스트를 환영합니다!

## 참고 자료

- [Anthropic API Documentation](https://docs.anthropic.com/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Cursor AI](https://cursor.sh/)
