# API Usage Examples

This directory contains practical examples of using the Claude Code API.

## Prerequisites

1. Make sure the API server is running:
   ```bash
   npm run dev
   ```

2. Install dependencies for examples:
   ```bash
   npm install axios
   ```

## Running Examples

### Generate Code Example
```bash
node examples/generate-code.js
```
Demonstrates how to generate code from a natural language prompt.

### Analyze Code Example
```bash
node examples/analyze-code.js
```
Demonstrates how to analyze code for potential bugs and issues.

### Refactor Code Example
```bash
node examples/refactor-code.js
```
Demonstrates how to refactor code with specific instructions.

## Example Output

Each example will print:
- The request being made
- The formatted response from the API
- Any relevant metadata (language, suggestions, changes, etc.)

## Customization

Feel free to modify the examples:
- Change the `prompt`, `code`, or `instructions` values
- Adjust `language` to test different programming languages
- Modify `analysisType` to focus on different aspects (bugs, performance, security)
- Experiment with `temperature` and `maxTokens` for different response styles
