<template>
  <div class="app-container" style="padding: 20px;">
    <el-empty description="该功能暂未配置，请联系管理员" />
  </div>
</template>

<script setup>
defineOptions({
  name: 'EmptyPage'
})
</script>

<style scoped lang="scss">
.app-container {
  min-height: calc(100vh - 84px);
  padding: 20px;
}
</style>

