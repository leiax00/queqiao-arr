<template>
  <el-card class="config-form-card macaron-card">
    <template #header>
      <div class="card-header">
        <div class="header-content">
          <h3 class="card-title">{{ title }}</h3>
          <p v-if="subtitle" class="card-subtitle">{{ subtitle }}</p>
        </div>
        <div v-if="$slots.actions" class="header-actions">
          <slot name="actions" />
        </div>
      </div>
    </template>

    <div class="card-body">
      <slot />
    </div>

    <template v-if="$slots.footer" #footer>
      <div class="card-footer">
        <slot name="footer" />
      </div>
    </template>
  </el-card>
</template>

<script setup lang="ts">
interface Props {
  title: string
  subtitle?: string
}

withDefaults(defineProps<Props>(), {
  subtitle: '',
})
</script>

<style lang="scss" scoped>
.config-form-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 16px;

    .header-content {
      flex: 1;

      .card-title {
        @apply text-lg font-semibold text-gray-900 dark:text-white mb-1;
      }

      .card-subtitle {
        @apply text-sm text-gray-600 dark:text-gray-400 m-0;
      }
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: 8px;
    }
  }

  .card-body {
    padding: 0;
  }

  .card-footer {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    gap: 12px;
    padding-top: 16px;
  }
}

:deep(.el-card__header) {
  padding: 20px;
}

:deep(.el-card__body) {
  padding: 24px 20px;
}

:deep(.el-card__footer) {
  padding: 0 20px 20px;
}
</style>

