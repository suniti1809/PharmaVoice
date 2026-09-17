/** Complaint register: recently logged complaints, so saving is visibly persistent. */

import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchComplaints } from '../features/complaint/complaintSlice';

export default function ComplaintRegister({ onNewComplaint }) {
  const dispatch = useDispatch();
  const register = useSelector((state) => state.complaint.register);
  const savedComplaint = useSelector((state) => state.complaint.savedComplaint);

  useEffect(() => {
    dispatch(fetchComplaints());
  }, [dispatch, savedComplaint?.id]);

  return (
    <div className="card register-card">
      <header className="card-header">
        <div>
          <h2>Complaint Register</h2>
          <span className="subtle small">{register.length} logged quality record(s)</span>
        </div>
        {onNewComplaint && (
          <button type="button" className="btn btn-primary btn-sm" onClick={onNewComplaint}>
            + New Complaint Intake
          </button>
        )}
      </header>

      {register.length === 0 ? (
        <p className="subtle small">No complaints logged yet.</p>
      ) : (
        <table className="register-table">
          <thead>
            <tr>
              <th>Complaint No.</th>
              <th>Customer</th>
              <th>Product</th>
              <th>Batch</th>
              <th>Type</th>
              <th>Severity</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {register.map((row) => (
              <tr key={row.id} className={row.id === savedComplaint?.id ? 'row-new' : ''}>
                <td>{row.complaint_number}</td>
                <td>{row.customer_name ?? '—'}</td>
                <td>{row.product_name ?? '—'}</td>
                <td>{row.batch_number ?? '—'}</td>
                <td>{row.complaint_type ?? '—'}</td>
                <td>
                  <span className={`pill pill-${(row.initial_severity ?? 'none').toLowerCase()}`}>
                    {row.initial_severity ?? '—'}
                  </span>
                </td>
                <td>{row.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
