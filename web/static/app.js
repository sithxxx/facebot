(function () {
  const tg = window.Telegram && window.Telegram.WebApp ? window.Telegram.WebApp : null;
  if (tg) {
    tg.ready();
    tg.expand();
    if (tg.colorScheme === "dark") document.body.classList.add("tg-dark");
    if (tg.onEvent) tg.onEvent("themeChanged", () => {
      document.body.classList.toggle("tg-dark", tg.colorScheme === "dark");
    });
  }

  const AUTH = "tma " + (tg ? tg.initData : "");
  const content = document.getElementById("content");
  const meChip = document.getElementById("me-chip");
  const tabs = document.querySelectorAll(".tab");
  const genderBtns = document.querySelectorAll(".gender-btn");

  let gender = "male";
  let view = "global";

  function haptic() {
    if (tg && tg.HapticFeedback) tg.HapticFeedback.impactOccurred("light");
  }

  async function api(path) {
    const sep = path.includes("?") ? "&" : "?";
    const res = await fetch(path + sep + "gender=" + gender, { headers: { Authorization: AUTH } });
    if (!res.ok) {
      const detail = res.status === 401 ? "Open the app through the bot" : "Error " + res.status;
      throw new Error(detail);
    }
    return res.json();
  }

  function el(tag, cls, text) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }

  function showState(msg) {
    content.innerHTML = "";
    content.appendChild(el("div", "state", msg));
  }

  function fmtScore(s) {
    return Number(s).toFixed(2);
  }

  function tierPhoto(t, cls) {
    const img = el("img", cls || "tier-photo");
    img.src = t.photo;
    img.alt = t.name;
    img.style.setProperty("--tier-color", t.color);
    img.onerror = () => {
      const fb = el("div", "tier-fallback", t.name[0]);
      fb.style.setProperty("--tier-color", t.color);
      img.replaceWith(fb);
    };
    return img;
  }

  function renderRows(entries, myId, container) {
    const list = el("div", "list");
    for (const e of entries) {
      const row = el("div", "row" + (myId && e.user_id === myId ? " me" : ""));
      row.append(
        el("div", "rank" + (e.rank <= 3 ? " top" : ""), "#" + e.rank),
        el("div", "name", e.name || "Anonymous"),
        el("div", "score", fmtScore(e.score))
      );
      list.appendChild(row);
    }
    container.appendChild(list);
  }

  function updateMeChip(me) {
    if (me && me.rank) {
      meChip.textContent = `#${me.rank} · ${fmtScore(me.score)}`;
      meChip.classList.remove("hidden");
    } else {
      meChip.classList.add("hidden");
    }
  }

  async function viewGlobal() {
    showState("Loading…");
    try {
      const data = await api("/api/leaderboard/global");
      content.innerHTML = "";
      if (!data.entries.length) {
        showState("Nobody here yet. Be the first!");
      } else {
        renderRows(data.entries, data.me ? data.me.user_id : null, content);
      }
      updateMeChip(data.me && data.me.gender === gender ? data.me : null);
    } catch (err) {
      showState(err.message);
    }
  }

  async function viewTiers() {
    showState("Loading…");
    try {
      const data = await api("/api/leaderboard/tiers");
      const wrap = el("div", "tiers");
      for (const t of data.tiers) {
        const card = el("div", "tier-card");
        card.style.setProperty("--tier-color", t.color);
        card.appendChild(tierPhoto(t));
        const info = el("div", "tier-info");
        info.appendChild(el("div", "tier-name", t.name === t.name_full ? t.name : `${t.name} · ${t.name_full}`));
        info.appendChild(el("div", "tier-sub", `PSL ${t.psl_range} · ${t.percentile}`));
        card.appendChild(info);
        card.appendChild(el("div", "tier-arrow", "›"));
        card.addEventListener("click", () => { haptic(); viewTierDetail(t.slug); });
        wrap.appendChild(card);
      }
      content.innerHTML = "";
      content.appendChild(wrap);
    } catch (err) {
      showState(err.message);
    }
  }

  async function viewTierDetail(slug) {
    showState("Loading…");
    try {
      const data = await api("/api/leaderboard/tier/" + encodeURIComponent(slug));
      const head = el("div", "detail-head");
      const back = el("button", "back-btn", "‹ Back");
      back.addEventListener("click", () => { haptic(); viewTiers(); });
      head.appendChild(back);
      const title = el("div", "detail-title");
      title.appendChild(tierPhoto(data.tier, "detail-photo"));
      title.appendChild(document.createTextNode(data.tier.name));
      head.appendChild(title);
      content.innerHTML = "";
      content.appendChild(head);
      if (!data.entries.length) {
        content.appendChild(el("div", "state", "Nobody in this tier yet."));
        return;
      }
      renderRows(data.entries, null, content);
    } catch (err) {
      showState(err.message);
    }
  }

  function refresh() {
    if (view === "global") viewGlobal();
    else viewTiers();
  }

  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      haptic();
      tabs.forEach((t) => t.classList.remove("active"));
      tab.classList.add("active");
      view = tab.dataset.view;
      refresh();
    });
  });

  genderBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      haptic();
      genderBtns.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      gender = btn.dataset.gender;
      refresh();
    });
  });

  refresh();
})();
