import { renderHook, act } from "@testing-library/react";
import { useTour } from "./useTour";

test("advances tab", () => {
  const { result } = renderHook(() => useTour(3, 100));
  act(() => {
    result.current.advance();
  });
  expect(result.current.active).toBe(1);
});