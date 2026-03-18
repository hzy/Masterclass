import { tool, ToolLoopAgent, DirectChatTransport } from "ai";
import { useChat } from "@ai-sdk/react";
import { z } from "zod";
import { createCliRenderer } from "@opentui/core";
import { createRoot } from "@opentui/react";
import { ChatInput } from "./src/components/ChatInput";
import { MessageItem } from "./src/components/MessageItem";
import { Spinner } from "./src/components/Spinner";
import { openai } from "./model";

const agent = new ToolLoopAgent({
  model: openai.responses("Qwen/Qwen2.5-3B-Instruct"),
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

function App() {
  const { messages, sendMessage, status } = useChat({
    transport: new DirectChatTransport({ agent }),
  });

  const isThinking =
    (status === "submitted" || status === "streaming") &&
    (messages.at(-1)?.role !== "assistant" ||
      messages.at(-1)?.parts.length === 0);

  return (
    <>
      <scrollbox stickyScroll flexGrow={1} flexShrink={1}>
        {messages.map((message) => (
          <MessageItem key={message.id} message={message} />
        ))}
        {isThinking ? (
          <box paddingLeft={2} marginBottom={1}>
            <Spinner label="Thinking..." />
          </box>
        ) : null}
      </scrollbox>

      <ChatInput
        onSend={(text) => sendMessage({ text })}
      />
    </>
  );
}

const renderer = await createCliRenderer();
createRoot(renderer).render(<App />);
