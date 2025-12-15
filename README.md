# Claude Code API

AI-powered code generation, analysis, and refactoring API using Claude AI.

## Features

- **Code Generation**: Generate code from natural language descriptions
- **Code Analysis**: Analyze code for bugs, performance issues, security vulnerabilities
- **Code Refactoring**: Automatically refactor and improve code quality
- **Multi-language Support**: Support for JavaScript, TypeScript, Python, Java, and more

## Installation

```bash
npm install
```

## Configuration

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Add your Anthropic API key to `.env`:
```
ANTHROPIC_API_KEY=your_api_key_here
PORT=3000
NODE_ENV=development
```

## Usage

### Development Mode
```bash
npm run dev
```

### Build and Run
```bash
npm run build
npm start
```

## API Endpoints

### Health Check
```http
GET /api/code/health
```

### Generate Code
```http
POST /api/code/generate
Content-Type: application/json

{
  "prompt": "Create a function to calculate fibonacci numbers",
  "language": "javascript",
  "maxTokens": 2048,
  "temperature": 0.7
}
```

### Analyze Code
```http
POST /api/code/analyze
Content-Type: application/json

{
  "code": "function add(a, b) { return a + b; }",
  "language": "javascript",
  "analysisType": "general"
}
```

Analysis types: `bugs`, `performance`, `security`, `general`

### Refactor Code
```http
POST /api/code/refactor
Content-Type: application/json

{
  "code": "function test() { var x = 1; var y = 2; return x + y; }",
  "language": "javascript",
  "instructions": "Use modern ES6+ syntax and improve readability"
}
```

## Examples

### JavaScript Example

```javascript
const axios = require('axios');

async function generateCode() {
  const response = await axios.post('http://localhost:3000/api/code/generate', {
    prompt: 'Create a REST API endpoint for user authentication',
    language: 'javascript',
    maxTokens: 2048
  });

  console.log(response.data.data.code);
}

generateCode();
```

### Python Example

```python
import requests

def analyze_code():
    response = requests.post('http://localhost:3000/api/code/analyze', json={
        'code': 'def add(a, b):\n    return a + b',
        'language': 'python',
        'analysisType': 'performance'
    })

    print(response.json()['data']['analysis'])

analyze_code()
```

### cURL Examples

```bash
# Generate Code
curl -X POST http://localhost:3000/api/code/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a binary search function",
    "language": "javascript"
  }'

# Analyze Code
curl -X POST http://localhost:3000/api/code/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "code": "function test() { console.log(\"hello\"); }",
    "language": "javascript",
    "analysisType": "security"
  }'

# Refactor Code
curl -X POST http://localhost:3000/api/code/refactor \
  -H "Content-Type: application/json" \
  -d '{
    "code": "var x = 1; var y = 2; console.log(x + y);",
    "language": "javascript",
    "instructions": "Convert to modern ES6 syntax"
  }'
```

## Response Format

All API responses follow this format:

```json
{
  "success": true,
  "data": {
    // Response data
  }
}
```

Error responses:
```json
{
  "success": false,
  "error": "Error Type",
  "message": "Error description"
}
```

## Project Structure

```
.
├── src/
│   ├── controllers/      # Request handlers
│   ├── services/         # Business logic and Claude AI integration
│   ├── routes/           # API route definitions
│   ├── middleware/       # Validation and error handling
│   ├── types/            # TypeScript type definitions
│   └── index.ts          # Application entry point
├── dist/                 # Compiled JavaScript (generated)
├── .env.example          # Environment variables template
├── package.json          # Dependencies and scripts
└── tsconfig.json         # TypeScript configuration
```

## Technologies

- **Node.js & Express**: Web server framework
- **TypeScript**: Type-safe development
- **Claude AI**: Anthropic's AI model for code operations
- **Axios**: HTTP client for API requests
- **Joi**: Request validation
- **Helmet & CORS**: Security middleware

## License

MIT

