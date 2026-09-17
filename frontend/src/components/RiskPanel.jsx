/** Right panel bottom: AI Copilot Risk Assessment + the bonus AI features. */

import React from 'react';
import { useSelector } from 'react-redux';

function band(score) {
  if (score >= 80) return 'critical';
  if (score >= 60) return 'high';
  if (score >= 40) return 'medium';
  return 'low';
}

function List({ title, items }) {
  if (!items?.length) return null;
  return (
    <div className="risk-list">
      <p className="eyebrow">{title}</p>
      <ul>
        {items.map((item, index) => (
          <li key={index}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

export default function RiskPanel({ onGoToIntake, onGoToRegister }) {
  const result = useSelector((state) => state.intake.result);

  if (!result) {
    return (
      <div className="card risk-card empty">
        <div className="empty-state-icon">
          <svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
            <path d="M12 8v4" />
            <path d="M12 16h.01" />
          </svg>
        </div>
        <h2>AI Copilot Risk Assessment</h2>
        <p className="subtle">
          Upload or paste a complaint in the Intake Assistant. The copilot evaluates severity,
          risk score, completeness, duplicate matches, probable root causes and CAPA recommendations.
        </p>
        {onGoToIntake && (
          <button type="button" className="btn btn-primary" onClick={onGoToIntake} style={{ marginTop: '16px' }}>
            Start New Complaint Intake
          </button>
        )}
      </div>
    );
  }

  const { risk, completeness, duplicates } = result;
  const scoreBand = band(risk.risk_score);

  return (
    <div className="card risk-card">
      <header className="card-header">
        <h2>AI Copilot Risk Assessment</h2>
        <span className={`badge badge-${scoreBand}`}>{risk.risk_band ?? scoreBand}</span>
      </header>

      {/* Score and headline attributes sit in a narrow rail; the AI findings
          spread across the remaining width so the full-width card stays dense. */}
      <div className="risk-body">
      <aside className="risk-rail">
      <div className="risk-top">
        <div className={`gauge gauge-${scoreBand}`}>
          <span className="gauge-value">{risk.risk_score}</span>
          <span className="gauge-label">RISK / 100</span>
        </div>
        <dl className="risk-meta">
          <div>
            <dt>Severity</dt>
            <dd>{risk.severity ?? '—'}</dd>
          </div>
          <div>
            <dt>Priority</dt>
            <dd>{risk.priority ?? '—'}</dd>
          </div>
          <div>
            <dt>Reportable</dt>
            <dd className={risk.regulatory_reportable ? 'text-critical' : ''}>
              {risk.regulatory_reportable ? 'Evaluate for reporting' : 'Not indicated'}
            </dd>
          </div>
          <div>
            <dt>Completeness</dt>
            <dd>{completeness.score}/100</dd>
          </div>
        </dl>
      </div>

      {risk.rationale && <p className="rationale">{risk.rationale}</p>}
      </aside>

      <div className="risk-details">
      {duplicates.length > 0 && (
        <div className="callout callout-warn">
          <p className="eyebrow">Possible duplicate complaints</p>
          <ul>
            {duplicates.map((duplicate) => (
              <li key={duplicate.complaint_number}>
                <strong>{duplicate.complaint_number}</strong> · {Math.round(duplicate.similarity * 100)}% match ·{' '}
                {duplicate.reason}
              </li>
            ))}
          </ul>
        </div>
      )}

      {completeness.missing_fields.length > 0 && (
        <div className="callout">
          <p className="eyebrow">Completeness checker</p>
          <p className="small">
            Missing: {completeness.missing_fields.map((f) => f.replace(/_/g, ' ')).join(', ')}
          </p>
          {completeness.follow_up_questions.length > 0 && (
            <ul>
              {completeness.follow_up_questions.map((question, index) => (
                <li key={index}>{question}</li>
              ))}
            </ul>
          )}
        </div>
      )}

      {risk.summary && (
        <div className="risk-list">
          <p className="eyebrow">Complaint summary</p>
          <p className="small">{risk.summary}</p>
        </div>
      )}

      <List title="Recommended immediate actions" items={risk.recommended_actions} />
      <List title="Probable root causes" items={risk.probable_root_causes} />
      <List title="CAPA recommendations" items={risk.capa_recommendations} />
      </div>
      </div>

      {(onGoToIntake || onGoToRegister) && (
        <footer className="risk-actions-footer">
          {onGoToIntake && (
            <button type="button" className="btn btn-ghost" onClick={onGoToIntake}>
              ← Review Complaint Form
            </button>
          )}
          {onGoToRegister && (
            <button type="button" className="btn btn-primary" onClick={onGoToRegister}>
              View in Complaint Register →
            </button>
          )}
        </footer>
      )}
    </div>
  );
}
