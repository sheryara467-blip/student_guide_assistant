import { useState, useEffect } from 'react'
import { fetchTopics } from '../services/api'

/**
 * useTopics
 * Fetches indexed topics from GET /topics on mount.
 */
export function useTopics() {
  const [topics, setTopics] = useState([])
  const [status, setStatus] = useState('loading') // 'loading' | 'ok' | 'error'

  useEffect(() => {
    let cancelled = false
    fetchTopics()
      .then((t) => { if (!cancelled) { setTopics(t); setStatus('ok') } })
      .catch(() => { if (!cancelled) setStatus('error') })
    return () => { cancelled = true }
  }, [])

  return { topics, status }
}