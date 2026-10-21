/* ===========================================================
   管理後台 — 瀏覽器直接 commit 去 GitHub（純靜態，無後端）
   • 密碼閘只係防誤觸，唔係真正安全機制
   • token 只存 sessionStorage（關分頁即消失），永不寫入 repo
   • 用 Git Data API 一次過原子 commit（HTML + games.json 同時生效）
   =========================================================== */

(function () {
  'use strict';

  /* ⬇️ 想改密碼，改呢一行就得（只係防學生亂撳） */
  var PASSWORD = 'mathgames2026';

  var API = 'https://api.github.com';
  var CFG_KEY = 'mgh_admin_cfg';
  var TOKEN_KEY = 'mgh_admin_token';
  var MAX_ALLOW = 25 * 1024 * 1024;   // 超過 25MB 直接拒絕
  var WARN_SIZE = 8 * 1024 * 1024;    // 8MB 以上黃燈

  var state = {
    games: {},
    sections: [],
    topics: {},
    file: null,
    fileBytes: null,
    fileText: '',
    open: { all: true, sections: {}, games: {}, message: '' },
    cfg: { owner: '', repo: 'math-game-hub', branch: 'main' }
  };

  function $(s) { return document.querySelector(s); }
  function show(el, type, text) {
    if (typeof el === 'string') el = $(el);
    if (!el) return;
    el.className = 'msg show ' + type;
    el.innerHTML = text;
  }
  function hide(el) {
    if (typeof el === 'string') el = $(el);
    if (el) el.className = 'msg';
  }
  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  /* ---------- base64 / 文字工具（分塊處理，避免爆 stack） ---------- */
  function bytesToB64(bytes) {
    var CHUNK = 0x8000;
    var parts = [];
    for (var i = 0; i < bytes.length; i += CHUNK) {
      parts.push(String.fromCharCode.apply(null, bytes.subarray(i, i + CHUNK)));
    }
    return btoa(parts.join(''));
  }
  function b64ToBytes(b64) {
    var clean = String(b64).replace(/\s/g, '');
    var bin = atob(clean);
    var out = new Uint8Array(bin.length);
    for (var i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
    return out;
  }
  function bytesToText(bytes) {
    return new TextDecoder('utf-8').decode(bytes);
  }
  function textToBytes(text) {
    return new TextEncoder().encode(text);
  }
  function humanSize(n) {
    if (n >= 1048576) return (n / 1048576).toFixed(1) + ' MB';
    if (n >= 1024) return Math.round(n / 1024) + ' KB';
    return n + ' B';
  }
  function wifiLevel(n) {
    if (n >= 8 * 1048576) return 'heavy';
    if (n >= 3 * 1048576) return 'medium';
    return 'light';
  }
  function sha256Hex(bytes) {
    if (!window.crypto || !window.crypto.subtle) return Promise.resolve('');
    return window.crypto.subtle.digest('SHA-256', bytes).then(function (buf) {
      return Array.prototype.map.call(new Uint8Array(buf), function (b) {
        return ('0' + b.toString(16)).slice(-2);
      }).join('');
    }).catch(function () { return ''; });
  }

  /* ---------- GitHub API ---------- */
  function api(path, opts) {
    opts = opts || {};
    var headers = {
      'Accept': 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28'
    };
    if (opts.token) headers['Authorization'] = 'Bearer ' + opts.token;
    if (opts.body) headers['Content-Type'] = 'application/json';
    return fetch(API + path, {
      method: opts.method || 'GET',
      headers: headers,
      body: opts.body ? JSON.stringify(opts.body) : undefined
    }).then(function (r) {
      return r.text().then(function (t) {
        var data = null;
        try { data = t ? JSON.parse(t) : null; } catch (e) { data = { raw: t }; }
        if (!r.ok) {
          var msg = (data && data.message) || ('HTTP ' + r.status);
          if (r.status === 401) msg = 'Token 唔啱或者過期（401）';
          if (r.status === 403) msg = '權限不足（403）：請確認 token 有 Contents 讀寫權限';
          if (r.status === 404) msg = '搵唔到 repo 或分支（404）：請檢查用戶名／repo／分支';
          if (r.status === 409) msg = '分支有衝突（409）：可能有人同時改，請重新整理再試';
          var err = new Error(msg);
          err.status = r.status;
          err.data = data;
          throw err;
        }
        return data;
      });
    });
  }

  /* ---------- 設定 ---------- */
  function loadCfg() {
    try {
      var raw = localStorage.getItem(CFG_KEY);
      if (raw) state.cfg = JSON.parse(raw);
    } catch (e) { /* ignore */ }
    if (state.cfg.owner) $('#owner').value = state.cfg.owner;
    $('#repo').value = state.cfg.repo || 'math-game-hub';
    $('#branch').value = state.cfg.branch || 'main';
    var tk = sessionStorage.getItem(TOKEN_KEY);
    if (tk) $('#token').value = tk;
  }
  function saveCfg() {
    state.cfg = {
      owner: $('#owner').value.trim(),
      repo: $('#repo').value.trim() || 'math-game-hub',
      branch: $('#branch').value.trim() || 'main'
    };
    localStorage.setItem(CFG_KEY, JSON.stringify(state.cfg));
    var tk = $('#token').value.trim();
    if (tk) sessionStorage.setItem(TOKEN_KEY, tk);
    show('#cfg-msg', 'ok', '已儲存連線設定（token 只留喺呢個分頁）');
  }
  function token() {
    return $('#token').value.trim() || sessionStorage.getItem(TOKEN_KEY) || '';
  }

  /* ---------- 載入資料 ---------- */
  function baseUrl() {
    return new URL('../', location.href).href;
  }
  function loadJSON(rel) {
    return fetch(new URL(rel, baseUrl()).href, { cache: 'no-store' })
      .then(function (r) { return r.json(); });
  }

  function fillSections() {
    var sel = $('#f-section');
    sel.innerHTML = state.sections.map(function (s) {
      return '<option value="' + esc(s.id) + '">' + esc(s.icon + ' ' + s.title) + '</option>';
    }).join('');
    var dl = $('#topic-list');
    var all = [];
    Object.keys(state.topics).forEach(function (k) {
      if (k.charAt(0) === '_') return;              // 跳過 _comment 之類嘅說明欄
      var arr = state.topics[k];
      if (!Array.isArray(arr)) return;
      arr.forEach(function (t) { if (all.indexOf(t) === -1) all.push(t); });
    });
    dl.innerHTML = all.map(function (t) { return '<option value="' + esc(t) + '">'; }).join('');
  }

  function renderTable() {
    var list = (state.games.games || []).slice();
    var tb = $('#game-table tbody');
    if (!list.length) {
      tb.innerHTML = '<tr><td colspan="4">仲未有遊戲</td></tr>';
      return;
    }
    tb.innerHTML = list.map(function (g) {
      return '<tr>' +
        '<td>' + esc(g.title) + '</td>' +
        '<td>' + esc(g.section) + '</td>' +
        '<td>' + esc(g.topic) + '</td>' +
        '<td>' + esc(g.sizeText || '') + '</td>' +
      '</tr>';
    }).join('');
  }

  /* ---------- slug ---------- */
  function suggestSlug(title) {
    var ascii = String(title).toLowerCase()
      .replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
    // 純中文標題冇辦法自動轉英文，唔好硬塞一個亂碼 slug —— 留空等波仔自己打
    if (ascii.length >= 3) return ascii;
    return '';
  }
  function currentSlug() {
    var v = $('#f-slug').value.trim().toLowerCase();
    if (!v) v = suggestSlug($('#f-title').value.trim());
    return v.replace(/[^a-z0-9-]/g, '-').replace(/-+/g, '-').replace(/^-+|-+$/g, '');
  }
  function updateUrlPreview() {
    var sec = $('#f-section').value;
    var slug = currentSlug();
    var o = ($('#owner').value || '<用戶名>').trim();
    var r = ($('#repo').value || 'math-game-hub').trim();
    $('#url-preview').textContent = slug
      ? '最終網址：https://' + o + '.github.io/' + r + '/games/' + sec + '/' + slug + '/'
      : '最終網址：—';
  }

  /* ---------- 選檔 ---------- */
  function onFileChange() {
    var input = $('#f-file');
    var f = input.files && input.files[0];
    var info = $('#size-info');
    var btn = $('#btn-upload');
    state.file = null; state.fileBytes = null; state.fileText = '';
    if (!f) { info.textContent = ''; btn.disabled = true; return; }

    if (f.size > MAX_ALLOW) {
      info.innerHTML = '<span class="size-pill heavy">' + humanSize(f.size) + ' · 太大</span> ' +
        '超過 25MB，瀏覽器上傳唔穩定。請用方法 A（叫我幫你跑 build.py）。';
      btn.disabled = true;
      return;
    }
    var lvl = wifiLevel(f.size);
    var pill = '<span class="size-pill ' + lvl + '">' + humanSize(f.size) + '</span>';
    var note = '';
    if (lvl === 'heavy') note = ' ⚠️ 檔案偏大，上傳可能要 30 秒以上，失敗就用方法 A。';
    else if (lvl === 'medium') note = ' 建議用 Wi-Fi 上傳。';
    else note = ' 大小正常。';

    var reader = new FileReader();
    reader.onload = function () {
      state.file = f;
      state.fileBytes = new Uint8Array(reader.result);
      state.fileText = bytesToText(state.fileBytes);
      var needsNet = /(?:src|href)\s*=\s*["']https?:\/\//i.test(state.fileText);
      info.innerHTML = pill + note + ' 選中：<strong>' + esc(f.name) + '</strong>' +
        (needsNet ? ' <span class="badge net">需外網</span>' : '');
      btn.disabled = false;
    };
    reader.onerror = function () {
      info.textContent = '讀取檔案失敗，請再試一次。';
      btn.disabled = true;
    };
    reader.readAsArrayBuffer(f);

    if (!state.fileText) {
      info.innerHTML = pill + note + ' 讀取中…';
    }
  }

  /* ================= 開放控制 🔒 ================= */

  var gateDirty = false;
  var gateTimer = null;
  var gateSaving = false;   // 防止連續撳掣造成 409

  function gameOpen(g) {
    var o = state.open || {};
    var v = o.games && o.games[g.id];
    if (v === true || v === false) return v;
    v = o.sections && o.sections[g.section];
    if (v === true || v === false) return v;
    return o.all !== false;
  }

  function sectionOpen(id) {
    var o = state.open || {};
    var v = o.sections && o.sections[id];
    if (v === true || v === false) return v;
    return o.all !== false;
  }

  function tglHtml(kind, key, label, sub, on) {
    return '' +
      '<div class="tgl-row">' +
        '<div class="tgl-label"><b>' + esc(label) + '</b>' +
          (sub ? '<span>' + esc(sub) + '</span>' : '') +
        '</div>' +
        '<button type="button" class="tgl' + (on ? ' on' : '') + '"' +
          ' data-kind="' + kind + '"' + (key ? ' data-key="' + esc(key) + '"' : '') + '>' +
          '<span class="tgl-track"><span class="tgl-knob"></span></span>' +
          '<span class="tgl-text">' + (on ? '開放' : '未開放') + '</span>' +
        '</button>' +
      '</div>';
  }

  function paintTgl(btn, on) {
    btn.classList.toggle('on', on);
    btn.querySelector('.tgl-text').textContent = on ? '開放' : '未開放';
  }

  function renderGate() {
    var o = state.open || {};
    var allOn = o.all !== false;
    paintTgl($('#tgl-all'), allOn);
    $('#f-gate-msg').value = o.message || '';

    $('#tgl-sections').innerHTML = state.sections.map(function (s) {
      return tglHtml('section', s.id, s.title, s.desc, sectionOpen(s.id));
    }).join('');

    var groups = {};
    (state.games.games || []).forEach(function (g) {
      (groups[g.section] = groups[g.section] || []).push(g);
    });
    var html = '';
    state.sections.forEach(function (s) {
      var list = groups[s.id] || [];
      if (!list.length) return;
      html += '<div class="tgl-group-title" style="margin-top:10px">' + esc(s.title) + '</div>';
      html += list.map(function (g) {
        return tglHtml('game', g.id, g.title, g.topic, gameOpen(g));
      }).join('');
    });
    $('#tgl-games').innerHTML = html;

    Array.prototype.forEach.call(
      document.querySelectorAll('.tgl[data-kind="section"], .tgl[data-kind="game"]'),
      function (btn) {
        btn.onclick = function () { toggleGate(btn); };
      });
  }

  function toggleGate(btn) {
    var kind = btn.getAttribute('data-kind');
    var key = btn.getAttribute('data-key');
    var o = state.open;
    o.sections = o.sections || {};
    o.games = o.games || {};

    if (kind === 'all') {
      o.all = !(o.all !== false);
      paintTgl($('#tgl-all'), o.all);
      renderGate();
    } else if (kind === 'section') {
      o.sections[key] = !sectionOpen(key);
      paintTgl(btn, sectionOpen(key));
    } else {
      var g = (state.games.games || []).filter(function (x) { return x.id === key; })[0];
      if (!g) return;
      o.games[key] = !gameOpen(g);
      paintTgl(btn, gameOpen(g));
    }
    markDirty();
  }

  function setSaveState(cls, text) {
    var el = $('#gate-state');
    el.className = 'save-state' + (cls ? ' ' + cls : '');
    el.textContent = text;
  }

  function markDirty() {
    gateDirty = true;
    setSaveState('dirty', '● 有改動未儲存');
    $('#btn-gate-save').disabled = false;
    clearTimeout(gateTimer);
    gateTimer = setTimeout(saveGate, 1800);   // 撳完 1.8 秒自動儲存
  }

  /* ---------- 測試連線（診斷用） ---------- */
  function testToken() {
    var msg = '#cfg-msg';
    var tk = token();
    var owner = state.cfg.owner || $('#owner').value.trim();
    var repo = ($('#repo').value || 'math-game-hub').trim();
    if (!tk) { show(msg, 'err', '請先貼 token'); return; }
    if (!owner) { show(msg, 'err', '請先填 GitHub 用戶名'); return; }
    show(msg, 'ok', '測試緊…');
    api('/repos/' + owner + '/' + repo, { token: tk })
      .then(function (d) {
        show(msg, 'ok', '✅ Token 正常！帳號 <b>' + esc(d.owner.login) +
          '</b>，repo「' + esc(d.name) + '」讀取成功。可以直接撳開關。');
      })
      .catch(function (e) {
        var extra = '';
        if (e.status === 401) extra = '（token 貼錯咗？試下撳「清除 token」再重新貼）';
        if (e.status === 404) extra = '（用戶名或 repo 名拼錯？）';
        show(msg, 'err', '❌ ' + esc(e.message) + extra);
      });
  }

  function saveGate() {
    clearTimeout(gateTimer);
    if (gateSaving) return;          // 上一個儲存未完，等佢自己完成
    var msg = '#gate-msg';
    hide(msg);
    var tk = token();
    var owner = state.cfg.owner || '';
    var repo = state.cfg.repo || 'math-game-hub';
    var branch = state.cfg.branch || 'main';

    if (!tk || !owner) {
      setSaveState('dirty', '● 未儲存（要先填 GitHub token）');
      show(msg, 'err', '要改開放設定，請先喺下面「2. GitHub 連線」填用戶名同 token。');
      return Promise.resolve();
    }

    var d = new Date(Date.now() + 8 * 3600 * 1000);
    state.open.updatedAt = d.toISOString().slice(0, 16).replace('T', ' ');
    var payload = JSON.stringify(state.open, null, 2) + '\n';
    var apiPath = '/repos/' + owner + '/' + repo + '/contents/data/open.json';
    setSaveState('saving', '儲存中…');
    $('#btn-gate-save').disabled = true;
    gateSaving = true;

    /* 用 Contents API：只改一個細檔，唔使行 Git Data API */
    return api(apiPath + '?ref=' + encodeURIComponent(branch), { token: tk })
      .then(function (info) { return info.sha || null; })
      .catch(function () { return null; })      // 檔案未存在 → 當新增
      .then(function (sha) {
        var bodyObj = {
          message: '更新開放設定',
          content: bytesToB64(textToBytes(payload)),
          branch: branch
        };
        if (sha) bodyObj.sha = sha;
        return api(apiPath, { method: 'PUT', token: tk, body: bodyObj });
      })
      .then(function () {
        gateDirty = false;
        gateSaving = false;
        setSaveState('ok', '✅ 已儲存 · 1–2 分鐘後生效');
        $('#btn-gate-save').disabled = true;
      })
      .catch(function (e) {
        gateSaving = false;
        setSaveState('dirty', '● 儲存失敗');
        $('#btn-gate-save').disabled = false;
        var hint = '';
        if (e.status === 401) {
          hint = '<br><b>401 = token 本身唔啱</b>。請檢查：' +
            '<br>· 有冇複製到完整（有冇甩頭尾）<br>· 有冇意外帶入空格或換行<br>' +
            '· 貼入前撳「清除 token」清走舊嗰個再貼過';
        } else if (e.status === 409) {
          hint = '<br><b>409 = 兩次儲存撞車</b>，唔關 token 事。撳多一下「立即儲存」就得。';
        } else {
          hint = '<br>請檢查用戶名／repo／分支填得啱唔啱。';
        }
        show(msg, 'err', '❌ 儲存失敗：' + esc(e.message) + hint);
      });
  }

  /* ---------- 上傳（原子 commit） ---------- */
  function sleep(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }

  function upload() {
    var btn = $('#btn-upload');
    var msg = '#up-msg';
    hide(msg);

    var tk = token();
    var owner = $('#owner').value.trim();
    var repo = ($('#repo').value || 'math-game-hub').trim();
    var branch = ($('#branch').value || 'main').trim();
    var title = $('#f-title').value.trim();
    var section = $('#f-section').value;
    var topic = $('#f-topic').value.trim();
    var slug = currentSlug();

    if (!tk) { show(msg, 'err', '請先填 GitHub token。'); return; }
    if (!owner) { show(msg, 'err', '請先填 GitHub 用戶名。'); return; }
    if (!title) { show(msg, 'err', '請填遊戲名稱。'); return; }
    if (!section) { show(msg, 'err', '請揀放喺邊一區。'); return; }
    if (!topic) { show(msg, 'err', '請填課題（用嚟做分類）。'); return; }
    if (!state.file || !state.fileBytes) { show(msg, 'err', '請揀一個 HTML 檔。'); return; }
    if (!slug) { show(msg, 'err', '請填網址代號（英文、細楷、用 - 連接），例如 fraction-adventure。中文標題冇辦法自動轉英文，所以要你自己打一個。'); return; }

    var exists = (state.games.games || []).some(function (g) { return g.id === slug; });
    if (exists) {
      show(msg, 'err', '已經有遊戲用咗 slug「' + esc(slug) + '」，請改另一個（或者去改舊嗰個嘅 slug）。');
      return;
    }

    btn.disabled = true;
    var step = '';
    function progress(t) { step = t; show(msg, 'warn', '⏳ ' + t + '…'); }

    var base = '/repos/' + owner + '/' + repo;
    var headSha, treeSha, htmlBlobSha, jsonBlobSha, gateBlobSha;
    var gamePath, gatePath, newGamesJson;

    progress('讀取遠端最新狀態');
    api(base + '/git/ref/heads/' + encodeURIComponent(branch), { token: tk })
      .then(function (ref) {
        headSha = ref.object.sha;
        return api(base + '/git/commits/' + headSha, { token: tk });
      })
      .then(function (commit) {
        treeSha = commit.tree.sha;
        return api(base + '/contents/data/games.json?ref=' + encodeURIComponent(branch), { token: tk });
      })
      .then(function (fileInfo) {
        var txt = bytesToText(b64ToBytes(fileInfo.content || ''));
        var data = JSON.parse(txt);
        state.games = data;

        /* 注入本機排行榜外掛，確保後台上傳嘅遊戲一樣有 🏆 掣 */
        var bytes = injectBoard(state.fileBytes,
          { id: slug, title: title, section: section });
        var total = bytes.length;
        var needsNet = /(?:src|href)\s*=\s*["']https?:\/\//i.test(state.fileText);

        progress('計算檔案指紋');
        return sha256Hex(bytes).then(function (hash) {
          data.games = data.games || [];
          data.games.push({
            id: slug,
            section: section,
            title: title,
            titleFromHtml: '',
            topic: topic,
            keywords: [],
            bytes: total,
            totalBytes: total,
            sizeText: humanSize(total),
            wifi: wifiLevel(total),
            depCount: 0,
            needsNetwork: needsNet,
            sha256: hash,
            source: '(後台上傳) ' + state.file.name,
            entry: 'games/' + section + '/' + slug + '/',
            file: 'play.html',
            deps: [],
            unresolvedRefs: []
          });
          data.games.sort(function (a, b) {
            return (a.section + a.title).localeCompare(b.section + b.title, 'zh-Hant');
          });
          data.count = data.games.length;
          data.totalBytes = data.games.reduce(function (a, g) { return a + (g.totalBytes || 0); }, 0);
          var d = new Date(Date.now() + 8 * 3600 * 1000);
          data.updated = d.toISOString().slice(0, 16).replace('T', ' ');
          newGamesJson = JSON.stringify(data, null, 2) + '\n';

          gamePath = 'games/' + section + '/' + slug + '/play.html';
          progress('上傳遊戲檔（' + humanSize(total) + '）');
          return api(base + '/git/blobs', {
            method: 'POST', token: tk,
            body: { content: bytesToB64(bytes), encoding: 'base64' }
          });
        });
      })
      .then(function (blob) {
        htmlBlobSha = blob.sha;
        progress('產生守門頁');
        /* 守門頁：index.html 會先查 open.json，未開放就唔放行去 play.html */
        return fetch(new URL('../scripts/gate_template.html', location.href).href)
          .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.text(); })
          .catch(function () { return null; });
      })
      .then(function (tpl) {
        var gateHtml;
        if (tpl) {
          gateHtml = tpl
            .replace('__SECTION__', JSON.stringify(section))
            .replace('__SLUG__', JSON.stringify(slug))
            .replace('__TITLE__', JSON.stringify(title));
        } else {
          /* 模板唔見咗都要起碼識直接跳去 play.html，唔可以變死連結 */
          gateHtml = '<!doctype html><meta charset="utf-8">' +
            '<meta http-equiv="refresh" content="0;url=play.html">' +
            '<script>location.replace("play.html")</script>';
        }
        gatePath = 'games/' + section + '/' + slug + '/index.html';
        return api(base + '/git/blobs', {
          method: 'POST', token: tk,
          body: { content: bytesToB64(textToBytes(gateHtml)), encoding: 'base64' }
        });
      })
      .then(function (blob) {
        gateBlobSha = blob.sha;
        progress('更新遊戲清單');
        return api(base + '/git/blobs', {
          method: 'POST', token: tk,
          body: { content: bytesToB64(textToBytes(newGamesJson)), encoding: 'base64' }
        });
      })
      .then(function (blob) {
        jsonBlobSha = blob.sha;
        progress('建立新版本');
        return api(base + '/git/trees', {
          method: 'POST', token: tk,
          body: {
            base_tree: treeSha,
            tree: [
              { path: gamePath, mode: '100644', type: 'blob', sha: htmlBlobSha },
              { path: gatePath, mode: '100644', type: 'blob', sha: gateBlobSha },
              { path: 'data/games.json', mode: '100644', type: 'blob', sha: jsonBlobSha }
            ]
          }
        });
      })
      .then(function (tree) {
        return api(base + '/git/commits', {
          method: 'POST', token: tk,
          body: {
            message: '新增遊戲：' + title + '（後台上傳）',
            tree: tree.sha,
            parents: [headSha]
          }
        });
      })
      .then(function (commit) {
        return api(base + '/git/refs/heads/' + encodeURIComponent(branch), {
          method: 'PATCH', token: tk,
          body: { sha: commit.sha, force: false }
        });
      })
      .then(function () {
        var url = 'https://' + owner + '.github.io/' + repo + '/games/' + section + '/' + slug + '/';
        show(msg, 'ok',
          '✅ 上傳成功！<br>' +
          'GitHub Pages 大約要 <strong>1–2 分鐘</strong>重新發佈，之后就可以開：<br>' +
          '<a href="' + esc(url) + '" target="_blank" rel="noopener">' + esc(url) + '</a><br><br>' +
          '<a href="../' + esc(section) + '/">→ 去' + esc(section) + '頁睇下</a>');
        $('#btn-upload').disabled = true;
        $('#f-file').value = '';
        $('#f-title').value = '';
        $('#f-slug').value = '';
        $('#f-topic').value = '';
      })
      .catch(function (e) {
        show(msg, 'err', '❌ 失敗（' + esc(step) + '）：' + esc(e.message) +
          '<br><br>如果係大檔失敗，請改用「方法 A」：叫我幫你跑 <code>python3 scripts/build.py</code>。');
      })
      .then(function () {
        btn.disabled = false;
      });
  }

  /* ---------- 解鎖 ---------- */
  function unlock() {
    var v = $('#pw').value;
    if (v === PASSWORD) {
      $('#lock-panel').hidden = true;
      $('#admin-body').hidden = false;
      sessionStorage.setItem('mgh_unlocked', '1');
      boot();
    } else {
      show('#pw-msg', 'err', '密碼唔啱，再試一次。');
    }
  }

  /* ---------- 注入本機排行榜外掛（同 build.py 完全一致） ---------- */
  var NEEDLE_BODY = [60, 47, 98, 111, 100, 121, 62]; // "</body>"

  function indexOfBytes(hay, needle, from) {
    var n = needle.length;
    outer:
    for (var i = from; i <= hay.length - n; i++) {
      for (var j = 0; j < n; j++) {
        if (hay[i + j] !== needle[j]) continue outer;
      }
      return i;
    }
    return -1;
  }

  function injectBoard(u8, meta) {
    try {
      // 已經有就唔重複注入
      var marker = textToBytes('MGH_GAME');
      if (indexOfBytes(u8, marker, 0) !== -1) return u8;

      var snippet = '\n<script>window.MGH_GAME=' +
        JSON.stringify(meta).replace(/</g, '\\u003c') + ';<\/script>\n' +
        '<script src="../../../assets/js/board.js"><\/script>\n';
      var tail = textToBytes(snippet);

      // 由尾搵最後一個 </body>，唔使掃全部（掃到就用）
      var pos = -1;
      for (var i = u8.length - NEEDLE_BODY.length; i >= 0; i--) {
        var hit = true;
        for (var j = 0; j < NEEDLE_BODY.length; j++) {
          if (u8[i + j] !== NEEDLE_BODY[j]) { hit = false; break; }
        }
        if (hit) { pos = i; break; }
      }
      if (pos === -1) pos = u8.length;

      var out = new Uint8Array(u8.length + tail.length);
      out.set(u8.subarray(0, pos), 0);
      out.set(tail, pos);
      out.set(u8.subarray(pos), pos + tail.length);
      return out;
    } catch (e) {
      return u8; // 注入失敗就照原樣上傳，唔好阻住
    }
  }

  function boot() {
    loadCfg();
    Promise.all([
      loadJSON('data/games.json'),
      loadJSON('data/sections.json'),
      loadJSON('data/topics.json'),
      /* 讀唔到 open.json 一律當全開：寧願漏鎖，都唔好搞到上唔到堂 */
      loadJSON('data/open.json').catch(function () {
        return { all: true, sections: {}, games: {}, message: '' };
      })
    ]).then(function (res) {
      state.games = res[0] || {};
      state.sections = res[1] || [];
      state.topics = res[2] || {};
      state.open = res[3] || { all: true, sections: {}, games: {}, message: '' };
      state.open.sections = state.open.sections || {};
      state.open.games = state.open.games || {};
      fillSections();
      renderTable();
      renderGate();
      updateUrlPreview();
    }).catch(function (e) {
      show('#up-msg', 'err', '載入清單失敗：' + esc(e.message));
    });

    $('#tgl-all').onclick = function () { toggleGate($('#tgl-all')); };
    $('#btn-gate-save').onclick = saveGate;
    $('#f-gate-msg').oninput = function () {
      state.open.message = $('#f-gate-msg').value;
      markDirty();
    };
    $('#btn-save-cfg').onclick = saveCfg;
    $('#btn-test-token').onclick = testToken;
    $('#btn-clear-token').onclick = function () {
      sessionStorage.removeItem(TOKEN_KEY);
      $('#token').value = '';
      show('#cfg-msg', 'ok', '已清除呢個分頁嘅 token');
    };
    $('#btn-upload').onclick = upload;
    $('#f-file').onchange = onFileChange;
    $('#f-title').oninput = function () {
      if (!$('#f-slug').value) {
        $('#f-slug').value = suggestSlug($('#f-title').value.trim());
      }
      updateUrlPreview();
    };
    $('#f-slug').oninput = updateUrlPreview;
    $('#f-section').onchange = updateUrlPreview;
    $('#owner').oninput = updateUrlPreview;
    $('#repo').oninput = updateUrlPreview;
  }

  $('#btn-unlock').onclick = unlock;
  $('#pw').addEventListener('keydown', function (e) {
    if (e.key === 'Enter') unlock();
  });

  if (sessionStorage.getItem('mgh_unlocked') === '1') {
    $('#lock-panel').hidden = true;
    $('#admin-body').hidden = false;
    boot();
  }
})();
