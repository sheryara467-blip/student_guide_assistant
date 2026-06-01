import styles from './Sidebar.module.css'
import { useTopics } from '../hooks/useTopics'

export default function Sidebar({ isOpen, onTopicClick }) {
  const { topics, status } = useTopics()

  return (
    <aside className={`${styles.sidebar} ${isOpen ? styles.open : ''}`}>
      <div className={styles.header}>
        <div className={styles.logoMark}>
          <div className={styles.logoIcon}>🎓</div>
          <span className={styles.logoText}>Student Guide</span>
        </div>
        <div className={styles.logoSub}>AI Knowledge Assistant</div>
      </div>

      <div className={styles.sectionTitle}>Indexed Topics</div>

      <div className={styles.topicsList}>
        {status === 'loading' && (
          <div className={styles.placeholder}>Loading topics…</div>
        )}
        {status === 'error' && (
          <div className={styles.placeholder}>⚠ Could not load topics</div>
        )}
        {status === 'ok' && topics.length === 0 && (
          <div className={styles.placeholder}>No topics found</div>
        )}
        {status === 'ok' && topics.map((t) => (
          <button
            key={t}
            className={styles.topicItem}
            onClick={() => onTopicClick(t)}
          >
            <span className={styles.topicDot} />
            <span>{t}</span>
          </button>
        ))}
      </div>

      <div className={styles.footer}>
        <span className={styles.statusDot} />
        Backend connected
      </div>
    </aside>
  )
}
