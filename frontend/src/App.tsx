import "./index.css";

const stackItems = [
  { label: "Backend", value: "FastAPI" },
  { label: "Frontend", value: "React + TypeScript + Vite" },
  { label: "Database", value: "PostgreSQL" },
  { label: "Local runtime", value: "Docker Compose" },
];

const appName = import.meta.env.VITE_APP_NAME ?? "EE-Eval";

function App() {
  return (
    <div className="page-shell">
      <main className="hero">
        <section className="hero-copy">
          <p className="eyebrow">Phase 0 Scaffold</p>
          <h1>{appName}</h1>
          <p className="lede">
            A simple monorepo foundation for a sensitive HR evaluation
            application. This first slice focuses on local setup, readability,
            and a clear path for the next phases.
          </p>
          <a
            className="button-link"
            href="http://localhost:8000/api/health"
            target="_blank"
            rel="noreferrer"
          >
            Backend health endpoint
          </a>
        </section>

        <section className="panel">
          <h2>Current stack</h2>
          <ul className="stack-list">
            {stackItems.map((item) => (
              <li key={item.label}>
                <span>{item.label}</span>
                <strong>{item.value}</strong>
              </li>
            ))}
          </ul>
        </section>
      </main>

      <section className="notes-grid" aria-label="Project notes">
        <article className="note-card">
          <h2>Included right now</h2>
          <p>
            The repository contains a FastAPI backend with configuration,
            PostgreSQL connectivity, Alembic migration tooling, a React landing
            page, and example environment files for local development.
          </p>
        </article>

        <article className="note-card">
          <h2>Not included yet</h2>
          <p>
            Business workflows, authentication, authorization, and real
            employee-facing data models are intentionally deferred to later
            roadmap phases.
          </p>
        </article>
      </section>
    </div>
  );
}

export default App;
