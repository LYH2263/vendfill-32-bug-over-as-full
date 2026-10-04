<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api } from '../api'
const lanes = ref<any[]>([])
onMounted(async () => {
  // 名单口径以后端 /refills/full 为唯一来源：只收 status === 'full'，
  // 绝不在前端再把所有“补量为 0”的行（含超占）并进来。
  const body = await api('/refills/full?location_id=1')
  lanes.value = body.lanes || []
})
</script>
<template>
  <h1>满仓</h1>
  <p class="sub">库存＋在途恰好等于容量的货道（只列满仓；超占不在此页）</p>
  <div class="card">
    <table>
      <thead><tr><th>货道</th><th>商品</th><th>库存</th><th>在途</th><th>容量</th></tr></thead>
      <tbody>
        <tr v-for="l in lanes" :key="l.lane_id">
          <td>{{ l.slot_no }}</td><td>{{ l.sku_name }}</td><td>{{ l.stock }}</td><td>{{ l.in_transit }}</td><td>{{ l.capacity }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
