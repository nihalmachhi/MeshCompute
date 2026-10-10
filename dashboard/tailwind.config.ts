import type { Config } from "tailwindcss";
const config: Config = { content: ["./src/**/*.{ts,tsx}"], theme: { extend: { colors: { ink: "#172331", paper: "#f4f5f2", muted: "#667481", line: "#dce1dc", accent: "#136d5a", warning: "#a35c16", danger: "#a63e3e" }, fontFamily: { sans: ["Arial", "Helvetica", "sans-serif"] } } }, plugins: [] };
export default config;
