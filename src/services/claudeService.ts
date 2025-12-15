import axios, { AxiosInstance } from 'axios';
import { CodeRequest, CodeResponse, AnalysisRequest, AnalysisResponse, RefactorRequest, RefactorResponse } from '../types';

export class ClaudeService {
  private client: AxiosInstance;
  private apiKey: string;

  constructor(apiKey: string) {
    this.apiKey = apiKey;
    this.client = axios.create({
      baseURL: 'https://api.anthropic.com/v1',
      headers: {
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01',
        'content-type': 'application/json',
      },
    });
  }

  async generateCode(request: CodeRequest): Promise<CodeResponse> {
    const { prompt, language = 'javascript', maxTokens = 2048, temperature = 0.7 } = request;

    const systemPrompt = `You are an expert software developer. Generate clean, efficient, and well-documented code in ${language}.`;
    const userPrompt = `Generate code for the following request:\n\n${prompt}\n\nProvide the code with clear explanations.`;

    try {
      const response = await this.client.post('/messages', {
        model: 'claude-3-5-sonnet-20241022',
        max_tokens: maxTokens,
        temperature,
        system: systemPrompt,
        messages: [
          {
            role: 'user',
            content: userPrompt,
          },
        ],
      });

      const content = response.data.content[0].text;

      return {
        code: this.extractCode(content),
        explanation: this.extractExplanation(content),
        language,
      };
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async analyzeCode(request: AnalysisRequest): Promise<AnalysisResponse> {
    const { code, language = 'javascript', analysisType = 'general' } = request;

    const analysisPrompts = {
      bugs: 'Analyze the following code for potential bugs and errors',
      performance: 'Analyze the following code for performance issues and optimization opportunities',
      security: 'Analyze the following code for security vulnerabilities',
      general: 'Provide a comprehensive analysis of the following code',
    };

    const systemPrompt = `You are an expert code reviewer specializing in ${language}.`;
    const userPrompt = `${analysisPrompts[analysisType]}:\n\n\`\`\`${language}\n${code}\n\`\`\`\n\nProvide detailed analysis and actionable suggestions.`;

    try {
      const response = await this.client.post('/messages', {
        model: 'claude-3-5-sonnet-20241022',
        max_tokens: 2048,
        temperature: 0.3,
        system: systemPrompt,
        messages: [
          {
            role: 'user',
            content: userPrompt,
          },
        ],
      });

      const content = response.data.content[0].text;

      return {
        analysis: content,
        suggestions: this.extractSuggestions(content),
        severity: this.determineSeverity(content, analysisType),
      };
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async refactorCode(request: RefactorRequest): Promise<RefactorResponse> {
    const { code, language = 'javascript', instructions = 'Improve code quality and readability' } = request;

    const systemPrompt = `You are an expert software engineer specializing in code refactoring for ${language}.`;
    const userPrompt = `Refactor the following code with these instructions: ${instructions}\n\n\`\`\`${language}\n${code}\n\`\`\`\n\nProvide the refactored code and explain the changes made.`;

    try {
      const response = await this.client.post('/messages', {
        model: 'claude-3-5-sonnet-20241022',
        max_tokens: 2048,
        temperature: 0.5,
        system: systemPrompt,
        messages: [
          {
            role: 'user',
            content: userPrompt,
          },
        ],
      });

      const content = response.data.content[0].text;

      return {
        originalCode: code,
        refactoredCode: this.extractCode(content),
        changes: this.extractChanges(content),
      };
    } catch (error) {
      throw this.handleError(error);
    }
  }

  private extractCode(content: string): string {
    const codeBlockRegex = /```[\w]*\n([\s\S]*?)```/g;
    const matches = content.match(codeBlockRegex);

    if (matches && matches.length > 0) {
      return matches[0].replace(/```[\w]*\n/, '').replace(/```$/, '').trim();
    }

    return content.trim();
  }

  private extractExplanation(content: string): string {
    const codeBlockRegex = /```[\w]*\n[\s\S]*?```/g;
    return content.replace(codeBlockRegex, '').trim();
  }

  private extractSuggestions(content: string): string[] {
    const suggestions: string[] = [];
    const lines = content.split('\n');

    for (const line of lines) {
      if (line.match(/^[\d\-\*]\.|^•|^-\s/)) {
        suggestions.push(line.replace(/^[\d\-\*]\.|^•|^-\s/, '').trim());
      }
    }

    return suggestions.length > 0 ? suggestions : ['See detailed analysis above'];
  }

  private extractChanges(content: string): string[] {
    const changes: string[] = [];
    const changeIndicators = [
      'changed',
      'refactored',
      'improved',
      'optimized',
      'renamed',
      'extracted',
      'removed',
      'added',
    ];

    const lines = content.split('\n');
    for (const line of lines) {
      if (changeIndicators.some(indicator => line.toLowerCase().includes(indicator))) {
        changes.push(line.trim());
      }
    }

    return changes.length > 0 ? changes : ['Code structure and quality improved'];
  }

  private determineSeverity(content: string, analysisType: string): 'low' | 'medium' | 'high' {
    const lowerContent = content.toLowerCase();

    if (analysisType === 'security') {
      if (lowerContent.includes('critical') || lowerContent.includes('severe')) {
        return 'high';
      }
      if (lowerContent.includes('vulnerability') || lowerContent.includes('risk')) {
        return 'medium';
      }
    }

    if (lowerContent.includes('error') || lowerContent.includes('bug')) {
      return 'high';
    }

    if (lowerContent.includes('warning') || lowerContent.includes('issue')) {
      return 'medium';
    }

    return 'low';
  }

  private handleError(error: any): Error {
    if (axios.isAxiosError(error)) {
      const message = error.response?.data?.error?.message || error.message;
      return new Error(`Claude API Error: ${message}`);
    }
    return error;
  }
}
