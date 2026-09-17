/** Reusable labelled inputs for the complaint form. */

import React from 'react';

const PLACEHOLDER = 'Awaiting AI extraction…';

function Wrapper({ label, aiFilled, children, hint }) {
  return (
    <label className="field">
      <span className="field-label">
        {label}
        {aiFilled && <span className="ai-chip" title="Populated by the AI agent">AI</span>}
      </span>
      {children}
      {hint && <span className="field-hint">{hint}</span>}
    </label>
  );
}

export function TextField({ label, name, value, onChange, aiFilled, type = 'text', hint, suffix }) {
  const input = (
    <input
      className={`input ${aiFilled ? 'input-ai' : ''}`}
      type={type}
      name={name}
      value={value}
      placeholder={type === 'date' ? '' : PLACEHOLDER}
      onChange={(event) => onChange(name, event.target.value)}
    />
  );
  return (
    <Wrapper label={label} aiFilled={aiFilled} hint={hint}>
      {suffix ? (
        <span className="input-with-suffix">
          {input}
          {suffix}
        </span>
      ) : (
        input
      )}
    </Wrapper>
  );
}

export function SelectField({ label, name, value, onChange, options, aiFilled, hint }) {
  return (
    <Wrapper label={label} aiFilled={aiFilled} hint={hint}>
      <select
        className={`input ${aiFilled ? 'input-ai' : ''}`}
        name={name}
        value={value}
        onChange={(event) => onChange(name, event.target.value)}
      >
        <option value="">{PLACEHOLDER}</option>
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </Wrapper>
  );
}

export function TextAreaField({ label, name, value, onChange, aiFilled, rows = 4 }) {
  return (
    <Wrapper label={label} aiFilled={aiFilled}>
      <textarea
        className={`input textarea ${aiFilled ? 'input-ai' : ''}`}
        name={name}
        rows={rows}
        value={value}
        placeholder={PLACEHOLDER}
        onChange={(event) => onChange(name, event.target.value)}
      />
    </Wrapper>
  );
}
