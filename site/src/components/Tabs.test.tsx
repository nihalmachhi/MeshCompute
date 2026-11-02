import { render, screen, fireEvent } from "@testing-library/react";
import { Tabs } from "./Tabs";

test("keyboard navigation", () => {
  render(<Tabs tabs={[{ label: "a", content: "A" }, { label: "b", content: "B" }]} />);
  const btn = screen.getByRole("tab", { name: "a" });
  fireEvent.keyDown(btn, { key: "ArrowRight" });
  expect(screen.getByRole("tab", { name: "b" })).toHaveAttribute("aria-selected", "true");
});