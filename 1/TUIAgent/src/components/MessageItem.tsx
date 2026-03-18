import { isReasoningUIPart, isTextUIPart, isToolUIPart } from "ai";
import type { UIMessage } from "ai";
import { SyntaxStyle } from "@opentui/core";
import { ToolCallPart } from "./ToolCallPart";

const syntaxStyle = SyntaxStyle.create();

type MessageItemProps = {
  message: UIMessage;
};

export function MessageItem({ message }: MessageItemProps) {
  return (
    <box flexDirection="column" marginBottom={1}>
      <text fg={message.role === "user" ? "#5B9BD5" : "#70C97A"} attributes={1}>
        {message.role === "user" ? " You " : " Assistant "}
      </text>
      <box flexDirection="column" paddingLeft={2}>
        {message.parts.map((part, i) => {
          if (isTextUIPart(part)) {
            if (message.role === "assistant") {
              return (
                <box key={i} flexDirection="column">
                  <markdown
                    content={part.text}
                    syntaxStyle={syntaxStyle}
                    streaming={part.state === "streaming"}
                    conceal
                  />
                  {part.state === "streaming" ? <text fg="#555555">▍</text> : null}
                </box>
              );
            }
            return (
              <text key={i} wrapMode="word">
                {part.text}
              </text>
            );
          }
          if (isReasoningUIPart(part)) {
            return (
              <text key={i} fg="#666666" wrapMode="word">
                {part.text}
              </text>
            );
          }
          if (isToolUIPart(part)) {
            return <ToolCallPart key={i} part={part} />;
          }
          return null;
        })}
      </box>
    </box>
  );
}
