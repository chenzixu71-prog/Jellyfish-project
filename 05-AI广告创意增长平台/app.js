const STORAGE_KEY = "adgrowth-ai-state-v2";

const platformTraits = {
  小红书: ["真实经历", "痛点共鸣", "收藏转化"],
  抖音: ["前三秒钩子", "强节奏", "评论区引导"],
  朋友圈广告: ["可信背书", "生活场景", "轻决策"],
  "Meta Ads": ["利益点清晰", "短句", "强 CTA"],
  "Google Search": ["搜索意图", "关键词匹配", "直接转化"],
};

const state = loadState();

function loadState() {
  const saved = localStorage.getItem(STORAGE_KEY);
  if (saved) return JSON.parse(saved);
  const seeded = createSampleState();
  localStorage.setItem(STORAGE_KEY, JSON.stringify(seeded));
  return seeded;
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

function calcMetric(metric = {}) {
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

function generateCreatives(brief) {
  const angles = [
    { name: "痛点直击", hook: "你不是能力不够，是项目表达没讲清楚", color: "blue", asset: "./assets/creative-cut-a.svg" },
    { name: "结果证明", hook: "把普通经历包装成可面试的 AI 项目", color: "green", asset: "./assets/creative-cut-b.svg" },
    { name: "低门槛试用", hook: "不会写代码，也能先做出能讲的作品集", color: "amber", asset: "./assets/creative-cut-c.svg" },
    { name: "专业可信", hook: "按产品经理面试逻辑重构你的简历", color: "violet", asset: "./assets/creative-cut-d.svg" },
  ];
  const traits = platformTraits[brief.platform] || ["清晰表达", "强 CTA"];

  return angles.map((angle, index) => {
    const version = String.fromCharCode(65 + index);
    const trait = traits[index % traits.length];
    return {
      id: uid("creative"),
      briefId: brief.id,
      version,
      platform: brief.platform,
      angle: angle.name,
      hook: angle.hook,
      tone: brief.tone,
      trait,
      color: angle.color,
      asset: angle.asset,
      headline: makeHeadline(brief, angle.name),
      body: makeBody(brief, trait),
      cta: makeCta(brief.goal),
      videoScript: makeVideoScript(brief, angle.hook),
      landingHero: makeLandingHero(brief),
      status: index === 0 ? "主推" : "测试",
      createdAt: new Date().toISOString(),
    };
  });
}

function makeHeadline(brief, angle) {
  const map = {
    痛点直击: `${brief.audience}，别再只写“负责需求分析”`,
    结果证明: `${brief.productName}：让你的项目经历更像 AI 产品作品`,
    低门槛试用: `不会写代码，也能先做出可展示的 AI 项目`,
    专业可信: `按真实产品经理面试逻辑，重构你的简历和作品集`,
  };
  return map[angle];
}

function makeBody(brief, trait) {
  return `围绕“${brief.sellingPoints}”，针对“${brief.audience}”生成 ${trait} 风格素材，帮助你在 ${brief.platform} 更快测试卖点并提升“${brief.goal}”效率。`;
}

function makeCta(goal) {
  const map = {
    注册试用: "领取 7 天体验",
    私域加微: "领取转行方案",
    "预约 Demo": "预约产品演示",
    购买订阅: "查看订阅方案",
  };
  return map[goal] || "立即开始";
}

function makeVideoScript(brief, hook) {
  return `前三秒：${hook}。\n中段：展示 ${brief.productName} 如何拆解岗位 JD、优化项目亮点、生成面试问答。\n结尾：用“${makeCta(brief.goal)}”收口，引导用户进入落地页。`;
}

function makeLandingHero(brief) {
  return `${brief.productName}：帮 ${brief.audience} 把简历、项目和面试表达整理成一套可展示的 AI 求职方案。`;
}

function createMetricsForCreative(creative, index) {
  const base = 12000 + index * 1800;
  const ctr = [0.039, 0.047, 0.031, 0.036][index % 4];
  const cvr = [0.085, 0.092, 0.071, 0.078][index % 4];
  const clicks = Math.round(base * ctr);
  const spend = Number((clicks * [3.2, 3.6, 2.9, 3.4][index % 4]).toFixed(2));
  const conversions = Math.max(1, Math.round(clicks * cvr));
  const revenue = Number((conversions * [168, 198, 118, 152][index % 4]).toFixed(2));
  return {
    id: uid("metric"),
    creativeId: creative.id,
    impressions: base,
    clicks,
    spend,
    conversions,
    revenue,
    date: new Date().toISOString().slice(0, 10),
  };
}

function createSampleState() {
  const brief = {
    id: uid("brief"),
    productName: "AI 简历面试增长助手",
    industry: "AI 求职工具 / 在线教育",
    audience: "想转行 AI 产品经理的非科班求职者",
    sellingPoints: "自动分析岗位 JD，优化简历项目经历，生成面试问答和作品集包装建议",
    platform: "小红书",
    goal: "注册试用",
    tone: "痛点共鸣",
    createdAt: new Date().toISOString(),
  };
  const creatives = generateCreatives(brief);
  const metrics = creatives.map(createMetricsForCreative);
  const best = creatives[1];
  return {
    briefs: [brief],
    creatives,
    metrics,
    experiments: [
      {
        id: uid("exp"),
        name: "测试“结果证明”是否比“痛点直击”更能提升注册",
        hypothesis: "目标用户已经知道自己缺项目，因此展示结果和作品集收益，比单纯强调焦虑更能提升转化。",
        goalMetric: "ROI / 注册 CPA",
        status: "completed",
        controlCreativeId: creatives[0].id,
        variantCreativeIds: [creatives[0].id, creatives[1].id],
        winnerCreativeId: best.id,
        conclusion: "B 版 ROI 最高，适合继续放量；A 版 CTR 不低，但注册 CPA 略高。",
        createdAt: new Date().toISOString(),
      },
    ],
    reports: [
      {
        id: uid("report"),
        title: "小红书首轮创意测试复盘",
        summary: "B 版“结果证明”在 ROI、CVR 上表现最好，说明用户更关心自己最终能拿到什么作品和面试表达。",
        winningReason: "标题直接承诺“把普通经历包装成 AI 项目”，和目标人群的求职焦虑、作品集需求高度匹配。",
        weakMetric: "C 版 CTR 偏低，说明“不会写代码”虽然降低门槛，但首屏钩子不够强。",
        nextTests: "下一轮新增 3 个方向：真实案例截图、面试官视角、7 天完成作品集计划，并继续以 CPA 和 ROI 作为主指标。",
        createdAt: new Date().toISOString(),
      },
    ],
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
    ["总曝光", metrics.impressions.toLocaleString(), "Impressions", "曝光池规模"],
    ["CTR", fmtPercent(metrics.ctr), "Clicks / Impressions", "素材吸引力"],
    ["CPA", fmtMoney(metrics.cpa), "Spend / Conversions", "获客成本"],
    ["ROI", metrics.roi.toFixed(2), "Revenue / Spend", "投放回收"],
  ];
  document.querySelector("#metricsGrid").innerHTML = cards
    .map(
      ([label, value, hint, note]) => `<article class="metric-card">
        <span>${label}</span>
        <strong>${value}</strong>
        <small>${hint}</small>
        <em>${note}</em>
      </article>`,
    )
    .join("");
}

function getCreativeMetricRows() {
  return state.creatives
    .map((creative) => {
      const metric = state.metrics.find((item) => item.creativeId === creative.id);
      return { creative, metric, calc: calcMetric(metric) };
    })
    .filter((item) => item.metric)
    .sort((a, b) => b.calc.roi - a.calc.roi);
}

function renderLeaderboard() {
  const box = document.querySelector("#leaderboard");
  const ranked = getCreativeMetricRows();
  if (!ranked.length) return renderEmpty(box);

  box.innerHTML = ranked
    .map((item, index) => {
      const width = Math.min(100, item.calc.roi * 22);
      return `<article class="rank-row">
        <div class="rank">${index + 1}</div>
        <div>
          <strong>版本 ${item.creative.version}｜${item.creative.angle}</strong>
          <p>${item.creative.headline}</p>
          <div class="bar"><i style="width:${width}%"></i></div>
        </div>
        <div class="rank-metric">
          <strong>ROI ${item.calc.roi.toFixed(2)}</strong>
          <span>CTR ${fmtPercent(item.calc.ctr)}</span>
          <span>CPA ${fmtMoney(item.calc.cpa)}</span>
        </div>
      </article>`;
    })
    .join("");
}

function renderAdvice() {
  const box = document.querySelector("#dailyAdvice");
  const rows = getCreativeMetricRows();
  if (!rows.length) return renderEmpty(box);
  const best = rows[0];
  const weak = [...rows].sort((a, b) => a.calc.ctr - b.calc.ctr)[0];

  box.innerHTML = [
    ["放量方向", `版本 ${best.creative.version} 的 ROI 为 ${best.calc.roi.toFixed(2)}，建议围绕“${best.creative.angle}”继续扩展 3 条素材。`],
    ["风险提醒", `版本 ${weak.creative.version} 的 CTR 为 ${fmtPercent(weak.calc.ctr)}，首屏钩子需要更直接。`],
    ["下一步动作", "保留 B 版作为对照组，新增案例截图版、面试官视角版、限时体验版，继续看 CPA 和 ROI。"],
  ]
    .map(([title, text]) => `<article class="advice-item"><strong>${title}</strong><p>${text}</p></article>`)
    .join("");
}

function renderCreatives() {
  const box = document.querySelector("#creativeList");
  if (!state.creatives.length) return renderEmpty(box);

  box.innerHTML = state.creatives
    .map((creative) => {
      const metric = state.metrics.find((item) => item.creativeId === creative.id);
      const calc = calcMetric(metric);
      return `<article class="creative-card">
        <div class="ad-preview ${creative.color}">
          <img src="${creative.asset}" alt="版本 ${creative.version} 广告切图预览" />
        </div>
        <div class="creative-detail">
          <div class="pill-row">
            <span class="pill">版本 ${creative.version}</span>
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
        <div class="card-title">
          <span class="status ${exp.status === "running" ? "running" : ""}">${exp.status === "running" ? "进行中" : "已完成"}</span>
          <strong>${exp.name}</strong>
        </div>
        <p><span>实验假设</span>${exp.hypothesis}</p>
        <p><span>目标指标</span>${exp.goalMetric}</p>
        <p><span>胜出版本</span>${winner ? `版本 ${winner.version} - ${winner.angle}` : "待观察"}</p>
        <p><span>实验结论</span>${exp.conclusion || "等待更多数据回收"}</p>
      </article>`;
    })
    .join("");
}

function renderReports() {
  const box = document.querySelector("#reportList");
  if (!state.reports.length) return renderEmpty(box);
  box.innerHTML = state.reports
    .map(
      (report) => `<article class="report-card">
        <h3>${report.title}</h3>
        <p><strong>总结：</strong>${report.summary}</p>
        <p><strong>胜出原因：</strong>${report.winningReason}</p>
        <p><strong>短板指标：</strong>${report.weakMetric}</p>
        <p><strong>下一轮测试：</strong>${report.nextTests}</p>
      </article>`,
    )
    .join("");
}

function renderEmpty(target) {
  target.innerHTML = document.querySelector("#emptyStateTemplate").innerHTML;
}

function createExperiment() {
  if (state.creatives.length < 2) {
    alert("请先生成至少 2 条创意版本。");
    return;
  }
  const ranked = getCreativeMetricRows();
  const best = ranked[0];
  const control = ranked[1] || ranked[0];
  state.experiments.unshift({
    id: uid("exp"),
    name: `测试“${best.creative.angle}”是否能继续提升转化`,
    hypothesis: `针对同一目标人群，${best.creative.angle} 角度可能比其他表达更能提升 CTR 和 ROI。`,
    goalMetric: "ROI / CTR / CPA",
    controlCreativeId: control.creative.id,
    variantCreativeIds: [control.creative.id, best.creative.id],
    status: "completed",
    winnerCreativeId: best.creative.id,
    conclusion: `版本 ${best.creative.version} 当前 ROI 最高，建议作为下一轮放量方向。`,
    createdAt: new Date().toISOString(),
  });
  saveState();
  render();
}

function createReport() {
  const ranked = getCreativeMetricRows();
  if (!ranked.length) {
    alert("请先生成创意和数据。");
    return;
  }
  const best = ranked[0];
  const weak = [...ranked].sort((a, b) => a.calc.ctr - b.calc.ctr)[0];
  state.reports.unshift({
    id: uid("report"),
    title: `${new Date().toISOString().slice(0, 10)} 投放复盘`,
    summary: `当前最佳版本是 ${best.creative.version}，ROI 达到 ${best.calc.roi.toFixed(2)}，CTR 为 ${fmtPercent(best.calc.ctr)}。`,
    winningReason: `“${best.creative.angle}”更贴近目标用户当下的求职焦虑和结果期待，CTA 也更明确。`,
    weakMetric: `版本 ${weak.creative.version} 的 CTR 为 ${fmtPercent(weak.calc.ctr)}，建议优化首屏标题。`,
    nextTests: "新增案例截图、真实用户反馈、限时体验三个版本，继续以 CPA 和 ROI 作为主指标。",
    createdAt: new Date().toISOString(),
  });
  saveState();
  render();
}

function seedData() {
  const seeded = createSampleState();
  Object.assign(state, seeded);
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
  const creatives = generateCreatives(brief);
  const metrics = creatives.map(createMetricsForCreative);
  state.briefs.unshift(brief);
  state.creatives.unshift(...creatives);
  state.metrics.unshift(...metrics);
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
