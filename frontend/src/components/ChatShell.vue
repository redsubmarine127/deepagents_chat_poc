<template>
  <main class="chat-shell">
    <header class="topbar">
      <div>
        <h1>DeepAgents Chat</h1>
        <p>Lightweight streaming conversation</p>
      </div>
      <button type="button" class="icon-button" title="New conversation" @click="startConversation">+</button>
    </header>

    <MessageList :messages="messages" />
    <MessageInput :disabled="isStreaming || !conversationId" @send="send" />
  </main>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { createConversation, listMessages, streamMessage } from '../api/chat'
import MessageInput from './MessageInput.vue'
import MessageList from './MessageList.vue'

const conversationId = ref('')
const messages = ref([])
const isStreaming = ref(false)

async function startConversation() {
  const conversation = await createConversation()
  conversationId.value = conversation.id
  messages.value = await listMessages(conversation.id)
}

async function send(content) {
  if (!conversationId.value || isStreaming.value) return

  messages.value.push({
    id: crypto.randomUUID(),
    conversationId: conversationId.value,
    role: 'user',
    content,
    status: 'completed'
  })
  isStreaming.value = true

  try {
    await streamMessage(conversationId.value, content, (event) => {
      if (event.type === 'started') {
        messages.value.push({
          id: event.messageId,
          conversationId: conversationId.value,
          role: 'assistant',
          content: '',
          status: 'streaming'
        })
      }

      const assistant = messages.value.find((message) => message.id === event.messageId)
      if (!assistant) return

      if (event.type === 'delta') assistant.content += event.content
      if (event.type === 'completed') {
        assistant.content = event.content || assistant.content
        assistant.status = 'completed'
      }
      if (event.type === 'failed') {
        assistant.content = event.content
        assistant.status = 'failed'
      }
    })
  } catch (error) {
    messages.value.push({
      id: crypto.randomUUID(),
      conversationId: conversationId.value,
      role: 'assistant',
      content: error.message,
      status: 'failed'
    })
  } finally {
    isStreaming.value = false
  }
}

onMounted(startConversation)
</script>
