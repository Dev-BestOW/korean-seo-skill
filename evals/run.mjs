#!/usr/bin/env node
// 스킬 없이·있이 같은 요청을 `claude -p` 로 시켜 evals.json 의 검사를 돌린다. Node 18+ 표준 라이브러리만.
//
//   node evals/run.mjs                       # 모든 경우 × 없이·있이 × 1번
//   node evals/run.mjs --runs 2 --only doc-head,ai-briefing --model sonnet
//   node evals/run.mjs --mode with           # 스킬 있이만
//   node evals/run.mjs --regrade evals/results/<시각>   # 저장된 답을 모델 호출 없이 다시 채점(검사를 고쳤을 때)
//
// - 빈 임시 폴더에서 실행해 프로젝트 파일·CLAUDE.md 영향을 없앤다.
// - `--setting-sources project` 로 사용자 설정(설치한 플러그인 포함)을 읽지 않고, "있이" 는 `--plugin-dir <이 저장소>` 로
//   작업 중인 스킬만 켠다 — 설치된 옛 버전이 아니라 지금 고친 것을 잰다.
// - 답은 evals/results/<시각>/ 에 남는다(커밋 안 함). 사람이 읽고 판단할 것은 거기서 본다.
// - 요청마다 실제로 모델을 부르므로 사용량이 든다. 경우 6개 × 2 = 12번이 기본.
import { spawnSync } from 'node:child_process';
import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const { cases } = JSON.parse(readFileSync(join(root, 'evals/evals.json'), 'utf8'));

const args = process.argv.slice(2);
const opt = (name, fallback) => {
  const i = args.indexOf(`--${name}`);
  return i >= 0 ? args[i + 1] : fallback;
};
const runs = Number(opt('runs', '1'));
const only = opt('only', '')?.split(',').filter(Boolean);
const model = opt('model', '');
const modes = opt('mode', 'both') === 'both' ? ['without', 'with'] : [opt('mode')];

/** 검사 하나 → { ok, note } */
export function check(answer, c) {
  // "in": "code" — 코드 블록(```) 안만 본다. 설명 글에 든 나쁜 예시("이렇게 쓰면 안 돼요")를 잡지 않게
  const text = c.in === 'code' ? [...answer.matchAll(/```[^\n]*\n([\s\S]*?)```/g)].map((m) => m[1]).join('\n') : answer;
  const re = (flags = '') => new RegExp(c.pattern, `${flags}m`);
  const captures = () => [...text.matchAll(re('g'))].map((m) => (m[1] ?? '').trim());
  switch (c.type) {
    case 'regex':
      return { ok: re().test(text) };
    case 'not_regex': {
      const m = text.match(re());
      return { ok: !m, note: m ? m[0].slice(0, 60) : '' };
    }
    case 'max_count': {
      const n = captures().length;
      return { ok: n <= c.max, note: `${n}개` };
    }
    case 'max_len': {
      const found = captures();
      if (!found.length) return { ok: false, note: '못 찾음' };
      // 글자 수는 코드 포인트로(한글 한 자 = 1)
      const lens = found.map((s) => [...s].length);
      return { ok: Math.max(...lens) <= c.max, note: lens.join('·') + '자' };
    }
    case 'no_repeat': {
      const found = captures();
      if (!found.length) return { ok: false, note: '못 찾음' };
      for (const s of found) {
        const words = s.split(/[\s,·|—\-–:()[\]]+/).filter((w) => [...w].length >= 2);
        const dup = words.find((w, i) => words.indexOf(w) !== i);
        if (dup) return { ok: false, note: `"${dup}"` };
      }
      return { ok: true };
    }
    default:
      throw new Error(`모르는 검사 type: ${c.type}`);
  }
}

function ask(prompt, mode) {
  const cwd = mkdtempSync(join(tmpdir(), 'korean-seo-eval-'));
  const cli = ['-p', prompt, '--setting-sources', 'project'];
  if (mode === 'with') cli.push('--plugin-dir', root);
  if (model) cli.push('--model', model);
  const r = spawnSync('claude', cli, { cwd, encoding: 'utf8', timeout: 10 * 60 * 1000, maxBuffer: 1 << 24 });
  rmSync(cwd, { recursive: true, force: true });
  if (r.error) throw r.error;
  return r.stdout + (r.status ? `\n\n[exit ${r.status}] ${r.stderr}` : '');
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const regrade = opt('regrade', '');
  const out = regrade || join(root, 'evals/results', new Date().toISOString().replace(/[:.]/g, '-'));
  mkdirSync(out, { recursive: true });
  const summary = [];
  for (const kase of cases.filter((k) => !only?.length || only.includes(k.id))) {
    for (const mode of modes) {
      for (let n = 1; n <= runs; n++) {
        const file = join(out, `${kase.id}-${mode}-${n}.md`);
        if (regrade && !existsSync(file)) continue;
        process.stderr.write(`${kase.id} ${mode} ${n}/${runs} … `);
        const text = regrade ? readFileSync(file, 'utf8') : ask(kase.prompt, mode);
        if (!regrade) writeFileSync(file, text);
        const results = kase.checks.map((c) => ({ ...c, ...check(text, c) }));
        const passed = results.filter((r) => r.ok).length;
        process.stderr.write(`${passed}/${results.length}\n`);
        summary.push({ id: kase.id, mode, n, passed, total: results.length, results });
      }
    }
  }
  writeFileSync(join(out, 'summary.json'), JSON.stringify(summary, null, 2));

  // 표: 경우·검사마다 없이/있이 통과 수
  console.log(`\n결과: ${out}\n`);
  console.log('| 경우 | 검사 | 없이 | 있이 |\n|---|---|---|---|');
  for (const kase of cases.filter((k) => !only?.length || only.includes(k.id))) {
    kase.checks.forEach((c, i) => {
      const cell = (mode) => {
        const rows = summary.filter((s) => s.id === kase.id && s.mode === mode);
        if (!rows.length) return '—';
        const ok = rows.filter((s) => s.results[i].ok).length;
        const notes = rows.map((s) => s.results[i].note).filter(Boolean);
        return `${ok}/${rows.length}${notes.length ? ` (${notes.join(', ')})` : ''}`;
      };
      console.log(`| ${kase.id} | ${c.desc} | ${cell('without')} | ${cell('with')} |`);
    });
  }
}
