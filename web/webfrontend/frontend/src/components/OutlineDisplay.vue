<template>
  <div
    v-for="(section, index) in sections"
    :key="section.id || index"
    class="section-block"
  >
    <el-card shadow="never">
      <!-- 段落标题 -->
      <template #header>
        <div class="section-header">
          <h3>{{ section.title }}</h3>
          <!-- <el-button type="info" size="small">编辑</el-button> -->
        </div>
      </template>

      <!-- 知识注入标识 -->
      <!-- <p class="kb-flag">📚 知识注入：无注入内容</p> -->

      <!-- 大纲内容区（仅大纲模式下显示） -->
      <div v-if="isOutlineMode && section.outline" class="outline-content">
        <h4>大纲内容：</h4>
        <p>{{ section.outline }}</p>
      </div>

      <!-- 正文内容区（仅正文模式下显示） -->
      <div
        v-if="!isOutlineMode"
        class="section-content"
      >
        <div>
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
          />
        </div>
      </div>

      <!-- ✅ 始终显示生成正文按钮，且保护性复制 emit -->
      <el-button
        type="primary"
        plain
        size="small"
        class="generate-btn"
        @click="
          $emit(
            'generate',
            JSON.parse(
              JSON.stringify({
                id: section.id || 's' + index,
                title: section.title,
                outline:
                  section.outline ||
                  (section.content
                    ? `根据现有内容扩展：${section.content.substring(
                        0,
                        200
                      )}...`
                    : ''),
                content: section.content || '',
              })
            )
          )
        "
      >
        生成正文
      </el-button>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed, nextTick } from "vue";
import { marked } from "marked";
import { update } from "lodash-es";
import { API } from "@/api";
export interface OutlineSection {
  id?: string;
  title: string;
  outline?: string;
  content?: string;
}
const isUpdate = ref(false);
const props = defineProps<{
  sections: OutlineSection[];
  isOutlineMode?: boolean;
  sortedOutlineList: [];
}>();
const textContent = ref("");
onMounted(async () => {});
const handleMouseLeave = async () => {
  isUpdate.value = false;
  console.log(props.sortedOutlineList, props.sections);
  let obj = props.sortedOutlineList[0];
  obj.original_structure = props.sections;
  const res = await fetch(API.BASE_URL + `/outlines/${obj.id}/`, {
    method: "PUT",
    headers: {
      Authorization: "Token " + localStorage.getItem("token"),
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(obj),
  });
  if (!res.ok) throw new Error("加载大纲详情失败");
  return await res.json();
};

// 将方法暴露给父组件
defineExpose({
  handleMouseLeave
});
</script>



<style>
.section-block {
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.kb-flag {
  font-size: 13px;
  color: #999;
  margin-bottom: 10px;
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

.text-placeholder {
  font-size: 13px;
  font-style: italic;
  color: #ccc;
  margin-bottom: 10px;
}

.generate-btn {
  margin-top: 10px;
}
</style>
