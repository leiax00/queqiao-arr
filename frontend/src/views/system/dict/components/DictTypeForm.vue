<template>
  <el-dialog
    v-model="dialogVisible"
    :title="isEdit ? '编辑字典类型' : '新增字典类型'"
    width="600px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="100px"
    >
      <el-form-item label="类型编码" prop="code">
        <el-input
          v-model="formData.code"
          placeholder="英文/数字/下划线，如 language"
          :disabled="isEdit"
          maxlength="50"
          show-word-limit
        />
        <template #extra>
          <div class="form-tip">唯一标识，创建后不可修改</div>
        </template>
      </el-form-item>

      <el-form-item label="类型名称" prop="name">
        <el-input
          v-model="formData.name"
          placeholder="如：语言选项"
          maxlength="100"
          show-word-limit
        />
      </el-form-item>

      <el-form-item label="备注说明" prop="remark">
        <el-input
          v-model="formData.remark"
          type="textarea"
          :rows="3"
          placeholder="记录该字典类型的用途、使用场景、注意事项等"
          maxlength="500"
          show-word-limit
        />
      </el-form-item>

      <el-form-item label="是否启用" prop="is_active">
        <el-switch v-model="formData.is_active" />
        <template #extra>
          <div class="form-tip">禁用后前端不展示相关选项</div>
        </template>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button
        type="primary"
        :loading="submitting"
        @click="handleSubmit"
      >
        确定
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { createDictType, updateDictType } from '@/api/dict'
import type { DictType, DictTypeCreate, DictTypeUpdate } from '@/api/types'

// Props
const props = defineProps<{
  visible: boolean
  typeData?: DictType | null
}>()

// Emits
const emit = defineEmits<{
  'update:visible': [value: boolean]
  success: []
}>()

// Computed
const dialogVisible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val),
})

const isEdit = computed(() => !!props.typeData)

// State
const formRef = ref<FormInstance>()
const submitting = ref(false)

const formData = reactive<DictTypeCreate & { id?: number }>({
  code: '',
  name: '',
  remark: '',
  is_active: true,
})

// 表单校验规则
const codeValidator = (_rule: any, value: string, callback: any) => {
  if (!value) {
    callback(new Error('请输入类型编码'))
  } else if (!/^[a-zA-Z0-9_]+$/.test(value)) {
    callback(new Error('编码只能包含英文、数字、下划线'))
  } else if (value.length < 2 || value.length > 50) {
    callback(new Error('编码长度为 2-50 个字符'))
  } else {
    callback()
  }
}

const formRules: FormRules = {
  code: [{ required: true, validator: codeValidator, trigger: 'blur' }],
  name: [
    { required: true, message: '请输入类型名称', trigger: 'blur' },
    { min: 2, max: 100, message: '名称长度为 2-100 个字符', trigger: 'blur' },
  ],
  remark: [
    { max: 500, message: '备注长度不能超过 500 个字符', trigger: 'blur' },
  ],
}

// Methods
const resetForm = () => {
  formData.code = ''
  formData.name = ''
  formData.remark = ''
  formData.is_active = true
  formRef.value?.clearValidate()
}

const loadFormData = () => {
  if (props.typeData) {
    formData.id = props.typeData.id
    formData.code = props.typeData.code
    formData.name = props.typeData.name
    formData.remark = props.typeData.remark || ''
    formData.is_active = props.typeData.is_active
  } else {
    resetForm()
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    const valid = await formRef.value.validate()
    if (!valid) return

    submitting.value = true

    if (isEdit.value && formData.id) {
      // 编辑
      const updateData: DictTypeUpdate = {
        name: formData.name,
        remark: formData.remark || null,
        is_active: formData.is_active,
      }
      await updateDictType(formData.id, updateData)
      ElMessage.success('更新成功')
    } else {
      // 新增
      const createData: DictTypeCreate = {
        code: formData.code,
        name: formData.name,
        remark: formData.remark || null,
        is_active: formData.is_active,
      }
      await createDictType(createData)
      ElMessage.success('创建成功')
    }

    emit('success')
    handleClose()
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  } finally {
    submitting.value = false
  }
}

const handleClose = () => {
  dialogVisible.value = false
  resetForm()
}

// Watch
watch(
  () => props.visible,
  (val) => {
    if (val) {
      loadFormData()
    }
  }
)
</script>

<style scoped lang="scss">
.form-tip {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 4px;
}

:deep(.el-form-item__extra) {
  margin-top: 0;
}
</style>

