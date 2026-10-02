"use client";

import { useMemo, useState } from "react";

type Case = {
  id: string;
  customer: string;
  initials: string;
  summary: string;
  outcome: string;
  priority: number;
  age: number;
  status: string;
  response: string;
  order: string;
  delivery: string;
};

const cases: Case[] = [
  { id: "TCK-0007", customer: "Ana Lopez", initials: "AL", summary: "Still waiting for replacement", outcome: "Failed", priority: 3, age: 14, status: "Open", response: "Unanswered", order: "ORD-1007", delivery: "DLV-1007" },
  { id: "TCK-0002", customer: "Mia Vergara", initials: "MV", summary: "Package never arrived", outcome: "Failed", priority: 3, age: 11, status: "Open", response: "Unanswered", order: "ORD-1002", delivery: "DLV-1002" },
  { id: "TCK-0001", customer: "Pat Dela Cruz", initials: "PC", summary: "Delivery arrived far beyond ETA", outcome: "Late", priority: 2, age: 12, status: "Open", response: "Unanswered", order: "ORD-1001", delivery: "DLV-1001" },
  { id: "TCK-0008", customer: "Ivan Sy", initials: "IS", summary: "Failed attempt no follow-up", outcome: "Failed", priority: 2, age: 5, status: "Open", response: "Unanswered", order: "ORD-1008", delivery: "DLV-1008" },
  { id: "TCK-0006", customer: "Lara Tan", initials: "LT", summary: "Delivery delayed", outcome: "Late", priority: 2, age: 6, status: "Pending", response: "Unanswered", order: "ORD-1006", delivery: "DLV-1006" },
  { id: "TCK-0009", customer: "Neil Abad", initials: "NA", summary: "Tracking stopped", outcome: "Unresolved", priority: 2, age: 4, status: "Open", response: "Unanswered", order: "ORD-1009", delivery: "DLV-1009" },
];

function StatusPill({ children, tone = "neutral" }: { children: React.ReactNode; tone?: "neutral" | "red" | "amber" | "green" }) {
  return <span className={`pill pill-${tone}`}>{children}</span>;
}

export default function Home() {
  const [branch, setBranch] = useState("Cubao");
  const [selectedId, setSelectedId] = useState("TCK-0007");
  const [approved, setApproved] = useState(false);
  const [notice, setNotice] = useState("");
  const [activeNav, setActiveNav] = useState("PromiseGuard");
  const selected = useMemo(() => cases.find((item) => item.id === selectedId) ?? cases[0], [selectedId]);

  function runTriage() {
    setNotice(`Triage complete for ${branch}. ${cases.length} cases ranked from verified delivery evidence.`);
  }

  function approveAction() {
    setApproved(true);
    setNotice("Action verified: Ana Lopez’s case is assigned to Mika Santos and moved to pending review.");
  }

  function selectNav(label: string) {
    setActiveNav(label);
    if (label !== "PromiseGuard") {
      setNotice(`${label} selected. This workspace view will connect to the shared operations data in the next integration step.`);
    }
  }

  const viewCopy = {
    PromiseGuard: ["PromiseGuard", "Recover the customer without making another promise the business cannot keep."],
    "Recovery queue": ["Recovery queue", "A focused worklist for unresolved customer promises across Suki Mart."],
    "Branch operations": ["Branch operations", "See where staffing, delivery outcomes, and customer friction meet."],
    "Audit history": ["Audit history", "Every recovery action is recorded, verified, and ready to explain."],
  }[activeNav] ?? ["PromiseGuard", "Evidence-backed customer recovery operations."];

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand"><div className="brand-mark">S</div><div><strong>Suki Mart</strong><span>Operations console</span></div></div>
        <div className="workspace-label">WORKSPACE</div>
        <nav>
          <button className={`nav-item ${activeNav === "PromiseGuard" ? "active" : ""}`} onClick={() => selectNav("PromiseGuard")}><span>◈</span> PromiseGuard</button>
          <button className={`nav-item ${activeNav === "Recovery queue" ? "active" : ""}`} onClick={() => selectNav("Recovery queue")}><span>⌁</span> Recovery queue <b>11</b></button>
          <button className={`nav-item ${activeNav === "Branch operations" ? "active" : ""}`} onClick={() => selectNav("Branch operations")}><span>◌</span> Branch operations</button>
          <button className={`nav-item ${activeNav === "Audit history" ? "active" : ""}`} onClick={() => selectNav("Audit history")}><span>▣</span> Audit history</button>
        </nav>
        <div className="sidebar-bottom"><div className="sandbox-dot" /> Sandbox connected<div className="sandbox-date">Data date · 30 Sep 2026</div></div>
      </aside>

      <section className="main-content">
        <header className="topbar"><div><div className="eyebrow">CUSTOMER EXPERIENCE · OPERATIONS</div><h1>{viewCopy[0]}</h1><p>{viewCopy[1]}</p></div><div className="top-actions"><span className="live-dot" /> Local sandbox <button className="avatar">GS</button></div></header>

        <div className="toolbar"><div><label htmlFor="branch">Branch</label><select id="branch" value={branch} onChange={(event) => setBranch(event.target.value)}><option>Cubao</option><option>BGC</option><option>Makati</option><option>Kapitolyo</option></select></div><button className="primary-button" onClick={runTriage}>↻ Find recovery cases</button></div>

        <div className="signal-strip"><div className="signal-copy"><span className="signal-icon">✦</span><div><strong>PromiseGuard is watching the queue</strong><small>Evidence-first recovery · no unsupported promises</small></div></div><div className="pipeline"><span className="pipeline-step done">01 <b>Detect</b></span><i /> <span className="pipeline-step active">02 <b>Investigate</b></span><i /> <span className="pipeline-step">03 <b>Recover</b></span></div></div>

        <section className="hero-banner"><div className="hero-glow" /><div className="hero-copy"><div className="hero-kicker">RECOVERY COMMAND CENTER</div><h2>Make the next promise<br /><em>a safe one.</em></h2><p>Turn delivery frustration into an evidence-backed action your team can actually keep.</p><div className="hero-tags"><span>✦ Evidence linked</span><span>⌁ Approval required</span><span>◷ Audit trail ready</span></div></div><div className="confidence-card"><div className="confidence-ring"><strong>92</strong><span>%</span></div><div><b>Evidence confidence</b><small>Across today’s queue</small></div></div><div className="hero-side-stat"><span>Next best action</span><strong>Assign an active CSR</strong><small>2 owners available in Cubao</small><button onClick={() => setNotice("Ready to review the highest-priority case: TCK-0007.")}>Review priority case →</button></div></section>

        {notice && <div className="notice"><span>✓</span>{notice}<button onClick={() => setNotice("")}>×</button></div>}

        <div className="stats-grid"><div className="stat-card"><span>Open recovery cases</span><strong>11</strong><small>8 older than 7 days</small></div><div className="stat-card"><span>Need a first response</span><strong>8</strong><small className="warning-text">Requires attention</small></div><div className="stat-card"><span>Promise checks blocked</span><strong>6</strong><small>No reliable ETA or refund authority</small></div><div className="stat-card accent"><span>Data integrity</span><strong>99.2%</strong><small>1 invalid chronology excluded</small></div></div>

        <div className={`content-grid ${activeNav !== "PromiseGuard" ? "view-hidden" : ""}`}>
          <section className="panel cases-panel"><div className="panel-heading"><div><h2>Recovery queue</h2><p>Ranked by priority, unanswered status, and case age.</p></div><span className="count-badge">{cases.length} shown</span></div><div className="case-list">{cases.map((item) => <button key={item.id} className={`case-row ${selected.id === item.id ? "selected" : ""}`} onClick={() => { setSelectedId(item.id); setApproved(false); }}><div className="case-avatar">{item.initials}</div><div className="case-copy"><div className="case-top"><strong>{item.customer}</strong><span>{item.id}</span></div><p>{item.summary}</p><div className="case-meta"><StatusPill tone={item.outcome === "Failed" ? "red" : item.outcome === "Late" ? "amber" : "neutral"}>{item.outcome}</StatusPill><span>{item.age} days old</span><span>{item.response}</span></div></div><div className="priority">{Array.from({ length: 3 }).map((_, index) => <i key={index} className={index < item.priority ? "on" : ""}>◆</i>)}</div></button>)}</div><div className="excluded">ⓘ TCK-0003 excluded · ticket created before its order</div></section>

          <section className="panel detail-panel"><div className="detail-header"><div><div className="eyebrow">CUSTOMER RECOVERY CASE</div><h2>{selected.id}</h2></div><StatusPill tone={approved ? "green" : "red"}>{approved ? "Pending review" : selected.status}</StatusPill></div><div className="customer-hero"><div className="hero-avatar">{selected.initials}</div><div><h3>{selected.customer}</h3><p>{selected.summary}</p></div></div><div className="evidence-block"><div className="section-title">EVIDENCE CHAIN <span>Verified from sandbox</span></div><div className="evidence-chain"><div><b>{selected.id}</b><small>Support ticket</small></div><span>→</span><div><b>{selected.order}</b><small>Order</small></div><span>→</span><div><b>{selected.delivery}</b><small>Delivery</small></div></div></div><div className="facts-grid"><div><span>Delivery outcome</span><strong>{selected.outcome}</strong></div><div><span>Ticket age</span><strong>{selected.age} days</strong></div><div><span>Branch</span><strong>{branch}</strong></div><div><span>Response status</span><strong>{selected.response}</strong></div></div><div className="promise-box"><div className="section-title">PROMISE CHECK <span>Before any customer response</span></div><div className="check-line safe"><span>✓</span><div><strong>Actual delivery facts verified</strong><small>Delivery outcome is recorded as failed.</small></div></div><div className="check-line safe"><span>✓</span><div><strong>Active owner available</strong><small>Mika Santos · Customer Service</small></div></div><div className="check-line blocked"><span>!</span><div><strong>No reliable new ETA</strong><small>Do not promise a replacement arrival time.</small></div></div><div className="check-line blocked"><span>!</span><div><strong>Refund authorization unavailable</strong><small>Do not offer a refund without approval.</small></div></div></div><div className="recovery-plan"><div className="section-title">SAFE RECOVERY PLAN</div><p>Assign an active CSR and move the case to pending review. Prepare an honest response, but do not send it automatically.</p><div className="response-draft">“Hi {selected.customer.split(" ")[0]}, we reviewed ticket {selected.id}. Your order is currently marked as failed. Our customer service team has been assigned to review the case. Draft only—not sent.”</div></div><div className="detail-actions"><button className="secondary-button">Preview response</button><button className="primary-button" onClick={approveAction}>{approved ? "✓ Action verified" : "Approve & assign"}</button></div></section>
        </div>

        {activeNav === "Recovery queue" && <section className="workspace-view"><div className="view-heading"><div><div className="eyebrow">WORK QUEUE · LIVE PRIORITIES</div><h2>Everyone who needs a human next</h2><p>Sort the queue by what is urgent, unanswered, and still safe to act on.</p></div><button className="secondary-button" onClick={() => setNotice("Queue refreshed from the local Suki Mart sandbox.")}>↻ Refresh queue</button></div><div className="queue-board"><div className="queue-column"><div className="column-title"><span className="column-dot urgent" />Needs owner <b>8</b></div>{cases.slice(0, 3).map((item) => <button className="mini-case" key={item.id} onClick={() => { setSelectedId(item.id); setActiveNav("PromiseGuard"); }}><div className="mini-case-top"><strong>{item.id}</strong><StatusPill tone="red">{item.age}d</StatusPill></div><p>{item.summary}</p><small>{item.customer} · {item.response}</small></button>)}</div><div className="queue-column"><div className="column-title"><span className="column-dot review" />Pending review <b>2</b></div><div className="empty-column"><span>◎</span><strong>No new escalations</strong><small>Cases here have an assigned owner.</small></div></div><div className="queue-column"><div className="column-title"><span className="column-dot done" />Verified today <b>1</b></div><div className="verified-card"><span>✓</span><div><strong>TCK-0010</strong><small>Response prepared · draft only</small></div></div></div></div></section>}

        {activeNav === "Branch operations" && <section className="workspace-view"><div className="view-heading"><div><div className="eyebrow">NETWORK PULSE · CUBAO</div><h2>What is happening at the branch?</h2><p>Operational context helps explain a delay, but never proves causality on its own.</p></div><StatusPill tone="amber">3 signals need review</StatusPill></div><div className="ops-grid"><div className="ops-card large"><span className="ops-label">DELIVERY RELIABILITY</span><strong>68%</strong><div className="bar"><i style={{ width: "68%" }} /></div><small>7 failed or late deliveries in the current recovery sample</small></div><div className="ops-card"><span className="ops-label">STAFFING COVERAGE</span><strong>82%</strong><div className="bar blue"><i style={{ width: "82%" }} /></div><small>18 scheduled · 15 active on the latest shift</small></div><div className="ops-card alert"><span className="ops-label">UNANSWERED CASES</span><strong>8</strong><small>Oldest open case is 14 days old</small><button onClick={() => { setActiveNav("Recovery queue"); setNotice("Showing the branch cases that need an owner."); }}>Open queue →</button></div></div></section>}

        {activeNav === "Audit history" && <section className="workspace-view"><div className="view-heading"><div><div className="eyebrow">CONTROLLED ACTIONS · AUDIT TRAIL</div><h2>Nothing disappears after approval</h2><p>PromiseGuard records what changed, who changed it, and what remains unresolved.</p></div><button className="secondary-button" onClick={() => setNotice("Audit export is available once Supabase persistence is connected.")}>Export log</button></div><div className="audit-list"><div className="audit-item"><span className="audit-icon green">✓</span><div><strong>Recovery action verified</strong><p>TCK-0010 · owner assigned to Mika Santos · status moved to pending</p></div><time>Today · 09:12</time></div><div className="audit-item"><span className="audit-icon amber">!</span><div><strong>Promise blocked</strong><p>TCK-0007 · no reliable ETA found in delivery evidence</p></div><time>Today · 09:08</time></div><div className="audit-item"><span className="audit-icon blue">↗</span><div><strong>Recovery queue refreshed</strong><p>Cubao · 11 cases ranked · 1 invalid chronology excluded</p></div><time>Today · 09:03</time></div></div></section>}
      </section>
    </main>
  );
}
