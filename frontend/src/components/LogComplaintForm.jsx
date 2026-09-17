/** Left panel: the Log Customer Complaint form (API & FDF Quality Assurance module). */

import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { resetForm, saveComplaint, updateField } from '../features/complaint/complaintSlice';
import { SelectField, TextAreaField, TextField } from './Field';

export default function LogComplaintForm({ onViewRegister }) {
  const dispatch = useDispatch();
  const { form, aiFilledFields, metadata, saveStatus, saveError, savedComplaint } = useSelector(
    (state) => state.complaint,
  );
  const intakeStatus = useSelector((state) => state.intake.status);
  const completeness = useSelector((state) => state.intake.result?.completeness);

  const isAi = (field) => aiFilledFields.includes(field);
  const change = (field, value) => dispatch(updateField({ field, value }));
  const missing = completeness?.missing_fields ?? [];

  const onSubmit = (event) => {
    event.preventDefault();
    dispatch(saveComplaint());
  };

  return (
    <form className="card form-card" onSubmit={onSubmit}>
      <header className="card-header">
        <div>
          <h1>Log Customer Complaint</h1>
          <p className="subtle">API &amp; FDF Quality Assurance Module</p>
        </div>
        <span className="badge badge-pending">
          {savedComplaint ? savedComplaint.status : 'Pending Triage'}
        </span>
      </header>

      {intakeStatus === 'running' && (
        <p className="inline-note">The AI agent is reading the document — fields will populate shortly.</p>
      )}

      <section className="form-section">
        <h2 className="section-title">1 · Origin &amp; Customer Details</h2>
        <div className="grid-2">
          <SelectField
            label="Complaint Source"
            name="complaint_source"
            value={form.complaint_source}
            options={metadata.complaint_sources}
            onChange={change}
            aiFilled={isAi('complaint_source')}
          />
          <TextField
            label="Customer Name"
            name="customer_name"
            value={form.customer_name}
            onChange={change}
            aiFilled={isAi('customer_name')}
            hint={missing.includes('customer_name') ? 'Flagged as missing by the completeness checker' : null}
          />
        </div>
      </section>

      <section className="form-section">
        <h2 className="section-title">2 · Product &amp; Batch Identification</h2>
        <div className="grid-2">
          <TextField
            label="Product Name"
            name="product_name"
            value={form.product_name}
            onChange={change}
            aiFilled={isAi('product_name')}
            hint={missing.includes('product_name') ? 'Flagged as missing' : null}
          />
          <TextField
            label="Product Strength / Grade"
            name="product_strength"
            value={form.product_strength}
            onChange={change}
            aiFilled={isAi('product_strength')}
          />
          <TextField
            label="Batch / Lot Number"
            name="batch_number"
            value={form.batch_number}
            onChange={change}
            aiFilled={isAi('batch_number')}
            hint={missing.includes('batch_number') ? 'Required to open an investigation' : null}
          />
          <TextField
            label="Manufacturing Date"
            name="manufacturing_date"
            type="date"
            value={form.manufacturing_date}
            onChange={change}
            aiFilled={isAi('manufacturing_date')}
          />
          <TextField
            label="Expiry Date"
            name="expiry_date"
            type="date"
            value={form.expiry_date}
            onChange={change}
            aiFilled={isAi('expiry_date')}
          />
          <TextField
            label="Quantity Affected"
            name="quantity_affected"
            type="number"
            value={form.quantity_affected}
            onChange={change}
            aiFilled={isAi('quantity_affected')}
            suffix={
              <select
                className="input suffix-select"
                value={form.quantity_uom}
                onChange={(event) => change('quantity_uom', event.target.value)}
              >
                {(metadata.uoms ?? ['kg']).map((uom) => (
                  <option key={uom} value={uom}>
                    {uom}
                  </option>
                ))}
              </select>
            }
          />
        </div>
      </section>

      <section className="form-section">
        <h2 className="section-title">3 · Complaint Details</h2>
        <div className="grid-2">
          <SelectField
            label="Complaint Type"
            name="complaint_type"
            value={form.complaint_type}
            options={metadata.complaint_types}
            onChange={change}
            aiFilled={isAi('complaint_type')}
          />
          <TextField
            label="Complaint Date"
            name="complaint_date"
            type="date"
            value={form.complaint_date}
            onChange={change}
            aiFilled={isAi('complaint_date')}
          />
        </div>
        <TextAreaField
          label="Detailed Complaint Description"
          name="description"
          value={form.description}
          onChange={change}
          aiFilled={isAi('description')}
          rows={4}
        />
      </section>

      <section className="form-section">
        <h2 className="section-title">4 · Initial Assessment &amp; Priority</h2>
        <div className="grid-2">
          <SelectField
            label="Initial Severity"
            name="initial_severity"
            value={form.initial_severity}
            options={metadata.severities}
            onChange={change}
            aiFilled={isAi('initial_severity')}
          />
          <SelectField
            label="Priority"
            name="priority"
            value={form.priority}
            options={metadata.priorities}
            onChange={change}
            aiFilled={isAi('priority')}
          />
        </div>
      </section>

      {saveStatus === 'failed' && <p className="alert alert-error">{saveError}</p>}
      {saveStatus === 'saved' && savedComplaint && (
        <div className="alert alert-success alert-with-action">
          <span>Saved as <strong>{savedComplaint.complaint_number}</strong> with the AI risk assessment attached.</span>
          {onViewRegister && (
            <button type="button" className="btn btn-secondary btn-sm" onClick={onViewRegister}>
              View in Register →
            </button>
          )}
        </div>
      )}

      <footer className="card-footer">
        <button type="button" className="btn btn-ghost" onClick={() => dispatch(resetForm())}>
          Reset Form
        </button>
        <button type="submit" className="btn btn-primary" disabled={saveStatus === 'saving'}>
          {saveStatus === 'saving' ? 'Saving…' : 'Save Complaint'}
        </button>
      </footer>
    </form>
  );
}
