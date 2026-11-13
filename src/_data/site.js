export default function () {
  const fallback = "https://waste-mining-lab.onrender.com";
  return {
    url: (process.env.SITE_URL || process.env.CF_PAGES_URL || fallback).replace(/\/$/, ""),
    buildYear: new Date().getUTCFullYear(),
    environment: process.env.CF_PAGES_BRANCH ? "cloudflare-pages" : "local",
  };
}
