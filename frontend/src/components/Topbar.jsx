import styles from './Topbar.module.css'

export default function Topbar({ onMenuClick }) {
  return (
    <header className={styles.topbar}>
      <div>
        <div className={styles.title}>Student Guide Assistant</div>
        <div className={styles.meta}>Ask anything about university policies &amp; procedures</div>
      </div>
      <button
        className={styles.menuBtn}
        onClick={onMenuClick}
        aria-label="Open topics"
      >
        ☰
      </button>
    </header>
  )
}