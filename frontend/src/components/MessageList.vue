<template>
  <div class="messages">
    <div v-if="messages.length === 0" class="empty-state">开始一段对话</div>
    <article
      v-for="message in messages"
      :key="message.id"
      class="message"
      :class="[`message-${message.role}`, { failed: message.status === 'failed' }]"
    >
      <div class="message-role">{{ message.role === 'user' ? 'You' : 'Assistant' }}</div>
      <details v-if="message.reasoning?.length" class="reasoning-panel" open>
        <summary>思考过程</summary>
        <ol>
          <li v-for="(item, index) in message.reasoning" :key="index">{{ item }}</li>
        </ol>
      </details>
      <div v-if="message.approvals?.length" class="approval-panel">
        <strong>需要人工确认</strong>
        <span v-for="approval in message.approvals" :key="approval.approvalId">{{ approval.content }}</span>
      </div>
      <div class="message-content">{{ message.content }}</div>
    </article>
  </div>
</template>

<script setup>
defineProps({
  messages: { type: Array, required: true }
})
</script>
