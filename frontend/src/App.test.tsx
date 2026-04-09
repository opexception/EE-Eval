import { render, screen } from "@testing-library/react";

import App from "./App";


describe("App", () => {
  it("renders the Phase 0 landing page", () => {
    render(<App />);

    expect(screen.getByText("Phase 0 Scaffold")).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: /EE-Eval/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: /Backend health endpoint/i }),
    ).toHaveAttribute("href", "http://localhost:8000/api/health");
  });
});

