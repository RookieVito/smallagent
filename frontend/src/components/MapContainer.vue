<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import AMapLoader from '@amap/amap-jsapi-loader'
import type { MapPoint } from '@/types'

const props = defineProps<{ mapPoints: MapPoint[] }>()

const containerRef = ref<HTMLDivElement>()
const mapInstance = ref<any>(null)
const markers = ref<any[]>([])
const loadError = ref(false)

async function initMap() {
  const key = import.meta.env.VITE_AMAP_KEY
  if (!key) {
    loadError.value = true
    return
  }

  try {
    const AMap = await AMapLoader.load({
      key,
      version: '2.0',
    })

    mapInstance.value = new AMap.Map(containerRef.value, {
      zoom: 12,
      resizeEnable: true,
    })

    addMarkers(AMap)
  } catch {
    loadError.value = true
  }
}

function addMarkers(AMap: any) {
  clearMarkers()
  if (!mapInstance.value || !props.mapPoints.length) return

  const newMarkers = props.mapPoints.map(
    (point) =>
      new AMap.Marker({
        position: [point.longitude, point.latitude],
        title: point.name,
      }),
  )

  mapInstance.value.add(newMarkers)
  markers.value = newMarkers

  if (newMarkers.length > 0) {
    mapInstance.value.setFitView(newMarkers)
  }
}

function clearMarkers() {
  if (mapInstance.value && markers.value.length) {
    mapInstance.value.remove(markers.value)
  }
  markers.value = []
}

watch(
  () => props.mapPoints,
  () => {
    if (mapInstance.value) {
      const key = import.meta.env.VITE_AMAP_KEY
      if (key) {
        AMapLoader.load({ key, version: '2.0' }).then(addMarkers)
      }
    }
  },
  { deep: true },
)

onMounted(initMap)
onUnmounted(() => {
  clearMarkers()
  mapInstance.value?.destroy()
})
</script>

<template>
  <div v-if="loadError" style="height: 300px; background: #f5f5f5; display: flex; align-items: center; justify-content: center; color: #999">
    <div>
      <p>地图不可用</p>
      <p style="font-size: 12px">请设置 VITE_AMAP_KEY 环境变量</p>
    </div>
  </div>
  <div v-else ref="containerRef" style="height: 300px; width: 100%"></div>
</template>
