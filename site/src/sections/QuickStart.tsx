export function QuickStart() {
  return (
    <section className="sec" id="start">
      <div className="wrap">
        <h2>Start a <span className="m">local cluster.</span></h2>
        <p className="lead2">Python 3.12+, uv, Docker, and PostgreSQL are used by the development stack.</p>
        <div className="steps qs">
          <article className="step">
            <h3>1. Install</h3>
            <p>Resolve the locked Python dependencies.</p>
            <pre className="code">uv sync --frozen --extra dev --all-extras</pre>
          </article>
          <article className="step">
            <h3>2. Configure</h3>
            <p>Copy the example settings and set worker/admin secrets.</p>
            <pre className="code">Copy-Item .env.example .env</pre>
          </article>
          <article className="step">
            <h3>3. Run</h3>
            <p>Start the coordinator, database, and workers.</p>
            <pre className="code">docker compose up --build</pre>
          </article>
        </div>
        <p className="note">The browser lab above is self-contained. It does not submit jobs to a server.</p>
      </div>
    </section>
  );
}
