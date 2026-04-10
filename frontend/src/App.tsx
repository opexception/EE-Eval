import { FormEvent, startTransition, useState } from "react";

import { API_BASE_URL, ApiError, getCurrentUser, login, type CurrentUser } from "./api";
import "./index.css";

const appName = import.meta.env.VITE_APP_NAME ?? "EE-Eval";

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

  function handleSignOut() {
    startTransition(() => {
      setToken(null);
      setCurrentUser(null);
    });
    setPassword("");
    setErrorMessage(null);
  }

  if (currentUser) {
    return (
      <div className="page-shell">
        <main className="shell-layout">
          <section className="hero-copy">
            <p className="eyebrow">Authenticated Shell</p>
            <h1>{appName}</h1>
            <p className="lede">
              Local sign-in is active, the backend knows who you are, and role
              checks are ready for future protected workflows.
            </p>
            <div className="button-row">
              <button
                className="button-link"
                type="button"
                onClick={handleRefreshCurrentUser}
                disabled={isRefreshing}
              >
                {isRefreshing ? "Refreshing..." : "Refresh current user"}
              </button>
              <button className="ghost-button" type="button" onClick={handleSignOut}>
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
                  {role}
                </span>
              ))}
            </div>
          </section>
        </main>

        <section className="notes-grid" aria-label="Authenticated notes">
          <article className="note-card">
            <h2>Available now</h2>
            <p>
              Login, current-user lookup, server-side role checks, and
              development-only seeded demo users are available for local
              development.
            </p>
          </article>

          <article className="note-card">
            <h2>Still deferred</h2>
            <p>
              LDAP integration, password reset flows, audit history, and
              employee evaluation workflows remain intentionally out of scope for
              this first pass.
            </p>
          </article>

          <article className="note-card">
            <h2>Backend endpoints</h2>
            <p className="api-line">{API_BASE_URL}/auth/login</p>
            <p className="api-line">{API_BASE_URL}/auth/me</p>
            <p className="api-line">{API_BASE_URL}/health</p>
          </article>
        </section>
      </div>
    );
  }

  return (
    <div className="page-shell">
      <main className="hero">
        <section className="hero-copy">
          <p className="eyebrow">Local Authentication</p>
          <h1>{appName}</h1>
          <p className="lede">
            Sign in with a locally managed demo account to reach the first
            authenticated shell. Business workflows are still intentionally
            hidden until the access model is in place.
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
                placeholder="hr.harper"
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
            README. For a conservative first pass, the frontend keeps the access
            token in memory only, so refreshing the page signs you out.
          </p>
        </section>
      </main>

      <section className="notes-grid" aria-label="Project notes">
        <article className="note-card">
          <h2>Included right now</h2>
          <p>
            The repository contains local database-backed users, secure password
            hashing, a login endpoint, a current-user endpoint, seeded fake
            users for development, and server-side role-check scaffolding.
          </p>
        </article>

        <article className="note-card">
          <h2>Not included yet</h2>
          <p>
            LDAP, password reset, audit reporting, and employee evaluation
            workflows are intentionally deferred to later roadmap phases.
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
