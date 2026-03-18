import { useEffect, useState } from "react";

const spinnerFrames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"];

export function useSpinner(active: boolean) {
  const [frame, setFrame] = useState(0);

  useEffect(() => {
    if (!active) return;
    const timer = setInterval(() => {
      setFrame((value) => (value + 1) % spinnerFrames.length);
    }, 80);
    return () => clearInterval(timer);
  }, [active]);

  return active ? (spinnerFrames[frame] ?? "⠋") : null;
}

type SpinnerProps = {
  label: string;
  color?: string;
};

export function Spinner({ label, color = "#D4A843" }: SpinnerProps) {
  const frame = useSpinner(true);

  return (
    <text>
      <span fg={color}>{frame} </span>
      <span fg="#888888">{label}</span>
    </text>
  );
}
