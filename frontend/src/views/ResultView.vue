<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { usePlanStore } from '@/composables/usePlanStore'
import { editTripPlan } from '@/services/api'
import MapContainer from '@/components/MapContainer.vue'

const router = useRouter()
const { currentPlan, setPlan } = usePlanStore()
const plan = computed(() => currentPlan.value)
const editing = ref(false)

const dateRange = computed(() => {
  if (!plan.value || plan.value.days.length === 0) return ''
  const days = plan.value.days
  return `${days[0].date} ~ ${days[days.length - 1].date}`
})

const dayCount = computed(() => plan.value?.days.length ?? 0)

function goBack() {
  router.push({ name: 'planning' })
}

async function deleteAttraction(dayIndex: number, attractionIndex: number) {
  if (!plan.value || editing.value) return
  editing.value = true
  try {
    const edited = await editTripPlan({
      plan: plan.value,
      operation: 'delete_attraction',
      day_index: dayIndex,
      attraction_index: attractionIndex,
    })
    setPlan(edited)
  } catch {
    message.error('删除失败')
  } finally {
    editing.value = false
  }
}

async function moveAttraction(dayIndex: number, attractionIndex: number, direction: 'up' | 'down') {
  if (!plan.value || editing.value) return
  editing.value = true
  try {
    const edited = await editTripPlan({
      plan: plan.value,
      operation: 'move_attraction',
      day_index: dayIndex,
      attraction_index: attractionIndex,
      direction,
    })
    setPlan(edited)
  } catch {
    message.error('移动失败')
  } finally {
    editing.value = false
  }
}
</script>

<template>
  <div v-if="plan">
    <a-page-header :title="plan.destination" :sub-title="`${dateRange} · ${dayCount}天`" @back="goBack" />

    <a-row :gutter="16">
      <a-col :span="14">
        <a-card title="每日行程" style="margin-bottom: 16px">
          <a-collapse>
            <a-collapse-panel v-for="(day, di) in plan.days" :key="di" :header="`第 ${di + 1} 天 · ${day.date}`">
              <div v-for="(attraction, ai) in day.attractions" :key="ai" style="margin-bottom: 12px">
                <a-card size="small">
                  <template #title>
                    {{ attraction.name }}
                    <span style="float: right">
                      <a-button size="small" title="上移" :disabled="ai === 0 || editing" @click="moveAttraction(di, ai, 'up')">↑</a-button>
                      <a-button size="small" title="下移" :disabled="ai === day.attractions.length - 1 || editing" @click="moveAttraction(di, ai, 'down')">↓</a-button>
                      <a-button size="small" danger title="删除" :disabled="editing" @click="deleteAttraction(di, ai)">✕</a-button>
                    </span>
                  </template>
                  <p style="margin: 0">{{ attraction.address }}</p>
                  <p style="margin: 0; color: #888">
                    建议时长 {{ attraction.suggested_duration_minutes }} 分钟
                    <span v-if="attraction.ticket_price"> · 门票 ¥{{ attraction.ticket_price }}</span>
                  </p>
                </a-card>
              </div>
              <a-divider />
              <p>🍽 餐饮建议：{{ day.dining_suggestion }}</p>
              <p>🏨 住宿：{{ day.accommodation_note }}</p>
            </a-collapse-panel>
          </a-collapse>
        </a-card>
      </a-col>

      <a-col :span="10">
        <a-card title="地图" style="margin-bottom: 16px">
          <MapContainer :map-points="plan.map_points" />
        </a-card>

        <a-card title="预算摘要" style="margin-bottom: 16px">
          <a-statistic title="预估总费用" :value="plan.budget_summary.estimated_total" :prefix="'¥'" />
          <a-descriptions v-if="Object.keys(plan.budget_summary.breakdown).length" :column="1" size="small" style="margin-top: 12px">
            <a-descriptions-item v-for="(amount, label) in plan.budget_summary.breakdown" :key="label" :label="String(label)">
              ¥{{ amount }}
            </a-descriptions-item>
          </a-descriptions>
          <p v-if="plan.budget_summary.notes" style="margin-top: 8px; color: #888">{{ plan.budget_summary.notes }}</p>
        </a-card>

        <a-card title="天气概况">
          <p>{{ plan.weather_summary.overview }}</p>
        </a-card>
      </a-col>
    </a-row>
  </div>

  <a-empty v-else description="暂无行程数据">
    <a-button type="primary" @click="goBack">返回规划</a-button>
  </a-empty>
</template>
