import { getToolName } from "ai";
import type { DynamicToolUIPart, ToolUIPart } from "ai";
import { useSpinner } from "./Spinner";

type ToolCallPartProps = {
  part: ToolUIPart | DynamicToolUIPart;
};

export function ToolCallPart({ part }: ToolCallPartProps) {
  const name = getToolName(part);
  const isRunning =
    part.state === "input-streaming" ||
    part.state === "input-available" ||
    part.state === "approval-requested" ||
    part.state === "approval-responded";

  const spinnerChar = useSpinner(isRunning);

  let icon: string;
  let iconColor: string;
  switch (part.state) {
    case "output-available":
      icon = "✓";
      iconColor = "#70C97A";
      break;
    case "output-error":
      icon = "✗";
      iconColor = "#E06C75";
      break;
    case "output-denied":
      icon = "⊘";
      iconColor = "#E06C75";
      break;
    default:
      icon = spinnerChar ?? "⋯";
      iconColor = "#D4A843";
  }

  const inputStr =
    part.state === "input-streaming" ? "..." : JSON.stringify(part.input);

  return (
    <box
      border
      borderStyle="rounded"
      borderColor={isRunning ? "#D4A843" : "#444444"}
      paddingX={1}
      flexDirection="column"
    >
      <text>
        <span fg={iconColor}>{icon}</span>
        <span fg="#D4A843"> {name}</span>
        <span fg="#888888">({inputStr})</span>
      </text>
      {part.state === "output-available" ? (
        <text fg="#888888" wrapMode="word">
          {"→ " + JSON.stringify(part.output)}
        </text>
      ) : null}
      {part.state === "output-error" ? (
        <text fg="#E06C75" wrapMode="word">
          {"Error: " + part.errorText}
        </text>
      ) : null}
    </box>
  );
}
