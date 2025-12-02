<template>
  <div class="user-management">
    <div class="header">
      <h1>用户管理</h1>
      <el-button type="primary" @click="logout">退出登录</el-button>
    </div>

    <!-- 用户列表表格 -->
    <el-table :data="userList" border style="width: 100%" v-loading="loading" height="600px">
      <el-table-column prop="id" label="ID" width="80" align="center" />
      <el-table-column prop="username" label="用户名" min-width="120" />
      <el-table-column prop="role" label="角色" width="100" align="center">
        <template #default="scope">
          <el-tag :type="scope.row.is_superuser ? 'danger' : 'primary'">
            {{ scope.row.is_superuser ? "管理员" : "普通用户" }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column
        prop="date_joined"
        label="创建时间"
        width="180"
        align="center"
      >
        <template #default="scope">
          {{ new Date(scope.row.date_joined).toLocaleString() }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" align="center" fixed="right">
        <template #default="scope">
          <el-button
            size="small"
            type="primary"
            link
            @click="handlePasswordSubmit(scope.row.id)"
            v-if="!scope.row.is_superuser"
          >
            重置密码
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    <!-- 修改密码对话框 -->
    <el-dialog
      v-model="passwordDialog.visible"
      :title="passwordDialog.title"
      width="500px"
      @close="handlePasswordDialogClose"
    >
      <el-form
        ref="passwordFormRef"
        :model="passwordForm"
        :rules="passwordRules"
        label-width="100px"
      >
        <el-form-item label="用户名">
          <el-input v-model="passwordDialog.userInfo.username" disabled />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input
            v-model="passwordForm.newPassword"
            type="password"
            placeholder="请输入新密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="passwordForm.confirmPassword"
            type="password"
            placeholder="请再次输入新密码"
            show-password
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="passwordDialog.visible = false">取消</el-button>
          <el-button
            type="primary"
            :loading="passwordDialog.loading"
            @click="handlePasswordSubmit"
          >
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { API } from "@/api";
import { useRoute, useRouter } from "vue-router";
import { ElNotification } from 'element-plus'
const router = useRouter();
const route = useRoute();
// 加载状态
const loading = ref(false);

// 分页配置
const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0,
});

// 用户列表数据
const userList = ref([]);

// 密码修改相关
const passwordFormRef = ref();
const passwordDialog = reactive({
  visible: false,
  loading: false,
  title: "修改密码",
  userInfo: {},
});

const passwordForm = ref({
  newPassword: "",
  confirmPassword: "",
});

// 用户添加/编辑相关
const userFormRef = ref();
const userDialog = reactive({
  visible: false,
  loading: false,
  title: "添加用户",
  mode: "add", // 'add' | 'edit'
});

const userForm = reactive({
  username: "",
  email: "",
  role: "user",
  password: "",
  status: 1,
});

// 密码验证规则
const validatePassword = (rule, value, callback) => {
  if (!value) {
    callback(new Error("请输入密码"));
  } else if (value.length < 6) {
    callback(new Error("密码长度不能少于6位"));
  } else {
    callback();
  }
};

const logout = async () => {
  const res = await fetch(API.BASE_URL + "/users/logout/", {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: "Token " + localStorage.getItem("token"),
    },
  });
  const result = await res.json();
  if (result.success) {
    localStorage.clear();
    router.push("/login");
  }
};
const validateConfirmPassword = (rule, value, callback) => {
  if (!value) {
    callback(new Error("请确认密码"));
  } else if (value !== passwordForm.value.newPassword) {
    callback(new Error("两次输入的密码不一致"));
  } else {
    callback();
  }
};

// 密码表单验证规则
const passwordRules = {
  newPassword: [
    { required: true, validator: validatePassword, trigger: "blur" },
  ],
  confirmPassword: [
    { required: true, validator: validateConfirmPassword, trigger: "blur" },
  ],
};

// 用户表单验证规则
const userRules = {
  username: [
    { required: true, message: "请输入用户名", trigger: "blur" },
    { min: 3, max: 20, message: "用户名长度为3-20个字符", trigger: "blur" },
  ],
  email: [
    { required: true, message: "请输入邮箱", trigger: "blur" },
    { type: "email", message: "请输入正确的邮箱格式", trigger: "blur" },
  ],
  role: [{ required: true, message: "请选择角色", trigger: "change" }],
  password: [{ required: true, validator: validatePassword, trigger: "blur" }],
};

// 获取用户列表
const fetchUserList = async () => {
  loading.value = true;
  const res = await fetch(API.BASE_URL + "/users/admin/dashboard/", {
    method: "GEt",
    headers: {
      "Content-Type": "application/json",
      Authorization: "Token " + localStorage.getItem("token"),
    },
  });
  const result = await res.json();
  if (result.success) {
    userList.value = result.users;
    loading.value = false;
  } else {
    ElMessage.error(result.error);
    loading.value = false;
  }
};

// 修改密码
const handleEditPassword = (user) => {
  passwordDialog.visible = true;
  passwordDialog.userInfo = { ...user };
  // 重置表单
  Object.assign(passwordForm.value, {
    newPassword: "",
    confirmPassword: "",
  });
};

// 提交密码修改
const handlePasswordSubmit = async (id) => {
  const res = await fetch(API.BASE_URL + "/users/admin/reset-password/" + id, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: "Token " + localStorage.getItem("token"),
    },
  });
  const result = await res.json();
  if (result.success) {
    ElNotification({
      title: "密码重置成功！",
      message: "新密码：" + result.new_password,
      duration: 0,
    });
    console.log(result);
  }
};

// 关闭密码对话框
const handlePasswordDialogClose = () => {
  passwordFormRef.value?.clearValidate();
};

// 初始化
onMounted(() => {
  fetchUserList();
});
</script>

<style scoped>
.user-management {
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
}

.header h1 {
  margin: 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
  padding: 20px 0;
}

:deep(.el-table) {
  margin-top: 20px;
}

:deep(.el-table .cell) {
  padding: 8px 12px;
}

:deep(.el-dialog) {
  border-radius: 8px;
}

:deep(.el-form-item) {
  margin-bottom: 20px;
}

:deep(.el-input) {
  width: 100%;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .user-management {
    padding: 10px;
  }

  .header {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }

  .header h1 {
    font-size: 20px;
  }
}
</style>