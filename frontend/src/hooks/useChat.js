import { useState, useCallback } from 'react'
import { sendQuestion } from '../services/api'

/**
 * useChat
 * Manages the full conversation state: messages list + loading/error state.
 *
 * Each message has the shape:
 *   { id, role: 'user'|'assistant', text, sources, modelUsed, isError }
 */
export function useChat() {
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)

  const addMessage = useCallback((msg) => {
    setMessages((prev) => [...prev, { id: Date.now() + Math.random(), ...msg }])
  }, [])

  const submit = useCallback(
    async (question) => {
      if (!question.trim() || isLoading) return

      // 1. Append user message immediately
      addMessage({ role: 'user', text: question })
      setIsLoading(true)

      try {
        // 2. Call POST /chat
        const data = await sendQuestion(question)

        // 3. Append assistant answer
        addMessage({
          role: 'assistant',
          text: data.answer ?? 'No answer returned.',
          sources: data.retrieved_context ?? [],
          modelUsed: data.model_used ?? null,
          isError: false,
        })
      } catch (err) {
        // 4. Append error as assistant message
        addMessage({
          role: 'assistant',
          text: err.message ?? 'An unknown error occurred.',
          isError: true,
        })
      } finally {
        setIsLoading(false)
      }
    },
    [isLoading, addMessage],
  )

  return { messages, isLoading, submit }
}