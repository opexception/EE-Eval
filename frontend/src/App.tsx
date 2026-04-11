import { FormEvent, startTransition, useEffect, useState } from "react";

import {
  API_BASE_URL,
  ApiError,
  createEvaluation,
  getCurrentUser,
  getEmployees,
  getEvaluations,
  getNineBoxMatrix,
  getReviewCycles,
  login,
  updateEvaluation,
  type CurrentUser,
  type Employee,
  type Evaluation,
  type NineBoxCell,
  type NineBoxEmployee,
  type NineBoxMatrix,
  type ReviewCycle,
} from "./api";
import "./index.css";

const appName = import.meta.env.VITE_APP_NAME ?? "EE-Eval";

type DraftState = {
  performanceRating: string;
  potentialRating: string;
  summaryComment: string;
};

function createEmptyDraft(): DraftState {
  return {
    performanceRating: "",
    potentialRating: "2",
    summaryComment: "",
  };
}

function createDraftFromEvaluation(evaluation: Evaluation): DraftState {
  return {
    performanceRating: evaluation.performance_rating.toFixed(2),
    potentialRating: String(evaluation.potential_rating),
    summaryComment: evaluation.summary_comment ?? "",
  };
}

function isManagerWorkflowUser(currentUser: CurrentUser): boolean {
  return currentUser.roles.includes("people_manager") || currentUser.roles.includes("hr_admin");
}

function formatRole(role: string): string {
  return role
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

function findPreferredReviewCycle(reviewCycles: ReviewCycle[]): ReviewCycle | null {
  return reviewCycles.find((reviewCycle) => reviewCycle.status === "active") ?? reviewCycles[0] ?? null;
}

function compareEvaluationsByCycleName(a: Evaluation, b: Evaluation): number {
  return a.review_cycle_name.localeCompare(b.review_cycle_name) * -1;
}

const POTENTIAL_ROW_ORDER = ["high", "moderate", "limited"] as const;
const PERFORMANCE_COLUMN_ORDER = ["at_risk", "effective", "high"] as const;

function formatEmployeeCount(count: number): string {
  return count === 1 ? "1 employee" : `${count} employees`;
}

function findCellForEmployee(
  matrix: NineBoxMatrix | null,
  employeeId: number | null,
): NineBoxCell | null {
  if (!matrix || !employeeId) {
    return null;
  }

  return (
    matrix.cells.find((cell) =>
      cell.employees.some((employee) => employee.employee_id === employeeId),
    ) ?? null
  );
}

function findFirstPopulatedCell(matrix: NineBoxMatrix | null): NineBoxCell | null {
  if (!matrix) {
    return null;
  }

  return matrix.cells.find((cell) => cell.employee_count > 0) ?? matrix.cells[0] ?? null;
}

function getMatrixCell(
  matrix: NineBoxMatrix | null,
  potentialTier: string,
  performanceTier: string,
): NineBoxCell | null {
  if (!matrix) {
    return null;
  }

  return (
    matrix.cells.find(
      (cell) =>
        cell.potential_tier === potentialTier &&
        cell.performance_tier === performanceTier,
    ) ?? null
  );
}

function compareNineBoxEmployeesByName(a: NineBoxEmployee, b: NineBoxEmployee): number {
  return a.employee_name.localeCompare(b.employee_name);
}

function createNineBoxEmployeeFromSelection(
  employee: Employee,
  evaluation: Evaluation,
): NineBoxEmployee {
  return {
    employee_id: employee.id,
    employee_number: employee.employee_number,
    employee_name: employee.full_name,
    job_title: employee.job_title,
    department: employee.department,
    manager_name: employee.manager_name,
    is_active: employee.is_active,
    evaluation_id: evaluation.id,
    performance_rating: evaluation.performance_rating,
    potential_rating: evaluation.potential_rating,
    performance_tier: evaluation.performance_tier,
    potential_tier: evaluation.potential_tier,
    nine_box_code: evaluation.nine_box_code,
    nine_box_label: evaluation.nine_box_label,
    summary_comment: evaluation.summary_comment,
    evaluation_status: evaluation.status,
  };
}

function updateMatrixWithEvaluation(
  matrix: NineBoxMatrix | null,
  employee: Employee,
  evaluation: Evaluation,
): NineBoxMatrix | null {
  if (!matrix) {
    return null;
  }

  const updatedEmployee = createNineBoxEmployeeFromSelection(employee, evaluation);
  const cells = matrix.cells.map((cell) => {
    const remainingEmployees = cell.employees.filter(
      (currentEmployee) => currentEmployee.employee_id !== employee.id,
    );
    const nextEmployees =
      cell.box_code === evaluation.nine_box_code
        ? [...remainingEmployees, updatedEmployee].sort(compareNineBoxEmployeesByName)
        : remainingEmployees;

    return {
      ...cell,
      employees: nextEmployees,
      employee_count: nextEmployees.length,
    };
  });

  return {
    ...matrix,
    total_employees: cells.reduce(
      (employeeCount, cell) => employeeCount + cell.employee_count,
      0,
    ),
    cells,
  };
}

type AuthenticatedShellProps = {
  currentUser: CurrentUser;
  isRefreshing: boolean;
  onRefreshCurrentUser: () => Promise<void>;
  onSignOut: () => void;
};

function AuthenticatedShell({
  currentUser,
  isRefreshing,
  onRefreshCurrentUser,
  onSignOut,
}: AuthenticatedShellProps) {
  return (
    <div className="page-shell">
      <main className="shell-layout">
        <section className="hero-copy">
          <p className="eyebrow">Authenticated Shell</p>
          <h1>{appName}</h1>
          <p className="lede">
            This account is signed in successfully. The first end-to-end workflow
            is currently focused on people managers and HR administrators.
          </p>
          <div className="button-row">
            <button
              className="button-link"
              type="button"
              onClick={onRefreshCurrentUser}
              disabled={isRefreshing}
            >
              {isRefreshing ? "Refreshing..." : "Refresh current user"}
            </button>
            <button className="ghost-button" type="button" onClick={onSignOut}>
              Sign out
            </button>
          </div>
        </section>

        <section className="panel">
          <h2>Signed in as</h2>
          <dl className="details-list">
            <div>
              <dt>Name</dt>
              <dd>{currentUser.full_name}</dd>
            </div>
            <div>
              <dt>Username</dt>
              <dd>{currentUser.username}</dd>
            </div>
            <div>
              <dt>Auth provider</dt>
              <dd>{currentUser.auth_provider}</dd>
            </div>
            <div>
              <dt>Status</dt>
              <dd>{currentUser.is_active ? "Active" : "Inactive"}</dd>
            </div>
          </dl>
          <h2>Roles</h2>
          <div className="role-list" aria-label="Assigned roles">
            {currentUser.roles.map((role) => (
              <span className="role-pill" key={role}>
                {formatRole(role)}
              </span>
            ))}
          </div>
        </section>
      </main>

      <section className="notes-grid" aria-label="Authenticated notes">
        <article className="note-card">
          <h2>Included right now</h2>
          <p>
            Local sign-in, employee directory access, review-cycle lookup, and
            evaluation CRUD foundations are active in the backend.
          </p>
        </article>

        <article className="note-card">
          <h2>Manager workflow</h2>
          <p>
            Sign in with `manager.avery` to use the first end-to-end manager
            workflow for draft evaluations.
          </p>
        </article>

        <article className="note-card">
          <h2>Backend endpoints</h2>
          <p className="api-line">{API_BASE_URL}/employees</p>
          <p className="api-line">{API_BASE_URL}/review-cycles</p>
          <p className="api-line">{API_BASE_URL}/evaluations</p>
        </article>
      </section>
    </div>
  );
}

type ManagerWorkspaceProps = {
  currentUser: CurrentUser;
  token: string;
  isRefreshing: boolean;
  onRefreshCurrentUser: () => Promise<void>;
  onSessionError: (message: string) => void;
  onSignOut: () => void;
};

function ManagerWorkspace({
  currentUser,
  token,
  isRefreshing,
  onRefreshCurrentUser,
  onSessionError,
  onSignOut,
}: ManagerWorkspaceProps) {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [reviewCycles, setReviewCycles] = useState<ReviewCycle[]>([]);
  const [employeeEvaluations, setEmployeeEvaluations] = useState<Evaluation[]>([]);
  const [nineBoxMatrix, setNineBoxMatrix] = useState<NineBoxMatrix | null>(null);
  const [selectedEmployeeId, setSelectedEmployeeId] = useState<number | null>(null);
  const [selectedReviewCycleId, setSelectedReviewCycleId] = useState<number | null>(null);
  const [selectedMatrixCellCode, setSelectedMatrixCellCode] = useState<string | null>(null);
  const [draft, setDraft] = useState<DraftState>(createEmptyDraft);
  const [workflowError, setWorkflowError] = useState<string | null>(null);
  const [saveMessage, setSaveMessage] = useState<string | null>(null);
  const [isLoadingWorkspace, setIsLoadingWorkspace] = useState(true);
  const [isLoadingEvaluations, setIsLoadingEvaluations] = useState(false);
  const [isLoadingNineBox, setIsLoadingNineBox] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    let isMounted = true;

    async function loadWorkspace() {
      setWorkflowError(null);
      setSaveMessage(null);
      setIsLoadingWorkspace(true);

      try {
        const [employeeResponses, reviewCycleResponses] = await Promise.all([
          getEmployees(token, { reportsOnly: true }),
          getReviewCycles(token),
        ]);

        if (!isMounted) {
          return;
        }

        const activeEmployees = employeeResponses.filter((employee) => employee.is_active);
        const nextEmployees = activeEmployees.length > 0 ? activeEmployees : employeeResponses;
        const preferredEmployee = nextEmployees[0] ?? null;
        const preferredReviewCycle = findPreferredReviewCycle(reviewCycleResponses);

        startTransition(() => {
          setEmployees(nextEmployees);
          setReviewCycles(reviewCycleResponses);
          setSelectedEmployeeId(preferredEmployee?.id ?? null);
          setSelectedReviewCycleId(preferredReviewCycle?.id ?? null);
        });
      } catch (error) {
        const message =
          error instanceof ApiError
            ? error.message
            : "Unable to load the manager workspace.";

        if (error instanceof ApiError && error.status === 401) {
          onSessionError(message);
          return;
        }

        if (!isMounted) {
          return;
        }

        setWorkflowError(message);
      } finally {
        if (isMounted) {
          setIsLoadingWorkspace(false);
        }
      }
    }

    void loadWorkspace();

    return () => {
      isMounted = false;
    };
  }, [onSessionError, token]);

  useEffect(() => {
    if (!selectedReviewCycleId) {
      setNineBoxMatrix(null);
      setSelectedMatrixCellCode(null);
      return;
    }

    const reviewCycleId = selectedReviewCycleId;
    let isMounted = true;

    async function loadNineBoxMatrix() {
      setIsLoadingNineBox(true);

      try {
        const matrix = await getNineBoxMatrix(token, {
          reviewCycleId,
        });

        if (!isMounted) {
          return;
        }

        const preferredCell =
          findCellForEmployee(matrix, selectedEmployeeId) ??
          findFirstPopulatedCell(matrix);

        startTransition(() => {
          setNineBoxMatrix(matrix);
          setSelectedMatrixCellCode(preferredCell?.box_code ?? null);
        });
      } catch (error) {
        const message =
          error instanceof ApiError
            ? error.message
            : "Unable to load the 9-box matrix.";

        if (error instanceof ApiError && error.status === 401) {
          onSessionError(message);
          return;
        }

        if (!isMounted) {
          return;
        }

        setWorkflowError(message);
      } finally {
        if (isMounted) {
          setIsLoadingNineBox(false);
        }
      }
    }

    void loadNineBoxMatrix();

    return () => {
      isMounted = false;
    };
  }, [onSessionError, selectedReviewCycleId, token]);

  useEffect(() => {
    if (!selectedEmployeeId) {
      setEmployeeEvaluations([]);
      setDraft(createEmptyDraft());
      return;
    }

    const employeeId = selectedEmployeeId;
    let isMounted = true;

    async function loadEmployeeEvaluations() {
      setWorkflowError(null);
      setSaveMessage(null);
      setIsLoadingEvaluations(true);

      try {
        const evaluations = await getEvaluations(token, {
          employeeId,
        });

        if (!isMounted) {
          return;
        }

        const sortedEvaluations = [...evaluations].sort(compareEvaluationsByCycleName);
        startTransition(() => {
          setEmployeeEvaluations(sortedEvaluations);
        });
      } catch (error) {
        const message =
          error instanceof ApiError
            ? error.message
            : "Unable to load evaluations for this employee.";

        if (error instanceof ApiError && error.status === 401) {
          onSessionError(message);
          return;
        }

        if (!isMounted) {
          return;
        }

        setWorkflowError(message);
      } finally {
        if (isMounted) {
          setIsLoadingEvaluations(false);
        }
      }
    }

    void loadEmployeeEvaluations();

    return () => {
      isMounted = false;
    };
  }, [onSessionError, selectedEmployeeId, token]);

  const selectedEmployee =
    employees.find((employee) => employee.id === selectedEmployeeId) ?? null;
  const selectedReviewCycle =
    reviewCycles.find((reviewCycle) => reviewCycle.id === selectedReviewCycleId) ?? null;
  const selectedEvaluation =
    employeeEvaluations.find(
      (evaluation) => evaluation.review_cycle_id === selectedReviewCycleId,
    ) ?? null;

  useEffect(() => {
    if (!selectedEmployee || !selectedReviewCycle) {
      setDraft(createEmptyDraft());
      return;
    }

    if (selectedEvaluation) {
      setDraft(createDraftFromEvaluation(selectedEvaluation));
      return;
    }

    setDraft(createEmptyDraft());
  }, [selectedEmployee, selectedEvaluation, selectedReviewCycle]);

  const priorEvaluations = employeeEvaluations.filter(
    (evaluation) => evaluation.review_cycle_id !== selectedReviewCycleId,
  );
  const selectedMatrixCell =
    (nineBoxMatrix?.cells.find((cell) => cell.box_code === selectedMatrixCellCode) ??
      findCellForEmployee(nineBoxMatrix, selectedEmployeeId) ??
      findFirstPopulatedCell(nineBoxMatrix)) ??
    null;
  const selectedMatrixEmployee =
    selectedMatrixCell?.employees.find(
      (employee) => employee.employee_id === selectedEmployeeId,
    ) ??
    selectedMatrixCell?.employees[0] ??
    null;

  useEffect(() => {
    if (!selectedEmployeeId || !nineBoxMatrix) {
      return;
    }

    const matchingCell = findCellForEmployee(nineBoxMatrix, selectedEmployeeId);
    if (matchingCell && matchingCell.box_code !== selectedMatrixCellCode) {
      setSelectedMatrixCellCode(matchingCell.box_code);
    }
  }, [nineBoxMatrix, selectedEmployeeId, selectedMatrixCellCode]);

  async function handleSaveDraft(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!selectedEmployee || !selectedReviewCycle) {
      setWorkflowError("Choose an employee and review cycle before saving.");
      return;
    }

    const parsedPerformanceRating = Number.parseFloat(draft.performanceRating);
    const parsedPotentialRating = Number.parseInt(draft.potentialRating, 10);

    if (Number.isNaN(parsedPerformanceRating) || parsedPerformanceRating < 0 || parsedPerformanceRating > 5) {
      setWorkflowError("Performance rating must be between 0.00 and 5.00.");
      return;
    }

    if (Number.isNaN(parsedPotentialRating) || parsedPotentialRating < 1 || parsedPotentialRating > 3) {
      setWorkflowError("Potential rating must be between 1 and 3.");
      return;
    }

    setWorkflowError(null);
    setSaveMessage(null);
    setIsSaving(true);

    try {
      const request = {
        performance_rating: parsedPerformanceRating,
        potential_rating: parsedPotentialRating,
        summary_comment: draft.summaryComment.trim() || null,
        status: "draft",
      };

      const savedEvaluation = selectedEvaluation
        ? await updateEvaluation(token, selectedEvaluation.id, request)
        : await createEvaluation(token, {
            employee_id: selectedEmployee.id,
            review_cycle_id: selectedReviewCycle.id,
            ...request,
          });

      startTransition(() => {
        setEmployeeEvaluations((previousEvaluations) => {
          const otherEvaluations = previousEvaluations.filter(
            (evaluation) => evaluation.id !== savedEvaluation.id,
          );
          return [savedEvaluation, ...otherEvaluations].sort(compareEvaluationsByCycleName);
        });
        setNineBoxMatrix((currentMatrix) =>
          updateMatrixWithEvaluation(currentMatrix, selectedEmployee, savedEvaluation),
        );
        setSelectedMatrixCellCode(savedEvaluation.nine_box_code);
      });
      setSaveMessage(selectedEvaluation ? "Draft updated." : "Draft created.");
    } catch (error) {
      const message =
        error instanceof ApiError
          ? error.message
          : "Unable to save the evaluation draft.";

      if (error instanceof ApiError && error.status === 401) {
        onSessionError(message);
        return;
      }

      setWorkflowError(message);
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <div className="page-shell">
      <main className="shell-layout">
        <section className="hero-copy">
          <p className="eyebrow">Manager Workflow</p>
          <h1>{appName}</h1>
          <p className="lede">
            View the employees in your reporting line, open a draft evaluation,
            save structured ratings with simple narrative notes, and review a
            first-pass 9-box matrix for the selected cycle.
          </p>
          <div className="button-row">
            <button
              className="button-link"
              type="button"
              onClick={onRefreshCurrentUser}
              disabled={isRefreshing}
            >
              {isRefreshing ? "Refreshing..." : "Refresh current user"}
            </button>
            <button className="ghost-button" type="button" onClick={onSignOut}>
              Sign out
            </button>
          </div>
        </section>

        <section className="panel">
          <h2>Signed in as</h2>
          <dl className="details-list">
            <div>
              <dt>Name</dt>
              <dd>{currentUser.full_name}</dd>
            </div>
            <div>
              <dt>Username</dt>
              <dd>{currentUser.username}</dd>
            </div>
            <div>
              <dt>Roles</dt>
              <dd>{currentUser.roles.map(formatRole).join(", ")}</dd>
            </div>
          </dl>
          <p className="supporting-text">
            The first pass keeps evaluations simple: one draft per employee per
            review cycle, with explicit save actions and server-side permission
            checks. The 9-box view uses the saved evaluation rating and
            potential input for the selected cycle.
          </p>
        </section>
      </main>

      <section className="workflow-grid" aria-label="Manager evaluation workspace">
        <section className="panel employee-panel">
          <h2>Your employees</h2>
          {isLoadingWorkspace ? (
            <p className="supporting-text">Loading authorized employees...</p>
          ) : employees.length === 0 ? (
            <p className="supporting-text">
              No report employees are available for this account yet.
            </p>
          ) : (
            <div className="employee-list" role="list">
              {employees.map((employee) => (
                <button
                  className={`employee-card${
                    employee.id === selectedEmployeeId ? " employee-card-selected" : ""
                  }`}
                  key={employee.id}
                  type="button"
                  onClick={() => {
                    setSelectedEmployeeId(employee.id);
                    setSaveMessage(null);
                    setWorkflowError(null);
                  }}
                >
                  <span className="employee-card-name">{employee.full_name}</span>
                  <span className="employee-card-meta">{employee.job_title}</span>
                  <span className="employee-card-meta">{employee.department}</span>
                </button>
              ))}
            </div>
          )}
        </section>

        <section className="panel editor-panel">
          <div className="editor-header">
            <div>
              <h2>Draft evaluation</h2>
              {selectedEmployee ? (
                <p className="supporting-text">
                  {selectedEmployee.full_name}
                  {" · "}
                  {selectedEmployee.job_title}
                  {" · "}
                  {selectedEmployee.department}
                </p>
              ) : (
                <p className="supporting-text">
                  Choose an employee from the left to begin.
                </p>
              )}
            </div>

            <label className="field compact-field">
              <span>Review cycle</span>
              <select
                value={selectedReviewCycleId ?? ""}
                onChange={(event) => {
                  setSelectedReviewCycleId(Number.parseInt(event.target.value, 10));
                  setSaveMessage(null);
                  setWorkflowError(null);
                }}
                disabled={isLoadingWorkspace || reviewCycles.length === 0}
              >
                {reviewCycles.map((reviewCycle) => (
                  <option key={reviewCycle.id} value={reviewCycle.id}>
                    {reviewCycle.name}
                  </option>
                ))}
              </select>
            </label>
          </div>

          {workflowError ? <p className="error-text">{workflowError}</p> : null}
          {saveMessage ? <p className="success-text">{saveMessage}</p> : null}

          {selectedEmployee && selectedReviewCycle ? (
            <form className="evaluation-form" onSubmit={handleSaveDraft}>
              <div className="field-grid">
                <label className="field">
                  <span>Performance rating (0.00 to 5.00)</span>
                  <input
                    name="performanceRating"
                    type="number"
                    inputMode="decimal"
                    min="0"
                    max="5"
                    step="0.01"
                    value={draft.performanceRating}
                    onChange={(event) => {
                      setDraft((currentDraft) => ({
                        ...currentDraft,
                        performanceRating: event.target.value,
                      }));
                      setSaveMessage(null);
                    }}
                    placeholder="3.75"
                    required
                  />
                </label>

                <label className="field">
                  <span>Potential rating (1 to 3)</span>
                  <select
                    name="potentialRating"
                    value={draft.potentialRating}
                    onChange={(event) => {
                      setDraft((currentDraft) => ({
                        ...currentDraft,
                        potentialRating: event.target.value,
                      }));
                      setSaveMessage(null);
                    }}
                  >
                    <option value="1">1 · Lower potential right now</option>
                    <option value="2">2 · Developing steadily</option>
                    <option value="3">3 · Strong growth potential</option>
                  </select>
                </label>
              </div>

              <label className="field">
                <span>Narrative notes</span>
                <textarea
                  name="summaryComment"
                  value={draft.summaryComment}
                  onChange={(event) => {
                    setDraft((currentDraft) => ({
                      ...currentDraft,
                      summaryComment: event.target.value,
                    }));
                    setSaveMessage(null);
                  }}
                  placeholder="Summarize the employee's current performance, momentum, and coaching themes."
                  rows={8}
                />
              </label>

              <div className="button-row">
                <button className="submit-button" type="submit" disabled={isSaving}>
                  {isSaving
                    ? "Saving..."
                    : selectedEvaluation
                      ? "Save draft changes"
                      : "Create draft"}
                </button>
              </div>

              <p className="supporting-text">
                {selectedEvaluation
                  ? `Editing the existing ${selectedReviewCycle.name} draft for ${selectedEmployee.full_name}.`
                  : `No draft exists yet for ${selectedEmployee.full_name} in ${selectedReviewCycle.name}.`}
              </p>
              {selectedEvaluation ? (
                <p className="supporting-text">
                  Current 9-box placement: {selectedEvaluation.nine_box_label}
                </p>
              ) : null}
            </form>
          ) : (
            <p className="supporting-text">
              Choose an employee and review cycle to start an evaluation draft.
            </p>
          )}
        </section>

        <section className="panel history-panel">
          <h2>Existing evaluations</h2>
          {isLoadingEvaluations ? (
            <p className="supporting-text">Loading evaluations...</p>
          ) : selectedEvaluation || priorEvaluations.length > 0 ? (
            <div className="history-list">
              {selectedEvaluation ? (
                <article className="history-card" key={selectedEvaluation.id}>
                  <p className="history-card-eyebrow">Current working cycle</p>
                  <h3>{selectedEvaluation.review_cycle_name}</h3>
                  <p className="history-card-rating">
                    Performance {selectedEvaluation.performance_rating.toFixed(2)}
                    {" · "}
                    Potential {selectedEvaluation.potential_rating}
                  </p>
                  <p className="history-card-rating">
                    9-Box {selectedEvaluation.nine_box_label}
                  </p>
                  <p>{selectedEvaluation.summary_comment ?? "No narrative notes saved yet."}</p>
                </article>
              ) : null}

              {priorEvaluations.map((evaluation) => (
                <article className="history-card" key={evaluation.id}>
                  <p className="history-card-eyebrow">Saved evaluation</p>
                  <h3>{evaluation.review_cycle_name}</h3>
                  <p className="history-card-rating">
                    Performance {evaluation.performance_rating.toFixed(2)}
                    {" · "}
                    Potential {evaluation.potential_rating}
                  </p>
                  <p className="history-card-rating">9-Box {evaluation.nine_box_label}</p>
                  <p>{evaluation.summary_comment ?? "No narrative notes were saved."}</p>
                </article>
              ))}
            </div>
          ) : (
            <p className="supporting-text">
              No draft or prior evaluations are available for the selected employee yet.
            </p>
          )}
        </section>
      </section>

      <section className="panel nine-box-panel" aria-label="9-box matrix">
        <div className="editor-header">
          <div>
            <h2>9-box matrix</h2>
            <p className="supporting-text">
              This first slice shows employees with saved evaluations in the selected cycle.
            </p>
          </div>
          {nineBoxMatrix ? (
            <p className="supporting-text">
              {nineBoxMatrix.review_cycle_name}
              {" · "}
              {formatEmployeeCount(nineBoxMatrix.total_employees)}
            </p>
          ) : null}
        </div>

        {isLoadingNineBox ? (
          <p className="supporting-text">Loading the 9-box matrix...</p>
        ) : nineBoxMatrix ? (
          <div className="nine-box-layout">
            <section>
              <div className="nine-box-column-headings" aria-hidden="true">
                <span />
                <span>At-Risk</span>
                <span>Effective</span>
                <span>High</span>
              </div>

              <div className="nine-box-board" role="grid" aria-label="9-box placement matrix">
                {POTENTIAL_ROW_ORDER.map((potentialTier) => (
                  <div className="nine-box-row" key={potentialTier} role="row">
                    <div className="nine-box-row-label">
                      {getMatrixCell(nineBoxMatrix, potentialTier, "at_risk")?.potential_label ??
                        "Potential"}
                    </div>
                    {PERFORMANCE_COLUMN_ORDER.map((performanceTier) => {
                      const cell = getMatrixCell(
                        nineBoxMatrix,
                        potentialTier,
                        performanceTier,
                      );

                      if (!cell) {
                        return <div className="nine-box-cell" key={performanceTier} />;
                      }

                      const isSelected = cell.box_code === selectedMatrixCell?.box_code;
                      return (
                        <button
                          className={`nine-box-cell-button${
                            isSelected ? " nine-box-cell-button-selected" : ""
                          }`}
                          key={cell.box_code}
                          type="button"
                          onClick={() => {
                            setSelectedMatrixCellCode(cell.box_code);
                            if (cell.employees[0]) {
                              setSelectedEmployeeId(cell.employees[0].employee_id);
                            }
                          }}
                        >
                          <span className="nine-box-cell-label">{cell.box_label}</span>
                          <span className="nine-box-cell-count">
                            {formatEmployeeCount(cell.employee_count)}
                          </span>
                        </button>
                      );
                    })}
                  </div>
                ))}
              </div>
            </section>

            <section className="nine-box-drilldown">
              {selectedMatrixCell ? (
                <>
                  <h3>{selectedMatrixCell.box_label}</h3>
                  <p className="supporting-text">
                    {selectedMatrixCell.potential_label}
                    {" · "}
                    {selectedMatrixCell.performance_label}
                  </p>

                  {selectedMatrixCell.employee_count === 0 ? (
                    <p className="supporting-text">
                      No employees currently land in this cell for the selected review cycle.
                    </p>
                  ) : (
                    <div className="employee-list" role="list">
                      {selectedMatrixCell.employees.map((employee) => (
                        <button
                          className={`employee-card${
                            employee.employee_id === selectedMatrixEmployee?.employee_id
                              ? " employee-card-selected"
                              : ""
                          }`}
                          key={employee.evaluation_id}
                          type="button"
                          onClick={() => setSelectedEmployeeId(employee.employee_id)}
                        >
                          <span className="employee-card-name">{employee.employee_name}</span>
                          <span className="employee-card-meta">{employee.job_title}</span>
                          <span className="employee-card-meta">
                            Performance {employee.performance_rating.toFixed(2)}
                            {" · "}
                            Potential {employee.potential_rating}
                          </span>
                        </button>
                      ))}
                    </div>
                  )}

                  {selectedMatrixEmployee ? (
                    <article className="history-card matrix-detail-card">
                      <p className="history-card-eyebrow">Employee detail</p>
                      <h3>{selectedMatrixEmployee.employee_name}</h3>
                      <p className="history-card-rating">
                        {selectedMatrixEmployee.nine_box_label}
                        {" · "}
                        Performance {selectedMatrixEmployee.performance_rating.toFixed(2)}
                        {" · "}
                        Potential {selectedMatrixEmployee.potential_rating}
                      </p>
                      <p>{selectedMatrixEmployee.job_title}</p>
                      <p>{selectedMatrixEmployee.department}</p>
                      <p>
                        Manager: {selectedMatrixEmployee.manager_name ?? "No manager assigned"}
                      </p>
                      <p>
                        {selectedMatrixEmployee.summary_comment ??
                          "No narrative note is saved for this evaluation yet."}
                      </p>
                    </article>
                  ) : null}
                </>
              ) : (
                <p className="supporting-text">
                  Select a matrix cell to review the employees in that placement.
                </p>
              )}
            </section>
          </div>
        ) : (
          <p className="supporting-text">
            Choose a review cycle to load the first 9-box view.
          </p>
        )}
      </section>
    </div>
  );
}

function App() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [token, setToken] = useState<string | null>(null);
  const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);

  async function handleLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErrorMessage(null);
    setIsSubmitting(true);

    try {
      const authResponse = await login({ username, password });
      const user = await getCurrentUser(authResponse.access_token);

      startTransition(() => {
        setToken(authResponse.access_token);
        setCurrentUser(user);
      });

      setPassword("");
    } catch (error) {
      const message =
        error instanceof ApiError
          ? error.message
          : "Unable to sign in right now.";

      startTransition(() => {
        setToken(null);
        setCurrentUser(null);
      });
      setErrorMessage(message);
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleRefreshCurrentUser() {
    if (!token) {
      return;
    }

    setErrorMessage(null);
    setIsRefreshing(true);

    try {
      const user = await getCurrentUser(token);
      startTransition(() => {
        setCurrentUser(user);
      });
    } catch (error) {
      const message =
        error instanceof ApiError
          ? error.message
          : "Unable to refresh the current user.";

      startTransition(() => {
        setToken(null);
        setCurrentUser(null);
      });
      setErrorMessage(message);
    } finally {
      setIsRefreshing(false);
    }
  }

  function handleSessionError(message: string) {
    startTransition(() => {
      setToken(null);
      setCurrentUser(null);
    });
    setPassword("");
    setErrorMessage(message);
  }

  function handleSignOut() {
    startTransition(() => {
      setToken(null);
      setCurrentUser(null);
    });
    setPassword("");
    setErrorMessage(null);
  }

  if (currentUser && token) {
    if (isManagerWorkflowUser(currentUser)) {
      return (
        <ManagerWorkspace
          currentUser={currentUser}
          token={token}
          isRefreshing={isRefreshing}
          onRefreshCurrentUser={handleRefreshCurrentUser}
          onSessionError={handleSessionError}
          onSignOut={handleSignOut}
        />
      );
    }

    return (
      <AuthenticatedShell
        currentUser={currentUser}
        isRefreshing={isRefreshing}
        onRefreshCurrentUser={handleRefreshCurrentUser}
        onSignOut={handleSignOut}
      />
    );
  }

  return (
    <div className="page-shell">
      <main className="hero">
        <section className="hero-copy">
          <p className="eyebrow">Manager Workflow</p>
          <h1>{appName}</h1>
          <p className="lede">
            Sign in with a locally managed demo account to view your authorized
            employees and create or edit draft evaluations with structured
            ratings and narrative notes.
          </p>
          <a
            className="button-link"
            href={`${API_BASE_URL}/health`}
            target="_blank"
            rel="noreferrer"
          >
            Backend health endpoint
          </a>
        </section>

        <section className="panel">
          <h2>Sign in</h2>
          <form className="login-form" onSubmit={handleLogin}>
            <label className="field">
              <span>Username</span>
              <input
                autoComplete="username"
                name="username"
                type="text"
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                placeholder="manager.avery"
                required
              />
            </label>

            <label className="field">
              <span>Password</span>
              <input
                autoComplete="current-password"
                name="password"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="Enter the demo password"
                required
              />
            </label>

            {errorMessage ? <p className="error-text">{errorMessage}</p> : null}

            <button className="submit-button" type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Signing in..." : "Sign in"}
            </button>
          </form>

          <p className="supporting-text">
            Demo credentials and setup steps are documented in the repository
            README. The frontend keeps the access token in memory only, so
            refreshing the page signs you out.
          </p>
        </section>
      </main>

      <section className="notes-grid" aria-label="Project notes">
        <article className="note-card">
          <h2>Manager workflow</h2>
          <p>
            The first UI flow lets managers view report employees, open a draft
            evaluation for a selected review cycle, save ratings plus
            narrative notes, and review a simple 9-box matrix.
          </p>
        </article>

        <article className="note-card">
          <h2>Simple by design</h2>
          <p>
            This pass does not add approvals, publishing, calibration, or
            advanced workflow engines. It focuses on an easy-to-follow draft
            editing experience.
          </p>
        </article>

        <article className="note-card">
          <h2>API base URL</h2>
          <p className="api-line">{API_BASE_URL}</p>
        </article>
      </section>
    </div>
  );
}

export default App;
