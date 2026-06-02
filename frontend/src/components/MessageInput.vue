<template>
  <form class="composer" @submit.prevent="submit">
    <textarea
      v-model="draft"
      :disabled="disabled"
      rows="2"
      placeholder="输入消息..."
      @keydown.enter.exact.prevent="submit"
    />
    <button type="submit" :disabled="disabled || !draft.trim()">Send</button>
  </form>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  disabled: { type: Boolean, default: false }
})

const emit = defineEmits(['send'])
const draft = ref('')

function submit() {
  const content = draft.value.trim()
  if (!content) return
  emit('send', content)
  draft.value = ''
}
</script>
