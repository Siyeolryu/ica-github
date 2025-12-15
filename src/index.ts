import express, { Application } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import dotenv from 'dotenv';
import { ClaudeService } from './services/claudeService';
import { CodeController } from './controllers/codeController';
import { createCodeRouter } from './routes/code';
import { errorHandler } from './middleware/errorHandler';

dotenv.config();

const app: Application = express();
const PORT = process.env.PORT || 3000;

// Security middleware
app.use(helmet());
app.use(cors({
  origin: process.env.CORS_ORIGIN || '*',
  credentials: true,
}));

// Body parser middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Request logging middleware
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
  next();
});

// Initialize services and controllers
const apiKey = process.env.ANTHROPIC_API_KEY;
if (!apiKey) {
  console.error('ANTHROPIC_API_KEY is not set in environment variables');
  process.exit(1);
}

const claudeService = new ClaudeService(apiKey);
const codeController = new CodeController(claudeService);

// Routes
app.get('/', (req, res) => {
  res.json({
    message: 'Claude Code API',
    version: '1.0.0',
    endpoints: {
      health: 'GET /api/code/health',
      generate: 'POST /api/code/generate',
      analyze: 'POST /api/code/analyze',
      refactor: 'POST /api/code/refactor',
    },
  });
});

app.use('/api/code', createCodeRouter(codeController));

// Error handling middleware (must be last)
app.use(errorHandler);

// Start server
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
  console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);
  console.log(`API Base URL: http://localhost:${PORT}/api/code`);
});

export default app;
