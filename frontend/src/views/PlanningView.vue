<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { createTripPlan } from '@/services/api'
import { usePlanStore } from '@/composables/usePlanStore'
import type { BudgetLevel, AccommodationType } from '@/types'

const router = useRouter()
const { setPlan } = usePlanStore()
const loading = ref(false)

const form = reactive({
  destination: '',
  dateRange: null as [string, string] | null,
  preferences: [] as string[],
  budget_level: 'moderate' as BudgetLevel,
  accommodation_type: 'hotel' as AccommodationType,
})

const budgetOptions: { value: BudgetLevel; label: string }[] = [
  { value: 'budget', label: '经济' },
  { value: 'moderate', label: '中等' },
  { value: 'luxury', label: '豪华' },
]

const accommodationOptions: { value: AccommodationType; label: string }[] = [
  { value: 'hotel', label: '酒店' },
  { value: 'hostel', label: '青旅' },
  { value: 'apartment', label: '公寓' },
  { value: 'resort', label: '度假村' },
  { value: 'any', label: '不限' },
]

async function handleSubmit() {
  if (!form.destination.trim()) {
    message.warning('请输入目的地')
    return
  }
  if (!form.dateRange || !form.dateRange[0] || !form.dateRange[1]) {
    message.warning('请选择出行日期')
    return
  }
  if (form.preferences.length === 0) {
    message.warning('请至少输入一个偏好')
    return
  }

  loading.value = true
  try {
    const plan = await createTripPlan({
      destination: form.destination.trim(),
      start_date: form.dateRange[0],
      end_date: form.dateRange[1],
      preferences: form.preferences,
      budget_level: form.budget_level,
      accommodation_type: form.accommodation_type,
    })
    setPlan(plan)
    router.push({ name: 'result' })
  } catch {
    message.error('行程规划失败，请稍后重试')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <a-card title="智能旅行助手" style="max-width: 600px; margin: 0 auto">
    <a-form layout="vertical" @submit.prevent="handleSubmit">
      <a-form-item label="目的地" required>
        <a-input v-model:value="form.destination" placeholder="请输入目的地" />
      </a-form-item>

      <a-form-item label="出行日期" required>
        <a-range-picker
          v-model:value="form.dateRange"
          style="width: 100%"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
        />
      </a-form-item>

      <a-form-item label="旅行偏好" required>
        <a-select
          v-model:value="form.preferences"
          mode="tags"
          placeholder="输入偏好后按回车添加"
          :token-separators="[',']"
        />
      </a-form-item>

      <a-form-item label="预算等级">
        <a-select v-model:value="form.budget_level">
          <a-select-option v-for="opt in budgetOptions" :key="opt.value" :value="opt.value">
            {{ opt.label }}
          </a-select-option>
        </a-select>
      </a-form-item>

      <a-form-item label="住宿类型">
        <a-select v-model:value="form.accommodation_type">
          <a-select-option v-for="opt in accommodationOptions" :key="opt.value" :value="opt.value">
            {{ opt.label }}
          </a-select-option>
        </a-select>
      </a-form-item>

      <a-form-item>
        <a-button type="primary" html-type="submit" :loading="loading" block>
          生成行程
        </a-button>
      </a-form-item>
    </a-form>
  </a-card>
</template>
