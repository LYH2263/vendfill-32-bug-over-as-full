<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api } from '../api'
const data = ref<any>(null)
async function run() { data.value = await api('/refills/run?location_id=1', { method: 'POST' }) }
onMounted(run)
</script>
<template>
  <h1>补货小票</h1>
  <p class="sub">gap = 容量 − 库存 − 在途 · 收据纸样式</p>
  <button class="btn" @click="run">生成补货单</button>
  <div style="margin-top:1rem" v-if="data">
    <div class="vf-receipt">
      <h2>*** VendFill 补货单 ***</h2>
      <div class="vf-receipt-line" style="font-weight:700;border-bottom:2px dashed #8a7e64">
        <span>货道 / 商品</span><span>补量</span>
      </div>
      <div class="vf-receipt-line" v-for="l in data.lines" :key="l.lane_id">
        <span>{{ l.slot_no }} {{ l.sku_name }}
          <small :class="`vf-line-${l.status}`">{{ l.status === 'need_fill' ? '待补' : l.status === 'full' ? '满仓' : '超占' }}</small>
        </span>
        <!-- 超占单独成句，绝不与满仓并句；满仓补量 0；待补才显示补量/缺口 -->
        <span v-if="l.status === 'overbooked'" class="vf-line-overbooked">
          超占 {{ l.stock }}＋{{ l.in_transit }} ＞ {{ l.capacity }}
        </span>
        <span v-else-if="l.status === 'full'">0（满仓）</span>
        <span v-else>{{ l.fill_qty }} / 缺{{ l.gap }}</span>
      </div>
      <p style="text-align:center;margin:1rem 0 0;font-size:0.72rem;color:#6a5e48">谢谢使用 · 请核对后装机</p>
    </div>
  </div>
</template>

<style scoped>
.vf-line-overbooked { color: var(--vf-red); font-weight: 700; }
.vf-line-full { color: var(--vf-led); }
</style>
