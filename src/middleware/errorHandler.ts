import { Request, Response, NextFunction } from 'express';
import { ApiError } from '../types';

export const errorHandler = (err: Error, req: Request, res: Response, next: NextFunction): void => {
  console.error('Error:', err);

  const apiError: ApiError = {
    error: err.name || 'Internal Server Error',
    message: err.message || 'An unexpected error occurred',
    statusCode: 500,
  };

  if (err.message.includes('Claude API Error')) {
    apiError.statusCode = 503;
    apiError.error = 'Service Unavailable';
  }

  if (err.message.includes('API key')) {
    apiError.statusCode = 401;
    apiError.error = 'Unauthorized';
  }

  res.status(apiError.statusCode).json({
    success: false,
    error: apiError.error,
    message: apiError.message,
  });
};
