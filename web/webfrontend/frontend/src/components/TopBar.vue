<template>
  <div class="top-bar">
    <div class="top-bar-inner">
      <div class="logo">结构化文档撰写系统</div>
      <el-menu
        mode="horizontal"
        router
        :default-active="activeMenu"
        background-color="transparent"
        text-color="#fff"
        active-text-color="#01783a"
        class="menu"
      >
        <el-menu-item index="/">首页</el-menu-item>
        <el-menu-item index="/format">格式设定</el-menu-item>
        <el-menu-item index="/outline">大纲编辑</el-menu-item>
        <el-menu-item index="/content">正文生成</el-menu-item>
        <el-menu-item index="/knowledge">知识库设置</el-menu-item>
        <el-menu-item index="/svgdraw">自动画图</el-menu-item>
      </el-menu>
      <!-- 右侧头像 dropdown -->
      <el-dropdown
        class="user-dropdown"
        trigger="click"
        @command="handleUserMenu"
      >
        <span class="user-trigger">
          <div style="display: flex; align-items: center">
            <el-avatar :size="28" icon="UserFilled" />
            <div style="margin-left: 5px">{{username }}</div>
            <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
          </div>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <!-- <el-dropdown-item command="settings">设置</el-dropdown-item> -->
            <el-dropdown-item divided command="logout"
              >退出登录</el-dropdown-item
            >
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from "vue-router";
import { computed } from "vue";
import { ArrowDown, UserFilled } from "@element-plus/icons-vue";
import { API } from "@/api";
import { ref, onMounted } from "vue";
const router = useRouter();
const route = useRoute();
const username=ref<any>('')
const activeMenu = computed(() => route.path);
onMounted(async () => {
  username.value=localStorage.getItem('username')
})
const handleUserMenu = async (command: string) => {
  if (command === "logout") {
    // 可在此清除 token、跳转登录页等】
    const res = await fetch(API.BASE_URL + "/users/logout/", {
      method: "GET",
      headers: { "Content-Type": "application/json",'Authorization':'Token '+localStorage.getItem('token') },
    });
    const result = await res.json();
    if (result.success) {
      localStorage.clear();
      router.push("/login");
    }
  } else if (command === "settings") {
    console.log("进入设置页面");
  }
};
</script>

<style scoped>
.top-bar {
  position: sticky;
  top: 0;
  z-index: 999;
  width: 100%;
  background-color: #6ca0dc;
  box-shadow: 0 2px 4px #6ca0dc;
}

.top-bar-inner {
  max-width: 1280px;
  margin: 0 auto;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.logo {
  font-size: 18px;
  font-weight: bold;
  color: white;
  white-space: nowrap;
}

.menu {
  flex: 1;
  justify-content: center;
  display: flex;
}

.dropdown-icon {
  font-size: 14px;
  margin-left: 12px; /* 控制箭头与头像的水平间距 */
  margin-top: 2px; /* 微调箭头垂直位置 */
}

:deep(.el-menu-item.is-active) {
  color: #fff !important;
  border-bottom: 2px solid #4e82bd !important;
  background-color: transparent !important;
}

:deep(.el-menu-item:hover) {
  background-color: rgba(0, 100, 0, 0.1);
}
</style>
