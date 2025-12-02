<template>
  <el-dialog
    v-model="visible"
    title="生成正文格式"
    width="600px"
    @close="$emit('cancel')"
  >
    <el-form label-width="120px">
      <!-- <el-form-item label="选择模型">
        <el-select v-model="model" placeholder="请选择模型">
          <el-option
            v-for="item in modelOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="知识库检索">
        <el-switch v-model="enableKnowledge" />
      </el-form-item>
      <el-form-item v-if="enableKnowledge" label="知识库配置">
        <el-select v-model="selectedKB" placeholder="选择知识库">
          <el-option
            v-for="kb in knowledgeBases"
            :key="kb.value"
            :label="kb.label"
            :value="kb.value"
          />
        </el-select>
      </el-form-item> -->
      <!-- 字体选择 -->
      <el-form-item label="正文字体">
        <!-- <el-select v-model="font" placeholder="选择字体">
          <el-option v-for="f in fontOptions" :key="f" :label="f" :value="f" />
        </el-select> -->

        <el-select v-model="font_name" placeholder="选择字体">
          <el-option-group
            v-for="group in fontOptions"
            :key="group.label"
            :label="group.label"
          >
            <el-option
              v-for="item in group.options"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-option-group>
        </el-select>
      </el-form-item>

      <!-- 字号选择 -->
      <el-form-item label="正文字号">
        <el-select v-model="font_size" placeholder="选择字号">
          <el-option
            v-for="s in fontSizeOptions"
            :key="s.name"
            :label="s.name"
            :value="s.value"
          />
        </el-select>
      </el-form-item>

      <!-- 加粗斜体 -->
      <el-form-item label="样式">
        <el-checkbox v-model="bold">加粗</el-checkbox>
        <el-checkbox v-model="italic">斜体</el-checkbox>
      </el-form-item>

      <!-- <el-form-item label="行文增强">
        <el-switch v-model="use_hw" />
      </el-form-item> -->
      <!-- 表格样式 -->
      <el-form-item label="表格样式">
        <el-select v-model="tableStyle" placeholder="选择样式">
          <el-option label="默认边框" value="default" />
          <el-option label="简约无边框" value="no_border" />
          <el-option label="条纹风格" value="striped" />
        </el-select>
      </el-form-item>
      <el-form-item label="导出密级">
        <el-select v-model="miji" placeholder="导出密级">
          <el-option label="公开" value="公开" />
          <el-option label="受控" value="受控" />
          <el-option label="内部" value="内部" />
        </el-select>
      </el-form-item>

      <!-- 标头选择 -->
      <!-- <el-form-item label="标头选择">
        <el-select v-model="header" placeholder="选择红头/信纸">
          <el-option
            v-for="item in headerOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
      </el-form-item> -->

      <!-- 内容格式 -->
      <el-form-item label="内容格式">
        <el-select v-model="file_type" placeholder="内容格式">
          <el-option label="docx" value="docx" />
          <el-option label="pdf" value="pdf" />
        </el-select>
      </el-form-item>
      <el-form-item label="行距">
        <el-select v-model="line_spacingType" placeholder="行距">
          <el-option label="单倍" value="single" />
          <el-option label="2倍" value="double" />
          <el-option label="最小值" value="at_least" />
          <el-option label="多倍行距" value="multiple" />
          <el-option label="1.5倍行距" value="one_point_five" />
          <el-option label="固定值" value="exact" />
        </el-select>
      </el-form-item>
      <el-form-item
        label="设置值"
        suffix-icon="el-icon-date"
        v-if="line_spacingType == 'exact' || line_spacingType == 'multiple'"
      >
        <el-input
          type="number"
          v-model="line_spacingValue"
          style="max-width: 600px"
          placeholder="设置值"
        >
        </el-input>
      </el-form-item>
    </el-form>
    <!-- <el-form-item label="自定义提示词">
        <el-input
          type="textarea"
          v-model="customPrompt"
          placeholder="可选提示词..."
          :rows="3"
        />
      </el-form-item> -->
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="$emit('cancel')">取消</el-button>
        <el-button type="primary" @click="submit">开始生成</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, defineEmits, defineProps, onMounted } from "vue";
import { API } from "@/api";
import { useKnowledgeOptions } from "@/composables/useKnowledgeOptions";
const emit = defineEmits(["submit", "cancel"]);
const { knowledgeOptions: knowledgeBases } = useKnowledgeOptions();
const visible = defineModel<boolean>();
const model = ref("");
const modelOptions = ref<{ label: string; value: string }[]>([]);
const enableKnowledge = ref(false);
const selectedKB = ref("");
const hw_knowledge = ref("");
const font_name = ref("宋体");
const miji = ref("");
const font_size = ref(14);
const bold = ref(false);
const italic = ref(false);
const use_hw = ref(false);
const tableStyle = ref("");
const header = ref("");
const file_type = ref("docx");
const line_spacingType = ref("exact");
const line_spacingValue = ref(12);
const customPrompt = ref("");

// 常用 Word 字体
// const fontOptions = [
//   "宋体",
//   "仿宋",
//   "黑体",
//   "微软雅黑",
//   "Times New Roman",
//   "Arial",
//   "Calibri",
// ];
const fontOptions = [
  {
    label: "中文字体",
    options: [
      {
        value: "宋体",
        label: "宋体",
      },
      {
        value: "黑体",
        label: "黑体",
      },
      {
        value: "微软雅黑",
        label: "微软雅黑",
      },
    ],
  },
  {
    label: "英文字体",
    options: [
      {
        value: "Arial",
        label: "Arial",
      },
      {
        value: "Times New Roman",
        label: "Times New Roman",
      },
      {
        value: "Calibri",
        label: "Calibri",
      },
    ],
  },
];

// Word 标准字号
const fontSizeOptions = [
  {
    name: "小四",
    value: 12,
  },
  {
    name: "四号",
    value: 14,
  },
  {
    name: "小三",
    value: 15,
  },
  {
    name: "三号",
    value: 16,
  },
  {
    name: "小二",
    value: 18,
  },
  {
    name: "二号",
    value: 22,
  },
];

// 表头（红头/信纸）选项（假设从后端接口获取）
const headerOptions = ref<{ label: string; value: string }[]>([]);

onMounted(async () => {
  // TODO：实际项目中改为从后端 API 获取
  headerOptions.value = [
    { label: "默认信纸", value: "默认信纸" },
    { label: "公司红头", value: "公司红头" },
    { label: "军工信纸", value: "军工信纸" },
  ];
});

function submit() {
  emit("submit", {
    // model:model.value,
    // custom_prompt:customPrompt.value,
    miji:miji.value,
    knowledge_config_id: selectedKB.value,
    // use_kb:enableKnowledge.value,
    font_name: font_name.value,
    font_size: font_size.value,
    bold: bold.value,
    italic: italic.value,
    use_hw: use_hw.value,
    tableStyle: tableStyle.value,
    header: header.value,
    file_type: file_type.value,
    line_spacing: {
      type: line_spacingType.value,
      value:
        line_spacingType.value == "exact" ||
        line_spacingType.value == "multiple"
          ? line_spacingValue.value
          : null,
    },
  });
}
const fetchModelOptions = async () => {
  try {
    const res = await fetch(API.BASE_URL + "/contents/models/", {
      headers: { Authorization: "Token " + localStorage.getItem("token") },
    });
    const result = await res.json();
    if (result.success) {
      modelOptions.value = result.models.map((m: string) => ({
        label: m,
        value: m,
      }));
    } else {
      console.warn("模型列表获取失败：", result);
    }
  } catch (error) {
    console.error("❌ 获取模型列表失败:", error);
  }
};
onMounted(() => {
  fetchModelOptions();
});
</script>

<style scoped>
.dialog-footer {
  text-align: right;
}
</style>
