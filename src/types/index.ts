export interface CodeRequest {
  prompt: string;
  language?: string;
  maxTokens?: number;
  temperature?: number;
}

export interface CodeResponse {
  code: string;
  explanation?: string;
  language: string;
}

export interface AnalysisRequest {
  code: string;
  language?: string;
  analysisType?: 'bugs' | 'performance' | 'security' | 'general';
}

export interface AnalysisResponse {
  analysis: string;
  suggestions: string[];
  severity?: 'low' | 'medium' | 'high';
}

export interface RefactorRequest {
  code: string;
  language?: string;
  instructions?: string;
}

export interface RefactorResponse {
  originalCode: string;
  refactoredCode: string;
  changes: string[];
}

export interface ApiError {
  error: string;
  message: string;
  statusCode: number;
}
