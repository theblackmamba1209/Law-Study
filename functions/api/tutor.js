// Cloudflare Pages Function: optional AI tutor for Sinag · Codal Studio.
// Enable it by adding two encrypted environment variables to the Pages project:
//   ANTHROPIC_API_KEY  – your Anthropic API key
//   TUTOR_PASSCODE     – any passphrase; the app asks for it once per device
// Optional: TUTOR_MODEL (defaults to claude-sonnet-5-5).
// GitHub Pages has no server, so the tutor simply stays hidden there.

const SYSTEM = `You are a Philippine law tutor for a Bar reviewee. You are given one codal provision, verbatim, and sometimes a list of case names that the student's textbooks cite under it.
Rules:
- Ground every statement about the provision in the verbatim text supplied. Quote its exact words when you rely on them.
- Explain in plain, everyday English first; then give the legal elements as a numbered list; then one short worked example with invented facts; then the most common confusions or exam traps.
- Mention a case only if it is in the supplied list, and only for a proposition you are confident the case stands for. If you are unsure what a case held, say so instead of guessing. Never invent G.R. numbers, dates or holdings.
- If the provision has been amended or the supplied text may be outdated, say that the student should check the current text.
- Keep it under 450 words. No preamble.`;

const json = (obj, status = 200) => new Response(JSON.stringify(obj), { status, headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' } });

export async function onRequestGet({ env }) {
  return json({ ok: Boolean(env.ANTHROPIC_API_KEY && env.TUTOR_PASSCODE) });
}

export async function onRequestPost({ request, env }) {
  if (!env.ANTHROPIC_API_KEY || !env.TUTOR_PASSCODE) return json({ error: 'The tutor is not configured on this site.' }, 503);
  if (request.headers.get('x-tutor-pass') !== env.TUTOR_PASSCODE) return json({ error: 'Wrong tutor passcode.' }, 401);
  let b;
  try { b = await request.json(); } catch { return json({ error: 'Bad request.' }, 400); }
  const text = String(b?.provision?.text || '').slice(0, 24000);
  if (!text) return json({ error: 'No provision text.' }, 400);
  const mode = b.mode === 'ask' ? 'ask' : 'explain';
  const question = String(b.question || '').slice(0, 1500);
  const cases = Array.isArray(b.cases) ? b.cases.slice(0, 25).map(c => String(c).slice(0, 200)) : [];
  const user = [
    `Code: ${String(b?.code?.title || '').slice(0, 200)} (${String(b?.code?.citation || '').slice(0, 200)})`,
    `Provision: ${String(b?.provision?.label || '').slice(0, 100)}${b?.provision?.caption ? ' — ' + String(b.provision.caption).slice(0, 200) : ''}`,
    `Verbatim text:\n"""\n${text}\n"""`,
    cases.length ? `Cases the student's textbooks cite under this provision:\n- ${cases.join('\n- ')}` : 'No case list supplied.',
    mode === 'ask' ? `Student's question: ${question}` : 'Explain this provision.',
  ].join('\n\n');
  const r = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: { 'content-type': 'application/json', 'x-api-key': env.ANTHROPIC_API_KEY, 'anthropic-version': '2023-06-01' },
    body: JSON.stringify({ model: env.TUTOR_MODEL || 'claude-sonnet-5-5', max_tokens: 1200, system: SYSTEM, messages: [{ role: 'user', content: user }] }),
  });
  const data = await r.json().catch(() => ({}));
  if (!r.ok) return json({ error: data?.error?.message || `Provider error ${r.status}` }, 502);
  const out = (data.content || []).filter(x => x.type === 'text').map(x => x.text).join('\n').trim();
  return json({ text: out || 'No answer returned.' });
}
