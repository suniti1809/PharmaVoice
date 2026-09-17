/**
 * Intake slice: owns everything in the right-hand "AI Complaint Intake Assistant"
 * panel - the uploaded/pasted input, a simulated extraction progress bar, the
 * agent result (risk, completeness, duplicates, trace) and the chat thread.
 */

import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { api } from '../../api/client';

const INITIAL_ASSISTANT_MESSAGE = {
  role: 'assistant',
  text:
    'Upload a complaint document or paste the email text above. I will extract the details, ' +
    'populate the form for you, and run an initial risk assessment.',
};

export const runIntakeFromText = createAsyncThunk(
  'intake/runFromText',
  async (text, { rejectWithValue }) => {
    try {
      return await api.intakeText(text);
    } catch (error) {
      return rejectWithValue(error.message);
    }
  },
);

export const runIntakeFromFile = createAsyncThunk(
  'intake/runFromFile',
  async (file, { rejectWithValue }) => {
    try {
      const result = await api.intakeFile(file);
      return { ...result, filename: file.name };
    } catch (error) {
      return rejectWithValue(error.message);
    }
  },
);

export const askAssistant = createAsyncThunk(
  'intake/ask',
  async (question, { getState, rejectWithValue }) => {
    const state = getState();
    try {
      const response = await api.chat(
        question,
        state.intake.result?.raw_text_preview ?? state.intake.pastedText,
        state.complaint.form,
      );
      return response.answer;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  },
);

const initialState = {
  pastedText: '',
  filename: null,
  status: 'idle', // idle | running | succeeded | failed
  progress: 0,
  stage: null,
  error: null,
  result: null,
  chat: [INITIAL_ASSISTANT_MESSAGE],
  chatStatus: 'idle',
};

const intakeSlice = createSlice({
  name: 'intake',
  initialState,
  reducers: {
    setPastedText(state, action) {
      state.pastedText = action.payload;
    },
    setProgress(state, action) {
      state.progress = action.payload.progress;
      state.stage = action.payload.stage;
    },
    resetIntake() {
      return { ...initialState };
    },
  },
  extraReducers(builder) {
    const started = (state, action) => {
      state.status = 'running';
      state.error = null;
      state.progress = 8;
      state.stage = 'Reading input…';
      state.filename = action.meta.arg?.name ?? null;
    };

    const finished = (state, action) => {
      state.status = 'succeeded';
      state.progress = 100;
      state.stage = 'Extraction complete';
      state.result = action.payload;
      state.filename = action.payload.filename ?? state.filename;

      const { risk, completeness, duplicates, latency_ms: latency } = action.payload;
      const lines = [
        `Extracted the complaint in ${(latency / 1000).toFixed(1)}s and populated the form.`,
        `Completeness: ${completeness.score}/100${
          completeness.missing_fields.length ? ` · missing: ${completeness.missing_fields.join(', ')}` : ' · all required fields present'
        }.`,
        `Initial assessment: ${risk.severity ?? 'n/a'} severity, risk score ${risk.risk_score}/100${
          risk.regulatory_reportable ? ' · flagged as potentially reportable' : ''
        }.`,
      ];
      if (duplicates.length) {
        lines.push(
          `Possible duplicate of ${duplicates.map((d) => d.complaint_number).join(', ')} — please verify before saving.`,
        );
      }
      state.chat.push({ role: 'assistant', text: lines.join('\n') });
    };

    const failed = (state, action) => {
      state.status = 'failed';
      state.progress = 0;
      state.stage = null;
      state.error = action.payload ?? 'Extraction failed';
      state.chat.push({ role: 'assistant', text: `I could not process that input: ${state.error}` });
    };

    builder
      .addCase(runIntakeFromText.pending, started)
      .addCase(runIntakeFromText.fulfilled, finished)
      .addCase(runIntakeFromText.rejected, failed)
      .addCase(runIntakeFromFile.pending, started)
      .addCase(runIntakeFromFile.fulfilled, finished)
      .addCase(runIntakeFromFile.rejected, failed)
      .addCase(askAssistant.pending, (state, action) => {
        state.chatStatus = 'running';
        state.chat.push({ role: 'user', text: action.meta.arg });
      })
      .addCase(askAssistant.fulfilled, (state, action) => {
        state.chatStatus = 'idle';
        state.chat.push({ role: 'assistant', text: action.payload });
      })
      .addCase(askAssistant.rejected, (state, action) => {
        state.chatStatus = 'idle';
        state.chat.push({ role: 'assistant', text: `Sorry — ${action.payload ?? 'the assistant failed'}` });
      });
  },
});

export const { setPastedText, setProgress, resetIntake } = intakeSlice.actions;
export default intakeSlice.reducer;
