const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8090'

export async function listMessages(conversationId) {
  const response = await fetch(`${API_BASE_URL}/api/conversations/${conversationId}/messages`)
  if (!response.ok) throw new Error('Unable to load messages')
  return response.json()
}

export async function listSkills() {
  const response = await fetch(`${API_BASE_URL}/api/skills`)
  if (!response.ok) throw new Error('Unable to load skills')
  return response.json()
}

export async function listTools() {
  const response = await fetch(`${API_BASE_URL}/api/tools`)
  if (!response.ok) throw new Error('Unable to load tools')
  return response.json()
}

export async function streamMessage(sessionId, content, messageId, onEvent) {
  const response = await fetch(`${API_BASE_URL}/api/conversations/messages`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      sessionId,
      streamFlag: 'stream',
      query: content,
      messageId,
      globalUserId: 'local-user',
      userAccount: 'local-account',
      payload: {}
    })
  })
  if (!response.ok || !response.body) throw new Error('Unable to start message stream')

  await readEventStream(response, onEvent)
}

async function readEventStream(response, onEvent) {
  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { value, done } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const frames = buffer.split('\n\n')
    buffer = frames.pop() || ''

    for (const frame of frames) {
      const line = frame.split('\n').find((item) => item.startsWith('data: '))
      if (line) await onEvent(JSON.parse(line.slice(6)))
    }
  }
}
