/**
 * Single place where the frontend talks to FastAPI.
 * Vite proxies /api to the backend in dev (see vite.config.js).
 */

const BASE = import.meta.env.VITE_API_BASE_URL ?? '';

async function handle(response) {
  if (!response.ok) {
    let detail = `Request failed with status ${response.status}`;
    try {
      const body = await response.json();
      if (body?.detail) detail = typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail);
    } catch {
      /* non-JSON error body - keep the generic message */
    }
    throw new Error(detail);
  }
  return response.json();
}

export const api = {
  metadata: () => fetch(`${BASE}/api/metadata`).then(handle),

  health: () => fetch(`${BASE}/api/health`).then(handle),

  intakeText: (text) =>
    fetch(`${BASE}/api/intake/text`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    }).then(handle),

  intakeFile: (file) => {
    const form = new FormData();
    form.append('file', file);
    return fetch(`${BASE}/api/intake/file`, { method: 'POST', body: form }).then(handle);
  },

  chat: (question, contextText, formState) =>
    fetch(`${BASE}/api/intake/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, context_text: contextText, form_state: formState }),
    }).then(handle),

  saveComplaint: (payload) =>
    fetch(`${BASE}/api/complaints`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }).then(handle),

  listComplaints: () => fetch(`${BASE}/api/complaints`).then(handle),
};
