<template>
   <el-form :model="form" label-width="80px">
      <el-form-item label="用户昵称">
         <el-input v-model="form.nickName" disabled />
      </el-form-item>
      <el-form-item label="手机号码">
         <el-input v-model="form.phonenumber" disabled />
      </el-form-item>
      <el-form-item label="邮箱">
         <el-input v-model="form.email" disabled />
      </el-form-item>
      <el-form-item label="性别">
         <el-radio-group v-model="form.sex" disabled>
            <el-radio value="0">男</el-radio>
            <el-radio value="1">女</el-radio>
         </el-radio-group>
      </el-form-item>
   </el-form>
</template>

<script setup>
const props = defineProps({
  user: {
    type: Object
  }
});

const form = ref({});

// 回显当前登录用户信息
watch(() => props.user, user => {
  if (user) {
    form.value = { nickName: user.nickName, phonenumber: user.phonenumber, email: user.email, sex: user.sex };
  }
},{ immediate: true });
</script>
