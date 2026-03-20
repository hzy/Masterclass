import { useRef } from "react";
import type { InputRenderable } from "@opentui/core";

type ChatInputProps = {
  onSend: (text: string) => void;
  focused?: boolean;
};

const inputAccentColor = "#FFB454";

export function ChatInput({ onSend, focused = true }: ChatInputProps) {
  const inputRef = useRef<InputRenderable>(null);

  return (
    <box
      border
      borderStyle="rounded"
      borderColor="#4A4A4A"
      paddingX={1}
      marginTop={1}
      flexDirection="row"
      flexShrink={0}
      minHeight={3}
    >
      <text fg={inputAccentColor} attributes={1}>
        {"❯ "}
      </text>
      <input
        ref={inputRef}
        flexGrow={1}
        focused={focused}
        showCursor
        cursorStyle={{ style: "line", blinking: true }}
        cursorColor={inputAccentColor}
        placeholder="Send a message..."
        onSubmit={(value) => {
          if (typeof value !== "string") return;
          const text = value.trim();
          if (!text) return;
          onSend(text);
          if (inputRef.current) inputRef.current.value = "";
        }}
      />
    </box>
  );
}
