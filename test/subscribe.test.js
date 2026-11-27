const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const handler = require('../api/subscribe');
const {GUIDE, PASSIVE, DISCLOSURE} = handler;
const API = 'https://api.resend.com';
const ROOT = path.join(__dirname, '..');

function mockRes(){
  return {
    statusCode: null,
    body: null,
    status(c){ this.statusCode = c; return this; },
    json(o){ this.body = o; return this; }
  };
}

function installFetch(routes){
  const calls = [];
  global.fetch = async (url, opts = {}) => {
    const body = opts.body ? JSON.parse(opts.body) : null;
    calls.push({url, method: opts.method || 'GET', body, headers: opts.headers || {}});
    const key = `${opts.method || 'GET'} ${url}`;
    const route = routes[key] || routes[url];
    if (!route) return {ok: false, status: 500, json: async () => ({}), text: async () => `unmocked ${key}`};
    return {
      ok: route.status ? route.status < 400 : true,
      status: route.status || 200,
      json: async () => route.json || {},
      text: async () => route.text || ''
    };
  };
  return calls;
}

test.beforeEach(() => {
  process.env.RESEND_API_KEY = 're_test';
  process.env.BREVO_API_KEY = 'brevo_test';
  process.env.SENDER_EMAIL = 'info@bowandarrowconsultingco.com';
  delete process.env.BREVO_SMTP_KEY;
  delete process.env.BREVO_SMTP_LOGIN;
});

test('rejects non-POST and a bad email without calling Resend', async () => {
  let called = false;
  global.fetch = async () => { called = true; throw new Error('should not fetch'); };
  const get = mockRes();
  await handler({method: 'GET', body: {}}, get);
  assert.equal(get.statusCode, 405);
  assert.equal(get.body.ok, false);
  const bad = mockRes();
  await handler({method: 'POST', body: {email: 'not-an-email', source: PASSIVE}}, bad);
  assert.equal(bad.statusCode, 400);
  assert.equal(bad.body.error, "That email doesn't look right.");
  assert.equal(called, false);
});

test('weekly signup keeps the original welcome and does not tag passive-stack', async () => {
  const calls = installFetch({
    [`GET ${API}/audiences`]: {json: {data: [{id: 'aud_main', name: 'AI without BS'}, {id: 'aud_ps', name: PASSIVE}]}},
    [`POST ${API}/audiences/aud_main/contacts`]: {json: {id: 'c1'}},
    'POST https://api.brevo.com/v3/smtp/email': {status: 201, json: {messageId: 'm1'}}
  });
  const res = mockRes();
  await handler({method: 'POST', body: {email: 'Owner@Shop.com'}}, res);
  assert.equal(res.statusCode, 200);
  assert.deepEqual(res.body, {ok: true});
  const contactPosts = calls.filter(c => c.url.includes('/contacts'));
  assert.deepEqual(contactPosts.map(c => c.url), [`${API}/audiences/aud_main/contacts`]);
  assert.equal(contactPosts[0].body.email, 'owner@shop.com');
  const mail = calls.find(c => c.url.includes('brevo'));
  assert.equal(mail.body.subject, "You're in: your first AI play (no BS)");
  assert.match(mail.body.htmlContent, /Your first play/);
  assert.equal(mail.body.htmlContent.includes(GUIDE), false);
  assert.equal(mail.body.htmlContent.includes('SurveySavvy'), false);
});

test('passive-stack tags a passive-stack audience and emails the guide', async () => {
  const calls = installFetch({
    [`GET ${API}/audiences`]: {json: {data: [{id: 'aud_main', name: 'AI without BS'}]}},
    'POST https://api.resend.com/audiences': {json: {id: 'aud_ps', name: PASSIVE}},
    [`POST ${API}/audiences/aud_main/contacts`]: {json: {id: 'c1'}},
    [`POST ${API}/audiences/aud_ps/contacts`]: {json: {id: 'c2'}},
    'POST https://api.brevo.com/v3/smtp/email': {status: 201, json: {}}
  });
  const res = mockRes();
  await handler({method: 'POST', body: JSON.stringify({email: 'ada@example.com', source: '  Passive-Stack '})}, res);
  assert.equal(res.statusCode, 200);
  assert.equal(res.body.ok, true);
  assert.equal(res.body.source, PASSIVE);
  assert.equal(GUIDE, 'https://aiwithoutbs.net/passive-stack-guide');
  assert.equal(res.body.guide, 'https://aiwithoutbs.net/passive-stack-guide');
  assert.equal(res.body.guide, GUIDE);
  assert.equal(res.body.emailed, true);
  const created = calls.find(c => c.method === 'POST' && c.url === `${API}/audiences`);
  assert.equal(created.body.name, PASSIVE);
  const mail = calls.find(c => c.url.includes('brevo'));
  assert.equal(mail.body.subject, 'Your 2026 passive income app stack guide');
  assert.equal(mail.body.to[0].email, 'ada@example.com');
  assert.match(mail.body.htmlContent, /~\$15\/month \(~\$180\/year\)/);
  assert.match(mail.body.htmlContent, /~\$34–\$37\/month \(~\$408–\$444\/year\)/);
  assert.match(mail.body.htmlContent, /Honeygain, EarnApp, Pawns/);
  assert.ok(mail.body.htmlContent.includes(GUIDE));
  assert.ok(mail.body.htmlContent.includes(DISCLOSURE));
});

test('an existing subscriber still gets the guide email', async () => {
  installFetch({
    [`GET ${API}/audiences`]: {json: {data: [{id: 'aud_main', name: 'AI without BS'}, {id: 'aud_ps', name: PASSIVE}]}},
    [`POST ${API}/audiences/aud_main/contacts`]: {status: 409, text: 'Contact already exists'},
    [`POST ${API}/audiences/aud_ps/contacts`]: {status: 409, text: 'Contact already exists'},
    'POST https://api.brevo.com/v3/smtp/email': {status: 201, json: {}}
  });
  const res = mockRes();
  await handler({method: 'POST', body: {email: 'ada@example.com', source: PASSIVE}}, res);
  assert.equal(res.statusCode, 200);
  assert.equal(res.body.ok, true);
  assert.equal(res.body.guide, 'https://aiwithoutbs.net/passive-stack-guide');
  assert.equal(res.body.guide, GUIDE);
});

test('a duplicate weekly signup still fails the way it used to', async () => {
  installFetch({
    [`GET ${API}/audiences`]: {json: {data: [{id: 'aud_main', name: 'AI without BS'}]}},
    [`POST ${API}/audiences/aud_main/contacts`]: {status: 409, text: 'Contact already exists'}
  });
  const res = mockRes();
  await handler({method: 'POST', body: {email: 'ada@example.com'}}, res);
  assert.equal(res.statusCode, 500);
  assert.equal(res.body.ok, false);
});

test('a stranger source does not receive the guide email', async () => {
  const calls = installFetch({
    [`GET ${API}/audiences`]: {json: {data: [{id: 'aud_main', name: 'AI without BS'}]}},
    [`POST ${API}/audiences/aud_main/contacts`]: {json: {id: 'c1'}},
    'POST https://api.brevo.com/v3/smtp/email': {status: 201, json: {}}
  });
  const res = mockRes();
  await handler({method: 'POST', body: {email: 'ada@example.com', source: 'passive-stack<script>'}}, res);
  assert.deepEqual(res.body, {ok: true});
  const mail = calls.find(c => c.url.includes('brevo'));
  assert.match(mail.body.htmlContent, /Your first play/);
  assert.equal(mail.body.htmlContent.includes(GUIDE), false);
  assert.equal(calls.some(c => c.body && c.body.name === PASSIVE), false);
});

test('the landing page, homepage promo, footer, and sitemap carry the audit', () => {
  const page = fs.readFileSync(path.join(ROOT, 'passive-stack.html'), 'utf8');
  const home = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8');
  const css = fs.readFileSync(path.join(ROOT, 'style.css'), 'utf8');
  const sitemap = fs.readFileSync(path.join(ROOT, 'sitemap.xml'), 'utf8');
  const review = fs.readFileSync(path.join(ROOT, 'reviews/claude.html'), 'utf8');
  const required = [
    '2026 Passive Income App Stack — Real-World Audit | AIwithoutBS',
    'The real-world 2026 audit of passive income apps: what pays cleanly (~$15–$37/month), what to cut immediately, and the free interactive setup guide + AI maintenance prompt.',
    '2026 REAL-WORLD AUDIT · NO HYPE · ZERO PROXY RISK',
    'The Real-World 2026 Passive Income App Stack',
    'I audited every "passive income" app so you don\'t wreck your home internet for $15. Won\'t buy a boat—will pay a bill.',
    'Safe Core',
    '~$15/month',
    '~$180/year',
    'Phone + Computer (Nielsen Pulse + SavvyConnect)',
    'Clean Ceiling',
    '~$34–$37/month',
    '~$408–$444/year',
    'Adding TVision, Nielsen on supported TVs, &amp; Google Screenwise Meter (invite-only)',
    'Cut Immediately',
    '0% Proxy Risk',
    'No Honeygain, EarnApp, Pawns, or bandwidth-sharing apps (FBI IC3 March 2026 warning)',
    'Clean-Network Core:',
    'Nielsen Computer &amp; Mobile Panel (Pulse) and SavvyConnect (~$15/mo baseline).',
    'What We Cut &amp; Why:',
    "aren't worth the risk or pennies.",
    'Smart TV &amp; Invite-Only Stack:',
    'Google Screenwise Meter to hit ~$34–$37/month.',
    'Copy-Paste AI Setup &amp; Monthly Maintenance Prompt:',
    'recurring monthly AI routine + calendar reminder so payouts never stall.',
    'source:"passive-stack"',
    GUIDE,
    DISCLOSURE
  ];
  for (const s of required) assert.ok(page.includes(s), `missing: ${s}`);
  assert.doesNotMatch(page, /\$\d+\s*-\s*\$?\d+/);
  assert.ok(home.includes('class="stack-promo"'));
  assert.ok(home.indexOf('stack-promo') < home.indexOf('class="cover"'));
  assert.match(home, /~\$15–\$37\/month/);
  assert.ok(home.includes('href="/passive-stack"'));
  assert.ok(css.includes('body.edition{--ink:#000000;--red:#d62828;--cream:#fffdf7;--gold:#f4b400}'));
  assert.ok(sitemap.includes('https://aiwithoutbs.vercel.app/passive-stack'));
  assert.ok(review.includes('href="/passive-stack">2026 passive stack</a>'));
  assert.ok(page.includes('href="/passive-stack">2026 passive stack</a>'));
  assert.equal(GUIDE, 'https://aiwithoutbs.net/passive-stack-guide');
  assert.equal(page.includes('https://aiwithoutbs.net/passive-stack-guide'), true);
});

test('the public guide replaces the canvas login wall', () => {
  const guideUrl = 'https://aiwithoutbs.net/passive-stack-guide';
  assert.equal(GUIDE, guideUrl);
  const guide = fs.readFileSync(path.join(ROOT, 'passive-stack-guide.html'), 'utf8');
  const page = fs.readFileSync(path.join(ROOT, 'passive-stack.html'), 'utf8');
  const api = fs.readFileSync(path.join(ROOT, 'api/subscribe.js'), 'utf8');
  const sitemap = fs.readFileSync(path.join(ROOT, 'sitemap.xml'), 'utf8');
  assert.ok(guide.includes(guideUrl));
  assert.ok(page.includes(guideUrl));
  assert.ok(api.includes(guideUrl));
  assert.ok(sitemap.includes(guideUrl));
  assert.equal(page.split(guideUrl).length - 1, 4);
  assert.ok(guide.includes('Copy Full AI Prompt'));
  assert.ok(guide.includes('id="copy-prompt"'));
  assert.ok(guide.includes('Copied!'));
  assert.ok(guide.includes('id="proxy-toggle"'));
  assert.ok(guide.includes('Include risky bandwidth-proxy stack (+$13/mo midpoint; exposes home IP)'));
  assert.ok(guide.includes('data-filter="recommended"'));
  assert.ok(guide.includes('https://www.surveysavvy.com/?m=9049737'));
  assert.ok(guide.split('(referral)').length - 1 >= 2);
  assert.ok(guide.includes(DISCLOSURE));
  assert.ok(guide.includes('FBI IC3\'s March 12, 2026 PSA'));
  assert.ok(guide.includes('PHASE 0'));
  assert.ok(guide.includes('PHASE 5'));
  assert.ok(guide.includes('A. AI ROUTINE'));
  assert.ok(guide.includes('B. CALENDAR EVENT'));
  assert.ok(guide.includes('https://calendar.google.com/calendar/render?action=TEMPLATE'));
  assert.ok(guide.includes('https://apps.apple.com/us/app/nielsen-pulse/id6755230383'));
  assert.ok(guide.includes('https://play.google.com/store/apps/details?id=com.nlsn.psc'));
  assert.ok(guide.includes('lekkladnjnbpgcoljekpnopdllnggmeo'));
  assert.ok(guide.includes('Nielsen Pulse — $12/mo (12 apps)'));
  assert.ok(guide.includes('$34–$37/mo'));
  assert.ok(guide.includes('$10–$16/mo'));
  assert.ok(guide.includes('$15–$37/month'));
  assert.ok(guide.includes('+$19–$22/mo'));
  assert.ok(guide.includes('$0–$5/mo'));
  assert.ok(guide.includes('$0–$2/mo'));
  assert.ok(guide.includes('$4–$6/mo'));
  assert.ok(guide.includes('$25–$50/mo'));
  assert.ok(guide.includes('$5–$12/mo'));
  assert.doesNotMatch(guide, /\$\d+\s*-\s*\$?\d+/);
  const banned = [
    ['cursor.com', 'canvas'].join('/'),
    ['cursor.com', 'canvas'].join('%2F'),
    ['cursor.com', 'canvas'].join('%2f')
  ];
  function walk(dir) {
    for (const name of fs.readdirSync(dir)) {
      if (name === 'node_modules' || name === '.git') continue;
      const p = path.join(dir, name);
      const st = fs.statSync(p);
      if (st.isDirectory()) walk(p);
      else if (st.isFile() && st.size < 2000000) {
        const buf = fs.readFileSync(p);
        const lower = buf.toString('utf8').toLowerCase();
        for (const needle of banned) {
          assert.equal(lower.includes(needle), false, `${needle} in ${path.relative(ROOT, p)}`);
        }
      }
    }
  }
  walk(ROOT);
});
