/* HOMERun Camp: Top 10 scoreboard and promo sign-up backend (Google Apps Script). Same setup as the ARGOPOWER game.
   SETUP
   1) Go to sheets.new and name the sheet "HOMERun Camp Scores".
   2) Extensions > Apps Script. Paste this whole file, then Save.
   3) Deploy > New deployment > type Web app. Execute as: Me. Who has access: Anyone. Deploy and authorize.
   4) Copy the Web app URL (ends in /exec) and paste it into config.js in the game's GitHub repo (between the quotes).
   5) After any later change here: Deploy > Manage deployments > Edit > Version: New version > Deploy.
   Scores are stored in the "scores" tab (one row per player, best score kept).
   PROMO SIGN-UPS (optional, with consent) are stored in a separate "contacts" tab. They are NEVER sent back to the game
   or shown on the leaderboard. Keep this spreadsheet private: share it only with the CBK staff who need it (Marketing),
   and ideally own it from a CBK company Google account, not a personal one.
   "contacts" columns: signed_up | name | email | mobile | consent_marketing | age_18_plus | consent_version | consent_text | device | status
   To honor an unsubscribe or removal request: set status to "unsubscribed" (or delete the row) and exclude those rows from campaigns. */
const ENDS = '';                 // optional campaign end, e.g. '2026-12-31T23:59:59+08:00'
const MAX_PTS_PER_SEC = 220;     // base points per second before the mission multiplier (x1-x30) and 2X power-up; faster is rejected as a fake
const MIN_GAP_SEC = 15;          // minimum seconds between submissions from one device
function sheet_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let s = ss.getSheetByName('scores');
  if (!s) { s = ss.insertSheet('scores'); s.appendRow(['updated', 'did', 'name', 'best', 'plays']); }
  return s;
}
function contacts_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let s = ss.getSheetByName('contacts');
  if (!s) {
    s = ss.insertSheet('contacts');
    s.appendRow(['signed_up', 'name', 'email', 'mobile', 'consent_marketing', 'age_18_plus', 'consent_version', 'consent_text', 'device', 'status']);
    s.setFrozenRows(1);
  }
  return s;
}
function json_(o) { return ContentService.createTextOutput(typeof o === 'string' ? o : JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }
function doGet() {
  const c = CacheService.getScriptCache();
  let t = c.get('top');
  if (!t) {
    const rows = sheet_().getDataRange().getValues().slice(1).map(r => ({ n: r[2], s: +r[3] })).sort((a, b) => b.s - a.s).slice(0, 100);
    t = JSON.stringify({ ok: true, rows }); c.put('top', t, 60);   // cached 60 s so many players opening the board at once stay fast
  }
  return json_(t);
}
function doPost(e) {
  const L = LockService.getScriptLock();
  try { L.waitLock(10000); } catch (x) { return json_({ ok: false, err: 'Busy, try again' }); }
  try {
    const p = JSON.parse(e.postData.contents), c = CacheService.getScriptCache();
    if (p.type === 'lead') return lead_(p, c);
    if (ENDS && Date.now() > new Date(ENDS).getTime()) return json_({ ok: false, err: 'The campaign has ended' });
    const name = String(p.name || '').replace(/[^\p{L}\p{N} .\-_]/gu, '').trim().slice(0, 16);
    const did = String(p.did || '').replace(/\W/g, '').slice(0, 20);
    const score = Math.floor(+p.score), secs = Math.floor(+p.secs);
    if (name.length < 2 || !did || !(score >= 0) || !(secs >= 3)) return json_({ ok: false, err: 'Invalid entry' });
    const mult = Math.min(30, Math.max(1, Math.floor(+p.mult) || 1));
    if (score > MAX_PTS_PER_SEC * secs * mult * 2 + 500) return json_({ ok: false, err: 'Score rejected' });
    if (c.get('g' + did)) return json_({ ok: false, err: 'Please wait a few seconds' });
    c.put('g' + did, '1', MIN_GAP_SEC);
    const s = sheet_(), v = s.getDataRange().getValues();
    let row = -1;
    for (let i = 1; i < v.length; i++) if (v[i][1] === did) { row = i + 1; break; }
    let best = score;
    if (row < 0) s.appendRow([new Date(), did, name, score, 1]);
    else { best = Math.max(+v[row - 1][3], score); s.getRange(row, 1, 1, 5).setValues([[new Date(), did, name, best, +v[row - 1][4] + 1]]); }
    c.remove('top');
    const rank = 1 + s.getDataRange().getValues().slice(1).filter(r => r[1] !== did && +r[3] > best).length;
    return json_({ ok: true, rank });
  } catch (x) { return json_({ ok: false, err: 'Server error' }); }
  finally { L.releaseLock(); }
}

/* Promo sign-up: saved only with both boxes ticked; one row per email (a repeat sign-up updates it). */
function lead_(p, c) {
  const name = String(p.name || '').replace(/[^\p{L} .'\-]/gu, '').replace(/\s+/g, ' ').trim().slice(0, 60);
  const email = String(p.email || '').trim().toLowerCase().slice(0, 80);
  const mobile = String(p.mobile || '').replace(/[^\d+]/g, '').slice(0, 16);
  const did = String(p.did || '').replace(/\W/g, '').slice(0, 20);
  if (name.length < 2 || !/^[^\s@]+@[^\s@]+\.[a-z]{2,}$/.test(email) || !/^\+639\d{9}$/.test(mobile)) return json_({ ok: false, err: 'Please check your details' });
  if (p.ok !== 1 || p.age !== 1) return json_({ ok: false, err: 'Consent is required' });
  if (c.get('L' + did)) return json_({ ok: false, err: 'Please wait a few seconds' });
  c.put('L' + did, '1', 20);
  const s = contacts_(), v = s.getDataRange().getValues();
  const row = [new Date(), name, email, "'" + mobile, true, true, String(p.cv || '').slice(0, 40), String(p.ct || '').slice(0, 400), did, 'subscribed'];
  let at = -1;
  for (let i = 1; i < v.length; i++) if (String(v[i][2]).toLowerCase() === email) { at = i + 1; break; }
  if (at < 0) s.appendRow(row); else s.getRange(at, 1, 1, row.length).setValues([row]);
  return json_({ ok: true });
}
