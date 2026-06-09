<template>
  <main class="chat-shell">
    <header class="topbar">
      <div>
        <h1>DeepAgents Chat</h1>
        <p>Lightweight streaming conversation</p>
      </div>
      <div class="topbar-actions">
        <div class="skills-menu">
          <button type="button" class="skills-button" title="Loaded skills" @click="showSkills = !showSkills">
            Skills: {{ skills.length }}
          </button>
          <div v-if="showSkills" class="skills-popover">
            <div v-if="skills.length === 0" class="skill-empty">No skills loaded</div>
            <div v-for="skill in skills" :key="skill.id" class="skill-item">
              <strong>{{ skill.name }}</strong>
              <span>{{ skill.description || skill.path }}</span>
            </div>
          </div>
        </div>
        <div class="skills-menu">
          <button type="button" class="skills-button" title="Loaded tools" @click="showTools = !showTools">
            Tools: {{ tools.length }}
          </button>
          <div v-if="showTools" class="skills-popover">
            <div v-if="tools.length === 0" class="skill-empty">No tools loaded</div>
            <div v-for="tool in tools" :key="tool.id" class="skill-item">
              <strong>{{ tool.name }}</strong>
              <span>{{ tool.description || tool.path }}</span>
            </div>
          </div>
        </div>
        <button type="button" class="icon-button" title="New conversation" @click="startConversation">+</button>
      </div>
    </header>

    <MessageList :messages="messages" :empty-text="emptyText" />
    <MessageInput :disabled="isInitializing || isStreaming" @send="send" />
  </main>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { listSkills, listTools, streamMessage } from '../api/chat'
import MessageInput from './MessageInput.vue'
import MessageList from './MessageList.vue'

const conversationId = ref('')
const messages = ref([])
const isInitializing = ref(true)
const isStreaming = ref(false)
const initError = ref('')
const skills = ref([])
const tools = ref([])
const showSkills = ref(false)
const showTools = ref(false)
const emptyText = computed(() => {
  if (initError.value) return initError.value
  if (isInitializing.value) return '正在准备对话...'
  return '开始一段对话'
})

async function startConversation() {
  isInitializing.value = true
  initError.value = ''
  conversationId.value = crypto.randomUUID()
  messages.value = []
  isInitializing.value = false
}

async function loadSkills() {
  try {
    skills.value = await listSkills()
  } catch {
    skills.value = []
  }
}

async function loadTools() {
  try {
    tools.value = await listTools()
  } catch {
    tools.value = []
  }
}

async function send(content) {
  if (isStreaming.value) return

  if (!conversationId.value) conversationId.value = crypto.randomUUID()
  const userMessageId = crypto.randomUUID()
  messages.value.push({
    id: userMessageId,
    conversationId: conversationId.value,
    role: 'user',
    content,
    status: 'completed'
  })
  isStreaming.value = true

  try {
    await streamMessage(conversationId.value, content, userMessageId, handleStreamEvent)
  } catch (error) {
    messages.value.push({
      id: crypto.randomUUID(),
      conversationId: conversationId.value,
      role: 'assistant',
      content: error.message,
      status: 'failed',
      reasoning: []
    })
  } finally {
    isStreaming.value = false
  }
}

async function handleStreamEvent(event) {
  if (event.sessionId) {
    conversationId.value = event.sessionId
    messages.value = messages.value.map((message) => {
      if (message.conversationId) return message
      return { ...message, conversationId: event.sessionId }
    })
  }

  const isChatApiEvent = Boolean(event.sessionId && event.messageId)
  const assistantMessageId = event.assistantMessageId || (isChatApiEvent ? assistantUiId(event.messageId) : event.messageId)
  if (!assistantMessageId) return

  let assistant = messages.value.find((message) => message.id === assistantMessageId)
  if (!assistant && (isChatApiEvent || event.type === 'started')) {
    messages.value.push({
      id: assistantMessageId,
      conversationId: event.sessionId || conversationId.value,
      role: 'assistant',
      content: '',
      status: 'streaming',
      reasoning: []
    })
    assistant = messages.value.find((message) => message.id === assistantMessageId)
  }
  if (!assistant) return

  if (event.error) {
    assistant.content = event.error
    assistant.status = 'failed'
    return
  }

  if (isChatApiEvent) {
    if (event.state === 'THINKING') {
      assistant.status = 'streaming'
    }

    if (event.state === 'GENERATE') {
      assistant.status = 'streaming'
    }

    if (event.content) {
      const reasoning = unwrapThink(event.content)
      if (!assistant.reasoning) assistant.reasoning = []
      if (reasoning !== event.content) {
        if (reasoning) assistant.reasoning.push(reasoning)
      } else if (event.endFlag === true) {
        assistant.content = event.content
      } else {
        assistant.content += event.content
      }
    }

    if (event.endFlag === true) assistant.status = 'completed'
    return
  }

  if (event.type === 'reasoning') {
    if (!assistant.reasoning) assistant.reasoning = []
    assistant.reasoning.push(event.content)
  }
  if (event.type === 'delta') assistant.content += event.content
  if (event.type === 'completed') {
    assistant.content = event.content || assistant.content
    assistant.status = 'completed'
  }
  if (event.type === 'failed') {
    assistant.content = event.content
    assistant.status = 'failed'
  }
}

function unwrapThink(content) {
  if (!content) return ''
  return content.replace(/^<think>/, '').replace(/<\/think>$/, '')
}

function assistantUiId(messageId) {
  return messageId ? `assistant:${messageId}` : ''
}

onMounted(async () => {
  await startConversation()
  await Promise.all([loadSkills(), loadTools()])
})
</script>
