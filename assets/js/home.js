/* Homepage enhancements. No framework, build step, or third-party dependency. */
(() => {
  "use strict";
  const $ = (s) => document.querySelector(s);
  const grid = $("#chapterGrid");
  const stagesNode = $("#stageGrid");
  const filterBar = $("#filterBar");
  const input = $("#chapterSearch");
  const count = $("#resultCount");
  const empty = $("#emptyState");
  const progressText = $("#progressText");
  const progressFill = $("#progressFill");
  const progressTrack = $("#progressTrack");
  const continueLink = $("#continueLink");
  const COMPLETED_KEY = "can-bus-tutorial:completed:v1";
  const LAST_KEY = "can-bus-tutorial:last:v1";
  const state = { chapters: [], stages: [], stage: "all", query: "", completed: new Set(), last: "" };

  function getLocal(key) {
    try { return window.localStorage.getItem(key); } catch (_) { return null; }
  }
  function setLocal(key, value) {
    try { window.localStorage.setItem(key, value); } catch (_) { /* Storage can be disabled. */ }
  }
  function node(tag, cls, value) {
    const result = document.createElement(tag);
    if (cls) result.className = cls;
    if (value !== undefined) result.textContent = value;
    return result;
  }
  function idOf(chapter) { return String(chapter.num).padStart(2, "0"); }
  function stageOf(chapter) {
    const number = Number(chapter.num);
    return state.stages.find((stage) => number >= stage.start && number <= stage.end);
  }
  function normalized(value) {
    return String(value == null ? "" : value).normalize("NFKC").toLowerCase().trim();
  }
  function validIds() { return new Set(state.chapters.map(idOf)); }
  function restoreProgress() {
    try {
      const value = JSON.parse(getLocal(COMPLETED_KEY) || "[]");
      state.completed = new Set(Array.isArray(value) ? value.map(String) : []);
    } catch (_) { state.completed = new Set(); }
    state.last = getLocal(LAST_KEY) || "";
  }
  function updateProgress() {
    const ids = validIds();
    const done = [...state.completed].filter((id) => ids.has(id)).length;
    const total = state.chapters.length;
    progressText.textContent = done + " / " + total;
    progressFill.style.width = (total ? done / total * 100 : 0) + "%";
    progressTrack.setAttribute("aria-valuemax", String(total));
    progressTrack.setAttribute("aria-valuenow", String(done));
    continueLink.hidden = !ids.has(state.last);
    if (!continueLink.hidden) {
      continueLink.href = state.last + ".html";
      continueLink.textContent = "继续第 " + state.last + " 章 →";
    }
  }
  function rememberLast(id) {
    state.last = id;
    setLocal(LAST_KEY, id);
    updateProgress();
  }
  function selectStage(id) {
    state.stage = id;
    filterBar.querySelectorAll("button[data-filter]").forEach((button) => {
      const active = button.dataset.filter === id;
      button.classList.toggle("active", active);
      button.setAttribute("aria-pressed", String(active));
    });
    renderChapters();
  }
  function renderStageCards() {
    const cards = state.stages.map((stage, index) => {
      const a = node("a", "stage-card");
      a.href = "#chapters";
      a.setAttribute("aria-label", "查看" + stage.title + "相关章节");
      const top = node("div", "stage-top");
      top.append(node("span", "stage-number", "STAGE " + String(index + 1).padStart(2, "0")));
      top.append(node("span", "stage-range", String(stage.start).padStart(2, "0") + "—" + String(stage.end).padStart(2, "0")));
      const cta = node("span", "stage-cta");
      cta.append(node("span", "", (stage.end - stage.start + 1) + " 章内容"), node("span", "", "查看章节 ↗"));
      a.append(top, node("h3", "", stage.title), node("p", "", stage.description), cta);
      a.addEventListener("click", () => selectStage(stage.id));
      return a;
    });
    stagesNode.replaceChildren(...cards);
    $("#heroStageCount").textContent = String(state.stages.length);
    $("#heroChapterCount").textContent = String(state.chapters.length);
  }
  function renderFilters() {
    filterBar.replaceChildren();
    const items = [{ id: "all", title: "全部章节" }, ...state.stages];
    for (const item of items) {
      const button = node("button", "filter", item.title);
      button.type = "button";
      button.dataset.filter = item.id;
      button.setAttribute("aria-pressed", "false");
      button.addEventListener("click", () => selectStage(item.id));
      filterBar.append(button);
    }
    selectStage("all");
  }
  function createChapterCard(chapter) {
    const id = idOf(chapter);
    const stage = stageOf(chapter);
    const done = state.completed.has(id);
    const article = node("article", "chapter-card" + (done ? " is-done" : ""));
    const top = node("div", "chapter-top");
    top.append(node("span", "chapter-id", "CH. " + id), node("span", "chapter-phase", stage ? stage.title : ""));
    const h3 = node("h3");
    const headingLink = node("a", "", chapter.title);
    headingLink.href = chapter.file;
    headingLink.addEventListener("click", () => rememberLast(id));
    h3.append(headingLink);
    const topics = node("p", "chapter-topics", chapter.topics.join(" · "));
    const actions = node("div", "chapter-actions");
    const read = node("a", "chapter-read", "阅读本章 →");
    read.href = chapter.file;
    read.setAttribute("aria-label", "阅读第 " + id + " 章：" + chapter.title);
    read.addEventListener("click", () => rememberLast(id));
    const mark = node("button", "mark-button", done ? "✓ 已标记" : "○ 标记已学");
    mark.type = "button";
    mark.setAttribute("aria-pressed", String(done));
    mark.setAttribute("aria-label", "第 " + id + " 章：" + (done ? "取消学习标记" : "标记已学"));
    mark.addEventListener("click", () => {
      if (state.completed.has(id)) state.completed.delete(id);
      else state.completed.add(id);
      setLocal(COMPLETED_KEY, JSON.stringify([...state.completed]));
      renderChapters();
      updateProgress();
      const match = [...grid.querySelectorAll(".chapter-id")].find((el) => el.textContent === "CH. " + id);
      if (match) match.closest(".chapter-card").querySelector(".mark-button").focus();
    });
    actions.append(read, mark);
    article.append(top, h3, topics, actions);
    return article;
  }
  function renderChapters() {
    const query = normalized(state.query);
    const matches = state.chapters.filter((chapter) => {
      const stage = stageOf(chapter);
      if (state.stage !== "all" && (!stage || stage.id !== state.stage)) return false;
      const searchable = [chapter.num, chapter.title, ...chapter.topics, stage ? stage.title : ""].join(" ");
      return !query || normalized(searchable).includes(query);
    });
    grid.replaceChildren(...matches.map(createChapterCard));
    empty.hidden = matches.length > 0;
    count.textContent = "显示 " + matches.length + " / " + state.chapters.length + " 章";
  }
  function validate(data) {
    if (!data || !Array.isArray(data.chapters) || !Array.isArray(data.stages)) throw new Error("无效的课程元数据");
    const ids = new Set();
    for (const chapter of data.chapters) {
      const id = idOf(chapter);
      if (!/^\d{2}$/.test(id) || ids.has(id) || chapter.file !== id + ".html" || !Array.isArray(chapter.topics)) throw new Error("章节元数据不完整");
      ids.add(id);
    }
    const stages = [...data.stages].sort((a, b) => a.start - b.start);
    let cursor = 1;
    for (const stage of stages) {
      if (!stage.id || !stage.title || !stage.description || !Number.isInteger(stage.start) || !Number.isInteger(stage.end) || stage.start !== cursor || stage.end < cursor) throw new Error("学习阶段元数据不完整");
      cursor = stage.end + 1;
    }
    if (cursor !== data.chapters.length + 1) throw new Error("学习阶段与章节数量不一致");
    return stages;
  }
  function showFailure() {
    grid.replaceChildren(node("p", "loading", "目录暂时无法加载。请通过 HTTP 服务器打开站点，或直接访问章节文件。"));
    const link = node("a", "chapter-read", "直接阅读第 01 章 →");
    link.href = "01.html";
    grid.append(link);
    stagesNode.replaceChildren(node("p", "loading", "学习路线加载失败"));
    count.textContent = "目录加载失败";
  }

  input.addEventListener("input", () => { state.query = input.value; renderChapters(); });
  $("#resetFilters").addEventListener("click", () => {
    input.value = "";
    state.query = "";
    selectStage("all");
    input.focus();
  });
  document.addEventListener("keydown", (event) => {
    if (event.key !== "/" || event.ctrlKey || event.metaKey || event.altKey) return;
    const tag = event.target && event.target.tagName;
    if (tag === "INPUT" || tag === "TEXTAREA" || (event.target && event.target.isContentEditable)) return;
    event.preventDefault();
    input.focus();
  });
  window.addEventListener("storage", (event) => {
    if (event.key !== COMPLETED_KEY && event.key !== LAST_KEY) return;
    restoreProgress();
    renderChapters();
    updateProgress();
  });

  fetch("courses.json")
    .then((response) => {
      if (!response.ok) throw new Error("HTTP " + response.status);
      return response.json();
    })
    .then((data) => {
      state.stages = validate(data);
      state.chapters = [...data.chapters].sort((a, b) => Number(a.num) - Number(b.num));
      restoreProgress();
      renderStageCards();
      renderFilters();
      updateProgress();
    })
    .catch(showFailure);
})();
