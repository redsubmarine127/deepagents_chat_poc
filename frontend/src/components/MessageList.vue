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
      <div class="message-content">{{ message.content }}</div>
    </article>
  </div>
</template>

<script setup>
defineProps({
  messages: { type: Array, required: true }
})
</script>
