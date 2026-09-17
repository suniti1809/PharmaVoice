/** Right panel top: upload / paste input, progress and chat with the agent. */

import React, { useEffect, useRef, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  askAssistant,
  resetIntake,
  runIntakeFromFile,
  runIntakeFromText,
  setPastedText,
  setProgress,
} from '../features/intake/intakeSlice';

/** Stages shown while the graph runs, so the user sees what the agent is doing. */
const STAGES = [
  [12, 'Reading document content…'],
  [30, 'Extracting complaint fields…'],
  [55, 'Checking completeness…'],
  [72, 'Searching for duplicate complaints…'],
  [88, 'Assessing risk, root cause and CAPA…'],
];

export default function IntakeAssistant() {
  const dispatch = useDispatch();
  const { pastedText, status, progress, stage, error, chat, chatStatus, filename, result } = useSelector(
    (state) => state.intake,
  );
  const [question, setQuestion] = useState('');
  const [dragging, setDragging] = useState(false);
  const fileInput = useRef(null);
  const chatThreadRef = useRef(null);

  // Advance the progress indicator while the request is in flight.
  useEffect(() => {
    if (status !== 'running') return undefined;
    let index = 0;
    const timer = setInterval(() => {
      if (index >= STAGES.length) return;
      const [value, label] = STAGES[index];
      dispatch(setProgress({ progress: value, stage: label }));
      index += 1;
    }, 900);
    return () => clearInterval(timer);
  }, [status, dispatch]);

  useEffect(() => {
    if (chatThreadRef.current) {
      chatThreadRef.current.scrollTo({
        top: chatThreadRef.current.scrollHeight,
        behavior: 'smooth'
      });
    }
  }, [chat.length, chatStatus]);

  const submitFile = (file) => {
    if (file) dispatch(runIntakeFromFile(file));
  };

  const onDrop = (event) => {
    event.preventDefault();
    setDragging(false);
    submitFile(event.dataTransfer.files?.[0]);
  };

  const onAsk = (event) => {
    event.preventDefault();
    const trimmed = question.trim();
    if (trimmed.length < 2 || chatStatus === 'running') return;
    dispatch(askAssistant(trimmed));
    setQuestion('');
  };

  return (
    <div className="card assistant-card">
      <header className="card-header">
        <div className="assistant-title">
          <span className="spark" aria-hidden="true">✦</span>
          <h2>AI Complaint Intake Assistant</h2>
        </div>
        <span className="badge badge-beta">BETA</span>
      </header>

      {/* Wide intake bar: upload, paste and chat sit in three columns so the
          card stays short instead of stacking into a tall panel. */}
      <div className="intake-grid">
      <div className="intake-col">
      <div
        className={`dropzone ${dragging ? 'dropzone-active' : ''}`}
        onDragOver={(event) => {
          event.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        onClick={() => fileInput.current?.click()}
        role="button"
        tabIndex={0}
        onKeyDown={(event) => event.key === 'Enter' && fileInput.current?.click()}
      >
        <span className="dropzone-icon" aria-hidden="true">⤒</span>
        <p>
          Drag &amp; drop complaint document here
          <br />
          <span className="link">or click to browse</span>
        </p>
        <input
          ref={fileInput}
          type="file"
          accept=".pdf,.docx,.txt,.eml,.md"
          hidden
          onChange={(event) => submitFile(event.target.files?.[0])}
        />
      </div>

      <p className="support-note">
        Supported formats: PDF, DOCX, TXT, EML · Max file size: 10MB
        {filename && <> · Loaded: <strong>{filename}</strong></>}
      </p>

      </div>

      <div className="intake-col">
      <div className="or-divider"><span>OR</span></div>

      <textarea
        className="input textarea paste-box"
        rows={4}
        placeholder="Paste Complaint Text / Email"
        value={pastedText}
        onChange={(event) => dispatch(setPastedText(event.target.value))}
      />
      <div className="paste-actions">
        <button
          type="button"
          className="btn btn-primary btn-sm"
          disabled={pastedText.trim().length === 0 || status === 'running'}
          onClick={() => dispatch(runIntakeFromText(pastedText))}
        >
          Extract with AI
        </button>
        <button type="button" className="btn btn-ghost btn-sm" onClick={() => dispatch(resetIntake())}>
          Clear
        </button>
      </div>

      {(status === 'running' || status === 'succeeded') && (
        <section className="progress-block">
          <div className="progress-head">
            <span>EXTRACTION PROGRESS</span>
            <span>{progress}%</span>
          </div>
          <div className="progress-track">
            <div className="progress-fill" style={{ width: `${progress}%` }} />
          </div>
          <p className="subtle small">
            {stage}
            {status === 'succeeded' && result
              ? ` · completed in ${(result.latency_ms / 1000).toFixed(1)}s`
              : ''}
          </p>
        </section>
      )}

      {error && <p className="alert alert-error">{error}</p>}
      </div>

      <section className="chat-block intake-col">
        <p className="eyebrow">AI ASSISTANT</p>
        <div className="chat-thread" ref={chatThreadRef}>
          {chat.map((message, index) => (
            <div key={index} className={`bubble bubble-${message.role}`}>
              {message.text.split('\n').map((line, lineIndex) => (
                <p key={lineIndex}>{line}</p>
              ))}
            </div>
          ))}
          {chatStatus === 'running' && <div className="bubble bubble-assistant">Thinking…</div>}
        </div>

        <form className="chat-input" onSubmit={onAsk}>
          <input
            className="input"
            placeholder="Ask me anything about this complaint…"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
          />
          <button type="submit" className="btn btn-primary btn-icon" aria-label="Send" disabled={chatStatus === 'running'}>
            ➤
          </button>
        </form>
        <p className="disclaimer">AI responses may contain errors. Please verify information.</p>
      </section>
      </div>
    </div>
  );
}
