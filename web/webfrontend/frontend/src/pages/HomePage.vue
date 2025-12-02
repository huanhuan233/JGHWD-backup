<template>
  <div class="home-page-wrapper">
    <el-form label-width="120px" label-position="left" class="home-form">
      <!-- 文章标题 -->
      <el-form-item label="文章标题">
        <el-input v-model="articleTitle" placeholder="请输入项目标题" />
      </el-form-item>

      <!-- 选择模板 -->
      <el-form-item label="选择模板">
        <el-select v-model="selectedTemplate" placeholder="请选择模板">
          <el-option
            v-for="item in templateOptions"
            :key="item.id"
            :label="item.name"
            :value="JSON.stringify(item)"
          />
        </el-select>
      </el-form-item>

      <!-- 选择模型 -->
      <el-form-item label="选择模型">
        <el-select v-model="selectedModel" placeholder="请选择模型">
          <el-option
            v-for="item in modelOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
      </el-form-item>

      <!-- 自定义提示词 -->
      <el-form-item label="自定义提示词">
        <el-input
          v-model="customPrompt"
          placeholder="可选，用于生成大纲的提示词"
          clearable
        />
      </el-form-item>

      <!-- 知识库开关 -->
      <el-form-item label="知识库检索">
        <el-switch v-model="enableKnowledge" />
      </el-form-item>
      <el-form-item label="行文增强">
        <el-switch v-model="use_hw" />
      </el-form-item>
      <el-form-item v-if="use_hw" label="行文知识库配置">
        <el-select v-model="hw_knowledge" placeholder="选择知识库">
          <el-option
            v-for="kb in knowledgeBases"
            :key="kb.value"
            :label="kb.label"
            :value="kb.value"
          />
        </el-select>
      </el-form-item>
      <!-- 选择知识库 -->
      <el-form-item label="选择知识库">
        <el-select
          v-model="selectedKnowledgeBase"
          placeholder="请选择知识库"
          :disabled="!enableKnowledge"
        >
          <el-option
            v-for="item in knowledgeOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
      </el-form-item>

      <!-- 生成大纲按钮 -->
      <el-form-item>
        <el-button
          type="primary"
          plain
          class="generate-btn"
          @click="generateOutline"
          :loading="generating"
        >
          生成大纲
        </el-button>
      </el-form-item>
    </el-form>
    <el-dialog
      v-model="showDialog"
      title="生成中"
      width="400px"
      :show-close="false"
      :close-on-click-modal="false"
    >
      <div style="text-align: center; padding: 40px 0; font-size: 16px">
        生成中...... 次数 {{ count }}/{{ JSON.parse(selectedTemplate).count }}
      </div>
    </el-dialog>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, reactive } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { eventBus } from "@/eventBus";
import { useKnowledgeOptions } from "@/composables/useKnowledgeOptions";
import { useOutlineStore } from "@/stores/outline"; // ⬅️ 新增
import { API } from "@/api";
interface TemplateItem {
  id: string;
  name: string;
  structure: OutlineNode[];
}

interface OutlineNode {
  title: string;
  level: number;
  children?: OutlineNode[];
}
const { knowledgeOptions: knowledgeBases } = useKnowledgeOptions();
const showDialog = ref(false);
const count = ref(1);
const router = useRouter();
const outlineStore = useOutlineStore(); // ⬅️ 新增
const hw_knowledge = ref("");
const use_hw = ref(false);
const articleTitle = ref("");
const selectedTemplate = ref("");
const selectedModel = ref("");
const customPrompt = ref("");
const enableKnowledge = ref(false);
const selectedKnowledgeBase = ref("");

const templateOptions = ref<any>([]);
const modelOptions = ref<{ label: string; value: string }[]>([]);

const templateMap = ref<Record<string, TemplateItem>>({});

const { knowledgeOptions } = useKnowledgeOptions();

function extractLeafTitles(structure: any[]): string[] {
  const result: string[] = [];

  function dfs(nodes: any[]) {
    for (const node of nodes) {
      if (!node.children || node.children.length === 0) {
        result.push(node.title);
      } else {
        dfs(node.children);
      }
    }
  }

  dfs(structure);
  return result;
}

const generating = ref(false);
const openDialog = () => {
  showDialog.value = true;
  count.value = 1;
JSON.parse(selectedTemplate.value).count
  const timer = setInterval(() => {
    count.value++;
    if (count.value >= JSON.parse(selectedTemplate.value).count) {
      clearInterval(timer);
    }
  }, 250 * 1000);
};
const generateOutline = async () => {
  if (generating.value) return;
  generating.value = true;
  openDialog();
  try {
    if (!JSON.parse(selectedTemplate.value).name || !selectedModel.value) {
      ElMessage.error("请选择模板和模型");
      return;
    }

    const selectedStructure = JSON.parse(selectedTemplate.value).structure;
    if (!selectedStructure || selectedStructure.length === 0) {
      ElMessage.error("模板结构为空");
      return;
    }

    const leafTitles = extractLeafTitles(selectedStructure);
    if (leafTitles.length === 0) {
      ElMessage.error("模板中没有可用标题");
      return;
    }

    const payload = {
      model: selectedModel.value,
      prompt: customPrompt.value,
      titles: leafTitles,
      title_setting: JSON.parse(selectedTemplate.value),
      use_kb: enableKnowledge.value,
      knowledge: enableKnowledge.value ? selectedKnowledgeBase.value : null,
      article_title: articleTitle.value,
      use_hw: use_hw.value,
      hw_knowledge: hw_knowledge.value,
    };

    console.log("📤 请求大纲生成 payload:", payload);

    const res = await fetch(API.GENERATE_OUTLINE_ITEMS, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Token " + localStorage.getItem("token"),
      },
      body: JSON.stringify(payload),
    });

    const result = await res.json();
    if (!result.success || !result.outline?.id) {
      ElMessage.error("生成失败");
      return;
    }

    console.log("✅ 模型大纲返回结构:", result.outline);

    // ✅ 保存至 Pinia 供后续使用
    outlineStore.setOutline(result.outline.title, result.outline.structure);
    outlineStore.setKnowledge(selectedKnowledgeBase.value);

    // ✅ 跳转到大纲编辑页
    router.replace({
      name: "OutlinePage",
      query: {
        templateId: JSON.parse(selectedTemplate.value).name,
        outlineId: result.outline.id,
      },
    });
  } catch (err) {
    showDialog.value = false;
    console.error("❌ 请求失败:", err);
    ElMessage.error("请求失败，请检查网络或后端服务");
  } finally {
    generating.value = false;
    showDialog.value = false;
  }
};

const loadModels = async () => {
  try {
    const res = await fetch(API.MODELS, {
      credentials: "include",
      headers: { Authorization: "Token " + localStorage.getItem("token") },
    });
    const data = await res.json();
    if (data.success) {
      modelOptions.value = data.models.map((m: string) => ({
        label: m,
        value: m,
      }));
    }
  } catch (err) {
    console.error("加载模型列表失败", err);
  }
};

const loadTemplates = async () => {
  try {
    const res = await fetch(API.TEMPLATES, {
      headers: { Authorization: "Token " + localStorage.getItem("token") },
    });
    const result: {
      success: boolean;
      templates: TemplateItem[];
    } = await res.json();

    if (result.success) {
      console.log(result);

      templateOptions.value = result.templates;
      templateMap.value = Object.fromEntries(
        result.templates.map((t) => [t.id, t])
      );
    }
  } catch (err) {
    console.error("加载模板列表失败", err);
  }
};

onMounted(() => {
  loadTemplates();
  loadModels();
  eventBus.on("template-updated", loadTemplates);
});

onBeforeUnmount(() => {
  eventBus.off("template-updated", loadTemplates);
});
</script>


<style>
.home-page-wrapper {
  padding: 40px 24px;
  max-width: 720px;
  margin: auto;
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(2, 47, 248, 0.04);
}
.home-form .el-form-item {
  margin-bottom: 24px;
}
/* .generate-btn {
  background-color: #40E0D0;
  border-color: #3dbcdb;
}
.generate-btn:hover {
  background-color: #5D8AA8;
  border-color: #40E0D0;
} */
</style>