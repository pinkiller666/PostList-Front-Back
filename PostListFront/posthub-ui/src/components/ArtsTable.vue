<script setup>
import { computed } from 'vue'

const props = defineProps({
  items: { type: Array, default: () => [] }
})

const rows = computed(() => props.items)
</script>

<template>
  <el-table :data="rows" style="width: 100%" size="large" stripe>
    <el-table-column prop="id" label="ID" width="70" />
    <el-table-column prop="name" label="Название" min-width="220" />
    <el-table-column prop="status" label="Статус" width="140" />
    <el-table-column prop="price" label="Цена" width="100" />
    <el-table-column prop="post_on_bsky" label="BSky" width="90">
      <template #default="{ row }">
        <el-tag :type="row.post_on_bsky ? 'success' : 'info'">
          {{ row.post_on_bsky ? 'да' : 'нет' }}
        </el-tag>
      </template>
    </el-table-column>
    <el-table-column label="Twitter">
      <template #default="{ row }">
        <el-space>
          <el-tag :type="row.post_on_decent_twi ? 'success' : 'info'">decent</el-tag>
          <el-tag :type="row.post_on_lewd_twi ? 'danger'  : 'info'">lewd</el-tag>
        </el-space>
      </template>
    </el-table-column>
    <el-table-column prop="created_at" label="Создано" width="190" />
  </el-table>
</template>
