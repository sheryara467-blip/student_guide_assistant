import { useState } from 'react'
import styles from './ChatMessage.module.css'

// ── tiny helpers ──────────────────────────────────────────────────────────────
function formatTime() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

function formatText(raw) {
  // markdown-lite: **bold**, `code`, newlines
  return raw
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/`([^`]+)`/g, '<code class="inlineCode">$1</code>')
    .replace(/\n/g, '<br />')
}

// ── SourcesPanel ─────────────────────────────────────────────────────────────
function SourcesPanel({ sources }) {
  const [open, setOpen] = useState(false)
  if (!sources || sources.length === 0) return null

  return (
    <>
      <button
        className={`${styles.sourcesToggle} ${open ? styles.open : ''}`}
        onClick={() => setOpen((v) => !v)}
      >
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        {sources.length} source{sources.length > 1 ? 's' : ''} retrieved
        <span className={styles.arrow}>▾</span>
      </button>

      {open && (
        <div className={styles.sourcesPanel}>
          {sources.map((s, i) => (
            <div key={i} className={styles.sourceCard}>
              <div className={styles.sourceCardHeader}>
                <span className={styles.sourceTopic}>{s.topic ?? 'Source'}</span>
                <span className={styles.sourceScore}>
                  score: {typeof s.score === 'number' ? s.score.toFixed(3) : s.score}
                </span>
              </div>
              <div className={styles.sourceContent}>{s.content ?? ''}</div>
              {s.source && (
                <div className={styles.sourceFile}>📄 {s.source}</div>
              )}
            </div>
          ))}
        </div>
      )}
    </>
  )
}

// ── LoadingBubble ─────────────────────────────────────────────────────────────
export function LoadingBubble() {
  return (
    <div className={`${styles.message} ${styles.assistant}`}>
      <div className={styles.avatar}>🤖</div>
      <div className={styles.body}>
        <div className={styles.meta}>
          <span className={`${styles.role} ${styles.roleAssistant}`}>Assistant</span>
          <span>Thinking…</span>
        </div>
        <div className={`${styles.bubble} ${styles.bubbleAssistant}`} style={{ padding: 0 }}>
          <div className={styles.loadingBubble}>
            <span className={styles.dot} />
            <span className={styles.dot} />
            <span className={styles.dot} />
          </div>
        </div>
      </div>
    </div>
  )
}

// ── ChatMessage ───────────────────────────────────────────────────────────────
export default function ChatMessage({ role, text, sources, modelUsed, isError }) {
  const isUser = role === 'user'
  const avatar = isUser ? '🧑‍🎓' : '🤖'
  const label  = isUser ? 'You' : 'Assistant'

  return (
    <div className={`${styles.message} ${isUser ? styles.user : styles.assistant}`}>
      <div className={`${styles.avatar} ${isUser ? styles.avatarUser : styles.avatarAssistant}`}>
        {avatar}
      </div>
      <div className={styles.body}>
        <div className={styles.meta}>
          <span className={`${styles.role} ${isUser ? styles.roleUser : styles.roleAssistant}`}>
            {label}
          </span>
          <span>{formatTime()}</span>
        </div>

        {isError ? (
          <div className={styles.errorMessage}>
            <span>⚠</span>
            <span>
              <strong>Connection error:</strong> {text}
              <br />
              <span style={{ fontSize: '12px', opacity: 0.7 }}>
                Make sure your FastAPI backend is running at the correct address.
              </span>
            </span>
          </div>
        ) : (
          <div
            className={`${styles.bubble} ${isUser ? styles.bubbleUser : styles.bubbleAssistant}`}
            dangerouslySetInnerHTML={{ __html: formatText(text) }}
          />
        )}

        {!isError && !isUser && (
          <>
            <SourcesPanel sources={sources} />
            {modelUsed && (
              <div className={styles.modelBadge}>⚡ {modelUsed}</div>
            )}
          </>
        )}
      </div>
    </div>
  )
}