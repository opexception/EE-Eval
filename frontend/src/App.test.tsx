import { render, screen } from "@testing-library/react";

import App from "./App";


describe("App", () => {
  it("renders the login page for local authentication", () => {
    render(<App />);

    expect(screen.getByText("Local Authentication")).toBeInTheDocument();
    expect(screen.getByLabelText("Username")).toBeInTheDocument();
    expect(screen.getByLabelText("Password")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /Sign in/i }),
    ).toBeInTheDocument();
  });
});
