<template>
  <el-container class="outline-page"   >
    <!-- 左侧大纲列表区域 -->
    <el-aside class="sidebar" @click="closeEdit" >
      <el-card class="config-list">
        <!-- 顶部标题和导入按钮 -->
        <div class="header" >
          <h3>大纲列表</h3>
          <!-- <el-button
            type="success"
            plain
            size="small"
            icon="Plus"
            @click="handleImport"
          >
            导入
          </el-button> -->
        </div>

        <!-- 大纲项分组列表 -->
        <el-scrollbar style="flex: 1">
          <div
            v-for="outline in sortedOutlineList"
            :key="outline.id"
            class="group-block"
          >
            <div
              class="group-header"
              :class="{ active: outline.id === currentOutlineId }"
              @click="selectOutline(outline.id)"
            >
              <el-tooltip
                :content="`标题：${outline.title}\nID：${
                  outline.id
                }\n时间：${formatTime(outline.created_at)}`"
                placement="top"
              >
                <span class="group-title">
                  {{ outline.title }} #{{ outline.id }}
                </span>
              </el-tooltip>

              <el-button
                type="danger"
                icon="Delete"
                circle
                size="small"
                @click.stop="handleDelete(outline.id)"
              />
            </div>
          </div>
        </el-scrollbar>
      </el-card>
    </el-aside>

    <!-- 右侧大纲编辑区域 -->
    <el-main class="outline-editor">
      <div v-if="outlineSections.length === 0" class="section-block">
        <el-input
          type="textarea"
          :rows="6"
          readonly
          placeholder="请先生成大纲"
        />
        <el-button type="primary" plain size="small" disabled
          >生成正文</el-button
        >
      </div>

      <OutlineDisplay
      ref="outlineDisplay"
        :sections="outlineSections"
        :sortedOutlineList="sortedOutlineList"
        @generate="openGenerateDialog"
      />

      <!-- 调试信息展示 -->
      <div class="debug-info" v-if="outlineStore.debugInfo?.prompts?.length">
        <el-divider>调试信息</el-divider>
        <el-collapse>
          <el-collapse-item
            v-for="[groupTitle, outlines] in groupedOutlineMap"
            :key="groupTitle"
          >
            <template #title>
              <div class="collapse-title-wrapper">
                <el-tooltip :content="groupTitle" placement="right">
                  <span class="collapse-title">{{ groupTitle }}</span>
                </el-tooltip>
                <el-button
                  type="danger"
                  icon="Delete"
                  circle
                  size="small"
                  @click.stop="handleDelete(outlines[0].id)"
                />
              </div>
            </template>

            <div
              v-for="outline in outlines"
              :key="outline.id"
              class="outline-item"
              :class="{ active: outline.id === currentOutlineId }"
              @click="selectOutline(outline.id)"
            >
              <el-tooltip :content="outline.title" placement="right">
                <span class="outline-name">段落组</span>
              </el-tooltip>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </el-main>

    <!-- 正文生成弹窗 -->
    <GenerateDialog
      v-if="showGenerateModal"
      :section="selectedSection"
      :outlineId="currentOutlineId"
      @cancel="showGenerateModal = false"
      @confirm="handleGenerate"
    />
  </el-container>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useRoute } from "vue-router";
import GenerateDialog from "@/components/GenerateDialog.vue";
import { useOutlineStore } from "@/stores/outline";
import { fetchOutlineList, fetchOutlineDetail } from "@/api/outline";
import { fetchTemplateList } from "@/api/template";
import {
  extractEffectiveTitles,
  splitByLevel2Titles,
  splitByLevel2TitlesFromStructure,
  filterVisibleSections,
} from "@/utils/useOutlineParser";
import { deleteOutline } from "@/api/outline";
import OutlineDisplay from "@/components/OutlineDisplay.vue";
import { useRouter } from "vue-router";
import { API } from "@/api";
import { marked } from "marked";
const outlineStore = useOutlineStore();
const outlineDisplay=ref(null)
const route = useRoute();
const templateId = route.query.templateId as string;

const outlineList = ref<any[]>([]);
const templateList = ref<any[]>([]);
const currentOutlineId = ref<number | null>(null);
const outlineSections = ref<{ title: string; content: string }[]>([]);
const showGenerateModal = ref(false);
const selectedSection = ref<any>(null);

const templateStructure = computed(() => {
  return templateList.value.find((t) => t.id === templateId)?.structure || [];
});
const closeEdit=()=>{
   if (outlineDisplay.value) {
    outlineDisplay.value.handleMouseLeave();
  }
}
async function loadOutlineList() {
  try {
    const list = await fetchOutlineList();
    outlineList.value = list;
    if (list.length > 0) {
      selectOutline(list[0].id);
    } else {
      outlineSections.value = [];
    }
  } catch (err) {
    console.error("❌ 获取大纲列表失败:", err);
  }
}
const groupedOutlineMap = computed(() => {
  const sortedList = [...outlineList.value].sort(
    (a, b) =>
      new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );

  const map = new Map<string, any[]>();

  for (const outline of sortedList) {
    const time = new Date(outline.created_at).toLocaleString("zh-CN", {
      hour12: false,
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });

    const groupKey = `${outline.title}（${time}）`;

    map.set(groupKey, [outline]); // 每个版本单独成组
  }

  return map;
});

async function selectOutline(id: number) {
  try {
    console.log("✅ 正在加载大纲 ID:", id);

    const detail = await fetchOutlineDetail(id);
    console.log("🧾 后端返回 structure:", detail.structure);
    console.log("📜 后端返回 original_structure:", detail.original_structure);

    // ✅ 使用原始结构（深拷贝）
    const structureToUse = detail.original_structure?.length
      ? JSON.parse(JSON.stringify(detail.original_structure))
      : JSON.parse(JSON.stringify(detail.structure));

    const templateStruct = templateStructure.value || [];
    const visibleTitles = extractEffectiveTitles(templateStruct);
    console.log("📌 模板提取的可视标题:", visibleTitles);

    const filtered =
      visibleTitles.length > 0
        ? filterVisibleSections(structureToUse, templateStruct)
        : [];

    // ✅ 设置展示数据（深拷贝，避免被正文页污染）
    outlineSections.value = JSON.parse(
      JSON.stringify(filtered.length > 0 ? filtered : structureToUse)
    );

    const htmlMD = marked(outlineSections.value[0].content);
    console.log(
      htmlMD,
      outlineSections.value[0].content,
      "alalalalalaalalalaalalalaalalalalalal"
    );
    currentOutlineId.value = id;
    outlineStore.setOutline(
      detail.title,
      JSON.parse(JSON.stringify(structureToUse))
    );

    console.log("📦 实际展示的段落数:", outlineSections.value.length);
  } catch (err) {
    console.error("❌ 获取大纲详情失败:", err);
  }
}

const openGenerateDialog = (section: any) => {
  console.log("打开生成对话框，段落信息:", section);

  // 从标题中提取ID（如果没有明确的ID）
  let sectionId = section.id;
  if (!sectionId && section.title) {
    // 使用标题作为ID的备选方案
    sectionId = "s" + section.title.replace(/[^a-zA-Z0-9]/g, "");
  }

  if (!sectionId) {
    ElMessage.error("无法识别段落ID，请检查数据结构");
    return;
  }

  // 如果大纲为空但有内容，则使用内容作为大纲
  const outline =
    section.outline ||
    (section.content
      ? `根据现有内容扩展：${section.content.substring(0, 200)}...`
      : "");

  selectedSection.value = {
    id: sectionId,
    title: section.title || "",
    outline: outline,
    content: section.content || "",
  };

  showGenerateModal.value = true;
};

const router = useRouter();

const handleGenerate = async (settings: any) => {
  showGenerateModal.value = false;

  // 显示加载状态
  const loadingInstance = ElLoading.service({
    lock: true,
    text: "正在生成正文，这可能需要一些时间...",
    background: "rgba(0, 0, 0, 0.7)",
  });

  try {
    ElMessage.info("正在生成正文，请稍候...");

    console.log("当前大纲ID:", currentOutlineId.value);
    console.log("选中的段落:", selectedSection.value);
    console.log("生成设置:", settings);
    console.log("当前大纲标题:", outlineStore.title);

    // 确保所有必要字段都有值
    if (!currentOutlineId.value) {
      throw new Error("未选择大纲");
    }

    if (!selectedSection.value) {
      throw new Error("未选择段落");
    }

    if (!selectedSection.value.id) {
      throw new Error("段落ID缺失");
    }

    if (!settings.model) {
      throw new Error("请选择模型");
    }

    // 获取当前大纲的完整信息
    const outlineDetail = await fetchOutlineDetail(currentOutlineId.value);
    const articleTitle =
      outlineDetail?.title || outlineStore.title || "未命名文章";

    // 准备请求数据
    const requestData = {
      outline_id: currentOutlineId.value, // 用于后端大纲备份和正文关联
      section_id: selectedSection.value.id,
      article_title: articleTitle,
      section_title: selectedSection.value.title || "未命名段落",
      section_outline: selectedSection.value.outline || "",
      model: settings.model,
      minWords: settings.minWords || 1000,
      use_kb: settings.enableKnowledge || false,
      use_hw: settings.use_hw,
      hw_knowledge: settings.hw_knowledge,
      knowledge_config_id: settings.selectedKB ? settings.selectedKB : "",
      custom_prompt: settings.customPrompt || "",
    };

    console.log("发送到后端的数据:", requestData);

    // 调用后端API生成正文
    const response = await fetch(API.BASE_URL + "/contents/auto-generate/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Token " + localStorage.getItem("token")
      },
      body: JSON.stringify(requestData),
    });

    // 获取响应文本以便调试
    const responseText = await response.text();
    console.log("API响应原始文本:", responseText);

    if (!response.ok) {
      if (response.status === 500 && responseText.includes("timeout")) {
        throw new Error("生成超时，请稍后重试或选择其他模型");
      } else {
        throw new Error(
          `API请求失败: ${response.status} ${response.statusText}\n响应内容: ${responseText}`
        );
      }
    }

    // 解析JSON响应
    let result;
    try {
      result = JSON.parse(responseText);
    } catch (e) {
      throw new Error(`解析响应失败: ${e.message}\n原始响应: ${responseText}`);
    }

    if (result.success) {
      ElMessage.success("正文生成成功");

      // 更新本地数据
      const sectionIndex = outlineSections.value.findIndex(
        (s) => s.id === selectedSection.value.id
      );
      if (sectionIndex !== -1) {
        outlineSections.value[sectionIndex].content = result.content;
      }

      // 跳转到正文生成界面
      router.push({
        path: "/content",
        query: { outline_id: currentOutlineId.value.toString() },
      });
    } else {
      ElMessage.error(`生成失败: ${result.error || "未知错误"}`);
    }
  } catch (error) {
    console.error("生成正文时出错:", error);
    ElMessage.error({
      message: `生成正文失败: ${
        error instanceof Error ? error.message : "未知错误"
      }`,
      duration: 5000,
    });
  } finally {
    // 关闭加载状态
    loadingInstance.close();
  }
};
const handleImport = () => {
  // TODO: 导入逻辑
};

const handleDeleteGroup = async (title: string) => {
  try {
    const group = groupedOutlineMap.value.get(title);
    if (!group || group.length === 0) return;

    await Promise.all(group.map((outline) => deleteOutline(outline.id)));
    ElMessage.success(`已删除文章《${title}》的大纲`);
    await loadOutlineList();
    if (
      currentOutlineId.value &&
      group.some((o) => o.id === currentOutlineId.value)
    ) {
      outlineSections.value = [];
      currentOutlineId.value = null;
    }
  } catch (err) {
    ElMessage.error("删除失败");
  }
};

const handleDelete = async (id: number) => {
  try {
    await deleteOutline(id);
    ElMessage.success("删除成功");
    await loadOutlineList();
  } catch (err) {
    ElMessage.error("删除失败");
  }
};
function getKbForTitle(title: string): string {
  const match = outlineStore.debugInfo?.knowledge_snippets?.find(
    (k) => k.title === title
  );
  return match ? match.kb : "无注入内容";
}
const sortedOutlineList = computed(() => {
  return [...outlineList.value].sort(
    (a, b) =>
      new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );
});

function formatTime(ts: string): string {
  return new Date(ts).toLocaleString("zh-CN", {
    hour12: false,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

onMounted(async () => {
  const outlineId = route.query.outlineId as string;

  // 加载模板列表
  const templates = await fetchTemplateList();
  templateList.value = templates;

  // 如果有 outlineId（即从生成页跳转过来），优先加载该大纲
  if (outlineId) {
    await loadOutlineList();
    await selectOutline(Number(outlineId));
  } else {
    await loadOutlineList();
    // 默认加载最新一条（如果有）
    if (outlineList.value.length > 0) {
      await selectOutline(outlineList.value[0].id);
    }
  }
});
</script>


<style scoped>
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

.outline-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 6px;
  border-radius: 6px;
  transition: background-color 0.2s ease;
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
}

.outline-editor {
  flex: 1;
  padding: 24px 32px;
  overflow-y: auto;
  background-color: #fff;
}

.section-block {
  margin-bottom: 24px;
}

.debug-info {
  margin-top: 40px;
}
.collapse-title {
  display: inline-block;
  max-width: 200px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.collapse-title-wrapper {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.collapse-title {
  display: inline-block;
  max-width: 200px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.group-block {
  margin-bottom: 12px;
}

.group-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 10px;
  border-radius: 6px;
  background-color: #f5f7fa;
  transition: background-color 0.2s ease;
  cursor: pointer;
}

.group-header.active {
  background-color: #e6f7ff;
  border: 1px solid #409eff;
}

.group-title {
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 14px;
  color: #333;
}
</style>