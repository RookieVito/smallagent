<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { usePlanStore } from '@/composables/usePlanStore'
import { editTripPlan } from '@/services/api'
import MapContainer from '@/components/MapContainer.vue'

const router = useRouter()
const { currentPlan, setPlan } = usePlanStore()
const plan = currentPlan
const editing = ref(false)
const lastEditError = ref<string | null>(null)

const dateRange = computed(() => {
  if (!plan.value || plan.value.days.length === 0) return ''
  const days = plan.value.days
  return `${days[0].date} ~ ${days[days.length - 1].date}`
})

const dayCount = computed(() => plan.value?.days.length ?? 0)

const forecastColumns = [
  { title: '日期', dataIndex: 'date', key: 'date' },
  { title: '天气', dataIndex: 'condition', key: 'condition' },
  { title: '最高温', dataIndex: 'high_celsius', key: 'high_celsius', customRender: ({ text }: { text: number }) => `${text}°C` },
  { title: '最低温', dataIndex: 'low_celsius', key: 'low_celsius', customRender: ({ text }: { text: number }) => `${text}°C` },
]

function goBack() {
  router.push({ name: 'planning' })
}

function dismissEditError() {
  lastEditError.value = null
}

function handleExport() {
  message.info('导出功能即将上线')
}

async function deleteAttraction(dayIndex: number, attractionIndex: number) {
  if (!plan.value || editing.value) return
  editing.value = true
  lastEditError.value = null
  try {
    const edited = await editTripPlan({
      plan: plan.value,
      operation: 'delete_attraction',
      day_index: dayIndex,
      attraction_index: attractionIndex,
    })
    setPlan(edited)
  } catch {
    lastEditError.value = '删除失败'
    message.error('删除失败')
  } finally {
    editing.value = false
  }
}

async function moveAttraction(dayIndex: number, attractionIndex: number, direction: 'up' | 'down') {
  if (!plan.value || editing.value) return
  editing.value = true
  lastEditError.value = null
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
    lastEditError.value = '移动失败'
    message.error('移动失败')
  } finally {
    editing.value = false
  }
}
</script>

<template>
  <div v-if="plan" style="min-height: 100vh">
    <a-page-header :title="plan.destination" :sub-title="`${dateRange} · ${dayCount}天`" @back="goBack">
      <template #extra>
        <a-tooltip title="导出功能即将上线">
          <a-button @click="handleExport">导出</a-button>
        </a-tooltip>
      </template>
    </a-page-header>

    <!-- Page-level editing progress indicator -->
    <a-alert
      v-if="editing"
      type="info"
      message="正在更新行程..."
      show-icon
      style="margin: 0 24px 16px"
    />

    <!-- Page-level edit failure indicator -->
    <a-alert
      v-if="lastEditError"
      type="error"
      :message="lastEditError"
      show-icon
      closable
      style="margin: 0 24px 16px"
      @close="dismissEditError"
    />

    <a-row :gutter="16" style="padding: 0 24px">
      <!-- Side navigation -->
      <a-col :span="5">
        <a-anchor :affix="false" offset-top="80">
          <a-anchor-link href="#section-overview" title="概览" />
          <a-anchor-link href="#section-budget" title="预算" />
          <a-anchor-link href="#section-map" title="地图" />
          <a-anchor-link href="#section-days" title="行程" />
          <a-anchor-link href="#section-weather" title="天气" />
        </a-anchor>
      </a-col>

      <!-- Main content -->
      <a-col :span="19">
        <!-- Overview section -->
        <div id="section-overview" style="margin-bottom: 24px">
          <a-card title="行程概览">
            <a-row :gutter="16" align="middle">
              <a-col :span="plan.cover_image_url ? 16 : 24">
                <a-descriptions :column="1" size="small">
                  <a-descriptions-item label="目的地">{{ plan.destination }}</a-descriptions-item>
                  <a-descriptions-item label="出行日期">{{ dateRange }}</a-descriptions-item>
                  <a-descriptions-item label="行程天数">{{ dayCount }} 天</a-descriptions-item>
                  <a-descriptions-item v-if="plan.created_at" label="创建时间">{{ plan.created_at }}</a-descriptions-item>
                  <a-descriptions-item v-if="plan.plan_version" label="版本">v{{ plan.plan_version }}</a-descriptions-item>
                </a-descriptions>
              </a-col>
              <a-col v-if="plan.cover_image_url" :span="8">
                <img
                  :src="plan.cover_image_url"
                  alt="封面"
                  style="width: 100%; border-radius: 8px"
                />
              </a-col>
            </a-row>
          </a-card>
        </div>

        <!-- Budget section -->
        <div id="section-budget" style="margin-bottom: 24px">
          <a-card title="预算摘要">
            <a-statistic title="预估总费用" :value="Number(plan.budget_summary.estimated_total)" prefix="¥" />
            <a-descriptions :column="1" size="small" style="margin-top: 12px">
              <a-descriptions-item label="住宿">¥{{ plan.budget_summary.breakdown.accommodation }}</a-descriptions-item>
              <a-descriptions-item label="餐饮">¥{{ plan.budget_summary.breakdown.dining }}</a-descriptions-item>
              <a-descriptions-item label="景点">¥{{ plan.budget_summary.breakdown.attractions }}</a-descriptions-item>
              <a-descriptions-item label="交通">¥{{ plan.budget_summary.breakdown.transport }}</a-descriptions-item>
            </a-descriptions>
          </a-card>
        </div>

        <!-- Map section -->
        <div id="section-map" style="margin-bottom: 24px">
          <a-card title="地图">
            <MapContainer :map-points="plan.map_points" />
          </a-card>
        </div>

        <!-- Days section -->
        <div id="section-days" style="margin-bottom: 24px">
          <a-card title="每日行程">
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
        </div>

        <!-- Weather section -->
        <div id="section-weather" style="margin-bottom: 24px">
          <a-card title="天气概况">
            <p>{{ plan.weather_summary.overview }}</p>
            <a-table
              v-if="plan.weather_summary.daily_forecasts?.length"
              :data-source="plan.weather_summary.daily_forecasts"
              :columns="forecastColumns"
              :pagination="false"
              size="small"
              style="margin-top: 12px"
              row-key="date"
            />
          </a-card>
        </div>
      </a-col>
    </a-row>
  </div>

  <div v-else style="min-height: 80vh; display: flex; align-items: center; justify-content: center">
    <a-empty description="暂无行程数据">
      <a-button type="primary" @click="goBack">返回规划</a-button>
    </a-empty>
  </div>
</template>
