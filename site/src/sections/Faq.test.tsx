import { render, screen } from "@testing-library/react";
import { Faq } from "./Faq";

test("renders faq", () => {
  render(<Faq />);
  expect(screen.getByText(/at-least-once/i)).toBeInTheDocument();
});