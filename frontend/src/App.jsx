import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { api } from './api/client';
import ComplaintRegister from './components/ComplaintRegister';
import IntakeAssistant from './components/IntakeAssistant';
import LogComplaintForm from './components/LogComplaintForm';
import RiskPanel from './components/RiskPanel';
import { fetchMetadata } from './features/complaint/complaintSlice';

const TABS = [
  {
    id: 'intake',
    title: 'New Complaint Intake',
    shortLabel: 'Intake & Form',
    subtitle: 'Multimodal AI document extraction with QA complaint logging',
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
        <polyline points="14 2 14 8 20 8" />
        <line x1="12" y1="18" x2="12" y2="12" />
        <line x1="9" y1="15" x2="15" y2="15" />
      </svg>
    ),
  },
  {
    id: 'assessment',
    title: 'Risk Evaluation & Intelligence',
    shortLabel: 'Risk Evaluation',
    subtitle: 'AI risk scoring, severity assessment, root causes, CAPA & duplicate audit',
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
        <path d="M12 8v4" />
        <path d="M12 16h.01" />
      </svg>
    ),
  },
  {
    id: 'register',
    title: 'Complaint Quality Register',
    shortLabel: 'Complaint Register',
    subtitle: 'Historical registry, audit trail, and persistent complaint log',
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
        <line x1="3" y1="9" x2="21" y2="9" />
        <line x1="9" y1="21" x2="9" y2="9" />
      </svg>
    ),
  },
];

export default function App() {
  const dispatch = useDispatch();
  const [activeTab, setActiveTab] = useState('intake');
  const [health, setHealth] = useState(null);
  const register = useSelector((state) => state.complaint.register);
  const risk = useSelector((state) => state.intake.result?.risk);

  useEffect(() => {
    dispatch(fetchMetadata());
    api.health().then(setHealth).catch(() => setHealth({ status: 'unreachable' }));
  }, [dispatch]);

  // Derived metrics from Redux register
  const openCount = register.filter((row) => row.status !== 'Closed').length;
  const criticalCount = register.filter((row) => row.initial_severity === 'Critical').length;

  const currentTab = TABS.find((t) => t.id === activeTab) || TABS[0];

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">PharmaVoice</span>
          <span className="brand-sub">Complaint Intake &amp; Quality Assurance</span>
        </div>

        <nav className="side-nav" aria-label="Primary Navigation">
          {TABS.map((tab) => {
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                type="button"
                className={`side-link ${isActive ? 'active' : ''}`}
                onClick={() => setActiveTab(tab.id)}
              >
                <span className="side-link-icon">{tab.icon}</span>
                <span className="side-link-text">{tab.shortLabel}</span>
                {tab.id === 'assessment' && risk?.risk_score !== undefined && (
                  <span className="side-link-badge badge-risk">{risk.risk_score}</span>
                )}
                {tab.id === 'register' && register.length > 0 && (
                  <span className="side-link-badge">{register.length}</span>
                )}
              </button>
            );
          })}
        </nav>

        <div className="side-stats" aria-label="System Metrics">
          <div
            className="stat stat-interactive"
            onClick={() => setActiveTab('register')}
            role="button"
            tabIndex={0}
            title="View full Complaint Register"
            onKeyDown={(e) => e.key === 'Enter' && setActiveTab('register')}
          >
            <span className="stat-value">{register.length}</span>
            <span className="stat-label">Total</span>
          </div>
          <div
            className="stat stat-interactive"
            onClick={() => setActiveTab('register')}
            role="button"
            tabIndex={0}
            title="View open complaints in Register"
            onKeyDown={(e) => e.key === 'Enter' && setActiveTab('register')}
          >
            <span className="stat-value">{openCount}</span>
            <span className="stat-label">Open</span>
          </div>
          <div
            className="stat stat-interactive"
            onClick={() => setActiveTab('register')}
            role="button"
            tabIndex={0}
            title="View critical complaints in Register"
            onKeyDown={(e) => e.key === 'Enter' && setActiveTab('register')}
          >
            <span className="stat-value stat-critical">{criticalCount}</span>
            <span className="stat-label">Critical</span>
          </div>
          <div
            className="stat stat-interactive"
            onClick={() => setActiveTab('assessment')}
            role="button"
            tabIndex={0}
            title="View AI Risk Evaluation"
            onKeyDown={(e) => e.key === 'Enter' && setActiveTab('assessment')}
          >
            <span className="stat-value">{risk?.risk_score ?? '—'}</span>
            <span className="stat-label">Risk</span>
          </div>
        </div>

        <div className="side-footer">
          {health && (
            <span className={`status-dot ${health.status === 'ok' ? 'ok' : 'down'}`}>
              {health.status === 'ok'
                ? health.llm_enabled
                  ? 'AI assistant online'
                  : 'AI key missing · rule mode'
                : 'Backend unreachable'}
            </span>
          )}
          <span className="crumb">Quality › Customer Complaints › {currentTab.shortLabel}</span>
        </div>
      </aside>

      {/* Main workspace with active tab views */}
      <div className="workspace">
        <header className="workspace-header">
          <div className="workspace-title-group">
            <div className="workspace-crumb">Quality Assurance › {currentTab.title}</div>
            <h1 className="workspace-title">{currentTab.title}</h1>
            <p className="workspace-subtitle">{currentTab.subtitle}</p>
          </div>

          <div className="workspace-tabs" role="tablist" aria-label="Workflow Tabs">
            {TABS.map((tab) => {
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  role="tab"
                  aria-selected={isActive}
                  className={`tab-btn ${isActive ? 'active' : ''}`}
                  onClick={() => setActiveTab(tab.id)}
                >
                  <span className="tab-btn-icon">{tab.icon}</span>
                  <span className="tab-btn-text">{tab.shortLabel}</span>
                  {tab.id === 'assessment' && risk?.risk_score !== undefined && (
                    <span className="tab-badge tab-badge-risk">{risk.risk_score}</span>
                  )}
                  {tab.id === 'register' && register.length > 0 && (
                    <span className="tab-badge">{register.length}</span>
                  )}
                </button>
              );
            })}
          </div>
        </header>

        <div className="workspace-body tab-content" key={activeTab}>
          {activeTab === 'intake' && (
            <div className="tab-pane tab-pane-intake">
              {risk?.risk_score !== undefined && (
                <aside className="risk-banner-notice">
                  <div className="risk-notice-text">
                    <span className="spark">⚡</span>
                    <div>
                      <strong>AI Risk Evaluation Ready:</strong> Evaluated score is{' '}
                      <strong>{risk.risk_score}/100</strong> ({risk.severity || risk.risk_band}).
                      CAPA recommendations and root causes detected.
                    </div>
                  </div>
                  <button
                    type="button"
                    className="btn btn-secondary btn-sm"
                    onClick={() => setActiveTab('assessment')}
                  >
                    Inspect Risk Evaluation →
                  </button>
                </aside>
              )}

              <section id="intake-section" className="row">
                <IntakeAssistant />
              </section>

              <section id="form-section" className="row">
                <LogComplaintForm onViewRegister={() => setActiveTab('register')} />
              </section>
            </div>
          )}

          {activeTab === 'assessment' && (
            <div className="tab-pane tab-pane-assessment">
              <RiskPanel
                onGoToIntake={() => setActiveTab('intake')}
                onGoToRegister={() => setActiveTab('register')}
              />
            </div>
          )}

          {activeTab === 'register' && (
            <div className="tab-pane tab-pane-register">
              <ComplaintRegister onNewComplaint={() => setActiveTab('intake')} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
