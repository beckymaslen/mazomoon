/**
 * Mazo Moon reader comments: a Google Apps Script attached to Rebecca's "Mazo Moon comments" Google Sheet.
 *
 * Each comment arrives as a new row. Nothing shows on the website until the "Show on site" box is ticked.
 * Delete a row to bin a comment. Anything typed in "My reply" shows under the comment, signed Rebecca.
 *
 * Setup (once): Extensions > Apps Script, paste this whole file, Save, run "setup" once (allow the permissions),
 * then Deploy > New deployment > Web app, Execute as: Me, Who has access: Anyone. Copy the web app URL
 * (it ends in /exec) into COMMENTS_URL in tools/blog.py.
 */

var SHEET = 'Comments';
var HEAD = ['Date', 'Page', 'Name', 'Stars', 'Comment', 'Show on site', 'My reply'];
var EMAIL_ME = true;  // email me when a new comment arrives

function setup() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(SHEET) || ss.insertSheet(SHEET);
  sh.getRange(1, 1, 1, HEAD.length).setValues([HEAD]).setFontWeight('bold');
  sh.setFrozenRows(1);
  sh.setColumnWidth(5, 420);
  // tick boxes are added row by row as comments arrive (a whole column of them would make the sheet look full)
}

function sheet_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(SHEET);
  if (!sh) { setup(); sh = ss.getSheetByName(SHEET); }
  return sh;
}

function out_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

function clean_(v, max) {
  return String(v == null ? '' : v).replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/g, '').trim().slice(0, max);
}

/* GET ?page=/reading/some-review/  ->  the approved comments for that page, oldest first */
function doGet(e) {
  var page = clean_(e && e.parameter && e.parameter.page, 300);
  var rows = sheet_().getDataRange().getValues().slice(1);
  var list = rows.filter(function (r) { return r[1] === page && r[5] === true && r[2] && r[4]; }).map(function (r) {
    return { date: r[0] instanceof Date ? r[0].toISOString() : String(r[0]), name: String(r[2]), stars: Number(r[3]) || 0,
             text: String(r[4]), reply: String(r[6] || '') };
  });
  return out_({ ok: true, comments: list });
}

/* POST {page, name, stars, text, website}  ->  a new row waiting for approval */
function doPost(e) {
  var d = {};
  try { d = JSON.parse(e.postData.contents); } catch (err) { return out_({ ok: false }); }
  if (d.website) return out_({ ok: true });  // the hidden box bots fill in
  var page = clean_(d.page, 300), name = clean_(d.name, 60), text = clean_(d.text, 3000);
  var stars = Math.max(0, Math.min(5, Math.round(Number(d.stars) || 0)));
  if (!/^\/(reading|blog)\/[a-z0-9-]+\/$/.test(page) || !name || !text) return out_({ ok: false });
  var lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    var sh = sheet_();
    sh.appendRow([new Date(), page, name, stars || '', text, false, '']);
    sh.getRange(sh.getLastRow(), 6).insertCheckboxes();
  } finally { lock.releaseLock(); }
  if (EMAIL_ME) {
    try {
      MailApp.sendEmail(Session.getEffectiveUser().getEmail(), 'New comment on mazomoon.com from ' + name,
        name + (stars ? ' (' + stars + '/5)' : '') + ' on https://www.mazomoon.com' + page + '\n\n' + text +
        '\n\nTick "Show on site" in your comments sheet to put it up, or delete the row to bin it:\n' +
        SpreadsheetApp.getActiveSpreadsheet().getUrl());
    } catch (err) {}
  }
  return out_({ ok: true });
}
