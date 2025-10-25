<template>
  <div class="secret-input">
    <el-input
      :model-value="modelValue"
      :type="showSecret ? 'text' : 'password'"
      :placeholder="placeholder"
      :disabled="disabled"
      :autocomplete="autocomplete"
      @update:model-value="$emit('update:modelValue', $event)"
      @blur="$emit('blur')"
      @focus="$emit('focus')"
    >
      <template #suffix>
        <div class="secret-input-actions">
          <el-icon
            v-if="modelValue"
            class="action-icon"
            :title="showSecret ? '隐藏' : '显示'"
            @click="toggleShow"
          >
            <View v-if="!showSecret" />
            <Hide v-else />
          </el-icon>
        </div>
      </template>
    </el-input>
    <div v-if="hint" class="secret-hint">
      <el-icon class="hint-icon"><InfoFilled /></el-icon>
      <span class="hint-text">
        <template v-if="hint.startsWith('已保存：')">
          <span class="hint-prefix">已保存：</span>
          <span class="hint-mask">{{ hint.slice(4) }}</span>
        </template>
        <template v-else>
          {{ hint }}
        </template>
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { View, Hide, InfoFilled } from '@element-plus/icons-vue'

interface Props {
  modelValue: string
  placeholder?: string
  disabled?: boolean
  autocomplete?: 'on' | 'off' | 'new-password' | 'current-password'
  hint?: string
}

interface Emits {
  (e: 'update:modelValue', value: string): void
  (e: 'blur'): void
  (e: 'focus'): void
}

withDefaults(defineProps<Props>(), {
  placeholder: '',
  disabled: false,
  autocomplete: 'new-password',
  hint: '',
})

defineEmits<Emits>()

const showSecret = ref(false)

const toggleShow = () => {
  showSecret.value = !showSecret.value
}
</script>

<style lang="scss" scoped>
.secret-input {
  width: 100%;

  .secret-input-actions {
    display: flex;
    align-items: center;
    gap: 8px;

    .action-icon {
      cursor: pointer;
      font-size: 16px;
      color: var(--el-text-color-secondary);
      transition: color 0.3s;

      &:hover {
        color: var(--el-color-primary);
      }
    }
  }

  .secret-hint {
    display: flex;
    align-items: flex-start;
    gap: 6px;
    margin-top: 6px;
    padding: 8px 12px;
    background-color: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    font-size: 12px;
    line-height: 1.5;

    .hint-icon {
      flex-shrink: 0;
      margin-top: 2px;
      font-size: 14px;
      color: #64748b;
    }

    .hint-text { color: #475569; }
    .hint-prefix { color: #64748b; }
    .hint-mask {
      color: var(--el-color-primary);
      opacity: 0.85;
    }
  }
}
</style>

<style lang="scss">
// 深色模式优化（非 scoped，使其生效）
.dark .secret-hint {
  background-color: rgba(30, 41, 59, 0.5) !important;
  border-color: rgba(51, 65, 85, 0.6) !important;
  
  .hint-icon {
    color: #94a3b8 !important;
  }
  
  .hint-text { color: #cbd5e1 !important; }
  .hint-prefix { color: #94a3b8 !important; }
  .hint-mask { color: var(--el-color-primary) !important; opacity: 0.9; }
}
</style>

