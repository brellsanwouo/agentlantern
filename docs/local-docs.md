# Run This Docs Site

This page is about the AgentLantern documentation site inside this repository.

From the AgentLantern repository root:

```bash
npm install
npm run docs:dev
```

Then open:

```text
http://127.0.0.1:9010
```

Stop it with `Ctrl+C` in the terminal.

## Production Build

VitePress builds static files that work on GitHub Pages:

```bash
npm run docs:build
```

The output is written to:

```text
docs/.vitepress/dist
```

Preview the production build locally:

```bash
npm run docs:preview
```

## Important Distinction

Do not use `lantern web .` to preview this product documentation site while developing AgentLantern itself.

`lantern web` is for an external agent project. It generates documentation into that project's `docs/` directory and serves it over HTTPS:

```bash
lantern web /path/to/my-agent-project
```

If you run `lantern web .` from this repository, AgentLantern treats AgentLantern itself as the target project and writes generated files into `docs/`. That is useful for testing the generator, but it is not how to preview the product docs site.

## When To Use Each Command

| Goal | Command |
| --- | --- |
| Preview this documentation site | `npm run docs:dev` |
| Build this documentation site | `npm run docs:build` |
| Generate docs for another agent project | `lantern docs /path/to/project` |
| Generate and serve docs for another agent project | `lantern web /path/to/project` on `https://localhost:9000` |
| Test the docs generator on AgentLantern itself | `lantern docs . -o /tmp/agentlantern-generated-docs` |
