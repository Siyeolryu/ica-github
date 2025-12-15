#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from "@modelcontextprotocol/sdk/types.js";
import Anthropic from "@anthropic-ai/sdk";

// Initialize Anthropic client
const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

// Define available tools
const TOOLS: Tool[] = [
  {
    name: "claude_code_chat",
    description:
      "Send a message to Claude Code and get a response. Use this for coding questions, debugging, code generation, and technical discussions.",
    inputSchema: {
      type: "object",
      properties: {
        message: {
          type: "string",
          description: "The message or question to send to Claude Code",
        },
        model: {
          type: "string",
          description: "The Claude model to use (default: claude-sonnet-4-5-20250929)",
          enum: [
            "claude-sonnet-4-5-20250929",
            "claude-opus-4-5-20251101",
            "claude-3-5-sonnet-20241022",
          ],
          default: "claude-sonnet-4-5-20250929",
        },
        max_tokens: {
          type: "number",
          description: "Maximum tokens in the response (default: 8000)",
          default: 8000,
        },
      },
      required: ["message"],
    },
  },
  {
    name: "claude_code_analyze",
    description:
      "Ask Claude Code to analyze code, find bugs, suggest improvements, or explain complex logic.",
    inputSchema: {
      type: "object",
      properties: {
        code: {
          type: "string",
          description: "The code to analyze",
        },
        task: {
          type: "string",
          description: "What to do with the code (e.g., 'find bugs', 'explain', 'optimize', 'add tests')",
        },
        language: {
          type: "string",
          description: "Programming language of the code (optional)",
        },
      },
      required: ["code", "task"],
    },
  },
  {
    name: "claude_code_generate",
    description:
      "Generate code based on requirements. Claude Code will write complete, production-ready code.",
    inputSchema: {
      type: "object",
      properties: {
        requirements: {
          type: "string",
          description: "Description of what code to generate",
        },
        language: {
          type: "string",
          description: "Programming language to use",
        },
        context: {
          type: "string",
          description: "Additional context or constraints (optional)",
        },
      },
      required: ["requirements", "language"],
    },
  },
];

// Create server instance
const server = new Server(
  {
    name: "claude-code-mcp",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Handle tool listing
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: TOOLS,
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case "claude_code_chat": {
        const { message, model = "claude-sonnet-4-5-20250929", max_tokens = 8000 } = args as {
          message: string;
          model?: string;
          max_tokens?: number;
        };

        const response = await anthropic.messages.create({
          model: model,
          max_tokens: max_tokens,
          messages: [
            {
              role: "user",
              content: message,
            },
          ],
        });

        const textContent = response.content.find((c) => c.type === "text");
        const responseText = textContent && "text" in textContent ? textContent.text : "";

        return {
          content: [
            {
              type: "text",
              text: responseText,
            },
          ],
        };
      }

      case "claude_code_analyze": {
        const { code, task, language } = args as {
          code: string;
          task: string;
          language?: string;
        };

        const prompt = `${task} the following ${language ? language + " " : ""}code:\n\n\`\`\`${language || ""}\n${code}\n\`\`\``;

        const response = await anthropic.messages.create({
          model: "claude-sonnet-4-5-20250929",
          max_tokens: 8000,
          messages: [
            {
              role: "user",
              content: prompt,
            },
          ],
        });

        const textContent = response.content.find((c) => c.type === "text");
        const responseText = textContent && "text" in textContent ? textContent.text : "";

        return {
          content: [
            {
              type: "text",
              text: responseText,
            },
          ],
        };
      }

      case "claude_code_generate": {
        const { requirements, language, context } = args as {
          requirements: string;
          language: string;
          context?: string;
        };

        const prompt = `Generate ${language} code for the following requirements:\n\n${requirements}${
          context ? `\n\nAdditional context: ${context}` : ""
        }\n\nProvide complete, production-ready code with proper error handling and documentation.`;

        const response = await anthropic.messages.create({
          model: "claude-sonnet-4-5-20250929",
          max_tokens: 8000,
          messages: [
            {
              role: "user",
              content: prompt,
            },
          ],
        });

        const textContent = response.content.find((c) => c.type === "text");
        const responseText = textContent && "text" in textContent ? textContent.text : "";

        return {
          content: [
            {
              type: "text",
              text: responseText,
            },
          ],
        };
      }

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    return {
      content: [
        {
          type: "text",
          text: `Error: ${errorMessage}`,
        },
      ],
      isError: true,
    };
  }
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Claude Code MCP Server running on stdio");
}

main().catch((error) => {
  console.error("Server error:", error);
  process.exit(1);
});
