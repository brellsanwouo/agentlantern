---
layout: home

hero:
  name: AgentLantern
  text: Developer tools for AI agent projects
  tagline: Generate clean architecture docs, lint agent design, inspect project structure, and watch supported agent runs in a live animated playground.
  image:
    src: /assets/logo.png
    alt: AgentLantern logo
  actions:
    - theme: brand
      text: Get Started
      link: /installation
    - theme: alt
      text: CLI Guide
      link: /usage
    - theme: alt
      text: lantern play
      link: /play
    - theme: alt
      text: Join Discord
      link: https://discord.gg/Ycc29yp4xQ

features:
  - title: Document agent systems
    details: Generate a browsable docs site with overview, architecture, diagrams, agents, tasks, runbook, and contacts.
  - title: Lint before runtime
    details: Catch missing fields, broken references, idle agents, risky config, and CI-facing issues without calling an LLM.
  - title: Watch runs live
    details: Start, stop, replay, and inspect supported agent runs inside a pixel-art execution environment.
---

<div class="agentlantern-product-strip">
  <div class="agentlantern-hero-mark">
    <img src="./assets/logo-horizontal.png" alt="AgentLantern" />
  </div>
  <div class="agentlantern-version-strip">
    <a href="./changelog">Current version: v0.1.22</a>
    <span>CLI, Play, Replay, docs, and lint tooling</span>
  </div>
</div>

<a class="agentlantern-discord-cta" href="https://discord.gg/Ycc29yp4xQ">
  <span class="agentlantern-discord-cta__icon">
    <svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M20.317 4.369A19.79 19.79 0 0 0 15.362 2.8a.074.074 0 0 0-.079.037c-.214.38-.452.875-.619 1.265a18.27 18.27 0 0 0-5.487 0a12.64 12.64 0 0 0-.63-1.265a.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.51 4.37a.07.07 0 0 0-.032.027C.534 8.796-.268 13.085.128 17.322a.082.082 0 0 0 .031.056a19.9 19.9 0 0 0 6.073 3.071a.078.078 0 0 0 .084-.027c.468-.64.885-1.316 1.238-2.026a.076.076 0 0 0-.041-.105a13.18 13.18 0 0 1-1.872-.893a.077.077 0 0 1-.008-.128c.126-.094.252-.192.372-.291a.074.074 0 0 1 .078-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .079.009c.12.099.246.198.373.292a.077.077 0 0 1-.006.128c-.6.35-1.224.647-1.873.892a.077.077 0 0 0-.041.106c.36.709.777 1.385 1.237 2.025a.076.076 0 0 0 .084.028a19.84 19.84 0 0 0 6.082-3.072a.077.077 0 0 0 .032-.055c.474-4.9-.796-9.154-3.764-12.925a.061.061 0 0 0-.031-.028ZM8.02 14.742c-1.183 0-2.157-1.085-2.157-2.419c0-1.333.955-2.418 2.157-2.418c1.21 0 2.176 1.095 2.157 2.418c0 1.334-.955 2.419-2.157 2.419Zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419c0-1.333.955-2.418 2.157-2.418c1.211 0 2.176 1.095 2.157 2.418c0 1.334-.946 2.419-2.157 2.419Z"/></svg>
  </span>
  <span>
    <strong>Join the AgentLantern community on Discord</strong>
    <em>Meet builders, learn together, follow updates, share ideas, and contribute to the project.</em>
  </span>
  <b>Join now</b>
</a>

<!-- <div class="agentlantern-pill-row">
  <span class="agentlantern-pill">Multi-framework direction</span>
  <span class="agentlantern-pill">CrewAI deep support today</span>
  <span class="agentlantern-pill">VitePress + GitHub Pages ready</span>
</div> -->

<div class="agentlantern-frameworks" aria-label="Agent framework support">
  <div class="agentlantern-frameworks__intro">
    <span>Framework support</span>
    <strong>Available for CrewAI today. Others are coming soon.</strong>
  </div>
  <div class="agentlantern-framework-grid">
    <div class="agentlantern-framework-card agentlantern-framework-card--available">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12.482.18C7.161 1.319 1.478 9.069 1.426 15.372c-.051 5.527 3.1 8.68 8.68 8.627c6.716-.05 14.259-6.87 12.09-10.9c-.672-1.292-1.396-1.344-2.687-.207c-1.602 1.395-1.654.31-.207-2.893c1.757-3.98 1.705-5.322-.31-7.544C17.03.388 14.962-.388 12.482.181Zm5.322 2.068c2.273 2.015 2.376 4.236.465 8.42c-1.395 3.1-2.17 3.515-3.824 1.86c-1.24-1.24-1.343-3.46-.258-6.044c1.137-2.635.982-3.1-.568-1.653c-3.72 3.358-6.458 9.765-5.424 12.503c.464 1.189.825 1.395 2.737 1.395c2.79 0 6.303-1.705 7.957-3.926c1.756-2.274 2.79-2.274 2.79-.052c0 3.875-6.459 8.627-11.625 8.627c-6.251 0-9.351-4.752-7.491-11.47c.878-2.995 4.443-7.904 7.077-9.66c3.255-2.17 5.684-2.17 8.164 0"/></svg>
      <strong>CrewAI</strong>
      <span>Available</span>
    </div>
    <div class="agentlantern-framework-card">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M5 19h5a5 5 0 1 1-5-5Zm14-5a5 5 0 1 1-5 5h5Zm-9-9a5 5 0 1 0-5 5V5Zm9 0v5a5 5 0 1 0-5-5Z"/></svg>
      <strong>LangGraph</strong>
      <span>Coming soon</span>
    </div>
    <div class="agentlantern-framework-card">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M0 0v11.408h11.408V0zm12.594 0v11.408H24V0zM0 12.594V24h11.408V12.594zm12.594 0V24H24V12.594z"/></svg>
      <strong>AutoGen</strong>
      <span>Coming soon</span>
    </div>
    <div class="agentlantern-framework-card">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12.025 1.13c-5.77 0-10.449 4.647-10.449 10.378c0 1.112.178 2.181.503 3.185c.064-.222.203-.444.416-.577a.96.96 0 0 1 .524-.15c.293 0 .584.124.84.284c.278.173.48.408.71.694c.226.282.458.611.684.951v-.014c.017-.324.106-.622.264-.874s.403-.487.762-.543c.3-.047.596.06.787.203s.31.313.4.467c.15.257.212.468.233.542c.01.026.653 1.552 1.657 2.54c.616.605 1.01 1.223 1.082 1.912c.055.537-.096 1.059-.38 1.572c.637.121 1.294.187 1.967.187c.657 0 1.298-.063 1.921-.178c-.287-.517-.44-1.041-.384-1.581c.07-.69.465-1.307 1.081-1.913c1.004-.987 1.647-2.513 1.657-2.539c.021-.074.083-.285.233-.542c.09-.154.208-.323.4-.467a1.08 1.08 0 0 1 .787-.203c.359.056.604.29.762.543s.247.55.265.874v.015c.225-.34.457-.67.683-.952c.23-.286.432-.52.71-.694c.257-.16.547-.284.84-.285a.97.97 0 0 1 .524.151c.228.143.373.388.43.625l.006.04a10.3 10.3 0 0 0 .534-3.273c0-5.731-4.678-10.378-10.449-10.378M8.327 6.583a1.5 1.5 0 0 1 .713.174a1.487 1.487 0 0 1 .617 2.013c-.183.343-.762-.214-1.102-.094c-.38.134-.532.914-.917.71a1.487 1.487 0 0 1 .69-2.803m7.486 0a1.487 1.487 0 0 1 .689 2.803c-.385.204-.536-.576-.916-.71c-.34-.12-.92.437-1.103.094a1.487 1.487 0 0 1 .617-2.013a1.5 1.5 0 0 1 .713-.174m-10.68 1.55a.96.96 0 1 1 0 1.921a.96.96 0 0 1 0-1.92m13.838 0a.96.96 0 1 1 0 1.92a.96.96 0 0 1 0-1.92M8.489 11.458c.588.01 1.965 1.157 3.572 1.164c1.607-.007 2.984-1.155 3.572-1.164c.196-.003.305.12.305.454c0 .886-.424 2.328-1.563 3.202c-.22-.756-1.396-1.366-1.63-1.32q-.011.001-.02.006l-.044.026l-.01.008l-.03.024q-.018.017-.035.036l-.032.04a1 1 0 0 0-.058.09l-.014.025q-.049.088-.11.19a1 1 0 0 1-.083.116a1.2 1.2 0 0 1-.173.18q-.035.029-.075.058a1.3 1.3 0 0 1-.251-.243a1 1 0 0 1-.076-.107c-.124-.193-.177-.363-.337-.444c-.034-.016-.104-.008-.2.022q-.094.03-.216.087q-.06.028-.125.063l-.13.074q-.067.04-.136.086a3 3 0 0 0-.135.096a3 3 0 0 0-.26.219a2 2 0 0 0-.12.121a2 2 0 0 0-.106.128l-.002.002a2 2 0 0 0-.09.132l-.001.001a1.2 1.2 0 0 0-.105.212q-.013.036-.024.073c-1.139-.875-1.563-2.317-1.563-3.203c0-.334.109-.457.305-.454m.836 10.354c.824-1.19.766-2.082-.365-3.194c-1.13-1.112-1.789-2.738-1.789-2.738s-.246-.945-.806-.858s-.97 1.499.202 2.362c1.173.864-.233 1.45-.685.64c-.45-.812-1.683-2.896-2.322-3.295s-1.089-.175-.938.647s2.822 2.813 2.562 3.244s-1.176-.506-1.176-.506s-2.866-2.567-3.49-1.898s.473 1.23 2.037 2.16c1.564.932 1.686 1.178 1.464 1.53s-3.675-2.511-4-1.297c-.323 1.214 3.524 1.567 3.287 2.405c-.238.839-2.71-1.587-3.216-.642c-.506.946 3.49 2.056 3.522 2.064c1.29.33 4.568 1.028 5.713-.624m5.349 0c-.824-1.19-.766-2.082.365-3.194c1.13-1.112 1.789-2.738 1.789-2.738s.246-.945.806-.858s.97 1.499-.202 2.362c-1.173.864.233 1.45.685.64c.451-.812 1.683-2.896 2.322-3.295s1.089-.175.938.647s-2.822 2.813-2.562 3.244s1.176-.506 1.176-.506s2.866-2.567 3.49-1.898s-.473 1.23-2.037 2.16c-1.564.932-1.686 1.178-1.464 1.53s3.675-2.511 4-1.297c.323 1.214-3.524 1.567-3.287 2.405c.238.839 2.71-1.587 3.216-.642c.506.946-3.49 2.056-3.522 2.064c-1.29.33-4.568 1.028-5.713-.624"/></svg>
      <strong>Smolagents</strong>
      <span>Coming soon</span>
    </div>
    <div class="agentlantern-framework-card">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M11.04 19.32Q12 21.51 12 24q0-2.49.93-4.68q.96-2.19 2.58-3.81t3.81-2.55Q21.51 12 24 12q-2.49 0-4.68-.93a12.3 12.3 0 0 1-3.81-2.58a12.3 12.3 0 0 1-2.58-3.81Q12 2.49 12 0q0 2.49-.96 4.68q-.93 2.19-2.55 3.81a12.3 12.3 0 0 1-3.81 2.58Q2.49 12 0 12q2.49 0 4.68.96q2.19.93 3.81 2.55t2.55 3.81"/></svg>
      <strong>Google ADK</strong>
      <span>Coming soon</span>
    </div>
  </div>
</div>

<div class="agentlantern-command-grid">
  <div class="agentlantern-command">
    <strong>lantern docs</strong>
    <span>Generate Markdown and a static docs site from an agent project.</span>
  </div>
  <div class="agentlantern-command">
    <strong>lantern lint</strong>
    <span>Run deterministic project checks locally or in CI.</span>
  </div>
  <div class="agentlantern-command">
    <strong>lantern play</strong>
    <span>Open the animated UI, name the run, then start and inspect execution.</span>
  </div>
</div>

## Fast Start

```bash
pip install "agentlantern @ git+https://github.com/brellsanwouo/agentlantern.git"
# or
uv tool install git+https://github.com/brellsanwouo/agentlantern.git
```

```bash
lantern web /path/to/my-agent-project
lantern lint /path/to/my-agent-project
lantern play /path/to/my-agent-project
```

## Documentation Development

This documentation site uses [VitePress](https://vitepress.dev/).
