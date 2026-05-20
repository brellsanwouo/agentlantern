import { defineConfig } from "vitepress";

const base = process.env.VITEPRESS_BASE ?? "/";

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
    ["meta", { property: "og:image", content: `${base}assets/logo-horizontal.png` }],
  ],
  markdown: {
    theme: {
      light: "github-light",
      dark: "github-dark",
    },
  },
  themeConfig: {
    logo: "/assets/logo.png",
    siteTitle: "AgentLantern",
    nav: [
      { text: "Guide", link: "/guide" },
      { text: "CLI", link: "/usage" },
      { text: "Play", link: "/play" },
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
          { text: "FAQ", link: "/faq" },
        ],
      },
    ],
    socialLinks: [
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
