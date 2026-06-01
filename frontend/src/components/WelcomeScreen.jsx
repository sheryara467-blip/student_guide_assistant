import styles from './WelcomeScreen.module.css'

const SUGGESTIONS = [
  { icon: '📋', text: 'What is the attendance policy?' },
  { icon: '💰', text: 'How does financial aid work?' },
  { icon: '🎓', text: 'What are the graduation requirements?' },
  { icon: '📅', text: 'What is the academic calendar?' },
]

export default function WelcomeScreen({ onSuggestion }) {
  return (
    <div className={styles.welcome}>
      <div className={styles.icon}>🎓</div>
      <h2>How can I help you today?</h2>
      <p>
        Ask me about attendance policies, financial aid, graduation requirements,
        campus resources, and much more. I'll find the most relevant answers
        from the official student guide.
      </p>

      <div className={styles.grid}>
        {SUGGESTIONS.map(({ icon, text }) => (
          <button
            key={text}
            className={styles.suggestionBtn}
            onClick={() => onSuggestion(text)}
          >
            <span className={styles.suggestionIcon}>{icon}</span>
            {text}
          </button>
        ))}
      </div>
    </div>
  )
}