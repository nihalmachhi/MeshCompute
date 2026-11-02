import { renderHook, act } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { useTour } from "./useTour";

describe("useTour", () => {
  it("advances index", () => {
    vi.useFakeTimers();
    const { result } = renderHook(() => useTour(3, 100));
    act(() => {
      vi.advanceTimersByTime(100);
    });
    expect(result.current.index).toBe(1);
    vi.useRealTimers();
  });
  it("pauses", () => {
    vi.useFakeTimers();
    const { result } = renderHook(() => useTour(3, 100));
    act(() => result.current.setPaused(true));
    act(() => {
      vi.advanceTimersByTime(200);
    });
    expect(result.current.index).toBe(0);
    vi.useRealTimers();
  });
});