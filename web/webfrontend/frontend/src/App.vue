<template>
  <div class="app-container">
    <TopBar v-if="showTopBar" />
    <div class="page-container">
      <router-view :key="$route.fullPath" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import TopBar from '@/components/TopBar.vue'

const route = useRoute()
const router = useRouter()
const showTopBar = ref(false)

// 检查 token 和角色权限
const checkAuthAndRole = () => {
  const token = localStorage.getItem('token')
  const role = localStorage.getItem('role')
  const currentPath = route.path

  // 检查 token
  if (!token && currentPath !== '/login') {
    ElMessage.warning('登录失效，请先登录')
    router.push('/login')
    return
  }

  // 检查角色权限
  if (token && role === '管理员' && currentPath !== '/userList') {
    router.push('/userList')
    return
  }

  // 如果有 token 且在登录页，跳转到首页
  if (token && currentPath === '/login') {
    if (role === '管理员') {
      router.push('/userList')
    } else {
      router.push('/')
    }
    return
  }
}

// 监听路由变化
watch(
  () => route.path,
  (newPath) => {
    showTopBar.value =( newPath !== '/login'&&newPath !== '/userList')
    checkAuthAndRole()
  }
)

// 页面加载时检查
onMounted(() => {
  showTopBar.value = ( route.path !== '/login'&&route.path !== '/userList')
  checkAuthAndRole()
})

// 监听 localStorage 变化（可选，用于响应其他页面的登出操作）
window.addEventListener('storage', (e) => {
  if (e.key === 'token' && !e.newValue) {
    router.push('/login')
  }
})
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
}
.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.page-container {
  flex: 1;
  overflow: auto;
}
</style>