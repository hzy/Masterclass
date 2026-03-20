import { useEffect, useRef, useState } from "react";
import type { InputRenderable, SelectOption } from "@opentui/core";

type PendingApproval = {
  approvalId: string;
  toolName: string;
  input: unknown;
};

type ApprovalBoxProps = {
  pendingApproval: PendingApproval | null;
  onRespond: (response: { id: string; approved: boolean; reason?: string }) => void;
};

const options: SelectOption[] = [
  {
    name: "同意",
    description: "允许本次工具调用立即执行",
    value: "approve",
  },
  {
    name: "不同意",
    description: "直接拒绝本次工具调用",
    value: "deny",
  },
  {
    name: "不同意并补充要求",
    description: "拒绝并附带额外说明",
    value: "deny-with-reason",
  },
];

export function ApprovalBox({ pendingApproval, onRespond }: ApprovalBoxProps) {
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [collectingReason, setCollectingReason] = useState(false);
  const reasonInputRef = useRef<InputRenderable>(null);

  useEffect(() => {
    setSelectedIndex(0);
    setCollectingReason(false);
    if (reasonInputRef.current) reasonInputRef.current.value = "";
  }, [pendingApproval?.approvalId]);

  if (!pendingApproval) return null;

  const currentOption = options[selectedIndex];
  const inputPreview = JSON.stringify(pendingApproval.input);

  return (
    <box
      border
      borderStyle="rounded"
      borderColor="#C98A1F"
      marginTop={1}
      paddingX={1}
      flexDirection="column"
      flexShrink={0}
    >
      <text attributes={1} fg="#8A5A00">
        Approval Required
      </text>
      <text  wrapMode="word">
        {`Tool: ${pendingApproval.toolName} | Approval ID: ${pendingApproval.approvalId}`}
      </text>
      <text wrapMode="word">
        {`Input: ${inputPreview}`}
      </text>

      <box marginTop={1}>
        <select
          focused={!collectingReason}
          options={options}
          selectedIndex={selectedIndex}
          showDescription
          minHeight={options.length * 2}
          backgroundColor="#FFFDF7"
          focusedBackgroundColor="#FFF3D6"
          selectedBackgroundColor="#F0C36A"
          onChange={(index) => setSelectedIndex(index)}
          onSelect={() => {
            if (currentOption?.value === "approve") {
              onRespond({
                id: pendingApproval.approvalId,
                approved: true,
              });
              return;
            }

            if (currentOption?.value === "deny") {
              onRespond({
                id: pendingApproval.approvalId,
                approved: false,
              });
              return;
            }

            setCollectingReason(true);
          }}
        />
      </box>

      {collectingReason ? (
        <box marginTop={1} flexDirection="column">
          <text fg="#CCCCCC">请输入补充要求并回车提交：</text>
          <input
            ref={reasonInputRef}
            focused
            showCursor
            cursorStyle={{ style: "line", blinking: true }}
            placeholder="请输入补充要求..."
            onSubmit={(value) => {
              if (typeof value !== "string") return;
              const reason = value.trim();
              if (!reason) return;
              onRespond({
                id: pendingApproval.approvalId,
                approved: false,
                reason,
              });
              setCollectingReason(false);
              if (reasonInputRef.current) reasonInputRef.current.value = "";
            }}
          />
        </box>
      ) : (
        <text marginTop={1}>
          使用方向键切换，按 Enter 确认。
        </text>
      )}
    </box>
  );
}
