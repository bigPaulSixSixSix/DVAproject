<template>
    <div class="app-container">
        <h1>任务配置页面</h1>
        <p>这是一个测试页面，用于验证工作台子菜单的跳转功能。</p>
        <p>当前路径：{{ $route.path }}</p>
    </div>
</template>

<script setup>
defineOptions({
  name: 'TaskConfiguration'
})
</script>

<style scoped>
.app-container {
  padding: 20px;
}

h1 {
  color: #409EFF;
  margin-bottom: 20px;
}

p {
  margin-bottom: 10px;
  color: #606266;
}
</style>