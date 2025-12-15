import { Router } from 'express';
import { CodeController } from '../controllers/codeController';
import { validateCodeGeneration, validateAnalysis, validateRefactor } from '../middleware/validation';

export const createCodeRouter = (codeController: CodeController): Router => {
  const router = Router();

  router.get('/health', codeController.healthCheck);
  router.post('/generate', validateCodeGeneration, codeController.generateCode);
  router.post('/analyze', validateAnalysis, codeController.analyzeCode);
  router.post('/refactor', validateRefactor, codeController.refactorCode);

  return router;
};
