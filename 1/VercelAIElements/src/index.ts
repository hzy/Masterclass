import { createOpenAI } from "@ai-sdk/openai";
import { convertToModelMessages, streamText, type UIMessage } from "ai";
import { serve } from "bun";
import index from "./index.html";

const openai = createOpenAI({
  baseURL: "http://localhost:8000/v1",
  /* cspell:disable-next-line */
  apiKey: "sk-xxx",
});

const server = serve({
  idleTimeout: 255,
  routes: {
    // Serve index.html for all unmatched routes.
    "/*": index,

    "/api/chat": {
      async POST(req) {
        const { messages }: { messages: UIMessage[] } = await req.json();

        const result = streamText({
          system: `You are a helpful assistant.`,
          model: openai.chat("Qwen/Qwen2.5-3B-Instruct"),
          messages: await convertToModelMessages(messages),
          // TODO: add tools and mcp servers
        });

        return result.toUIMessageStreamResponse({
          sendSources: true,
          sendReasoning: true,
          originalMessages: messages,
        });
      },
    },
  },

  development: process.env.NODE_ENV !== "production" && {
    // Enable browser hot reloading in development
    hmr: true,

    // Echo console logs from the browser to the server
    console: true,
  },
});

console.log(`🚀 Server running at ${server.url}`);
