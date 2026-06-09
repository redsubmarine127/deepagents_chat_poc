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
        <div class="skills-menu">
          <button type="button" class="skills-button" title="Human approvals" @click="toggleApprovals">
            Approvals: {{ pendingApprovals.length }}
          </button>
          <div v-if="showApprovals" class="skills-popover">
            <div v-if="approvals.length === 0" class="skill-empty">No approval requests</div>
            <div v-for="approval in approvals" :key="approval.id" class="approval-item">
              <strong>{{ approval.toolName }}</strong>
              <span>{{ approval.description }}</span>
              <small>{{ approval.status }}</small>
              <div v-if="approval.status === 'pending'" class="approval-actions">
                <button type="button" @click="decideApproval(approval.id, 'approve')">Approve</button>
                <button type="button" @click="decideApproval(approval.id, 'reject')">Reject</button>
              </div>
            </div>
          </div>
        </div>
        <button type="button" class="icon-button" title="New conversation" @click="startConversation">+</button>
      </div>
    </header>

    <MessageList :messages="messages" :empty-text="emptyText" />
    <MessageInput :disabled="isInitializing || isStreaming || !conversationId" @send="send" />
  </main>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import {
  approveRequest,
  createConversation,
  listApprovals,
  listMessages,
  listSkills,
  listTools,
  rejectRequest,
  streamApprovalDecision,
  streamMessage
} from '../api/chat'
import MessageInput from './MessageInput.vue'
import MessageList from './MessageList.vue'

const conversationId = ref('')
const messages = ref([])
const isInitializing = ref(true)
const isStreaming = ref(false)
const initError = ref('')
const skills = ref([])
const tools = ref([])
const approvals = ref([])
const showSkills = ref(false)
const showTools = ref(false)
const showApprovals = ref(false)
const pendingApprovals = computed(() => approvals.value.filter((approval) => approval.status === 'pending'))
const emptyText = computed(() => {
  if (initError.value) return initError.value
  if (isInitializing.value) return '正在创建对话...'
  return '开始一段对话'
})

async function startConversation() {
  isInitializing.value = true
  initError.value = ''
  try {
    const conversation = await createConversation()
    conversationId.value = conversation.id
    messages.value = await listMessages(conversation.id)
  } catch {
    conversationId.value = ''
    messages.value = []
    initError.value = '对话初始化失败，请检查后端服务后点击 + 重试'
  } finally {
    isInitializing.value = false
  }
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

async function loadApprovals() {
  try {
    approvals.value = await listApprovals()
  } catch {
    approvals.value = []
  }
}

async function toggleApprovals() {
  showApprovals.value = !showApprovals.value
  if (showApprovals.value) await loadApprovals()
}

async function decideApproval(approvalId, decision) {
  if (isStreaming.value) return

  isStreaming.value = true
  try {
    await streamApprovalDecision(approvalId, decision, handleStreamEvent)
  } catch {
    if (decision === 'approve') await approveRequest(approvalId)
    if (decision === 'reject') await rejectRequest(approvalId)
  } finally {
    isStreaming.value = false
    await loadApprovals()
  }
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
    await streamMessage(conversationId.value, content, handleStreamEvent)
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
  if (event.type === 'started') {
    messages.value.push({
      id: event.messageId,
      conversationId: conversationId.value,
      role: 'assistant',
      content: '',
      status: 'streaming',
      reasoning: []
    })
  }

  const assistant = messages.value.find((message) => message.id === event.messageId)
  if (!assistant) return

  if (event.type === 'reasoning') {
    if (!assistant.reasoning) assistant.reasoning = []
    assistant.reasoning.push(event.content)
  }
  if (event.type === 'approval_required') {
    if (!assistant.reasoning) assistant.reasoning = []
    assistant.reasoning.push(`需要人工确认：${event.content}`)
    assistant.status = 'pending_approval'
    await loadApprovals()
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

onMounted(async () => {
  await startConversation()
  await Promise.all([loadSkills(), loadTools(), loadApprovals()])
})
</script>
