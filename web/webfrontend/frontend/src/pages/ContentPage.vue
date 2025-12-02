<template>
  <div class="outline-page" >
    <!-- 左侧文章列表 -->
    <div class="sidebar" @click="handleMouseLeave">
      <el-card class="config-list">
        <div class="header">
          <h3>正文列表</h3>
        </div>
        <el-scrollbar style="flex: 1">
          <div class="outline-list">
            <div
              v-for="article in articles"
              :key="article.id"
              class="outline-item"
              :class="{ active: selectedArticleId === article.id.toString() }"
              @click="handleSelectArticle(article.id.toString(), article)"
            >
              <span class="outline-name">{{ article.title }}</span>
              <el-button
                icon="Delete"
                type="danger"
                size="small"
                circle
                @click.stop="handleDelete(article.id)"
              />
            </div>
          </div>
        </el-scrollbar>
      </el-card>
    </div>

    <!-- 右侧正文展示区 -->
    <div class="outline-editor">
      <div class="toolbar" style="text-align: right; margin-bottom: 16px;" >
        <el-button
          type="primary"
          icon="Document"
          @click="settingWord()"
          :disabled="!selectedArticle"
        >
          生成文档
        </el-button>
      </div>
      <div v-if="selectedArticle">
        <el-card
          v-for="(section, idx) in strippedSections"
          :key="section.id"
          class="content-card"
        >
          <template #header >
            <div  >{{ section.title }}</div>
          </template>
             <div
            v-if="!isUpdate"
            class="text-content"
            v-html="marked(section.content)"
            @dblclick="isUpdate = !isUpdate"
          ></div>
          <el-input
            v-model="section.content"
            v-else
            style="width: 100%"
            :rows="15"
            type="textarea"
            @dblclick="isUpdate = !isUpdate"
            @click="isUpdate =true"
          />
        </el-card>
      </div>

      <div v-else class="placeholder">
        <p>请选择左侧文章以查看正文内容。</p>
      </div>
    </div>
  </div>
  <GenerateSettingDialog v-model="showSettingDialog" @submit="handleGenerate" />
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from "vue";
import { ElMessage } from "element-plus";
import { useRoute, useRouter } from "vue-router";
import { API } from "@/api";
import { marked } from "marked";
const isUpdate = ref(false);
import GenerateSettingDialog from "@/components/GenerateSettingDialog.vue";
import { log } from "util";
interface Section {
  id: string;
  title: string;
  outline?: string;
  content: string;
}

interface Article {
  id: number;
  title: string;
  structure: Section[];
}

const articles = ref<Article[]>([]);
const selectedArticleId = ref("");
const selectedArticle = ref<Article | null>(null);
const content_lines = ref<any>("");
const route = useRoute();
const router = useRouter();
const section_outline = ref("");
const section_title = ref("");
const article_title = ref<any>("");
const showSettingDialog = ref(false);
const title_setting=ref<any>()
const strippedSections = ref<any>([])
const getstrippedSections=()=>{
    return (
    selectedArticle.value?.structure.map(({ id, title, content }) => ({
      id,
      title,
      content,
    })) || []
  );
}
const handleSelectArticle = (id: string, article: any) => {
  
  selectedArticleId.value = id;
  selectedArticle.value =
    articles.value.find((a) => a.id.toString() === id) || null;

  if (!selectedArticle.value) {
    loadArticles().then(() => {
      selectedArticle.value =
        articles.value.find((a) => a.id.toString() === id) || null;
      if (!selectedArticle.value) {
        // ElMessage.warning("未找到对应的文章，请刷新页面重试");
      }
    });
  }
  console.log(selectedArticle.value);
  title_setting.value=selectedArticle.value?.title_setting
  article_title.value=selectedArticle.value?.title
  content_lines.value = selectedArticle.value?.structure
    .map((item) => item.content)
    .join(" \n ");
    strippedSections.value=getstrippedSections()
};
const settingWord = () => {
  showSettingDialog.value = true;
};

const loadArticles = async () => {
  const res = await fetch(API.BASE_URL + "/contents/articles/",{headers:{Authorization: "Token " + localStorage.getItem("token"),}});
  const data = await res.json();
  articles.value = data;
  if (data[0]) {
    handleSelectArticle(data[0].id.toString());
  }
};

onMounted(async () => {
  try {
    await loadArticles();
    const passedId = route.query.outline_id;
    if (passedId) {
      handleSelectArticle(passedId.toString());
    }
  } catch (err) {
    ElMessage.error("❌ 正文数据加载失败");
  }
});

watch(
  () => route.query.outline_id,
  (newId) => {
    if (newId) {
      handleSelectArticle(newId.toString());
    }
  },
  { immediate: true }
);

const handleDelete = async (id: number) => {
  ElMessage.success("删除成功");
  const res = await fetch(API.BASE_URL + `/contents/delete_content/${id}`,{headers:{Authorization: "Token " + localStorage.getItem("token"),}});
    console.log(res.ok);
  if (res.ok) {
    loadArticles()
    handleSelectArticle('','')
  }
};
const handleGenerate = async (settings: any) => {
  // 显示加载状态
  const loadingInstance = ElLoading.service({
    lock: true,
    text: "正在生成正文，这可能需要一些时间...",
    background: "rgba(0, 0, 0, 0.7)",
  });
  console.log("✅ 获取到的生成设置参数：", settings);

  // 在这里调用生成 Word 文档的逻辑
  // 可以将 settings 和 selectedArticle 一起传给 API 或 Word 导出模块
  // exportToWordWithSettings(settings);
  // settings.section_outline = section_outline.value;
  // settings.section_title = section_title.value;
  settings.content_lines = content_lines.value;
  settings.title_setting=title_setting.value
  // delete settings.miji;
  let data = settings;
  try {
    const res = await fetch(API.BASE_URL + `/contents/export/`, {
      method: "POST",
      headers: { "Content-Type": "application/json",Authorization: "Token " + localStorage.getItem("token") },
      body: JSON.stringify({
        // type: "format",
        ...data,
      }),
    });
    const blob = await res.blob();
    if (res.ok) {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = '['+settings.miji+']'+article_title.value + "." + data.file_type; // 或者从响应头获取文件名
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      ElMessage.success("文件生成成功，开始下载");
    }
  } catch (error) {
    console.log(error);
  } finally {
    showSettingDialog.value = false;
    // 关闭加载状态
    loadingInstance.close();
  }
};

const updateSectionContent = async (sectionId: string, content: string) => {
  if (!selectedArticle.value) return;
  try {
    const res = await fetch(
      API.BASE_URL +
        `/contents/articles/${selectedArticle.value.id}/sections/${sectionId}/`,
      {
        method: "PATCH",
        headers: { "Content-Type": "application/json",Authorization: "Token " + localStorage.getItem("token") },
        body: JSON.stringify({ content }),
      }
    );
    const result = await res.json();
    if (!result.success) throw new Error(result.error || "更新失败");
    ElMessage.success("已保存该段正文");
  } catch (err) {
    ElMessage.error("❌ 正文保存失败");
  }
};

const handleMouseLeave = async () => {
  isUpdate.value = false;
  console.log(articles.value[0],strippedSections.value);
  
  // console.log(props.sortedOutlineList, props.sections);
  let obj ={
    id:articles.value[0].id,
    structure:strippedSections.value,
  }
  // obj.original_structure = strippedSections.value;
  const res = await fetch(API.BASE_URL + `/outlines/${articles.value[0].id}/`, {
    method: "PATCH",
    headers: {
      Authorization: "Token " + localStorage.getItem("token"),
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(obj),
  });
};
</script>

<style >
.outline-page {
  height: 100%;
  max-width: 1280px;
  margin: 0 auto;
  display: flex;
  background-color: #f8f8f8;
}

.sidebar {
  width: 320px;
  padding: 20px;
  background-color: #f8f8f8;
}

.config-list {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 16px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.header h3 {
  font-size: 14px;
  font-weight: bold;
  margin: 0;
  color: #333;
}

.outline-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.outline-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s ease;
  background-color: #fff;
}

.outline-item:hover {
  background-color: #f5f7fa;
}

.outline-item.active {
  background-color: #e6f7ff;
  border: 1px solid #409eff;
}

.outline-name {
  font-size: 14px;
  color: #333;
  word-break: break-word;
  flex: 1;
  margin-right: 8px;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.outline-editor {
  flex: 1;
  padding: 24px 32px;
  overflow-y: auto;
  background-color: #fff;
}

.content-card {
  margin-bottom: 24px;
}

.placeholder {
  padding: 80px;
  text-align: center;
  color: #aaa;
}
.text-content {
  height: 300px;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
  color: #333;
  margin-bottom: 10px;
  overflow: auto;
}
.text-content table {
  border-collapse: collapse; /* 确保边框合并 */
}
table,
th,
td {
  border: 1px solid #666; /* 添加边框 */
}
th {
  background: #ccc;
}
</style>
