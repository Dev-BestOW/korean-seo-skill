// 마크다운 글의 프론트매터 title·description 을 네이버 기준으로 검사한다.
// 사용: node check-meta.mjs <폴더 또는 파일>...   (예: node check-meta.mjs src/content/posts content-queue)
// - 실패(exit 1): title 40자·description 80자 초과, 빈 값, title 과 description 이 같음
// - 경고: 한 필드 안에서 같은 낱말 반복 — 조사까지 붙여 세는 단순한 방식이라
//   "미디어 쿼리는 … 컨테이너 쿼리는" 같은 비교 문장도 잡힌다. 경고는 사람이 읽고 판단한다.
// Node 18+ 표준 라이브러리만 쓴다.

import { readdir, readFile, stat } from 'node:fs/promises';
import { join } from 'node:path';

const TITLE_MAX = 40;
const DESCRIPTION_MAX = 80;

function readField(source, key) {
  const front = source.match(/^---\r?\n([\s\S]*?)\r?\n---/)?.[1] ?? '';
  const line = front.match(new RegExp(`^${key}:\\s*(.*)$`, 'm'))?.[1]?.trim();
  if (line === undefined) return undefined;
  if (line.startsWith("'") && line.endsWith("'")) return line.slice(1, -1).replace(/''/g, "'");
  if (line.startsWith('"') && line.endsWith('"')) return JSON.parse(line);
  return line;
}

function repeatedWords(text) {
  const counts = new Map();
  for (const word of text.toLowerCase().match(/[가-힣a-z@_.]{2,}/g) ?? []) {
    counts.set(word, (counts.get(word) ?? 0) + 1);
  }
  return [...counts].filter(([, n]) => n > 1).map(([w]) => w);
}

function checkMeta(title, description) {
  const problems = [];
  const warnings = [];
  if (!title) problems.push('title 없음');
  if (!description) problems.push('description 없음');
  if (title && title.length > TITLE_MAX) problems.push(`title ${title.length}자 (최대 ${TITLE_MAX})`);
  if (description && description.length > DESCRIPTION_MAX)
    problems.push(`description ${description.length}자 (최대 ${DESCRIPTION_MAX})`);
  if (title && description && title === description) problems.push('title 과 description 이 같음');
  for (const [name, value] of [
    ['title', title],
    ['description', description],
  ]) {
    const words = value ? repeatedWords(value) : [];
    if (words.length) warnings.push(`${name} 낱말 반복: ${words.join(', ')}`);
  }
  return { problems, warnings };
}

async function collect(path) {
  const info = await stat(path).catch(() => null);
  if (!info) return [];
  if (info.isFile()) return /\.mdx?$/.test(path) ? [path] : [];
  const names = await readdir(path);
  return names
    .filter((f) => /\.mdx?$/.test(f) && f.toLowerCase() !== 'readme.md')
    .map((f) => join(path, f));
}

const targets = process.argv.slice(2);
if (!targets.length) {
  console.error('사용: node check-meta.mjs <폴더 또는 파일>...');
  process.exit(2);
}
let failed = 0;
let checked = 0;
for (const target of targets) {
  for (const file of await collect(target)) {
    const source = await readFile(file, 'utf8');
    const { problems, warnings } = checkMeta(readField(source, 'title'), readField(source, 'description'));
    checked += 1;
    if (problems.length) {
      failed += 1;
      console.error(`✗ ${file}\n  - ${problems.join('\n  - ')}`);
    }
    if (warnings.length) console.warn(`! ${file} (경고 — 키워드 반복인지 읽고 판단)\n  - ${warnings.join('\n  - ')}`);
  }
}
if (failed) {
  console.error(`\n${checked}편 중 ${failed}편이 기준(제목 ${TITLE_MAX}자·설명 ${DESCRIPTION_MAX}자)을 넘었습니다.`);
  process.exit(1);
}
console.log(`✓ ${checked}편 통과 (제목 ≤${TITLE_MAX}, 설명 ≤${DESCRIPTION_MAX})`);
