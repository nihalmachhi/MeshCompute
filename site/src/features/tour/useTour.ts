import { useEffect, useState } from "react";

export function useTour(length: number, intervalMs = 7000) {
  const [index, setIndex] = useState(0);
  const [paused, setPaused] = useState(false);
  useEffect(() => {
    if (paused) return;
    const id = window.setInterval(() => setIndex((i) => (i + 1) % length), intervalMs);
    return () => window.clearInterval(id);
  }, [paused, length, intervalMs]);
  return { index, setIndex, paused, setPaused };
}