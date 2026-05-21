"use client";

import { useEffect } from "react";
import Link from "next/link";

/* ── Design tokens (mirrors reference palette) ── */
const C = {
  ink:       "#1a1814",
  inkLight:  "#4a4640",
  inkMist:   "#8a857e",
  paper:     "#f7f4ee",
  paperWarm: "#ede9e0",
  paperDeep: "#e0dbd0",
  gold:      "#b8860b",
  goldLight: "#d4a843",
  green:     "#3a6b4a",
  red:       "#8b2a2a",
  dotLine:   "rgba(26,24,20,0.12)",
} as const;

const serif = "'Noto Serif SC', 'STSong', serif";
const sans  = "'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif";

/* ── Scroll-reveal hook ── */
function useFadeIn() {
  useEffect(() => {
    const obs = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            e.target.classList.add("hp-vis");
            obs.unobserve(e.target);
          }
        });
      },
      { threshold: 0.12 },
    );
    document.querySelectorAll(".hp-fade").forEach((el) => obs.observe(el));
    return () => obs.disconnect();
  }, []);
}

/* ── Section label ── */
function SectionLabel({ children, light }: { children: React.ReactNode; light?: boolean }) {
  return (
    <div style={{
      display: "flex", alignItems: "center", gap: "0.75rem",
      fontSize: "0.72rem", fontWeight: 500, letterSpacing: "0.18em",
      textTransform: "uppercase", color: light ? C.goldLight : C.gold,
      marginBottom: "1rem",
    }}>
      {children}
      <span style={{ flex: 1, maxWidth: 60, height: "0.5px", background: light ? C.goldLight : C.gold }} />
    </div>
  );
}

/* ── Hero Section ── */
function HeroSection() {
  const stats = [
    { num: "4章", label: "系统化演进路径" },
    { num: "9要素", label: "商业画布全覆盖" },
    { num: "15+", label: "核心职能AI场景" },
    { num: "点线面", label: "三阶价值跃迁" },
  ];
  return (
    <section style={{ minHeight: "100vh", display: "flex", alignItems: "center", position: "relative", padding: "8rem 3rem 5rem", overflow: "hidden" }}>
      {/* grid background */}
      <div style={{
        position: "absolute", inset: 0,
        backgroundImage: `linear-gradient(${C.dotLine} 1px, transparent 1px), linear-gradient(90deg, ${C.dotLine} 1px, transparent 1px)`,
        backgroundSize: "60px 60px",
        maskImage: "radial-gradient(ellipse 80% 80% at 50% 50%, black 30%, transparent 100%)",
        WebkitMaskImage: "radial-gradient(ellipse 80% 80% at 50% 50%, black 30%, transparent 100%)",
      }} />
      {/* floating seal */}
      <svg className="hp-seal-anim" viewBox="0 0 160 160" fill="none"
        style={{ position: "absolute", top: "12rem", right: "8rem", width: 160, height: 160, opacity: 0.06 }}>
        <circle cx="80" cy="80" r="76" stroke={C.ink} strokeWidth="2"/>
        <circle cx="80" cy="80" r="64" stroke={C.ink} strokeWidth="0.5"/>
        <text x="80" y="72" textAnchor="middle" fontFamily={serif} fontSize="22" fontWeight="700" fill={C.ink}>美太</text>
        <text x="80" y="96" textAnchor="middle" fontFamily={serif} fontSize="11" fill={C.ink} letterSpacing="4">AI商业创新</text>
        <text x="80" y="114" textAnchor="middle" fontFamily={serif} fontSize="9" fill={C.ink} letterSpacing="2">智能体</text>
      </svg>
      {/* content */}
      <div className="hp-hero-anim" style={{ position: "relative", maxWidth: 760 }}>
        <div style={{
          display: "inline-flex", alignItems: "center", gap: "0.5rem",
          fontSize: "0.75rem", fontWeight: 500, letterSpacing: "0.15em",
          color: C.gold, border: `0.5px solid ${C.gold}`, padding: "0.35rem 0.9rem",
          borderRadius: 2, marginBottom: "2rem", textTransform: "uppercase",
        }}>
          <span style={{ display: "inline-block", width: 16, height: 1, background: C.gold }} />
          AI 商业创新智能体
        </div>
        <h1 style={{ fontFamily: serif, fontSize: "clamp(2.4rem, 5vw, 3.8rem)", fontWeight: 700, lineHeight: 1.25, letterSpacing: "0.02em", color: C.ink, marginBottom: "1.5rem" }}>
          以道驭术<br />
          <span style={{ color: C.gold }}>点线面</span>三阶跃迁<br />
          重构商业新范式
        </h1>
        <p style={{ fontSize: "1.05rem", fontWeight: 300, color: C.inkLight, maxWidth: 560, lineHeight: 2, marginBottom: "3rem" }}>
          融合咨询级方法论与前沿AI技术，协助中高层管理者在 AI 时代完成从诊断到落地的系统性商业模式创新——从单点提效到生态壁垒，一步步构建不可复制的竞争优势。
        </p>
        <Link href="/assessment" style={{
          display: "inline-flex", alignItems: "center", gap: "0.75rem",
          background: C.ink, color: C.paper, fontFamily: sans,
          fontSize: "0.9rem", fontWeight: 500, letterSpacing: "0.05em",
          padding: "0.9rem 2rem", border: "none", cursor: "pointer",
          textDecoration: "none", borderRadius: 2,
          transition: "background 0.2s, transform 0.15s",
        }}
          onMouseEnter={(e) => { (e.currentTarget as HTMLAnchorElement).style.background = C.gold; }}
          onMouseLeave={(e) => { (e.currentTarget as HTMLAnchorElement).style.background = C.ink; }}
        >
          开始探索
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
            <path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </Link>
        <div className="hp-hero-anim-delay" style={{ display: "flex", gap: "3rem", marginTop: "4rem", paddingTop: "2.5rem", borderTop: `0.5px solid ${C.dotLine}`, flexWrap: "wrap" }}>
          {stats.map((s) => (
            <div key={s.label}>
              <div style={{ fontFamily: serif, fontSize: "1.8rem", fontWeight: 700, color: C.gold, lineHeight: 1 }}>{s.num}</div>
              <div style={{ fontSize: "0.78rem", color: C.inkMist, marginTop: "0.3rem", letterSpacing: "0.04em" }}>{s.label}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ── Philosophy Section ── */
function PhilosophySection() {
  return (
    <section style={{ background: C.ink, color: C.paper, padding: "7rem 3rem" }}>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "4rem", alignItems: "center", maxWidth: 1100, margin: "0 auto" }}>
        <div className="hp-fade">
          <SectionLabel light>道 · 底层认知</SectionLabel>
          <h2 style={{ fontFamily: serif, fontSize: "clamp(1.8rem, 3.5vw, 2.6rem)", fontWeight: 700, lineHeight: 1.3, color: C.paper, marginBottom: "1rem" }}>
            AI 时代<br />商业底层逻辑的范式转移
          </h2>
          <p style={{ fontSize: "0.95rem", color: "rgba(247,244,238,0.65)", maxWidth: 540, lineHeight: 2 }}>
            AI 不仅是效率工具，更是重构商业底层逻辑的范式力量。理解 AI 对商业的三大底层冲击，是一切创新行动的认知起点。
          </p>
          <blockquote style={{ fontFamily: serif, fontSize: "1.6rem", fontWeight: 600, lineHeight: 1.7, color: C.paper, borderLeft: `2px solid ${C.gold}`, paddingLeft: "1.5rem", marginTop: "2.5rem" }}>
            知其<span style={{ color: C.goldLight }}>道</span>，方能<br />善用其<span style={{ color: C.goldLight }}>术</span>
          </blockquote>
        </div>
        <div className="hp-fade">
          <svg viewBox="0 0 320 320" width="100%" style={{ maxWidth: 340, display: "block", margin: "0 auto" }}>
            <circle cx="160" cy="160" r="148" stroke="rgba(247,244,238,0.12)" strokeWidth="1" fill="none"/>
            <circle cx="160" cy="160" r="118" stroke="rgba(247,244,238,0.08)" strokeWidth="0.5" fill="none"/>
            <circle cx="160" cy="160" r="52" fill="rgba(184,134,11,0.18)" stroke={C.gold} strokeWidth="1"/>
            <text x="160" y="154" textAnchor="middle" fontFamily={serif} fontSize="18" fontWeight="700" fill={C.paper}>认知</text>
            <text x="160" y="174" textAnchor="middle" fontFamily={serif} fontSize="11" fill="rgba(247,244,238,0.5)">底层 · 道</text>
            <circle cx="160" cy="42" r="38" fill="rgba(58,107,74,0.2)" stroke="#5a9b6a" strokeWidth="0.8"/>
            <text x="160" y="38" textAnchor="middle" fontFamily={serif} fontSize="12" fontWeight="600" fill={C.paper}>规模化</text>
            <text x="160" y="54" textAnchor="middle" fontFamily={serif} fontSize="11" fill="rgba(247,244,238,0.5)">个性服务</text>
            <circle cx="60" cy="240" r="38" fill="rgba(212,168,67,0.18)" stroke={C.goldLight} strokeWidth="0.8"/>
            <text x="60" y="236" textAnchor="middle" fontFamily={serif} fontSize="12" fontWeight="600" fill={C.paper}>经验</text>
            <text x="60" y="252" textAnchor="middle" fontFamily={serif} fontSize="11" fill="rgba(247,244,238,0.5)">算法化</text>
            <circle cx="260" cy="240" r="38" fill="rgba(139,42,42,0.2)" stroke="#b05050" strokeWidth="0.8"/>
            <text x="260" y="236" textAnchor="middle" fontFamily={serif} fontSize="12" fontWeight="600" fill={C.paper}>生态</text>
            <text x="260" y="252" textAnchor="middle" fontFamily={serif} fontSize="11" fill="rgba(247,244,238,0.5)">重构壁垒</text>
            <line x1="160" y1="112" x2="160" y2="80" stroke="rgba(247,244,238,0.2)" strokeWidth="0.5" strokeDasharray="3,3"/>
            <line x1="115" y1="192" x2="90" y2="210" stroke="rgba(247,244,238,0.2)" strokeWidth="0.5" strokeDasharray="3,3"/>
            <line x1="205" y1="192" x2="228" y2="210" stroke="rgba(247,244,238,0.2)" strokeWidth="0.5" strokeDasharray="3,3"/>
          </svg>
        </div>
      </div>
    </section>
  );
}

/* ── Framework Section ── */
const fwCards = [
  {
    num: "01", tier: "点 · 短期", tierColor: C.green, tierBg: "rgba(58,107,74,0.12)",
    title: "五大核心职能\nAI 重塑提效",
    sub: "识别高价值职能场景，通过 AI 实现单一环节降本增效，快速获得切实成果。",
    items: ["销售提效：AI 重塑客户关系，提升收入转化", "渠道提效：打通数据壁垒，实现全域协同", "产品开发：降低试错成本，加速研发迭代", "生产管理：优化运营效率，重构成本结构", "客户服务：升级服务体验，强化客户留存"],
  },
  {
    num: "02", tier: "线 · 中期", tierColor: C.gold, tierBg: "rgba(184,134,11,0.12)",
    title: "系统串联\n构建差异化竞争力",
    sub: "将孤立的 AI「点」优势串联成系统性方案，重构价值主张，建立可持续差异化优势。",
    items: ["客户端：「一客一策」规模化个性化创造", "渠道端：「一渠一策」构建全域渠道体系", "交付端：「柔性供应链」保障个性化交付", "成本端：「系统成本最优」构筑竞争底座"],
  },
  {
    num: "03", tier: "面 · 长期", tierColor: C.red, tierBg: "rgba(139,42,42,0.12)",
    title: "生态重构\n开辟第二增长曲线",
    sub: "全画布重构，构建私域 + 生态 + OPC 模式下的商业终局，建立不可复制的生态壁垒。",
    items: ["生态数据体系：打造不可复制的数据核心", "裂变型商业体系：AI 驱动收入复利增长", "新增长路径：重构收入，开辟第三增长曲线"],
  },
];

function FrameworkSection() {
  return (
    <section id="framework" style={{ background: C.paperWarm, padding: "7rem 3rem" }}>
      <div style={{ maxWidth: 1100, margin: "0 auto" }}>
        <div className="hp-fade" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", marginBottom: "4rem", gap: "2rem", flexWrap: "wrap" }}>
          <div>
            <SectionLabel>术 · 三阶演进</SectionLabel>
            <h2 style={{ fontFamily: serif, fontSize: "clamp(1.8rem, 3.5vw, 2.6rem)", fontWeight: 700, lineHeight: 1.3, color: C.ink }}>
              点 · 线 · 面<br />结构化价值跃迁
            </h2>
          </div>
          <p style={{ fontSize: "0.95rem", color: C.inkLight, maxWidth: 360, lineHeight: 2 }}>
            从单一职能的AI提效出发，逐步串联成系统性竞争优势，最终构建生态壁垒与第二增长曲线——三个层次，三种时间维度，三段价值跃迁。
          </p>
        </div>
        <div className="hp-fade" style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", border: `0.5px solid ${C.paperDeep}`, borderRadius: 4, overflow: "hidden" }}>
          {fwCards.map((card, i) => (
            <div key={card.num} style={{ padding: "2.8rem 2rem", background: C.paper, borderRight: i < 2 ? `0.5px solid ${C.paperDeep}` : "none", position: "relative", cursor: "default" }}>
              <div style={{ fontFamily: serif, fontSize: "4rem", fontWeight: 700, color: C.paperDeep, lineHeight: 1, marginBottom: "1.5rem" }}>{card.num}</div>
              <span style={{ display: "inline-block", fontSize: "0.7rem", fontWeight: 500, letterSpacing: "0.12em", textTransform: "uppercase", padding: "0.25rem 0.7rem", borderRadius: 2, marginBottom: "1rem", background: card.tierBg, color: card.tierColor }}>{card.tier}</span>
              <h3 style={{ fontFamily: serif, fontSize: "1.3rem", fontWeight: 700, color: C.ink, marginBottom: "0.8rem", lineHeight: 1.4, whiteSpace: "pre-line" }}>{card.title}</h3>
              <p style={{ fontSize: "0.82rem", color: C.inkMist, lineHeight: 1.7, marginBottom: "1.5rem" }}>{card.sub}</p>
              <ul style={{ listStyle: "none", display: "flex", flexDirection: "column", gap: "0.5rem", padding: 0, margin: 0 }}>
                {card.items.map((item) => (
                  <li key={item} style={{ fontSize: "0.8rem", color: C.inkLight, display: "flex", alignItems: "flex-start", gap: "0.6rem", lineHeight: 1.5 }}>
                    <span style={{ color: C.inkMist, flexShrink: 0 }}>—</span>{item}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ── Steps Section ── */
const steps = [
  {
    num: "STEP 01", title: "数据采集与画像初始化",
    desc: "学员输入企业现状与痛点描述，AI 自动提取关键信息，建立企业基本画像，预填充商业画布要素，并进行行业定位与认知校准。",
    tags: ["语义解析", "画布预填充", "行业定位", "认知校准"],
  },
  {
    num: "STEP 02", title: "AI 提效场景识别——点",
    desc: "调用九要素问题库，引导筛选 2—3 个期望创新突破的要素，执行「结构化 × 复杂度」双维评分，生成优先级矩阵与提效场景方案。",
    tags: ["场景优先级", "双维评分", "AI成熟度报告"],
  },
  {
    num: "STEP 03", title: "差异化竞争力设计——线",
    desc: "将孤立 AI 优势系统串联，形成「柔性供应链」「智能运营」「一客一策」等系统性方案，重构价值主张，构建差异化竞争力路径。",
    tags: ["系统创新串联", "VP重构", "竞争力路径"],
  },
  {
    num: "STEP 04", title: "AI 商业创新落地规划",
    desc: "综合前三步诊断成果，构建行业商业终局模型，对比多维路径，匹配标杆案例，生成三阶段执行路线图，支持 PDF/Word 一键导出。",
    tags: ["商业终局", "三阶路线图", "标杆案例", "一键导出"],
  },
];

function StepsSection() {
  return (
    <section id="steps" style={{ background: C.paper, padding: "7rem 3rem" }}>
      <div style={{ maxWidth: 1100, margin: "0 auto" }}>
        <div className="hp-fade" style={{ marginBottom: "5rem", maxWidth: 600 }}>
          <SectionLabel>智能体 · 工作流程</SectionLabel>
          <h2 style={{ fontFamily: serif, fontSize: "clamp(1.8rem, 3.5vw, 2.6rem)", fontWeight: 700, lineHeight: 1.3, color: C.ink }}>
            四步走完整路径<br />从诊断到落地规划
          </h2>
        </div>
        <div className="hp-fade" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.5px", background: C.paperDeep, borderRadius: 4, overflow: "hidden" }}>
          {steps.map((step) => (
            <div key={step.num} style={{ background: C.paper, padding: "2.5rem 2rem", position: "relative", overflow: "hidden" }}>
              <div style={{ position: "absolute", top: 0, left: 0, width: 3, height: "100%", background: C.paperDeep }} />
              <div style={{ fontSize: "0.75rem", fontFamily: serif, fontWeight: 700, color: C.inkMist, letterSpacing: "0.1em", marginBottom: "1rem" }}>{step.num}</div>
              <h3 style={{ fontFamily: serif, fontSize: "1.1rem", fontWeight: 700, color: C.ink, marginBottom: "0.6rem", lineHeight: 1.4 }}>{step.title}</h3>
              <p style={{ fontSize: "0.83rem", color: C.inkLight, lineHeight: 1.8, marginBottom: "1.2rem" }}>{step.desc}</p>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem" }}>
                {step.tags.map((tag) => (
                  <span key={tag} style={{ fontSize: "0.72rem", color: C.inkMist, border: `0.5px solid ${C.paperDeep}`, padding: "0.2rem 0.6rem", borderRadius: 2, letterSpacing: "0.04em" }}>{tag}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ── Features Section ── */
const featCards = [
  { icon: "★", color: C.green, bg: "rgba(58,107,74,0.1)", name: "企业画像智能生成", text: "语义解析输入内容，自动提取关键词并映射至商业画布九格，将非结构化描述转化为专业画布语言。" },
  { icon: "⊞", color: C.gold,  bg: "rgba(184,134,11,0.1)", name: "场景优先级矩阵",   text: "结构化 × 复杂度双维评分，从 15 个核心职能中精准识别最高价值的 AI 提效突破口。" },
  { icon: "↑", color: C.red,   bg: "rgba(139,42,42,0.1)",  name: "差异化策略设计",   text: "将孤立 AI「点」串联为系统性竞争方案，重构价值主张，生成个性化 VP 交付策略报告。" },
  { icon: "◎", color: C.green, bg: "rgba(58,107,74,0.1)",  name: "商业终局构建",     text: "引导学员构建所在行业的商业终局模型，聚焦「私域 + 生态 + OPC」模式，匹配标杆案例。" },
  { icon: "≡", color: C.gold,  bg: "rgba(184,134,11,0.1)", name: "一键导出落地规划", text: "「生成→自检」双步流程确保可执行性，输出含画布诊断、商业终局模型、三阶段路线图的完整报告。" },
  { icon: "♥", color: C.red,   bg: "rgba(139,42,42,0.1)",  name: "引导式深度问诊",   text: "预设九大要素精准引导问题，帮助学员发掘企业数据金矿、劳动深坑、生态协同盲区，触发真实业务洞察。" },
];

function FeaturesSection() {
  return (
    <section id="features" style={{ background: C.paperWarm, padding: "7rem 3rem" }}>
      <div style={{ maxWidth: 1100, margin: "0 auto" }}>
        <div className="hp-fade" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "4rem", alignItems: "center", marginBottom: "5rem" }}>
          <div>
            <SectionLabel>核心功能</SectionLabel>
            <h2 style={{ fontFamily: serif, fontSize: "clamp(1.8rem, 3.5vw, 2.6rem)", fontWeight: 700, lineHeight: 1.3, color: C.ink, marginBottom: "1rem" }}>
              咨询侧方法论<br />× AI 技术赋能
            </h2>
            <p style={{ fontSize: "0.95rem", color: C.inkLight, maxWidth: 540, lineHeight: 2 }}>
              整合美太道术方法论与前沿 AI 能力，覆盖从企业诊断到战略落地的全链条，为每位学员生成专属的商业创新规划。
            </p>
          </div>
          <div style={{ background: C.paper, borderRadius: 4, padding: "2rem", border: `0.5px solid ${C.paperDeep}` }}>
            <div style={{ fontFamily: serif, fontSize: "0.85rem", fontWeight: 700, color: C.ink, marginBottom: "1.5rem", lineHeight: 1.6 }}>可提供知识库覆盖</div>
            {[
              { dot: C.green, label: "通用知识库", text: "课件文档、商业画布工具、商业创新十型、美太道术方法论" },
              { dot: C.gold,  label: "定制化知识库", text: "学员所属行业报告、画布要素引导问题库、AI 商业布局落地案例" },
              { dot: C.red,   label: "行业终局库", text: "各行业商业终局模型、标杆案例、美太 20+ 变革落地框架" },
            ].map((kb) => (
              <div key={kb.label} style={{ display: "flex", alignItems: "flex-start", gap: "0.75rem", fontSize: "0.8rem", color: C.inkLight, marginBottom: "0.8rem" }}>
                <span style={{ color: kb.dot, flexShrink: 0, marginTop: 2 }}>◆</span>
                <span><strong style={{ color: C.ink }}>{kb.label}</strong>：{kb.text}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="hp-fade" style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "1px", background: C.paperDeep, borderRadius: 4, overflow: "hidden" }}>
          {featCards.map((fc) => (
            <div key={fc.name} style={{ background: C.paperWarm, padding: "2rem 1.6rem" }}>
              <div style={{ width: 40, height: 40, borderRadius: 4, display: "flex", alignItems: "center", justifyContent: "center", marginBottom: "1.2rem", background: fc.bg, fontSize: "1.2rem", color: fc.color }}>{fc.icon}</div>
              <div style={{ fontSize: "0.92rem", fontWeight: 500, color: C.ink, marginBottom: "0.5rem" }}>{fc.name}</div>
              <p style={{ fontSize: "0.8rem", color: C.inkMist, lineHeight: 1.75 }}>{fc.text}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ── Canvas Section ── */
const canvasCells = [
  { key: "kp",  label: "KP", name: "重要合作", hint: "识别上下游信息不对称，构建 AI 驱动的生态协同网络", ai: "AI 生态重构", isVP: false, style: { gridColumn: "1/3", gridRow: "1/3" } },
  { key: "ka",  label: "KA", name: "关键业务", hint: "识别「劳动深坑」，通过 AI 自动化释放人力效能", ai: "AI 流程替代", isVP: false, style: { gridColumn: "3/5", gridRow: "1/2" } },
  { key: "vp",  label: "VP", name: "价值主张", hint: "从「黑盒经验」到算法化交付，重构核心价值创造逻辑", ai: "AI VP 重构", isVP: true,  style: { gridColumn: "5/6", gridRow: "1/3" } },
  { key: "cr",  label: "CR", name: "客户关系", hint: "从定期回访到实时情绪数字感应器，构建反馈闭环", ai: "一客一策", isVP: false, style: { gridColumn: "6/8", gridRow: "1/2" } },
  { key: "cs",  label: "CS", name: "客户细分", hint: "AI 驱动「千人千面」规模化个性服务，实现精准画像", ai: "规模个性化", isVP: false, style: { gridColumn: "8/10", gridRow: "1/3" } },
  { key: "kr",  label: "KR", name: "核心资源", hint: "将企业「数据金矿」转化为不可复制的 AI 训练资产", ai: "数据资产化", isVP: false, style: { gridColumn: "3/5", gridRow: "2/3" } },
  { key: "ch",  label: "CH", name: "渠道通路", hint: "消除信息断流，打造全域可追踪的智能渠道体系", ai: "全域渠道", isVP: false, style: { gridColumn: "6/8", gridRow: "2/3" } },
  { key: "cs2", label: "C$", name: "成本结构", hint: "精准预测替代经验判断，消除预测不准导致的结构性浪费，构建系统成本最优", ai: "成本最优化", isVP: false, style: { gridColumn: "1/5", gridRow: "3/4" } },
  { key: "rs",  label: "R$", name: "收入来源", hint: "突破获客成本、产能瓶颈限制，挖掘现有客群增值服务点，开辟第二收入曲线", ai: "增长曲线", isVP: false, style: { gridColumn: "5/10", gridRow: "3/4" } },
];

function CanvasSection() {
  return (
    <section id="canvas" style={{ background: C.paper, padding: "7rem 3rem" }}>
      <div style={{ maxWidth: 1100, margin: "0 auto" }}>
        <div className="hp-fade" style={{ marginBottom: "3.5rem" }}>
          <SectionLabel>商业画布 · AI 重塑</SectionLabel>
          <h2 style={{ fontFamily: serif, fontSize: "clamp(1.8rem, 3.5vw, 2.6rem)", fontWeight: 700, lineHeight: 1.3, color: C.ink, marginBottom: "0.5rem" }}>
            九要素全覆盖<br />AI 驱动画布重构
          </h2>
          <p style={{ fontSize: "0.95rem", color: C.inkLight, maxWidth: 540, lineHeight: 2 }}>
            智能体深度耦合商业画布方法论，对每一个要素进行 AI 化诊断与创新延展，从「现状描述」升维至「战略重塑」。
          </p>
        </div>
        <div className="hp-fade" style={{ display: "grid", gridTemplateColumns: "repeat(9, 1fr)", gridTemplateRows: "auto auto auto", gap: "1px", background: C.paperDeep, borderRadius: 4, overflow: "hidden", fontSize: "0.75rem" }}>
          {canvasCells.map((cell) => (
            <div key={cell.key} style={{ background: cell.isVP ? C.ink : C.paperWarm, padding: "1.2rem 1rem", minHeight: 90, ...cell.style }}>
              <div style={{ fontSize: "0.65rem", fontWeight: 700, letterSpacing: "0.1em", textTransform: "uppercase", color: cell.isVP ? "rgba(247,244,238,0.5)" : C.inkMist, marginBottom: "0.5rem" }}>{cell.label}</div>
              <div style={{ fontFamily: serif, fontSize: "0.8rem", fontWeight: 700, color: cell.isVP ? C.paper : C.ink, marginBottom: "0.4rem" }}>{cell.name}</div>
              <div style={{ fontSize: "0.72rem", color: cell.isVP ? "rgba(247,244,238,0.55)" : C.inkMist, lineHeight: 1.6 }}>{cell.hint}</div>
              <div style={{ display: "inline-flex", alignItems: "center", gap: "0.3rem", fontSize: "0.65rem", fontWeight: 500, color: cell.isVP ? C.goldLight : C.gold, border: `0.5px solid ${cell.isVP ? C.goldLight : C.gold}`, padding: "0.15rem 0.5rem", borderRadius: 2, marginTop: "0.6rem", letterSpacing: "0.05em" }}>{cell.ai}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ── CTA Section ── */
function CTASection() {
  return (
    <section style={{ background: C.ink, textAlign: "center", padding: "8rem 3rem" }}>
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", gap: "0.75rem", fontSize: "0.72rem", fontWeight: 500, letterSpacing: "0.18em", textTransform: "uppercase", color: C.goldLight, marginBottom: "1.5rem" }}>
        开启您的 AI 商业创新之旅
      </div>
      <h2 style={{ fontFamily: serif, fontSize: "clamp(2rem, 4vw, 3.2rem)", fontWeight: 700, color: C.paper, marginBottom: "1.2rem", lineHeight: 1.3 }}>
        现在就开始<br />构建<span style={{ color: C.goldLight }}>不可复制</span>的竞争优势
      </h2>
      <p style={{ fontSize: "0.95rem", color: "rgba(247,244,238,0.55)", maxWidth: 480, margin: "0 auto 3rem", lineHeight: 2 }}>
        输入您企业的真实现状，让智能体为您生成专属的商业画布诊断与 AI 创新落地规划。
      </p>
      <Link href="/assessment" style={{
        display: "inline-flex", alignItems: "center", gap: "0.75rem",
        background: C.gold, color: C.ink, fontFamily: sans,
        fontSize: "0.9rem", fontWeight: 700, letterSpacing: "0.06em",
        padding: "1rem 2.5rem", border: "none", cursor: "pointer",
        textDecoration: "none", borderRadius: 2, transition: "background 0.2s, transform 0.15s",
      }}>
        立即启动智能体
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
          <path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </Link>
    </section>
  );
}

/* ── Page Footer ── */
function PageFooter() {
  return (
    <footer style={{ background: "#111", padding: "2.5rem 3rem", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "1rem" }}>
      <div style={{ fontFamily: serif, fontSize: "1rem", fontWeight: 700, color: "rgba(247,244,238,0.4)", letterSpacing: "0.08em" }}>
        美太<span style={{ color: "rgba(212,168,67,0.6)" }}>AI</span> · 商业创新智能体
      </div>
      <div style={{ fontSize: "0.75rem", color: "rgba(247,244,238,0.25)", letterSpacing: "0.04em" }}>
        以道驭术 · 点线面三阶跃迁 · 重构商业新范式
      </div>
    </footer>
  );
}

/* ── Page ── */
export default function Home() {
  useFadeIn();
  return (
    <div style={{ background: C.paper, color: C.ink, fontFamily: sans, fontWeight: 300, lineHeight: 1.8, overflowX: "hidden" }}>
      <HeroSection />
      <PhilosophySection />
      <FrameworkSection />
      <StepsSection />
      <FeaturesSection />
      <CanvasSection />
      <CTASection />
      <PageFooter />
    </div>
  );
}
