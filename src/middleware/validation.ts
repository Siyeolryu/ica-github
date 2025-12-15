import { Request, Response, NextFunction } from 'express';
import Joi from 'joi';

const codeGenerationSchema = Joi.object({
  prompt: Joi.string().required().min(10).max(5000),
  language: Joi.string().optional().default('javascript'),
  maxTokens: Joi.number().optional().min(100).max(4096).default(2048),
  temperature: Joi.number().optional().min(0).max(1).default(0.7),
});

const analysisSchema = Joi.object({
  code: Joi.string().required().min(1).max(50000),
  language: Joi.string().optional().default('javascript'),
  analysisType: Joi.string().optional().valid('bugs', 'performance', 'security', 'general').default('general'),
});

const refactorSchema = Joi.object({
  code: Joi.string().required().min(1).max(50000),
  language: Joi.string().optional().default('javascript'),
  instructions: Joi.string().optional().max(1000).default('Improve code quality and readability'),
});

export const validateCodeGeneration = (req: Request, res: Response, next: NextFunction): void => {
  const { error, value } = codeGenerationSchema.validate(req.body);
  if (error) {
    res.status(400).json({
      success: false,
      error: 'Validation Error',
      message: error.details[0].message,
    });
    return;
  }
  req.body = value;
  next();
};

export const validateAnalysis = (req: Request, res: Response, next: NextFunction): void => {
  const { error, value } = analysisSchema.validate(req.body);
  if (error) {
    res.status(400).json({
      success: false,
      error: 'Validation Error',
      message: error.details[0].message,
    });
    return;
  }
  req.body = value;
  next();
};

export const validateRefactor = (req: Request, res: Response, next: NextFunction): void => {
  const { error, value } = refactorSchema.validate(req.body);
  if (error) {
    res.status(400).json({
      success: false,
      error: 'Validation Error',
      message: error.details[0].message,
    });
    return;
  }
  req.body = value;
  next();
};
