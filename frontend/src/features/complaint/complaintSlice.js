/**
 * Complaint slice: owns the Log Customer Complaint form.
 *
 * The interesting bit is `extraReducers`: this slice listens to the *intake*
 * thunks, so when the AI agent finishes, the form fills itself. The two panels
 * never talk to each other directly - the store is the contract.
 */

import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { api } from '../../api/client';
import { runIntakeFromFile, runIntakeFromText } from '../intake/intakeSlice';

export const EMPTY_FORM = {
  complaint_source: '',
  customer_name: '',
  product_name: '',
  product_strength: '',
  batch_number: '',
  manufacturing_date: '',
  expiry_date: '',
  quantity_affected: '',
  quantity_uom: 'kg',
  complaint_type: '',
  complaint_date: '',
  description: '',
  initial_severity: '',
  priority: '',
};

export const fetchMetadata = createAsyncThunk('complaint/metadata', async () => api.metadata());

export const fetchComplaints = createAsyncThunk('complaint/list', async () => api.listComplaints());

export const saveComplaint = createAsyncThunk(
  'complaint/save',
  async (_, { getState, rejectWithValue }) => {
    const { complaint, intake } = getState();
    const payload = { ...complaint.form };

    // Empty strings must become null: FastAPI/Pydantic validates dates and numbers.
    Object.keys(payload).forEach((key) => {
      if (payload[key] === '') payload[key] = null;
    });
    payload.quantity_affected =
      payload.quantity_affected === null ? null : Number(payload.quantity_affected);
    payload.ai_assessment = intake.result
      ? {
          risk: intake.result.risk,
          completeness: intake.result.completeness,
          duplicates: intake.result.duplicates,
          confidence: intake.result.confidence,
          trace: intake.result.trace,
          model_used: intake.result.model_used,
        }
      : null;
    payload.source_document = intake.filename ?? null;
    payload.raw_text = intake.result?.raw_text_preview ?? intake.pastedText ?? null;

    try {
      return await api.saveComplaint(payload);
    } catch (error) {
      return rejectWithValue(error.message);
    }
  },
);

/** Convert the agent's ExtractedComplaint into form-friendly strings. */
function formFromExtraction(extracted) {
  const next = { ...EMPTY_FORM };
  Object.entries(extracted).forEach(([key, value]) => {
    if (!(key in next)) return;
    next[key] = value === null || value === undefined ? '' : String(value);
  });
  if (!next.quantity_uom) next.quantity_uom = 'kg';
  return next;
}

const initialState = {
  form: { ...EMPTY_FORM },
  aiFilledFields: [], // drives the "AI extracted" highlight in the UI
  metadata: {
    complaint_sources: [],
    complaint_types: [],
    severities: [],
    priorities: [],
    uoms: ['kg'],
  },
  saveStatus: 'idle',
  saveError: null,
  savedComplaint: null,
  register: [],
};

const complaintSlice = createSlice({
  name: 'complaint',
  initialState,
  reducers: {
    updateField(state, action) {
      const { field, value } = action.payload;
      state.form[field] = value;
      // A human edit removes the AI highlight - the reviewer now owns the value.
      state.aiFilledFields = state.aiFilledFields.filter((f) => f !== field);
      state.saveStatus = 'idle';
    },
    resetForm(state) {
      state.form = { ...EMPTY_FORM };
      state.aiFilledFields = [];
      state.saveStatus = 'idle';
      state.saveError = null;
      state.savedComplaint = null;
    },
  },
  extraReducers(builder) {
    const applyExtraction = (state, action) => {
      state.form = formFromExtraction(action.payload.extracted);
      state.aiFilledFields = Object.entries(state.form)
        .filter(([, value]) => value !== '' && value !== 'kg')
        .map(([key]) => key);
      state.savedComplaint = null;
      state.saveStatus = 'idle';
    };

    builder
      .addCase(runIntakeFromText.fulfilled, applyExtraction)
      .addCase(runIntakeFromFile.fulfilled, applyExtraction)
      .addCase(fetchMetadata.fulfilled, (state, action) => {
        state.metadata = action.payload;
      })
      .addCase(fetchComplaints.fulfilled, (state, action) => {
        state.register = action.payload;
      })
      .addCase(saveComplaint.pending, (state) => {
        state.saveStatus = 'saving';
        state.saveError = null;
      })
      .addCase(saveComplaint.fulfilled, (state, action) => {
        state.saveStatus = 'saved';
        state.savedComplaint = action.payload;
        state.register = [action.payload, ...state.register];
      })
      .addCase(saveComplaint.rejected, (state, action) => {
        state.saveStatus = 'failed';
        state.saveError = action.payload ?? 'Could not save the complaint';
      });
  },
});

export const { updateField, resetForm } = complaintSlice.actions;
export default complaintSlice.reducer;
