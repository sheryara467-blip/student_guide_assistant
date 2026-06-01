/**
 * api.js
 * Centralised API layer for the Student Guide Assistant frontend.
 *
 * Endpoints (matching the existing FastAPI backend exactly):
 *   GET  /topics          → { topics: string[] }
 *   POST /chat            → { answer, retrieved_context, model_used }
 */

const BASE_URL = import.meta.env.VITE_API_URL ?? ''
// If VITE_API_URL is set (e.g. in production), requests go there directly.
// In development, Vite's proxy forwards /chat and /topics to localhost:8000.

// ─── GET /topics ─────────────────────────────────────────────────────────────
/**
 * Fetch the list of indexed topics from the backend.
 * @returns {Promise<string[]>}
 */
export async function fetchTopics() {
  const res = await fetch(`${BASE_URL}/topics`)
  if (!res.ok) throw new Error(`GET /topics failed: HTTP ${res.status}`)
  const data = await res.json()
  return data.topics ?? []
}

// ─── POST /chat ───────────────────────────────────────────────────────────────
/**
 * Send a student question to the RAG pipeline.
 *
 * @param {string} question
 * @returns {Promise<{ answer: string, retrieved_context: object[], model_used: string }>}
 */
export async function sendQuestion(question) {
  const res = await fetch(`${BASE_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  })

  if (!res.ok) {
    // Try to surface the backend error message if available
    let detail = `HTTP ${res.status}`
    try {
      const err = await res.json()
      detail = err.detail ?? err.message ?? detail
    } catch {
      // ignore parse error
    }
    throw new Error(detail)
  }

  return res.json()
}