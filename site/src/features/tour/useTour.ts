import { useCallback, useEffect, useRef, useState } from "react";

export function useTour(tabCount: number, intervalMs: number = 7000) {
  const [active, setActive] = useState(0);
  const [paused, setPaused] = useState(false);
  const [progress, setProgress] = useState(0);
  const timerRef = useRef<number | null>(null);
  const startRef = useRef<number>(Date.now());

  const advance = useCallback(() => {
    setActive((a) => (a + 1) % tabCount);
    setProgress(0);
    startRef.current = Date.now();
  }, [tabCount]);

  useEffect(() => {
    if (paused) return;
    startRef.current = Date.now();
    timerRef.current = window.setInterval(() => {
      const elapsed = Date.now() - startRef.current;
      setProgress(Math.min(100, (elapsed / intervalMs) * 100));
      if (elapsed >= intervalMs) advance();
    }, 100);
    return () => {
      if (timerRef.current) window.clearInterval(timerRef.current);
    };
  }, [paused, advance, intervalMs]);

  const pause = () => setPaused(true);
  const play = () => setPaused(false);
  const goTo = (i: number) => {
    setActive(i);
    setProgress(0);
    startRef.current = Date.now();
  };

  return { active, paused, progress, pause, play, goTo, advance };
}