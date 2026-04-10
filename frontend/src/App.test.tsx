import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import App from "./App";

type MockResponseOptions = {
  body: unknown;
  ok?: boolean;
  status?: number;
};

function createMockResponse({
  body,
  ok = true,
  status = 200,
}: MockResponseOptions): Response {
  return {
    ok,
    status,
    json: async () => body,
  } as Response;
}

function installManagerWorkflowFetchMock(options?: {
  evaluations?: unknown[];
  postEvaluationBody?: unknown;
}) {
  const employees = [
    {
      id: 1300,
      employee_number: "EMP-1300",
      first_name: "Taylor",
      last_name: "Brooks",
      full_name: "Taylor Brooks",
      job_title: "Senior Software Engineer",
      department: "Product Engineering",
      manager_id: 1200,
      manager_name: "Avery Jordan",
      is_active: true,
    },
  ];

  const reviewCycles = [
    {
      id: 2026,
      name: "2026 Annual Review",
      cycle_type: "annual",
      start_date: "2026-01-01",
      end_date: "2026-12-31",
      status: "active",
      created_by_user_id: 6,
      updated_by_user_id: 6,
    },
  ];

  let evaluations =
    options?.evaluations ??
    [
      {
        id: 501,
        employee_id: 1300,
        employee_name: "Taylor Brooks",
        review_cycle_id: 2026,
        review_cycle_name: "2026 Annual Review",
        author_user_id: 2,
        updated_by_user_id: 2,
        performance_rating: 3.7,
        potential_rating: 2,
        summary_comment:
          "Taylor is trending upward and taking on more mentoring work.",
        status: "draft",
      },
    ];

  const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input);
    const method = init?.method ?? "GET";

    if (url.endsWith("/auth/login") && method === "POST") {
      return createMockResponse({
        body: {
          access_token: "demo-token",
          token_type: "bearer",
          expires_in_seconds: 3600,
        },
      });
    }

    if (url.endsWith("/auth/me")) {
      return createMockResponse({
        body: {
          id: 2,
          username: "manager.avery",
          full_name: "Avery Jordan",
          auth_provider: "local",
          roles: ["people_manager"],
          is_active: true,
        },
      });
    }

    if (url.includes("/employees?reports_only=true")) {
      return createMockResponse({ body: employees });
    }

    if (url.endsWith("/review-cycles")) {
      return createMockResponse({ body: reviewCycles });
    }

    if (url.includes("/evaluations?employee_id=1300") && method === "GET") {
      return createMockResponse({ body: evaluations });
    }

    if (url.endsWith("/evaluations") && method === "POST") {
      const body = JSON.parse(String(init?.body));
      const createdEvaluation = options?.postEvaluationBody ?? {
        id: 777,
        employee_id: body.employee_id,
        employee_name: "Taylor Brooks",
        review_cycle_id: body.review_cycle_id,
        review_cycle_name: "2026 Annual Review",
        author_user_id: 2,
        updated_by_user_id: 2,
        performance_rating: body.performance_rating,
        potential_rating: body.potential_rating,
        summary_comment: body.summary_comment,
        status: body.status,
      };
      evaluations = [createdEvaluation];
      return createMockResponse({ body: createdEvaluation });
    }

    if (url.endsWith("/evaluations/501") && method === "PUT") {
      const body = JSON.parse(String(init?.body));
      const updatedEvaluation = {
        id: 501,
        employee_id: 1300,
        employee_name: "Taylor Brooks",
        review_cycle_id: 2026,
        review_cycle_name: "2026 Annual Review",
        author_user_id: 2,
        updated_by_user_id: 2,
        performance_rating: body.performance_rating,
        potential_rating: body.potential_rating,
        summary_comment: body.summary_comment,
        status: body.status,
      };
      evaluations = [updatedEvaluation];
      return createMockResponse({ body: updatedEvaluation });
    }

    throw new Error(`Unhandled fetch request: ${method} ${url}`);
  });

  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

async function signInAsManager() {
  fireEvent.change(screen.getByLabelText("Username"), {
    target: { value: "manager.avery" },
  });
  fireEvent.change(screen.getByLabelText("Password"), {
    target: { value: "DemoPass123!ChangeMe" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Sign in" }));

  await screen.findByRole("button", { name: /Taylor Brooks/i });
}

describe("App", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it("renders the login page for the manager workflow", () => {
    render(<App />);

    expect(screen.getByText("Manager Workflow")).toBeInTheDocument();
    expect(screen.getByLabelText("Username")).toBeInTheDocument();
    expect(screen.getByLabelText("Password")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Sign in" })).toBeInTheDocument();
  });

  it("loads the manager workspace and opens an existing draft evaluation", async () => {
    installManagerWorkflowFetchMock();

    render(<App />);
    await signInAsManager();

    expect(screen.getByRole("button", { name: /Taylor Brooks/i })).toBeInTheDocument();
    expect(await screen.findByDisplayValue("3.70")).toBeInTheDocument();
    expect(
      await screen.findByDisplayValue(
        "Taylor is trending upward and taking on more mentoring work.",
      ),
    ).toBeInTheDocument();
    expect(screen.getByText("Current working cycle")).toBeInTheDocument();
  });

  it("creates a new draft evaluation for a selected report", async () => {
    const fetchMock = installManagerWorkflowFetchMock({ evaluations: [] });

    render(<App />);
    await signInAsManager();

    fireEvent.change(
      screen.getByLabelText("Performance rating (0.00 to 5.00)"),
      {
        target: { value: "4.10" },
      },
    );
    fireEvent.change(screen.getByLabelText("Potential rating (1 to 3)"), {
      target: { value: "3" },
    });
    fireEvent.change(screen.getByLabelText("Narrative notes"), {
      target: {
        value:
          "Taylor is ready for broader ownership and has been mentoring newer teammates well.",
      },
    });

    fireEvent.click(screen.getByRole("button", { name: "Create draft" }));

    expect(await screen.findByText("Draft created.")).toBeInTheDocument();

    const createCall = fetchMock.mock.calls.find(
      ([url, init]) => String(url).endsWith("/evaluations") && init?.method === "POST",
    );

    expect(createCall).toBeDefined();
    expect(JSON.parse(String(createCall?.[1]?.body))).toEqual({
      employee_id: 1300,
      review_cycle_id: 2026,
      performance_rating: 4.1,
      potential_rating: 3,
      summary_comment:
        "Taylor is ready for broader ownership and has been mentoring newer teammates well.",
      status: "draft",
    });

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Save draft changes" })).toBeInTheDocument();
    });
  });
});
