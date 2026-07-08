const STORAGE_KEY = "adgrowth-ai-state-v1";

const state = loadState();

const platforms = {
  "小红书": ["种草感", "痛点共鸣", "真实体验"],
  "抖音": ["前三秒钩子", "强节奏", "评论区引导"],
  "Meta Ads": ["利益点清晰", "短句", "强 CTA"],
  "Google Search": ["搜索意图", "关键词匹配", "直接转化"],
  "朋友圈广告": ["可信背书", "生活场景", "轻决策"],
};

function loadState() {
  const saved = localStorage.getItem(STORAGE_KEY);
  if (saved) return JSON.parse(saved);
  return { briefs: [], creatives: [], experiments: [], reports: [], metrics: [] };
}

function saveState() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

function uid(prefix) {
  return `${prefix}_${Math.random().toString(36).slice(2, 9)}_${Date.now().toString(36)}`;
}

function fmtPercent(value) {
  return `${(value * 100).toFixed(2)}%`;
}

function fmtMoney(value) {
  return `¥${Number(value || 0).toFixed(2)}`;
}

function calcMetric(metric) {
  const ctr = metric.impressions ? metric.clicks / metric.impressions : 0;
  const cpc = metric.clicks ? metric.spend / metric.clicks : 0;
  const cvr = metric.clicks ? metric.conversions / metric.clicks : 0;
  const cpa = metric.conversions ? metric.spend / metric.conversions : 0;
  const roi = metric.spend ? metric.revenue / metric.spend : 0;
  return { ctr, cpc, cvr, cpa, roi };
}

function aggregateMetrics() {
  const total = state.metrics.reduce(
    (acc, item) => {
      acc.impressions += item.impressions;
      acc.clicks += item.clicks;
      acc.spend += item.spend;
      acc.conversions += item.conversions;
      acc.revenue += item.revenue;
      return acc;
    },
    { impressions: 0, clicks: 0, spend: 0, conversions: 0, revenue: 0 },
  );
  return { ...total, ...calcMetric(total) };
}

function generateCreatives(brief) {
  const angles = [
    "痛点直击",
    "效率提升",
    "结果证明",
    "低门槛尝试",
    "专业可信",
  ];
  const platformTraits = platforms[brief.platform] || ["清晰表达", "强 CTA"];
  return angles.slice(0, 4).map((angle, index) => {
    const version = String.fromCharCode(65 + index);
    const trait = platformTraits[index % platformTraits.length];
    const headline = makeHeadline(brief, angle);
    return {
      id: uid("creative"),
      briefId: brief.id,
      version,
      platform: brief.platform,
      angle,
      tone: brief.tone,
      trait,
      headline,
      body: makeBody(brief, angle, trait),
      cta: makeCta(brief.goal),
      videoScript: makeVideoScript(brief, angle),
      landingHero: makeLandingHero(brief, angle),
      status: index === 0 ? "favorite" : "active",
      createdAt: new Date().toISOString(),
    };
  });
}

function makeHeadline(brief, angle) {
  const map = {
    痛点直击: `还在为${brief.audience}转化低发愁？`,
    效率提升: `${brief.productName}，把广告创意效率提升 3 倍`,
    结果证明: `用${brief.productName}，让${brief.goal}更可控`,
    低门槛尝试: `不用广告经验，也能写出高转化素材`,
    专业可信: `为${brief.industry}打造的 AI 广告增长工具`,
  };
  return map[angle];
}

function makeBody(brief, angle, trait) {
  return `围绕「${brief.sellingPoints}」，针对「${brief.audience}」生成${trait}风格素材，帮助你在${brief.platform}更快测试卖点并提升${brief.goal}效率。`;
}

function makeCta(goal) {
  const map = {
    注册试用: "立即免费试用",
    购买订阅: "查看订阅方案",
    私域加微: "领取专属方案",
    "预约 Demo": "预约产品演示",
  };
  return map[goal] || "立即开始";
}

function makeVideoScript(brief, angle) {
  return `前三秒：提出${brief.audience}的核心痛点。\n中段：展示${brief.productName}如何围绕「${brief.sellingPoints}」解决问题。\n结尾：强调${brief.goal}，用「${makeCta(brief.goal)}」收口。`;
}

function makeLandingHero(brief, angle) {
  return `${brief.productName}：让${brief.audience}用 AI 快速完成广告创意、测试和复盘。`;
}

function createMetricsForCreative(creative, index) {
  const base = 8500 + index * 1700 + Math.floor(Math.random() * 2400);
  const ctr = 0.018 + index * 0.004 + Math.random() * 0.012;
  const cvr = 0.055 + Math.random() * 0.04;
  const clicks = Math.round(base * ctr);
  const spend = clicks * (2.8 + Math.random() * 3.2);
  const conversions = Math.max(1, Math.round(clicks * cvr));
  const revenue = conversions * (89 + Math.random() * 160);
  return {
    id: uid("metric"),
    creativeId: creative.id,
    impressions: base,
    clicks,
    spend: Number(spend.toFixed(2)),
    conversions,
    revenue: Number(revenue.toFixed(2)),
    date: new Date().toISOString().slice(0, 10),
  };
}

function createBriefFromForm(form) {
  const data = Object.fromEntries(new FormData(form).entries());
  return {
    id: uid("brief"),
    productName: data.productName.trim(),
    industry: data.industry.trim(),
    audience: data.audience.trim(),
    sellingPoints: data.sellingPoints.trim(),
    platform: data.platform,
    goal: data.goal,
    tone: data.tone,
    createdAt: new Date().toISOString(),
  };
}

function render() {
  renderMetrics();
  renderLeaderboard();
  renderAdvice();
  renderCreatives();
  renderExperiments();
  renderReports();
}

function renderMetrics() {
  const metrics = aggregateMetrics();
  const cards = [
    ["总曝光", metrics.impressions.toLocaleString(), "Impressions"],
    ["点击率 CTR", fmtPercent(metrics.ctr), "Clicks / Impressions"],
    ["转化成本 CPA", fmtMoney(metrics.cpa), "Spend / Conversions"],
    ["投入产出 ROI", metrics.roi.toFixed(2), "Revenue / Spend"],
  ];
  document.querySelector("#metricsGrid").innerHTML = cards
    .map(([label, value, hint]) => `<div class="metric-card"><span>${label}</span><strong>${value}</strong><span>${hint}</span></div>`)
    .join("");
}

function renderLeaderboard() {
  const box = document.querySelector("#leaderboard");
  if (!state.creatives.length) return renderEmpty(box);
  const ranked = state.creatives
    .map((creative) => {
      const metric = state.metrics.find((item) => item.creativeId === creative.id);
      return { creative, metric, calc: metric ? calcMetric(metric) : null };
    })
    .filter((item) => item.metric)
    .sort((a, b) => b.calc.roi - a.calc.roi);

  box.innerHTML = ranked
    .map((item, index) => {
      const width = Math.min(100, item.calc.roi * 25);
      return `<div class="rank-row">
        <div class="rank">${index + 1}</div>
        <div>
          <strong>版本 ${item.creative.version}：${item.creative.headline}</strong>
          <div class="bar"><i style="width:${width}%"></i></div>
        </div>
        <div><strong>ROI ${item.calc.roi.toFixed(2)}</strong><br><span>CTR ${fmtPercent(item.calc.ctr)}</span></div>
      </div>`;
    })
    .join("");
}

function renderAdvice() {
  const box = document.querySelector("#dailyAdvice");
  if (!state.creatives.length) return renderEmpty(box);
  const best = getBestCreative();
  const weak = getWeakCreative();
  box.innerHTML = [
    ["胜出方向", `版本 ${best.creative.version} 的 ROI ${best.calc.roi.toFixed(2)}，建议围绕「${best.creative.angle}」继续扩展素材。`],
    ["风险提醒", `版本 ${weak.creative.version} 的 CTR ${fmtPercent(weak.calc.ctr)} 偏低，可能首句钩子不够直接。`],
    ["下一轮实验", "建议新增一个“强痛点 + 限时 CTA”版本，并和当前胜出版本做对照测试。"],
  ]
    .map(([title, text]) => `<div class="advice-item"><strong>${title}</strong><p>${text}</p></div>`)
    .join("");
}

function renderCreatives() {
  const box = document.querySelector("#creativeList");
  if (!state.creatives.length) return renderEmpty(box);
  box.innerHTML = state.creatives
    .map((creative) => {
      const metric = state.metrics.find((item) => item.creativeId === creative.id);
      const calc = calcMetric(metric || {});
      return `<article class="creative-card">
        <div>
          <div class="pill-row">
            <span class="pill">版本 ${creative.version}</span>
            <span class="pill">${creative.platform}</span>
            <span class="pill">${creative.angle}</span>
            <span class="pill">${creative.trait}</span>
          </div>
          <h3>${creative.headline}</h3>
          <div class="creative-copy">
            ${copyBlock("主文案", creative.body)}
            ${copyBlock("CTA", creative.cta)}
            ${copyBlock("短视频脚本", creative.videoScript)}
            ${copyBlock("落地页首屏", creative.landingHero)}
          </div>
        </div>
        <div class="mini-metrics">
          ${miniMetric("CTR", fmtPercent(calc.ctr))}
          ${miniMetric("CPC", fmtMoney(calc.cpc))}
          ${miniMetric("CVR", fmtPercent(calc.cvr))}
          ${miniMetric("ROI", calc.roi.toFixed(2))}
        </div>
      </article>`;
    })
    .join("");
}

function copyBlock(label, value) {
  return `<div class="copy-block"><span>${label}</span>${String(value).replace(/\n/g, "<br>")}</div>`;
}

function miniMetric(label, value) {
  return `<div class="mini-metric"><span>${label}</span><strong>${value}</strong></div>`;
}

function renderExperiments() {
  const box = document.querySelector("#experimentList");
  if (!state.experiments.length) return renderEmpty(box);
  box.innerHTML = state.experiments
    .map((exp) => {
      const winner = state.creatives.find((item) => item.id === exp.winnerCreativeId);
      return `<article class="experiment-card">
        <span class="status ${exp.status === "running" ? "running" : ""}">${exp.status === "running" ? "进行中" : "已完成"}</span>
        <h3>${exp.name}</h3>
        <p><strong>实验假设：</strong>${exp.hypothesis}</p>
        <p><strong>目标指标：</strong>${exp.goalMetric}</p>
        <p><strong>胜出版本：</strong>${winner ? `版本 ${winner.version} - ${winner.angle}` : "待观察"}</p>
      </article>`;
    })
    .join("");
}

function renderReports() {
  const box = document.querySelector("#reportList");
  if (!state.reports.length) return renderEmpty(box);
  box.innerHTML = state.reports
    .map((report) => `<article class="report-card">
      <h3>${report.title}</h3>
      <p><strong>总结：</strong>${report.summary}</p>
      <p><strong>胜出原因：</strong>${report.winningReason}</p>
      <p><strong>短板指标：</strong>${report.weakMetric}</p>
      <p><strong>下一轮测试：</strong>${report.nextTests}</p>
    </article>`)
    .join("");
}

function renderEmpty(target) {
  target.innerHTML = document.querySelector("#emptyStateTemplate").innerHTML;
}

function getBestCreative() {
  return state.creatives
    .map((creative) => {
      const metric = state.metrics.find((item) => item.creativeId === creative.id);
      return { creative, metric, calc: calcMetric(metric || {}) };
    })
    .sort((a, b) => b.calc.roi - a.calc.roi)[0];
}

function getWeakCreative() {
  return state.creatives
    .map((creative) => {
      const metric = state.metrics.find((item) => item.creativeId === creative.id);
      return { creative, metric, calc: calcMetric(metric || {}) };
    })
    .sort((a, b) => a.calc.ctr - b.calc.ctr)[0];
}

function createExperiment() {
  if (state.creatives.length < 2) {
    alert("请先生成至少 2 个创意版本。");
    return;
  }
  const best = getBestCreative();
  const variants = state.creatives.filter((item) => item.id !== best.creative.id).slice(0, 3);
  state.experiments.unshift({
    id: uid("exp"),
    name: `测试「${best.creative.angle}」是否能提升转化`,
    hypothesis: `针对同一目标人群，${best.creative.angle}角度比其他表达更能提升 CTR 和 ROI。`,
    goalMetric: "ROI / CTR",
    controlCreativeId: variants[0].id,
    variantCreativeIds: [best.creative.id, ...variants.map((item) => item.id)],
    status: "completed",
    winnerCreativeId: best.creative.id,
    createdAt: new Date().toISOString(),
  });
  saveState();
  render();
}

function createReport() {
  if (!state.creatives.length) {
    alert("请先生成创意和数据。");
    return;
  }
  const best = getBestCreative();
  const weak = getWeakCreative();
  state.reports.unshift({
    id: uid("report"),
    title: `${new Date().toISOString().slice(0, 10)} 投放复盘`,
    summary: `当前最佳版本是 ${best.creative.version}，ROI 达到 ${best.calc.roi.toFixed(2)}，CTR 为 ${fmtPercent(best.calc.ctr)}。整体表现说明「${best.creative.angle}」更适合当前人群。`,
    winningReason: `标题更直接，卖点和${best.creative.platform}平台的用户浏览场景更匹配，CTA 指向明确。`,
    weakMetric: `版本 ${weak.creative.version} 的 CTR 为 ${fmtPercent(weak.calc.ctr)}，建议优化首句钩子或更换素材角度。`,
    nextTests: "新增 3 个版本：强痛点版本、结果证明版本、限时福利版本；继续以 CTR 和 CPA 作为主指标。",
    createdAt: new Date().toISOString(),
  });
  saveState();
  render();
}

function seedData() {
  state.briefs = [];
  state.creatives = [];
  state.metrics = [];
  state.experiments = [];
  state.reports = [];
  const brief = {
    id: uid("brief"),
    productName: "AI 简历面试增长助手",
    industry: "AI 求职工具",
    audience: "想转行 AI 产品经理的非科班求职者",
    sellingPoints: "自动分析岗位 JD，优化项目经历，生成面试问答和简历亮点",
    platform: "小红书",
    goal: "注册试用",
    tone: "痛点共鸣",
    createdAt: new Date().toISOString(),
  };
  state.briefs.push(brief);
  const creatives = generateCreatives(brief);
  state.creatives.push(...creatives);
  state.metrics.push(...creatives.map(createMetricsForCreative));
  createExperiment();
  createReport();
  saveState();
  render();
}

document.querySelectorAll(".nav-item").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".nav-item").forEach((item) => item.classList.remove("active"));
    document.querySelectorAll(".view").forEach((view) => view.classList.remove("active"));
    button.classList.add("active");
    document.querySelector(`#${button.dataset.view}`).classList.add("active");
  });
});

document.querySelector("#briefForm").addEventListener("submit", (event) => {
  event.preventDefault();
  const brief = createBriefFromForm(event.currentTarget);
  state.briefs.unshift(brief);
  const creatives = generateCreatives(brief);
  state.creatives.unshift(...creatives);
  state.metrics.unshift(...creatives.map(createMetricsForCreative));
  saveState();
  render();
  document.querySelector('[data-view="creatives"]').click();
});

document.querySelector("#generateFromLatestBtn").addEventListener("click", () => {
  const latest = state.briefs[0];
  if (!latest) {
    alert("请先创建一个 Brief。");
    return;
  }
  const creatives = generateCreatives(latest);
  state.creatives.unshift(...creatives);
  state.metrics.unshift(...creatives.map(createMetricsForCreative));
  saveState();
  render();
});

document.querySelector("#createExperimentBtn").addEventListener("click", createExperiment);
document.querySelector("#createReportBtn").addEventListener("click", createReport);
document.querySelector("#seedBtn").addEventListener("click", seedData);
document.querySelector("#resetBtn").addEventListener("click", () => {
  if (!confirm("确认清空所有本地数据？")) return;
  state.briefs = [];
  state.creatives = [];
  state.experiments = [];
  state.reports = [];
  state.metrics = [];
  saveState();
  render();
});

render();
