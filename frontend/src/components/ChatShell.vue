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

    <MessageList :messages="messages" />
    <MessageInput :disabled="isStreaming || !conversationId" @send="send" />
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
  streamMessage
} from '../api/chat'
import MessageInput from './MessageInput.vue'
import MessageList from './MessageList.vue'

const conversationId = ref('')
const messages = ref([])
const isStreaming = ref(false)
const skills = ref([])
const tools = ref([])
const approvals = ref([])
const showSkills = ref(false)
const showTools = ref(false)
const showApprovals = ref(false)
const pendingApprovals = computed(() => approvals.value.filter((approval) => approval.status === 'pending'))

async function startConversation() {
  const conversation = await createConversation()
  conversationId.value = conversation.id
  messages.value = await listMessages(conversation.id)
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
  if (decision === 'approve') await approveRequest(approvalId)
  if (decision === 'reject') await rejectRequest(approvalId)
  await loadApprovals()
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
    })
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

onMounted(async () => {
  await Promise.all([startConversation(), loadSkills(), loadTools(), loadApprovals()])
})
</script>
