import { tool, ToolLoopAgent } from "ai";
import { createOpenAI } from "@ai-sdk/openai";
import { z } from "zod";

const openai = createOpenAI({
  baseURL: "http://localhost:8000/v1",
  /* cspell:disable-next-line */
  apiKey: "sk-xxx",

  // uncomment this to see the requests and responses in the console
  // fetch: async (input: string | URL | Request, init?: BunFetchRequestInit) => {
  //   const res = await globalThis.fetch(input, init);
  //   console.log(init, res);
  //   return res;
  // },
});

const agent = new ToolLoopAgent({
  model: openai.chat("Qwen/Qwen2.5-3B-Instruct"),
  instructions: "You are a helpful assistant.",
  tools: {
    weather: tool({
      description: "Get the weather in a location",
      inputSchema: z.object({
        location: z.string().describe("The location to get the weather for"),
      }),
      execute: async ({ location }) => ({
        location,
        temperature: 72 + Math.floor(Math.random() * 21) - 10,
      }),
    }),
  },
});

const result = await agent.generate({
  prompt: "What is the weather in NYC?",
});

console.log(result.text);
