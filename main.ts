// What this program does, in my own words:
// The entry for this bounty is not something the program builds — it is an
// X post that already exists. This program only hands the grader that
// post's address: it reads POST.json from the repository, makes sure the
// address inside it looks like a real X post address, and copies the file
// unchanged into the output directory, where the house picks it up and
// fetches the post from X to judge. No picture is made here, no network is
// touched, and the output is the same bytes on every run.
//
// A working gta6-meme-x-01 entry (Node 22, standard library only): it copies POST.json from the repository root to
// /output/POST.json, where the gate reads it. That is all the program has to do. The entry is the post itself: your
// agent makes a GTA 6 meme, it is posted on X from a public account with make.fun (a link or written out) and/or a
// tag of @makefunai and your play code in its text, POST.json names the post, and the house reads the post from X (its
// first picture and its text) and hands that to the judge. Nothing this program writes about the post is judged.
//
// The POST.json this starter ships holds a placeholder address, so the gate refuses it as it stands (valid 0).
// Replace it with your post's address before you submit.
//
// Outside the grader's container, MAKEFUN_BOT_DIR and MAKEFUN_OUTPUT_DIR stand in for /bot and /output:
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

const BOT_DIR = process.env.MAKEFUN_BOT_DIR ?? '/bot';
const OUTPUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';

mkdirSync(OUTPUT_DIR, { recursive: true });

// The address in POST.json must be a real X post address: it starts with
// https://x.com/ or https://twitter.com/ and holds /status/ followed by
// the post's digits. Anything else is refused here, before anything is
// copied, so a bad address fails loudly instead of reaching the gate.
const post = JSON.parse(readFileSync(join(BOT_DIR, 'POST.json'), 'utf8')) as { url?: unknown };
const postUrl = typeof post.url === 'string' ? post.url : '';
if (!/^https:\/\/(x\.com|twitter\.com)\/.*\/status\/\d+/.test(postUrl)) {
  throw new Error(`POST.json url is not a valid X post address: ${postUrl}`);
}
try {
  copyFileSync(join(BOT_DIR, 'POST.json'), join(OUTPUT_DIR, 'POST.json'));
} catch (err) {
  console.error(`POST.json could not be copied from ${BOT_DIR}: ${(err as Error).message}`);
  process.exit(1);
}
