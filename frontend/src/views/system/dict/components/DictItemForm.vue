<template>
  <el-dialog
    v-model="dialogVisible"
    :title="isEdit ? '编辑字典项' : '新增字典项'"
    width="700px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="120px"
    >
      <el-form-item label="字典类型" prop="dict_type_code">
        <el-input
          v-model="formData.dict_type_code"
          disabled
          placeholder="自动填充"
        />
      </el-form-item>

      <el-form-item label="项编码" prop="code">
        <el-input
          v-model="formData.code"
          placeholder="英文/数字/下划线/中划线，如 zh-CN"
          :disabled="isEdit"
          maxlength="50"
          show-word-limit
        />
        <template #extra>
          <div class="form-tip">唯一标识，创建后不可修改</div>
        </template>
      </el-form-item>

      <el-form-item label="显示名称" prop="name">
        <el-input
          v-model="formData.name"
          placeholder="如：简体中文"
          maxlength="100"
          show-word-limit
        />
      </el-form-item>

      <el-form-item label="实际值" prop="value">
        <el-input
          v-model="formData.value"
          placeholder="如：zh-CN"
          maxlength="200"
          show-word-limit
        />
      </el-form-item>

      <el-form-item label="排序" prop="sort_order">
        <el-input-number
          v-model="formData.sort_order"
          :min="0"
          :max="9999"
          :step="1"
          controls-position="right"
        />
        <template #extra>
          <div class="form-tip">数值越小越靠前</div>
        </template>
      </el-form-item>

      <el-form-item label="备注说明" prop="remark">
        <el-input
          v-model="formData.remark"
          type="textarea"
          :rows="2"
          placeholder="记录该选项的使用场景、注意事项等"
          maxlength="500"
          show-word-limit
        />
      </el-form-item>

      <el-form-item label="是否启用" prop="is_active">
        <el-switch v-model="formData.is_active" />
        <template #extra>
          <div class="form-tip">禁用后前端不返回该选项</div>
        </template>
      </el-form-item>

      <el-form-item label="扩展数据" prop="extra_data">
        <el-input
          v-model="extraDataText"
          type="textarea"
          :rows="4"
          placeholder='JSON 格式，如: { "icon": "🇨🇳" }'
          @blur="validateExtraData"
        />
        <template #extra>
          <div class="form-tip">可选，需为合法的 JSON 格式</div>
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
import { createDictItem, updateDictItem } from '@/api/dict'
import type { DictItem, DictItemCreate, DictItemUpdate } from '@/api/types'

// Props
const props = defineProps<{
  visible: boolean
  typeCode?: string
  itemData?: DictItem | null
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

const isEdit = computed(() => !!props.itemData)

// State
const formRef = ref<FormInstance>()
const submitting = ref(false)
const extraDataText = ref('')

const formData = reactive<DictItemCreate & { id?: number }>({
  dict_type_code: '',
  code: '',
  name: '',
  value: '',
  sort_order: 0,
  parent_id: null,
  remark: '',
  is_active: true,
  extra_data: null,
})

// 表单校验规则
const codeValidator = (_rule: any, value: string, callback: any) => {
  if (!value) {
    callback(new Error('请输入项编码'))
  } else if (!/^[a-zA-Z0-9_-]+$/.test(value)) {
    callback(new Error('编码只能包含英文、数字、下划线、中划线'))
  } else if (value.length < 1 || value.length > 50) {
    callback(new Error('编码长度为 1-50 个字符'))
  } else {
    callback()
  }
}

const extraDataValidator = (_rule: any, _value: any, callback: any) => {
  if (!extraDataText.value.trim()) {
    callback()
    return
  }

  try {
    JSON.parse(extraDataText.value)
    callback()
  } catch {
    callback(new Error('扩展数据必须是合法的 JSON 格式'))
  }
}

const formRules: FormRules = {
  dict_type_code: [
    { required: true, message: '字典类型不能为空', trigger: 'blur' },
  ],
  code: [{ required: true, validator: codeValidator, trigger: 'blur' }],
  name: [
    { required: true, message: '请输入显示名称', trigger: 'blur' },
    { min: 1, max: 100, message: '名称长度为 1-100 个字符', trigger: 'blur' },
  ],
  value: [
    { required: true, message: '请输入实际值', trigger: 'blur' },
    { min: 1, max: 200, message: '值长度为 1-200 个字符', trigger: 'blur' },
  ],
  sort_order: [
    { type: 'number', min: 0, max: 9999, message: '排序范围为 0-9999', trigger: 'blur' },
  ],
  remark: [
    { max: 500, message: '备注长度不能超过 500 个字符', trigger: 'blur' },
  ],
  extra_data: [{ validator: extraDataValidator, trigger: 'blur' }],
}

// Methods
const resetForm = () => {
  formData.dict_type_code = props.typeCode || ''
  formData.code = ''
  formData.name = ''
  formData.value = ''
  formData.sort_order = 0
  formData.parent_id = null
  formData.remark = ''
  formData.is_active = true
  formData.extra_data = null
  extraDataText.value = ''
  formRef.value?.clearValidate()
}

const loadFormData = () => {
  if (props.itemData) {
    formData.id = props.itemData.id
    formData.dict_type_code = props.itemData.dict_type_code
    formData.code = props.itemData.code
    formData.name = props.itemData.name
    formData.value = props.itemData.value
    formData.sort_order = props.itemData.sort_order
    formData.parent_id = props.itemData.parent_id
    formData.remark = props.itemData.remark || ''
    formData.is_active = props.itemData.is_active
    
    // 格式化 extra_data
    if (props.itemData.extra_data) {
      extraDataText.value = JSON.stringify(props.itemData.extra_data, null, 2)
      formData.extra_data = props.itemData.extra_data
    } else {
      extraDataText.value = ''
      formData.extra_data = null
    }
  } else {
    resetForm()
  }
}

const validateExtraData = () => {
  if (!extraDataText.value.trim()) {
    formData.extra_data = null
    return
  }

  try {
    formData.extra_data = JSON.parse(extraDataText.value)
  } catch {
    // 校验会在提交时处理
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    const valid = await formRef.value.validate()
    if (!valid) return

    // 最后一次尝试解析 extra_data
    validateExtraData()

    submitting.value = true

    if (isEdit.value && formData.id) {
      // 编辑
      const updateData: DictItemUpdate = {
        name: formData.name,
        value: formData.value,
        sort_order: formData.sort_order,
        parent_id: formData.parent_id,
        remark: formData.remark || null,
        is_active: formData.is_active,
        extra_data: formData.extra_data,
      }
      await updateDictItem(formData.id, updateData)
      ElMessage.success('更新成功')
    } else {
      // 新增
      const createData: DictItemCreate = {
        dict_type_code: formData.dict_type_code,
        code: formData.code,
        name: formData.name,
        value: formData.value,
        sort_order: formData.sort_order,
        parent_id: formData.parent_id,
        remark: formData.remark || null,
        is_active: formData.is_active,
        extra_data: formData.extra_data,
      }
      await createDictItem(createData)
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

