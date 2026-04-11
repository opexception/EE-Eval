export interface LoginRequest {
  username: string;
  password: string;
}

export interface AuthTokenResponse {
  access_token: string;
  token_type: string;
  expires_in_seconds: number;
}

export interface CurrentUser {
  id: number;
  username: string;
  full_name: string;
  auth_provider: string;
  roles: string[];
  is_active: boolean;
}

export interface Employee {
  id: number;
  employee_number: string;
  first_name: string;
  last_name: string;
  full_name: string;
  job_title: string;
  department: string;
  manager_id: number | null;
  manager_name: string | null;
  is_active: boolean;
}

export interface ReviewCycle {
  id: number;
  name: string;
  cycle_type: string;
  start_date: string;
  end_date: string;
  status: string;
  created_by_user_id: number;
  updated_by_user_id: number;
}

export interface Evaluation {
  id: number;
  employee_id: number;
  employee_name: string;
  review_cycle_id: number;
  review_cycle_name: string;
  author_user_id: number;
  updated_by_user_id: number;
  performance_rating: number;
  potential_rating: number;
  performance_tier: string;
  potential_tier: string;
  nine_box_code: string;
  nine_box_label: string;
  summary_comment: string | null;
  status: string;
}

export interface NineBoxEmployee {
  employee_id: number;
  employee_number: string;
  employee_name: string;
  job_title: string;
  department: string;
  manager_name: string | null;
  is_active: boolean;
  evaluation_id: number;
  performance_rating: number;
  potential_rating: number;
  performance_tier: string;
  potential_tier: string;
  nine_box_code: string;
  nine_box_label: string;
  summary_comment: string | null;
  evaluation_status: string;
}

export interface NineBoxCell {
  box_code: string;
  box_label: string;
  performance_tier: string;
  performance_label: string;
  potential_tier: string;
  potential_label: string;
  employee_count: number;
  employees: NineBoxEmployee[];
}

export interface NineBoxMatrix {
  review_cycle_id: number;
  review_cycle_name: string;
  review_cycle_status: string;
  total_employees: number;
  cells: NineBoxCell[];
}

export interface EvaluationSaveRequest {
  performance_rating: number;
  potential_rating: number;
  summary_comment: string | null;
  status: string;
}

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function readErrorMessage(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as { detail?: string };
    if (body.detail) {
      return body.detail;
    }
  } catch {
    return "Request failed.";
  }

  return "Request failed.";
}

async function requestJson<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, init);
  if (!response.ok) {
    throw new ApiError(await readErrorMessage(response), response.status);
  }

  return (await response.json()) as T;
}

function createAuthHeaders(token: string, headers?: HeadersInit): HeadersInit {
  return {
    ...(headers ?? {}),
    Authorization: `Bearer ${token}`,
  };
}

function buildQuery(
  params: Record<string, string | number | boolean | undefined>,
): string {
  const searchParams = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined) {
      continue;
    }

    searchParams.set(key, String(value));
  }

  const query = searchParams.toString();
  return query ? `?${query}` : "";
}

export function login(request: LoginRequest): Promise<AuthTokenResponse> {
  return requestJson<AuthTokenResponse>("/auth/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });
}

export function getCurrentUser(token: string): Promise<CurrentUser> {
  return requestJson<CurrentUser>("/auth/me", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

export function getEmployees(
  token: string,
  options?: { reportsOnly?: boolean },
): Promise<Employee[]> {
  const query = buildQuery({
    reports_only: options?.reportsOnly,
  });

  return requestJson<Employee[]>(`/employees${query}`, {
    headers: createAuthHeaders(token),
  });
}

export function getReviewCycles(token: string): Promise<ReviewCycle[]> {
  return requestJson<ReviewCycle[]>("/review-cycles", {
    headers: createAuthHeaders(token),
  });
}

export function getEvaluations(
  token: string,
  options?: { employeeId?: number; reviewCycleId?: number },
): Promise<Evaluation[]> {
  const query = buildQuery({
    employee_id: options?.employeeId,
    review_cycle_id: options?.reviewCycleId,
  });

  return requestJson<Evaluation[]>(`/evaluations${query}`, {
    headers: createAuthHeaders(token),
  });
}

export function getNineBoxMatrix(
  token: string,
  options?: { reviewCycleId?: number },
): Promise<NineBoxMatrix> {
  const query = buildQuery({
    review_cycle_id: options?.reviewCycleId,
  });

  return requestJson<NineBoxMatrix>(`/nine-box${query}`, {
    headers: createAuthHeaders(token),
  });
}

export function createEvaluation(
  token: string,
  request: EvaluationSaveRequest & {
    employee_id: number;
    review_cycle_id: number;
  },
): Promise<Evaluation> {
  return requestJson<Evaluation>("/evaluations", {
    method: "POST",
    headers: createAuthHeaders(token, {
      "Content-Type": "application/json",
    }),
    body: JSON.stringify(request),
  });
}

export function updateEvaluation(
  token: string,
  evaluationId: number,
  request: EvaluationSaveRequest,
): Promise<Evaluation> {
  return requestJson<Evaluation>(`/evaluations/${evaluationId}`, {
    method: "PUT",
    headers: createAuthHeaders(token, {
      "Content-Type": "application/json",
    }),
    body: JSON.stringify(request),
  });
}
