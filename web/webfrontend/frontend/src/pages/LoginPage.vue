<template>
  <div class="auth-container">
    <div class="auth-card">
      <!-- 标题 -->
      <h1 class="auth-title">结构化文档撰写系统</h1>

      <!-- 登录/注册/找回密码切换 -->
      <div class="auth-tabs">
        <el-radio-group
          v-model="activeTab"
          size="large"
          @change="handleTabChange"
        >
          <el-radio-button label="login">登录</el-radio-button>
          <el-radio-button label="register">注册</el-radio-button>
          <el-radio-button label="forgot">找回密码</el-radio-button>
        </el-radio-group>
      </div>

      <!-- 登录表单 -->
      <el-form
        v-if="activeTab === 'login'"
        :model="loginForm"
        :rules="loginRules"
        ref="loginFormRef"
        class="auth-form"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            size="large"
            :prefix-icon="User"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>

        <el-button
          type="primary"
          size="large"
          class="auth-button"
          @click="handleLogin"
          :loading="loading"
        >
          登录
        </el-button>
      </el-form>

      <!-- 注册表单 -->
      <el-form
        v-else-if="activeTab === 'register'"
        :model="registerForm"
        :rules="registerRules"
        ref="registerFormRef"
        class="auth-form"
      >
        <el-form-item prop="username">
          <el-input
            v-model="registerForm.username"
            placeholder="请输入用户名"
            size="large"
            :prefix-icon="User"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="请输入密码（不少于8位数字+英文混合）"
            size="large"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>

        <el-form-item prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="请确认密码"
            size="large"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>

        <!-- 密码提示区域 -->
        <div class="password-hint-section">
          <h3 class="hint-title">密码提示设置</h3>
          <el-form-item prop="question">
            <el-input
              v-model="registerForm.question"
              placeholder="找回问题"
              size="large"
            />
          </el-form-item>

          <el-form-item prop="answer">
            <el-input
              v-model="registerForm.answer"
              placeholder="答案"
              size="large"
            />
          </el-form-item>
        </div>

        <el-button
          type="primary"
          size="large"
          class="auth-button"
          @click="handleRegister"
          :loading="loading"
        >
          注册
        </el-button>
      </el-form>

      <!-- 找回密码表单 -->
      <el-form
        v-else
        :model="forgotForm"
        :rules="forgotRules"
        ref="forgotFormRef"
        class="auth-form"
      >
        <!-- 第一步：验证用户名 -->
        <div v-if="forgotStep === 1">
          <el-form-item prop="username">
            <el-input
              v-model="forgotForm.username"
              placeholder="请输入要找回密码的用户名"
              size="large"
              :prefix-icon="User"
            />
          </el-form-item>

          <el-button
            type="primary"
            size="large"
            class="auth-button"
            @click="verifyUsername"
            :loading="loading"
          >
            下一步
          </el-button>
        </div>

        <!-- 第二步：验证安全问题 -->
        <div v-else-if="forgotStep === 2">
          <div class="security-question-section">
            <h3 class="question-title">安全问题验证</h3>
            <p class="question-text">{{ securityQuestion }}</p>

            <el-form-item prop="answer">
              <el-input
                v-model="forgotForm.answer"
                placeholder="请输入答案"
                size="large"
              />
            </el-form-item>
          </div>

          <div class="step-buttons">
            <el-button size="large" class="step-button" @click="forgotStep = 1">
              上一步
            </el-button>
            <el-button
              type="primary"
              size="large"
              class="step-button"
              @click="verifySecurityAnswer"
              :loading="loading"
            >
              验证答案
            </el-button>
          </div>
        </div>

        <!-- 第三步：重置密码 -->
        <div v-else-if="forgotStep === 3">
          <el-form-item prop="newPassword">
            <el-input
              v-model="forgotForm.newPassword"
              type="password"
              placeholder="请输入新密码（不少于8位数字+英文混合）"
              size="large"
              :prefix-icon="Lock"
              show-password
            />
          </el-form-item>

          <el-form-item prop="confirmNewPassword">
            <el-input
              v-model="forgotForm.confirmNewPassword"
              type="password"
              placeholder="请确认新密码"
              size="large"
              :prefix-icon="Lock"
              show-password
            />
          </el-form-item>

          <div class="step-buttons">
            <el-button size="large" class="step-button" @click="forgotStep = 2">
              上一步
            </el-button>
            <el-button
              type="primary"
              size="large"
              class="step-button"
              @click="resetPassword"
              :loading="loading"
            >
              重置密码
            </el-button>
          </div>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue";
import { ElMessage } from "element-plus";
import { User, Lock } from "@element-plus/icons-vue";
import { API } from "@/api";
import { useRoute, useRouter } from "vue-router";
const route = useRoute();
const router = useRouter();
const activeTab = ref("login");
const loading = ref(false);
const loginFormRef = ref();
const registerFormRef = ref();
const forgotFormRef = ref();
const token_ls = ref("");
// 找回密码步骤
const forgotStep = ref(1);
const securityQuestion = ref("");

// 模拟用户数据存储（实际项目中应该从后端获取）
const userDatabase = ref([
  // 示例用户数据，实际应该从后端API获取
  {
    username: "test",
    password: "test12345",
    question: "你最喜欢的颜色？",
    answer: "蓝色",
  },
]);

// 登录表单数据
const loginForm = ref({
  username: "",
  password: "",
});

// 注册表单数据
const registerForm = ref({
  username: "",
  password: "",
  confirmPassword: "",
  question: "",
  answer: "",
});

// 找回密码表单数据
const forgotForm = ref({
  username: "",
  answer: "",
  newPassword: "",
  confirmNewPassword: "",
});

// 密码验证函数
const validatePassword = (rule, value, callback) => {
  if (!value) {
    callback(new Error("请输入密码"));
  } else if (value.length < 8) {
    callback(new Error("密码长度不能少于8位"));
  } else if (!/(?=.*[a-zA-Z])(?=.*\d)/.test(value)) {
    callback(new Error("密码必须包含数字和英文"));
  } else {
    callback();
  }
};

const validateConfirmPassword = (rule, value, callback) => {
  if (!value) {
    callback(new Error("请确认密码"));
  } else if (value !== registerForm.value.password) {
    console.log(value, registerForm.value.password);

    callback(new Error("两次输入的密码不一致"));
  } else {
    callback();
  }
};

const validateConfirmNewPassword = (rule, value, callback) => {
  if (!value) {
    callback(new Error("请确认新密码"));
  } else if (value !== forgotForm.value.newPassword) {
    callback(new Error("两次输入的密码不一致"));
  } else {
    callback();
  }
};

// 登录验证规则
const loginRules = {
  username: [{ required: true, message: "请输入用户名", trigger: "blur" }],
  password: [{ required: true, message: "请输入密码", trigger: "blur" }],
};

// 注册验证规则
const registerRules = {
  username: [
    { required: true, message: "请输入用户名", trigger: "blur" },
    { min: 3, max: 20, message: "用户名长度为3-20个字符", trigger: "blur" },
  ],
  password: [{ required: true, validator: validatePassword, trigger: "blur" }],
  confirmPassword: [
    { required: true, validator: validateConfirmPassword, trigger: "blur" },
  ],
  question: [{ required: true, message: "请输入找回问题", trigger: "blur" }],
  answer: [{ required: true, message: "请输入答案", trigger: "blur" }],
};

// 找回密码验证规则
const forgotRules = {
  username: [{ required: true, message: "请输入用户名", trigger: "blur" }],
  answer: [{ required: true, message: "请输入答案", trigger: "blur" }],
  newPassword: [
    { required: true, validator: validatePassword, trigger: "blur" },
  ],
  confirmNewPassword: [
    { required: true, validator: validateConfirmNewPassword, trigger: "blur" },
  ],
};

// Tab切换处理
const handleTabChange = (tab) => {
  if (tab !== "forgot") {
    resetForgotForm();
  }
};

// 登录处理
const handleLogin = async () => {
  if (!loginFormRef.value) return;
  await loginFormRef.value.validate();
  loading.value = true;

  const res = await fetch(API.BASE_URL + "/users/login/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      ...loginForm.value,
    }),
  });
  const result = await res.json();
  if (result.success) {
    setTimeout(() => {
      localStorage.setItem("token", result.token);
      localStorage.setItem("username", result.username);
      localStorage.setItem("role", result.is_admin ? "管理员" : "普通用户");
      ElMessage.success("登录成功！");
      loading.value = false;
      router.push("/");
    }, 1000);
  } else {
    ElMessage.error(result.error);
    loading.value = false;
  }
};

// 注册处理
const handleRegister = async () => {
  if (!registerFormRef.value) return;
  await registerFormRef.value.validate();
  loading.value = true;
  const newUser = {
    username: registerForm.value.username,
    password: registerForm.value.password,
    confirm_password: registerForm.value.confirmPassword,
    password_hint_question: registerForm.value.question,
    password_hint_answer: registerForm.value.answer,
  };
  const res = await fetch(API.BASE_URL + "/users/register/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      ...newUser,
    }),
  });
  const result = await res.json();
  console.log(result);

  if (result.success) {
    await fetch(API.BASE_URL + "/templates/default-template", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Token " + result.token,
      },
    });

    setTimeout(() => {
      ElMessage.success("注册成功！");
      loading.value = false;
      // 重置表单并切换到登录
      Object.assign(registerForm.value, {
        username: "",
        password: "",
        confirmPassword: "",
        question: "",
        answer: "",
      });
      activeTab.value = "login";
    }, 1000);
  } else {
    loading.value = false;
    ElMessage.error(result.error);
  }
};

// 验证用户名
const verifyUsername = async () => {
  if (!forgotFormRef.value) return;
  // 只验证用户名字段
  await forgotFormRef.value.validateField("username");
  loading.value = true;
  const res = await fetch(API.BASE_URL + "/users/verify-user/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      username: forgotForm.value.username,
    }),
  });
  const result = await res.json();
  console.log(result);
  if (result.success) {
    securityQuestion.value = result.hint_question;
    forgotStep.value = 2;
    ElMessage.success("用户名验证成功");
    loading.value = false;
  } else {
    loading.value = false;
    ElMessage.error(result.error);
  }
};

// 验证安全问题答案
const verifySecurityAnswer = async () => {
  if (!forgotFormRef.value) return;
  await forgotFormRef.value.validateField("answer");
  loading.value = true;
  const res = await fetch(API.BASE_URL + "/users/verify-question/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      hint_answer: forgotForm.value.answer,
      username: forgotForm.value.username,
    }),
  });
  const result = await res.json();
  console.log(result);
  if (result.success) {
    token_ls.value = result.token;
    forgotStep.value = 3;
    ElMessage.success("安全问题验证成功");
    loading.value = false;
  } else {
    loading.value = false;
    ElMessage.error(result.error);
  }
};

// 重置密码
const resetPassword = async () => {
  if (!forgotFormRef.value) return;
  await forgotFormRef.value.validate();
  loading.value = true;
  const res = await fetch(API.BASE_URL + "/users/reset-password/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: "Token " + token_ls.value,
    },
    body: JSON.stringify({
      new_password: forgotForm.value.newPassword,
      confirm_password: forgotForm.value.confirmNewPassword,
    }),
  });
  const result = await res.json();
  console.log(result);
  if (result.success) {
    forgotStep.value = 1;

    // 重置找回密码表单并切换到登录
    resetForgotForm();
    activeTab.value = "login";
    ElMessage.success("密码修改成功！");
    loading.value = false;
  } else {
    loading.value = false;
    ElMessage.error(result.error);
  }
};

// 重置找回密码表单
const resetForgotForm = () => {
  Object.assign(forgotForm.value, {
    username: "",
    answer: "",
    newPassword: "",
    confirmNewPassword: "",
  });
  forgotStep.value = 1;
  securityQuestion.value = "";
};
</script>

<style scoped>
.auth-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #f8f8f8 100%);
}

.auth-card {
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

.auth-title {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
  font-size: 24px;
  font-weight: 600;
}

.auth-tabs {
  display: flex;
  justify-content: center;
  margin-bottom: 30px;
}

:deep(.el-radio-group) {
  width: 100%;
}

:deep(.el-radio-button) {
  flex: 1;
}

:deep(.el-radio-button__inner) {
  width: 100%;
}

.auth-form {
  width: 100%;
}

:deep(.el-form-item) {
  margin-bottom: 20px;
}

:deep(.el-input) {
  width: 100%;
}

.auth-button {
  width: 100%;
  margin-top: 10px;
  height: 45px;
  font-size: 16px;
}

.password-hint-section {
  margin: 25px 0 15px 0;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.hint-title {
  margin: 0 0 15px 0;
  color: #495057;
  font-size: 14px;
  font-weight: 600;
  text-align: center;
}

.security-question-section {
  margin: 15px 0;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.question-title {
  margin: 0 0 10px 0;
  color: #495057;
  font-size: 14px;
  font-weight: 600;
}

.question-text {
  margin: 0 0 15px 0;
  color: #e74c3c;
  font-weight: 600;
  text-align: center;
  padding: 10px;
  background: white;
  border-radius: 4px;
  border: 1px solid #ddd;
}

.step-buttons {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.step-button {
  flex: 1;
  height: 45px;
  font-size: 16px;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .auth-card {
    padding: 30px 20px;
    margin: 10px;
  }

  .auth-title {
    font-size: 20px;
  }

  .step-buttons {
    flex-direction: column;
  }
}
</style>