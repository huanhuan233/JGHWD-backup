<template>
  <div class="knowledge-config-page">
    <!-- 左侧配置列表 -->
    <el-card class="config-list">
      <div class="header">
        <h3>API 配置列表</h3>
        <el-button type="primary" plain icon="Plus" @click="addNewConfig"
          >新增配置</el-button
        >
      </div>
      <el-scrollbar class="config-scroll">
        <div
          v-for="(conf, index) in savedConfigs"
          :key="conf.id"
          class="config-item"
          @click="selectConfig(index)"
          :class="{ active: currentId === conf.id }"
        >
          <span>{{ conf.name }} ({{ conf.type }})</span>
          <el-button
            type="danger"
            icon="Delete"
            circle
            size="small"
            @click.stop="deleteConfig(index)"
          />
        </div>
      </el-scrollbar>

      <div v-if="extraFiles.length > 0" class="extra-warning">
        <el-divider>未注册的配置文件（可手动删除）</el-divider>
        <el-alert
          type="warning"
          title="以下配置文件存在于文件夹中，但未注册在数据库中。"
          :closable="false"
        />
        <el-scrollbar height="150px" style="margin-top: 10px">
          <div
            v-for="(file, i) in extraFiles"
            :key="file"
            class="config-item orphan"
          >
            <span>{{ file }}</span>
            <el-button
              type="danger"
              icon="Delete"
              circle
              size="small"
              @click.stop="deleteOrphanFile(file)"
            />
          </div>
        </el-scrollbar>
      </div>
    </el-card>

    <!-- 右侧配置面板 -->
    <el-card class="config-panel">
      <el-scrollbar class="config-scroll">
        <el-form :model="form">
          <el-form-item label="知识库选择">
            <el-select v-model="form.type" placeholder="请选择知识库">
              <el-option label="Dify" value="dify" />
              <el-option label="Milvus" value="milvus" />
              <el-option label="FastGpt" value="FastGpt" />
            </el-select>
          </el-form-item>

          <el-form-item label="配置名称">
            <el-input v-model="form.name" placeholder="请输入配置名称" />
          </el-form-item>

          <el-form-item label="API KEY">
            <el-input v-model="form.api_key" placeholder="请输入 API KEY" />
          </el-form-item>

          <el-form-item>
            <div class="btns">
              <el-button type="success" plain @click="saveConfig"
                >保存配置</el-button
              >
              <el-button type="warning" plain @click="cancelEdit"
                >取消编辑</el-button
              >
              <el-button plain @click="showDialog = true">知识库设置</el-button>
            </div>
          </el-form-item>
        </el-form>
      </el-scrollbar>
    </el-card>

    <el-dialog v-model="showDialog" title="知识库设置" width="75%">
      <div style="height: 500px; overflow: auto">
        <p>访问地址http://192.168.0.97:3000/</p>
        <p>第一步：新建通用知识库</p>
        <img src="../assets/images/1.png" width="100%" />
        <img src="../assets/images/2.png" width="100%" />
        <p>第二步知识库文件：</p>
        <img src="../assets/images/3.png" width="100%" />
        <img src="../assets/images/4.png" width="100%" />
        <p>根据提示进行操作</p>
        <img src="../assets/images/5.png" width="100%" />
        <img src="../assets/images/6.png" width="100%" />
        <p>提示：状态为已就绪代表可用</p>
        <p>第三步：创建应用</p>
        <p>点击工作台新建简易应</p>
        <img src="../assets/images/7.png" width="100%" />
        <img src="../assets/images/8.png" width="100%" />
        <p>关联相关的知识库 关联成功后点击发布渠道</p>
        <img src="../assets/images/9.png" width="100%" />
        <img src="../assets/images/10.png" width="100%" />
        <p>
          点击api访问点击新建填好昵称后返回相对应的key 这一步要拿记事本复制下来
        </p>
        <img src="../assets/images/11.png" width="100%" />
        <p>回到应用配置保存并发布</p>
        <img src="../assets/images/12.png" width="100%" />
        <p>第四步：回到页面</p>
        <img src="../assets/images/13.png" width="100%" />
        <p>填写并保存既可以使用</p>
      </div>

      <template #footer>
        <el-button @click="showDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { API } from "@/api";
const showDialog = ref(false);
interface KnowledgeConfig {
  id?: number;
  type: string;
  name: string;
  api_key: string;
}

const form = ref<KnowledgeConfig>({
  type: "",
  name: "",
  api_key: "",
});

const savedConfigs = ref<KnowledgeConfig[]>([]);
const extraFiles = ref<string[]>([]);
const currentId = ref<number | null>(null);

async function loadKnowledgeConfigs() {
  try {
    const response = await fetch(API.GET_KNOWLEDGE_CONFIGS, {
      headers: { Authorization: "Token " + localStorage.getItem("token") },
    });
    const result = await response.json();
    savedConfigs.value = result.configs;
    extraFiles.value = result.extra_files || [];
  } catch (error) {
    console.error("❌ 获取配置失败:", error);
  }
}

async function saveConfig() {
  if (!form.value.name || !form.value.type || !form.value.api_key) {
    return ElMessage.error("请完整填写配置信息");
  }

  const payload = {
    name: form.value.name,
    type: form.value.type,
    api_key: form.value.api_key,
  };

  const method = currentId.value ? "PUT" : "POST";
  const url = API.GET_KNOWLEDGE_CONFIG_DETAIL(
    currentId.value != null ? String(currentId.value) : undefined
  );

  try {
    const response = await fetch(url, {
      method,
      headers: {
        "Content-Type": "application/json",
        Authorization: "Token " + localStorage.getItem("token"),
      },
      body: JSON.stringify(payload),
    });

    const result = await response.json();

    if (result.success) {
      ElMessage.success(currentId.value ? "修改成功！" : "保存成功！");
      currentId.value = null;
      await loadKnowledgeConfigs();
    } else {
      ElMessage.error(
        "保存失败：" + (result.errors || result.error || "未知错误")
      );
    }
  } catch (err) {
    ElMessage.error("请求失败：" + err);
  }
}

async function deleteConfig(index: number) {
  const config = savedConfigs.value[index];
  if (!config.id) {
    ElMessage.error("缺少配置 ID，无法删除");
    return;
  }

  try {
    const response = await fetch(
      `${API.DELETE_KNOWLEDGE_CONFIG}?id=${config.id}`,
      {
        method: "DELETE",
        headers: { Authorization: "Token " + localStorage.getItem("token") },
      }
    );
    const result = await response.json();

    if (result.success) {
      ElMessage.success("配置及文件已删除");
      await loadKnowledgeConfigs();
    } else {
      ElMessage.error("删除失败：" + (result.error || "未知错误"));
    }
  } catch (err) {
    ElMessage.error("请求失败：" + err);
  }
}

async function deleteOrphanFile(file: string) {
  try {
    const res = await fetch(API.DELETE_ORPHAN_FILE, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Token " + localStorage.getItem("token"),
      },
      body: JSON.stringify({ filename: file }),
    });
    const result = await res.json();
    if (result.success) {
      ElMessage.success(`已删除文件: ${file}`);
      await loadKnowledgeConfigs();
    } else {
      ElMessage.error("删除失败: " + (result.error || "未知错误"));
    }
  } catch (err) {
    ElMessage.error("删除请求失败：" + err);
  }
}

function selectConfig(index: number) {
  const config = savedConfigs.value[index];
  currentId.value = config.id || null;
  form.value = {
    name: config.name,
    type: config.type,
    api_key: config.api_key,
  };
}

function addNewConfig() {
  form.value = { type: "", name: "", api_key: "" };
}
function cancelEdit() {
  currentId.value = null;
  form.value = { type: "", name: "", api_key: "" };
  ElMessage.info("已取消编辑");
}

onMounted(loadKnowledgeConfigs);
</script>

<style scoped>
.knowledge-config-page {
  display: flex;
  gap: 16px;
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  height: calc(100vh - 100px);
}

.config-list,
.config-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.config-scroll {
  flex: 1;
  overflow: auto;
}

.config-list {
  width: 340px;
  min-width: 320px;
  flex-shrink: 0;
}

.config-panel {
  flex: 1;
  min-width: 400px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.config-item {
  cursor: pointer;
  padding: 8px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-radius: 6px;
  transition: background-color 0.2s ease;
}

.config-item:hover {
  background-color: #f5f7fa;
}

.config-item.active {
  background-color: #e6f7ff;
  border: 1px solid #409eff;
}

.config-item.orphan {
  background-color: #fff4e6;
  color: #d46b08;
  border: 1px dashed #faad14;
  font-style: italic;
}
</style>
