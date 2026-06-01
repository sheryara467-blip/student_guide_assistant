import { useState } from 'react'
import Sidebar from './components/Sidebar.jsx'
import Topbar from './components/Topbar.jsx'
import WelcomeScreen from './components/WelcomeScreen.jsx'
import ChatMessage, { LoadingBubble } from './components/ChatMessage.jsx'
import { useChat } from './hooks/useChat.js'

export default function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [input, setInput] = useState('')
  const { messages, isLoading, submit } = useChat()

  const send = async (value = input) => {
    const question = value.trim()
    if (!question || isLoading) return
    setInput('')
    setSidebarOpen(false)
    await submit(question)
  }

  const handleSubmit = (event) => {
    event.preventDefault()
    send()
  }

  return (
    <div className="appShell">
      <Sidebar
        isOpen={sidebarOpen}
        onTopicClick={(topic) => send(`Tell me about ${topic}`)}
      />

      {sidebarOpen && (
        <button
          className="sidebarBackdrop"
          aria-label="Close topics"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <main className="mainPanel">
        <Topbar onMenuClick={() => setSidebarOpen((open) => !open)} />

        <section className="chatArea">
          {messages.length === 0 ? (
            <WelcomeScreen onSuggestion={send} />
          ) : (
            <div className="messageList">
              {messages.map((message) => (
                <ChatMessage key={message.id} {...message} />
              ))}
              {isLoading && <LoadingBubble />}
            </div>
          )}
        </section>

        <form className="composer" onSubmit={handleSubmit}>
          <input
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="Ask a question about the student guide..."
            disabled={isLoading}
          />
          <button type="submit" disabled={isLoading || !input.trim()}>
            Send
          </button>
        </form>
      </main>
    </div>
  )
}
