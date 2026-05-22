import { defineConfig } from "vitepress";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const base = process.env.VITEPRESS_BASE ?? "/";
const pyproject = readFileSync(resolve(__dirname, "../../pyproject.toml"), "utf-8");
const version = pyproject.match(/^version = "([^"]+)"/m)?.[1] ?? "0.0.0";

export default defineConfig({
  title: "AgentLantern",
  description: "Document, lint, inspect, play, and replay AI agent projects.",
  base,
  cleanUrls: true,
  lastUpdated: true,
  head: [
    ["link", { rel: "icon", href: `${base}assets/logo.png` }],
    ["meta", { name: "theme-color", content: "#3841fc" }],
    ["meta", { property: "og:title", content: "AgentLantern" }],
    ["meta", { property: "og:description", content: "Developer tools for AI agent projects." }],
    ["meta", { property: "og:image", content: `${base}assets/logo-horizontal-2.png` }],
  ],
  markdown: {
    theme: {
      light: "github-light",
      dark: "github-dark",
    },
  },
  themeConfig: {
    logo: "/assets/logo-horizontal-2.png",
    siteTitle: false,
    nav: [
      { text: "Guide", link: "/guide" },
      { text: "CLI", link: "/usage" },
      { text: "Play", link: "/play" },
      { text: "Formation", link: "https://discord.gg/Ycc29yp4xQ" },
      {
        text: `v${version}`,
        items: [
          { text: "Changelog", link: "/changelog" },
          { text: "GitHub Releases", link: "https://github.com/brellsanwouo/agentlantern/releases" },
        ],
      },
    ],
    sidebar: [
      {
        text: "Start Here",
        items: [
          { text: "Overview", link: "/guide" },
          { text: "Installation", link: "/installation" },
          { text: "Usage Guide", link: "/usage" },
        ],
      },
      {
        text: "lantern docs",
        items: [
          { text: "Overview", link: "/lantern-docs" },
          { text: "Quick Start", link: "/quick-start" },
          { text: "Examples", link: "/examples" },
        ],
      },
      {
        text: "lantern lint",
        items: [
          { text: "Overview", link: "/linter" },
          { text: "Run the Linter", link: "/lint/running" },
          { text: "CrewAI Rules", link: "/lint/rules" },
          { text: "JSON & CI", link: "/lint/json-ci" },
          { text: "Troubleshooting", link: "/lint/troubleshooting" },
        ],
      },
      {
        text: "lantern play",
        items: [
          { text: "Overview", link: "/play" },
          { text: "Quick Start", link: "/play/quick-start" },
          { text: "Interface", link: "/play/interface" },
          { text: "Agent Layouts", link: "/play/layouts" },
          { text: "Tool Hub", link: "/play/tool-hub" },
          { text: "Replay", link: "/play/replay" },
          { text: "Command Reference", link: "/play/reference" },
          { text: "Troubleshooting", link: "/play/troubleshooting" },
        ],
      },
      {
        text: "Reference",
        items: [
          { text: "CLI Reference", link: "/api" },
          { text: "Changelog", link: "/changelog" },
          { text: "FAQ", link: "/faq" },
        ],
      },
    ],
    socialLinks: [
      {
        icon: {
          svg: '<svg role="img" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg"><path d="M20.317 4.369A19.79 19.79 0 0 0 15.362 2.8a.074.074 0 0 0-.079.037c-.214.38-.452.875-.619 1.265a18.27 18.27 0 0 0-5.487 0a12.64 12.64 0 0 0-.63-1.265.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.51 4.37a.07.07 0 0 0-.032.027C.534 8.796-.268 13.085.128 17.322a.082.082 0 0 0 .031.056a19.9 19.9 0 0 0 6.073 3.071a.078.078 0 0 0 .084-.027c.468-.64.885-1.316 1.238-2.026a.076.076 0 0 0-.041-.105a13.18 13.18 0 0 1-1.872-.893a.077.077 0 0 1-.008-.128c.126-.094.252-.192.372-.291a.074.074 0 0 1 .078-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .079.009c.12.099.246.198.373.292a.077.077 0 0 1-.006.128c-.6.35-1.224.647-1.873.892a.077.077 0 0 0-.041.106c.36.709.777 1.385 1.237 2.025a.076.076 0 0 0 .084.028a19.84 19.84 0 0 0 6.082-3.072a.077.077 0 0 0 .032-.055c.474-4.9-.796-9.154-3.764-12.925a.061.061 0 0 0-.031-.028ZM8.02 14.742c-1.183 0-2.157-1.085-2.157-2.419c0-1.333.955-2.418 2.157-2.418c1.21 0 2.176 1.095 2.157 2.418c0 1.334-.955 2.419-2.157 2.419Zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419c0-1.333.955-2.418 2.157-2.418c1.211 0 2.176 1.095 2.157 2.418c0 1.334-.946 2.419-2.157 2.419Z"/></svg>',
        },
        link: "https://discord.gg/Ycc29yp4xQ",
        ariaLabel: "Discord",
      },
      { icon: "github", link: "https://github.com/brellsanwouo/agentlantern" },
    ],
    search: {
      provider: "local",
    },
    footer: {
      message: "Released under the MIT License.",
      copyright: "AgentLantern",
    },
  },
});
