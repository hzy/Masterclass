import {
  ToolLoopAgent,
  DirectChatTransport,
  getToolName,
  isToolUIPart,
  lastAssistantMessageIsCompleteWithApprovalResponses,
} from "ai";
import type { UIMessage } from "ai";
import { useChat } from "@ai-sdk/react";
import { createCliRenderer } from "@opentui/core";
import { createRoot } from "@opentui/react";
import { ApprovalBox } from "./src/components/ApprovalBox";
import { ChatInput } from "./src/components/ChatInput";
import { MessageItem } from "./src/components/MessageItem";
import { Spinner } from "./src/components/Spinner";
import { createBashTool } from "./src/tools/CreateBashTool";
import {
  createEditTool,
  createReadTool,
  createWriteTool,
} from "./src/tools/CreateFileSystemTools";
import { model } from "./model";

const agent = new ToolLoopAgent({
  model,
  instructions:
    "You are a helpful assistant. Use read/write/edit/bash tools for local engineering tasks and clearly summarize results.",
  tools: {
    bash: createBashTool(),
    read: createReadTool(),
    write: createWriteTool(),
    edit: createEditTool(),
  },
});

type PendingApproval = {
  approvalId: string;
  toolName: string;
  input: unknown;
};

function getPendingApproval(messages: UIMessage[]): PendingApproval | null {
  for (let messageIndex = messages.length - 1; messageIndex >= 0; messageIndex--) {
    const message = messages[messageIndex];
    if (!message) continue;
    for (let partIndex = message.parts.length - 1; partIndex >= 0; partIndex--) {
      const part = message.parts[partIndex];
      if (!part) continue;
      if (isToolUIPart(part) && part.state === "approval-requested") {
        return {
          approvalId: part.approval.id,
          toolName: getToolName(part),
          input: part.input,
        };
      }
    }
  }

  return null;
}

function App() {
  const { messages, sendMessage, status, addToolApprovalResponse } = useChat({
    transport: new DirectChatTransport({ agent }),
    sendAutomaticallyWhen: lastAssistantMessageIsCompleteWithApprovalResponses,
  });

  const pendingApproval = getPendingApproval(messages);

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

      <ApprovalBox
        pendingApproval={pendingApproval}
        onRespond={({ id, approved, reason }) => {
          addToolApprovalResponse({ id, approved, reason });
        }}
      />

      <ChatInput onSend={(text) => sendMessage({ text })} focused={!pendingApproval} />
    </>
  );
}

const renderer = await createCliRenderer();
createRoot(renderer).render(<App />);
