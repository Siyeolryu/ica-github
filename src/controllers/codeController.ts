import { Request, Response, NextFunction } from 'express';
import { ClaudeService } from '../services/claudeService';
import { CodeRequest, AnalysisRequest, RefactorRequest } from '../types';

export class CodeController {
  private claudeService: ClaudeService;

  constructor(claudeService: ClaudeService) {
    this.claudeService = claudeService;
  }

  generateCode = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      const request: CodeRequest = req.body;
      const result = await this.claudeService.generateCode(request);
      res.json({
        success: true,
        data: result,
      });
    } catch (error) {
      next(error);
    }
  };

  analyzeCode = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      const request: AnalysisRequest = req.body;
      const result = await this.claudeService.analyzeCode(request);
      res.json({
        success: true,
        data: result,
      });
    } catch (error) {
      next(error);
    }
  };

  refactorCode = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      const request: RefactorRequest = req.body;
      const result = await this.claudeService.refactorCode(request);
      res.json({
        success: true,
        data: result,
      });
    } catch (error) {
      next(error);
    }
  };

  healthCheck = async (req: Request, res: Response): Promise<void> => {
    res.json({
      success: true,
      message: 'Claude Code API is running',
      timestamp: new Date().toISOString(),
    });
  };
}
