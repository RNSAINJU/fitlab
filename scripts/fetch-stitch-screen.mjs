#!/usr/bin/env node
/**
 * Fetch Stitch screen screenshot + HTML for a project/screen ID.
 * Usage:
 *   STITCH_API_KEY=... node scripts/fetch-stitch-screen.mjs <projectId> <screenId> [outputDir]
 */
import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { stitch } from "@google/stitch-sdk";

const projectId = process.argv[2];
const screenId = process.argv[3];
const outputDir = process.argv[4] || path.join("stitch", projectId, screenId);

if (!projectId || !screenId) {
  console.error("Usage: STITCH_API_KEY=... node scripts/fetch-stitch-screen.mjs <projectId> <screenId> [outputDir]");
  process.exit(1);
}

if (!process.env.STITCH_API_KEY && !process.env.STITCH_ACCESS_TOKEN) {
  console.error("Missing STITCH_API_KEY. Get one at https://stitch.withgoogle.com/settings");
  process.exit(1);
}

const project = stitch.project(projectId);
const screen = await project.getScreen(screenId);
const htmlUrl = await screen.getHtml();
const imageUrl = await screen.getImage();

if (!htmlUrl || !imageUrl) {
  console.error("Screen found but download URLs are missing:", { htmlUrl, imageUrl });
  process.exit(1);
}

await mkdir(outputDir, { recursive: true });

const [htmlRes, imgRes] = await Promise.all([
  fetch(htmlUrl),
  fetch(imageUrl),
]);

if (!htmlRes.ok) throw new Error(`HTML download failed: ${htmlRes.status}`);
if (!imgRes.ok) throw new Error(`Image download failed: ${imgRes.status}`);

const html = await htmlRes.text();
const imgBuf = Buffer.from(await imgRes.arrayBuffer());

const meta = {
  projectId,
  screenId,
  title: screen.data?.title || screen.data?.displayName || null,
  htmlUrl,
  imageUrl,
  width: screen.data?.width ?? null,
  height: screen.data?.height ?? null,
  deviceType: screen.data?.deviceType ?? null,
};

await writeFile(path.join(outputDir, "screen.html"), html);
await writeFile(path.join(outputDir, "screenshot.png"), imgBuf);
await writeFile(path.join(outputDir, "meta.json"), JSON.stringify(meta, null, 2));

console.log(JSON.stringify({ outputDir, ...meta }, null, 2));
