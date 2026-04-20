<script setup lang="ts">
import type { MapPoint } from '@/types'

defineProps<{ mapPoints: MapPoint[] }>()
</script>

<template>
  <div style="height: 300px; background: #f0f0f0; display: flex; align-items: center; justify-content: center">
    地图加载中...
  </div>
</template>
