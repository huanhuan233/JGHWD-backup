<template>
  <div class="format-page-wrapper">
    <div class="format-page">
      <el-row :gutter="20" justify="center">
        <el-col :span="6" class="sidebar">
          <el-card shadow="never">
            <h3>模板列表</h3>
            <el-button-group class="mt-2">
              <el-button type="primary" @click="createNewTemplate"
                >新建模板</el-button
              >
              <el-button @click="dialogUpdate = true">导入模板</el-button>
            </el-button-group>
            <el-menu class="template-list">
              <el-menu-item
                v-for="template in templates"
                :key="template.id"
                @click="selectTemplate(template)"
              >
                <div
                  class="template-name"
                  style="
                    width: 200px;
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                  "
                >
                  {{ template.name }}
                </div>
                <div class="template-actions">
                  <el-button
                    type="primary"
                    plain
                    size="small"
                    @click.stop="exportTemplate(template)"
                    title="导出"
                    >导出</el-button
                  >
                  <el-button
                    type="danger"
                    plain
                    size="small"
                    @click.stop="deleteTemplate(template.id, template.name)"
                    title="删除"
                    >删除</el-button
                  >
                </div>
              </el-menu-item>
            </el-menu>
          </el-card>
        </el-col>

        <el-col :span="14" class="editor">
          <div class="editor-header">
            <h2>模板编辑</h2>
            <el-button type="primary" plain @click="saveTemplate"
              >保存</el-button
            >
          </div>

          <el-input
            v-model="currentTemplate.name"
            placeholder="请输入模板标题"
            class="mb-4"
          />

          <div class="outline-structure">
            <div class="add-button-wrapper">
              <el-button type="success" plain @click="addLevel1"
                ><el-icon><Plus /></el-icon>添加一级标题</el-button
              >
              <!-- 新增：添加一级标题至特定段落按钮 -->
              <el-button type="info" plain @click="showAddToPositionDialog"
                ><el-icon><Position /></el-icon
                >添加一级标题至特定段落</el-button
              >
            </div>

            <OutlineItem
              v-for="(item, index) in currentTemplate.structure"
              :key="item.id"
              :item="item"
              @edit="openEditDialog"
              @add-child="addChild"
              @remove="() => removeOutline(index)"
              @position-up="movePositionUp"
              @position-down="movePositionDown"
              @level-up="moveLevelUp"
              @level-down="moveLevelDown"
              @remove-child="removeChild"
              @move="openMoveDialog"
            />
          </div>
        </el-col>
      </el-row>

      <!-- 编辑大纲项弹窗 -->
      <EditOutlineDialog
        v-model="dialogVisible"
        :item="editingItem"
        :fonts="wordFonts"
        :sizes="wordFontSizes"
        @confirm="confirmEdit"
        @cancel="cancelEdit"
      />

      <!-- 密级选择弹窗 -->
      <el-dialog
        v-model="importDialog"
        title="密级"
        width="500"
        :before-close="handleClose"
      >
        <div class="classIfication">
          <el-select
            v-model="classIfication"
            placeholder="请选择导出的密级"
            style="width: 240px"
          >
            <el-option label="公开" value="公开" />
            <el-option label="受控" value="受控" />
            <el-option label="内部" value="内部" />
          </el-select>
        </div>
        <template #footer>
          <div class="dialog-footer">
            <el-button @click="importDialog = false">取消</el-button>
            <el-button type="primary" @click="submitexportTemplate()">
              确认
            </el-button>
          </div>
        </template>
      </el-dialog>

      <!-- 新增：添加至特定段落弹窗 -->
      <el-dialog
        v-model="addToPositionDialogVisible"
        title="添加一级标题至特定段落"
        width="500"
        :before-close="handleAddToPositionClose"
      >
        <div class="add-to-position-content">
          <p>选择要将新一级标题添加到的位置：</p>
          <el-select
            v-model="selectedPosition"
            placeholder="请选择段落位置"
            style="width: 100%"
            clearable
          >
            <el-option
              v-for="position in positionOptions"
              :key="position.value"
              :label="position.label"
              :value="position.value"
            />
          </el-select>
          <div class="dialog-tip" v-if="selectedPosition">
            <el-alert
              type="info"
              :closable="false"
              show-icon
              :title="`将在第 ${selectedPosition} 段插入新标题，原第 ${selectedPosition} 段及后续段落将依次后移`"
            />
          </div>
        </div>
        <template #footer>
          <div class="dialog-footer">
            <el-button @click="addToPositionDialogVisible = false"
              >取消</el-button
            >
            <el-button
              type="primary"
              @click="confirmAddToPosition"
              :disabled="!selectedPosition"
            >
              确认添加
            </el-button>
          </div>
        </template>
      </el-dialog>

      <!-- 新增：移动标题弹窗 -->
      <el-dialog
        v-model="moveDialogVisible"
        title="移动标题"
        width="500"
        :before-close="handleMoveDialogClose"
      >
        <div class="move-dialog-content">
          <p>
            将标题 "<strong>{{ movingItem?.title }}</strong
            >" 移动到：
          </p>

          <div class="move-form">
            <div class="form-item">
              <label>选择段落：</label>
              <el-select
                v-model="moveTarget.paragraph"
                placeholder="请选择目标段落"
                style="width: 100%"
                @change="handleParagraphChange"
                clearable
              >
                <el-option
                  v-for="position in moveParagraphOptions"
                  :key="position.value"
                  :label="position.label"
                  :value="position.value"
                />
              </el-select>
            </div>

            <div class="form-item">
              <label>选择层级：</label>
              <el-select
                v-model="moveTarget.level"
                placeholder="请选择目标层级"
                style="width: 100%"
                :disabled="!moveTarget.paragraph"
                clearable
              >
                <el-option
                  v-for="level in moveLevelOptions"
                  :key="level.value"
                  :label="level.label"
                  :value="level.value"
                />
              </el-select>
            </div>

            <div
              class="move-preview"
              v-if="moveTarget.paragraph && moveTarget.level"
            >
              <el-alert
                type="info"
                :closable="false"
                show-icon
                :title="getMovePreviewText()"
              />
            </div>
          </div>
        </div>
        <template #footer>
          <div class="dialog-footer">
            <el-button @click="handleMoveDialogClose">取消</el-button>
            <el-button
              type="primary"
              @click="confirmMove"
              :disabled="!moveTarget.paragraph || !moveTarget.level"
            >
              确认移动
            </el-button>
          </div>
        </template>
      </el-dialog>
    </div>

    <!-- 导入 -->
    <el-dialog
      v-model="dialogUpdate"
      title="导入模板"
      width="500"
      :before-close="handleUpdateClose"
      :close-on-click-modal="false"
      :show-close="false"
      :data="{
        type: 'format',
      }"
    >
      <div class="upateFile" v-loading="loading">
        <el-upload
          class="upload-demo"
          drag
          :auto-upload="true"
          :show-file-list="false"
          accept=".json,.pdf,.docx"
          :headers="{
            'Content-Type': 'multipart/form-data',
            Authorization: 'Token ' + token,
          }"
          :http-request="customUploadWithFetch"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            将文件拖放到此处或 <em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">仅支持json/pdf/docx</div>
          </template>
        </el-upload>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogUpdate = false" :disabled="loading"
            >关闭</el-button
          >
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import OutlineItem from "@/components/OutlineItem.vue";
import EditOutlineDialog from "@/components/EditOutlineDialog.vue";
import {
  Plus,
  Top,
  Bottom,
  ArrowUp,
  ArrowDown,
  Position,
  UploadFilled,
} from "@element-plus/icons-vue";
import { eventBus } from "@/eventBus";
import { API } from "@/api";
import { ElMessage } from "element-plus";

export interface OutlineItemType {
  id: string;
  title: string;
  font: string;
  size: any;
  color: string;
  bold: boolean;
  italic: boolean;
  id_level: number;
  children?: OutlineItemType[];
}

interface TemplateData {
  id: string;
  name: string;
  structure: OutlineItemType[];
}
const loading = ref(false);
const token = ref();
const dialogUpdate = ref(false);
const templates = ref<TemplateData[]>([]);
const currentTemplate = ref<TemplateData>({ id: "", name: "", structure: [] });
const fileInput = ref<HTMLInputElement | null>(null);

// 新增：添加至特定段落相关变量
const addToPositionDialogVisible = ref(false);
const selectedPosition = ref<number | null>(null);

// 新增：移动标题相关变量
const moveDialogVisible = ref(false);
const movingItem = ref<OutlineItemType | null>(null);
const moveTarget = ref({
  paragraph: null as number | null,
  level: null as number | null,
});

onMounted(async () => {
  token.value = localStorage.getItem("token");
  try {
    const res = await fetch(API.BASE_URL + "/list-templates?type=format", {
      headers: { Authorization: "Token " + localStorage.getItem("token") },
    });
    const result = await res.json();
    if (result.success) {
      templates.value = result.templates;
    }
  } catch (err) {
    console.error("加载模板列表失败:", err);
  }
});

const editingItem = ref<OutlineItemType>({
  id: "",
  id_level: 1,
  title: "",
  font: "宋体",
  size: "",
  color: "#000000",
  bold: false,
  italic: false,
});
const dialogVisible = ref(false);
const importDialog = ref(false);
const classIfication = ref<String>("公开");
const selecTexportTemplate = ref<any>([]);

const wordFonts = [
  {
    label: "中文字体",
    options: [
      { value: "宋体", label: "宋体" },
      { value: "黑体", label: "黑体" },
      { value: "微软雅黑", label: "微软雅黑" },
    ],
  },
  {
    label: "英文字体",
    options: [
      { value: "Arial", label: "Arial" },
      { value: "Times New Roman", label: "Times New Roman" },
      { value: "Calibri", label: "Calibri" },
    ],
  },
];

const wordFontSizes = [
  { name: "小四", value: 12 },
  { name: "四号", value: 14 },
  { name: "小三", value: 15 },
  { name: "三号", value: 16 },
  { name: "小二", value: 18 },
  { name: "二号", value: 22 },
];

// 新增：计算位置选项
const positionOptions = computed(() => {
  const count = currentTemplate.value.structure?.length || 0;
  const options = [];
  for (let i = 1; i <= count + 1; i++) {
    options.push({
      value: i,
      label: `第 ${i} 段${i === count + 1 ? " (末尾)" : ""}`,
    });
  }
  return options;
});

// 新增：计算移动段落的选项
const moveParagraphOptions = computed(() => {
  const count = currentTemplate.value.structure?.length || 0;
  const options = [];
  for (let i = 1; i <= count; i++) {
    options.push({
      value: i,
      label: `第 ${i} 段`,
    });
  }
  return options;
});

// 新增：计算移动层级选项
const moveLevelOptions = computed(() => {
  if (!moveTarget.value.paragraph) return [];

  const paragraphIndex = moveTarget.value.paragraph - 1;
  const paragraph = currentTemplate.value.structure[paragraphIndex];
  if (!paragraph) return [];

  // 获取该段落的所有可能层级
  const levels = new Set<number>();
  const collectLevels = (item: OutlineItemType) => {
    levels.add(item.id_level);
    if (item.children) {
      item.children.forEach((child) => collectLevels(child));
    }
  };
  collectLevels(paragraph);

  // 添加下一个可能的层级
  const maxLevel = Math.max(...Array.from(levels));
  if (maxLevel < 6) {
    levels.add(maxLevel + 1);
  }

  // 转换为选项
  return Array.from(levels)
    .sort((a, b) => a - b)
    .map((level) => ({
      value: level,
      label: `${level} 级标题`,
    }));
});

// 新增：打开移动对话框
const openMoveDialog = (item: OutlineItemType) => {
  movingItem.value = item;
  moveTarget.value = {
    paragraph: null,
    level: null,
  };
  moveDialogVisible.value = true;
};

// 新增：处理段落选择变化
const handleParagraphChange = () => {
  moveTarget.value.level = null;
};

// 新增：获取移动预览文本
const getMovePreviewText = () => {
  if (
    !moveTarget.value.paragraph ||
    !moveTarget.value.level ||
    !movingItem.value
  )
    return "";

  const paragraphIndex = moveTarget.value.paragraph - 1;
  const paragraph = currentTemplate.value.structure[paragraphIndex];

  if (!paragraph) return "";

  if (moveTarget.value.level === 1) {
    return `将标题移动到第 ${moveTarget.value.paragraph} 段作为一级标题`;
  } else {
    return `将标题移动到第 ${moveTarget.value.paragraph} 段作为 ${moveTarget.value.level} 级标题`;
  }
};

// 新增：确认移动
const confirmMove = () => {
  if (
    !movingItem.value ||
    !moveTarget.value.paragraph ||
    !moveTarget.value.level
  ) {
    ElMessage.warning("请选择目标段落和层级");
    return;
  }

  const sourceItem = movingItem.value;
  const targetParagraphIndex = moveTarget.value.paragraph - 1;
  const targetLevel = moveTarget.value.level;

  // 从原位置删除
  const removeFromStructure = (items: OutlineItemType[]): boolean => {
    for (let i = 0; i < items.length; i++) {
      if (items[i].id === sourceItem.id) {
        items.splice(i, 1);
        return true;
      }
      if (items[i].children && removeFromStructure(items[i].children)) {
        return true;
      }
    }
    return false;
  };

  // 添加到目标位置
  const addToTarget = () => {
    const targetParagraph =
      currentTemplate.value.structure[targetParagraphIndex];

    // 更新移动项的层级
    sourceItem.id_level = targetLevel;

    if (targetLevel === 1) {
      // 如果目标层级是1级，添加到段落数组中
      currentTemplate.value.structure.splice(
        targetParagraphIndex,
        0,
        sourceItem
      );
    } else {
      // 如果目标层级大于1级，需要找到合适的位置插入到子项中
      const findInsertPosition = (
        items: OutlineItemType[],
        parentLevel: number
      ): boolean => {
        for (let i = items.length - 1; i >= 0; i--) {
          const item = items[i];

          if (item.id_level === targetLevel - 1) {
            // 找到父级标题，插入到其子项中
            if (!item.children) {
              item.children = [];
            }

            // 在子项中找到合适的插入位置（按层级顺序）
            let insertIndex = item.children.length;
            for (let j = 0; j < item.children.length; j++) {
              if (item.children[j].id_level >= targetLevel) {
                insertIndex = j;
                break;
              }
            }

            item.children.splice(insertIndex, 0, sourceItem);
            return true;
          }

          // 如果当前项层级小于目标层级-1，继续在其子项中查找
          if (item.id_level < targetLevel - 1 && item.children) {
            if (findInsertPosition(item.children, item.id_level)) {
              return true;
            }
          }
        }
        return false;
      };

      // 从目标段落的子项开始查找
      if (!findInsertPosition([targetParagraph], targetParagraph.id_level)) {
        // 如果找不到合适位置，需要构建层级结构
        const buildHierarchy = (
          items: OutlineItemType[],
          currentLevel: number
        ): boolean => {
          if (currentLevel >= targetLevel - 1) {
            return false;
          }

          for (let i = items.length - 1; i >= 0; i--) {
            const item = items[i];
            if (item.id_level === currentLevel) {
              if (!item.children) {
                item.children = [];
              }

              // 如果已经到达目标层级的上一级，直接插入
              if (currentLevel === targetLevel - 1) {
                item.children.push(sourceItem);
                return true;
              }

              // 否则继续在子项中查找
              if (buildHierarchy(item.children, currentLevel + 1)) {
                return true;
              }

              // 如果子项中没有合适位置，创建一个新的中间层级
              if (currentLevel < targetLevel - 1) {
                const intermediateItem = createOutlineItem(
                  `中间标题`,
                  currentLevel + 1
                );
                intermediateItem.children = [sourceItem];
                item.children.push(intermediateItem);
                return true;
              }
            }
          }
          return false;
        };

        if (!buildHierarchy([targetParagraph], targetParagraph.id_level)) {
          // 如果还是找不到，创建一个完整的层级链
          let currentParent = targetParagraph;
          for (
            let level = targetParagraph.id_level + 1;
            level < targetLevel;
            level++
          ) {
            const intermediateItem = createOutlineItem(`中间标题`, level);
            intermediateItem.children = [];
            if (!currentParent.children) {
              currentParent.children = [];
            }
            currentParent.children.push(intermediateItem);
            currentParent = intermediateItem;
          }
          if (!currentParent.children) {
            currentParent.children = [];
          }
          currentParent.children.push(sourceItem);
        }
      }
    }
  };

  // 执行移动操作
  removeFromStructure(currentTemplate.value.structure);
  addToTarget();

  // 强制更新视图
  currentTemplate.value = {
    ...currentTemplate.value,
    structure: [...currentTemplate.value.structure],
  };

  ElMessage.success("标题移动成功");
  moveDialogVisible.value = false;
  movingItem.value = null;
};

// 新增：关闭移动对话框
const handleMoveDialogClose = () => {
  moveDialogVisible.value = false;
  movingItem.value = null;
  moveTarget.value = {
    paragraph: null,
    level: null,
  };
};

// 其他现有方法保持不变...
const showAddToPositionDialog = () => {
  if (
    !currentTemplate.value.structure ||
    currentTemplate.value.structure.length === 0
  ) {
    // 如果没有一级标题，直接添加到开头
    addLevel1();
    ElMessage.info("已添加第一个一级标题");
    return;
  }
  addToPositionDialogVisible.value = true;
  selectedPosition.value = null;
};

const confirmAddToPosition = () => {
  if (!selectedPosition.value) {
    ElMessage.warning("请选择要添加的位置");
    return;
  }

  const position = selectedPosition.value;
  const newItem = createOutlineItem("新一级标题", 1);

  if (!Array.isArray(currentTemplate.value.structure)) {
    currentTemplate.value.structure = [];
  }

  // 在指定位置插入新的一级标题
  if (position > currentTemplate.value.structure.length) {
    // 如果位置超过当前长度，添加到末尾
    currentTemplate.value.structure.push(newItem);
  } else {
    // 在指定位置插入，后续元素后移
    currentTemplate.value.structure.splice(position - 1, 0, newItem);
  }

  // 强制更新视图
  currentTemplate.value = {
    ...currentTemplate.value,
    structure: [...currentTemplate.value.structure],
  };

  ElMessage.success(`已成功在第 ${position} 段添加新一级标题`);
  addToPositionDialogVisible.value = false;
  selectedPosition.value = null;
};

const handleAddToPositionClose = () => {
  addToPositionDialogVisible.value = false;
  selectedPosition.value = null;
};

const movePositionUp = (item: OutlineItemType) => {
  console.log("FormatPage: 位置上移", item.title);
  const findAndMove = (items: OutlineItemType[]): boolean => {
    for (let i = 0; i < items.length; i++) {
      if (items[i].id === item.id) {
        if (i > 0) {
          [items[i - 1], items[i]] = [items[i], items[i - 1]];
          return true;
        }
        return false;
      }

      if (Array.isArray(items[i].children)) {
        if (findAndMove(items[i].children)) {
          return true;
        }
      }
    }
    return false;
  };

  const success = findAndMove(currentTemplate.value.structure);
  console.log("位置上移结果:", success);

  currentTemplate.value = {
    ...currentTemplate.value,
    structure: [...currentTemplate.value.structure],
  };
};

const movePositionDown = (item: OutlineItemType) => {
  console.log("FormatPage: 位置下移", item.title);

  const findAndMove = (items: OutlineItemType[]): boolean => {
    for (let i = 0; i < items.length; i++) {
      if (items[i].id === item.id) {
        if (i < items.length - 1) {
          [items[i], items[i + 1]] = [items[i + 1], items[i]];
          return true;
        }
        return false;
      }

      if (Array.isArray(items[i].children)) {
        if (findAndMove(items[i].children)) {
          return true;
        }
      }
    }
    return false;
  };

  const success = findAndMove(currentTemplate.value.structure);
  console.log("位置下移结果:", success);

  currentTemplate.value = {
    ...currentTemplate.value,
    structure: [...currentTemplate.value.structure],
  };
};

const moveLevelUp = (item: OutlineItemType) => {
  console.log("FormatPage: 层级上移", item.title, "当前层级:", item.id_level);

  if (item.id_level <= 1) {
    console.log("一级标题不能再上移层级");
    return;
  }

  const findAndPromote = (
    items: OutlineItemType[],
    parentItems?: OutlineItemType[]
  ): boolean => {
    for (let i = 0; i < items.length; i++) {
      if (items[i].id === item.id) {
        const newLevel = item.id_level - 1;

        if (parentItems && newLevel === parentItems[0]?.id_level) {
          const [removed] = items.splice(i, 1);
          removed.id_level = newLevel;
          const parentIndex = parentItems.indexOf(items);
          if (parentIndex !== -1) {
            parentItems.splice(parentIndex + 1, 0, removed);
          } else {
            parentItems.push(removed);
          }
        } else {
          items[i].id_level = newLevel;
        }
        return true;
      }

      if (Array.isArray(items[i].children)) {
        if (findAndPromote(items[i].children, items)) {
          return true;
        }
      }
    }
    return false;
  };

  const success = findAndPromote(currentTemplate.value.structure);
  console.log("层级上移结果:", success);

  currentTemplate.value = {
    ...currentTemplate.value,
    structure: [...currentTemplate.value.structure],
  };
};

const moveLevelDown = (item: OutlineItemType) => {
  console.log(
    "FormatPage: 层级下移",
    item.title,
    "当前层级:",
    item.id_level,
    item
  );
  if (item.children.length == 0) {
    ElMessage.warning("当前标题没有子标题无法下移！");
    return false;
  }
  const findAndDemote = (items: OutlineItemType[]): boolean => {
    for (let i = 0; i < items.length; i++) {
      if (items[i].id === item.id) {
        const newLevel = item.id_level + 1;
        items[i].id_level = newLevel;

        if (i > 0) {
          const prevSibling = items[i - 1];
          if (!prevSibling.children) {
            prevSibling.children = [];
          }
          const [demotedItem] = items.splice(i, 1);
          prevSibling.children.push(demotedItem);
        }
        return true;
      }

      if (Array.isArray(items[i].children)) {
        if (findAndDemote(items[i].children)) {
          return true;
        }
      }
    }
    return false;
  };

  const success = findAndDemote(currentTemplate.value.structure);
  console.log("层级下移结果:", success);

  currentTemplate.value = {
    ...currentTemplate.value,
    structure: [...currentTemplate.value.structure],
  };
};

const removeChild = ({
  parent,
  index,
}: {
  parent: OutlineItemType;
  index: number;
}) => {
  if (Array.isArray(parent.children)) {
    parent.children.splice(index, 1);
    currentTemplate.value = {
      ...currentTemplate.value,
      structure: [...currentTemplate.value.structure],
    };
  }
};

const createNewTemplate = () => {
  currentTemplate.value = {
    id: generateTemplateId(""),
    name: "",
    structure: [],
  };
};

const createOutlineItem = (title: string, level: number): OutlineItemType => ({
  id: Date.now().toString(),
  title,
  font: "宋体",
  size: 14,
  color: "#000000",
  bold: false,
  italic: false,
  id_level: level,
  children: [],
});

const addLevel1 = () => {
  if (!Array.isArray(currentTemplate.value.structure)) {
    currentTemplate.value.structure = [];
  }
  currentTemplate.value.structure.push(createOutlineItem("新一级标题", 1));
};

const openEditDialog = (item: OutlineItemType) => {
  editingItem.value = { ...item };
  dialogVisible.value = true;
};

const confirmEdit = (updated: OutlineItemType) => {
  const updateItem = (items: OutlineItemType[]): boolean => {
    for (let i = 0; i < items.length; i++) {
      if (items[i].id === updated.id) {
        items[i] = { ...updated };
        return true;
      }

      const children = items[i].children;
      if (Array.isArray(children) && updateItem(children)) {
        return true;
      }
    }
    return false;
  };

  updateItem(currentTemplate.value.structure);
  dialogVisible.value = false;
};

const cancelEdit = () => {
  dialogVisible.value = false;
};

const addChild = (parent: OutlineItemType) => {
  const nextLevel = (parent.id_level || 1) + 1;
  parent.children = parent.children || [];
  parent.children.push(createOutlineItem("新子标题", nextLevel));
};

const removeOutline = (index: number) => {
  currentTemplate.value.structure.splice(index, 1);
};

const saveTemplate = async () => {
  const name = currentTemplate.value.name?.trim();
  if (!name) {
    console.warn("模板名称不能为空");
    return;
  }

  if (!currentTemplate.value.id || /^\d+$/.test(currentTemplate.value.id)) {
    currentTemplate.value.id = generateTemplateId(name);
  }

  const index = templates.value.findIndex(
    (t) => t.id === currentTemplate.value.id
  );
  const newTemplate: TemplateData = {
    id: currentTemplate.value.id,
    name: currentTemplate.value.name,
    structure: currentTemplate.value.structure,
  };

  if (index === -1) {
    templates.value.push(newTemplate);
  } else {
    templates.value[index] = newTemplate;
  }

  try {
    const res = await fetch(API.SAVE_TEMPLATE, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Token " + localStorage.getItem("token"),
      },
      body: JSON.stringify({
        type: "format",
        ...newTemplate,
      }),
    });
    const result = await res.json();
    if (!result.success) {
      console.error("保存失败:", result.error);
    }
  } catch (err) {
    console.error("请求出错:", err);
  }
  eventBus.emit("template-updated");
};

const selectTemplate = (template: TemplateData) => {
  currentTemplate.value = JSON.parse(JSON.stringify(template));
  if (!Array.isArray(currentTemplate.value.structure)) {
    currentTemplate.value.structure = [];
  }
};

const importTemplate = async (event: Event) => {
  const file = (event.target as HTMLInputElement).files?.[0];
  if (!file) return;

  try {
    const text = await file.text();
    const json = JSON.parse(text);

    if (!json.id || !json.name || !Array.isArray(json.structure)) {
      console.error("导入失败：模板格式不正确");
      return;
    }

    currentTemplate.value = json;
    const index = templates.value.findIndex((t) => t.id === json.id);
    if (index === -1) {
      templates.value.push({
        id: json.id,
        name: json.name,
        structure: json.structure,
      });
    }

    await fetch(API.SAVE_TEMPLATE, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Token " + localStorage.getItem("token"),
      },
      body: JSON.stringify({
        type: "format",
        ...json,
      }),
    });

    console.log("导入并保存成功");
  } catch (err) {
    console.error("导入失败:", err);
  }
};

const exportTemplate = (template?: any) => {
  selecTexportTemplate.value = template;
  importDialog.value = true;
};

const submitexportTemplate = () => {
  const data = selecTexportTemplate.value || currentTemplate.value;
  if (!data || !data.id) {
    console.warn("没有可导出的模板");
    return;
  }

  const json = JSON.stringify(data, null, 2);
  const blob = new Blob([json], { type: "application/json" });
  const url = URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;
  a.download = `(${classIfication.value})${data.name || "未命名模板"}.json`;
  a.click();

  URL.revokeObjectURL(url);
  importDialog.value = false;
};

const deleteTemplate = async (templateId: string, templateName: string) => {
  try {
    const res = await fetch(API.DELETE_TEMPLATE, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Token " + localStorage.getItem("token"),
      },
      body: JSON.stringify({
        id: templateId,
        type: "format",
        name: templateName || "",
      }),
    });
    const result = await res.json();
    if (result.success) {
      templates.value = templates.value.filter((t) => t.id !== templateId);
      if (currentTemplate.value.id === templateId) {
        currentTemplate.value = { id: "", name: "", structure: [] };
      }
    } else {
      console.error("删除失败:", result.error);
    }
  } catch (err) {
    console.error("删除请求出错:", err);
  }
};

const generateTemplateId = (name: string) => {
  const safeName = (name || "未命名模板").replace(
    /[^a-zA-Z0-9\u4e00-\u9fa5_-]/g,
    ""
  );
  return `${Date.now()}_${safeName}`;
};

const handleClose = () => {
  dialogVisible.value = false;
};
const handleUpdateClose = () => {
  dialogUpdate.value = false;
};

const customUploadWithFetch = async (options: any) => {
  loading.value = true;
  const { file, onSuccess, onError, onProgress } = options;

  try {
    const formData = new FormData();
    formData.append("file", file);
    const response = await fetch(
      "http://192.168.0.97:8274/api/templates/save-template2",
      {
        method: "POST",
        headers: {
          Authorization: "Token " + token.value,
        },
        body: formData,
      }
    );

    if (response.ok) {
      const result = await response.json();
      onSuccess(result, response);
      ElMessage.success("文件上传成功！");
      dialogUpdate.value = false;
      loading.value = false;
    } else {
      throw new Error("上传失败");
    }
  } catch (error) {
    onError(error);
    ElMessage.error("文件上传失败！");
  }
};
</script>

<style scoped>
.format-page-wrapper {
  width: 100%;
  display: flex;
  justify-content: center;
  padding-top: 30px;
}
.format-page {
  max-width: 1200px;
  width: 100%;
}
.sidebar {
  padding-right: 10px;
}
.editor {
  padding-left: 10px;
}
.outline-structure {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.add-button-wrapper {
  margin-bottom: 12px;
  text-align: left;
  display: flex;
  gap: 12px;
}
.add-button-wrapper .el-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 38px;
  padding: 0 20px;
  font-size: 14px;
  line-height: 1;
}
.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.template-item {
  display: flex !important;
  flex-direction: column !important;
  align-items: flex-start !important;
  padding-bottom: 12px;
}

.template-name {
  font-weight: bold;
  margin-bottom: 6px;
}

.template-actions {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.template-actions .el-button {
  border-radius: 2 !important;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 35px;
  height: 28px;
  padding: 0;
}
.classIfication {
  width: 100%;
  display: flex;
  justify-content: center;
}

/* 新增样式 */
.add-to-position-content {
  padding: 10px 0;
}

.dialog-tip {
  margin-top: 15px;
}

.move-dialog-content {
  padding: 10px 0;
}

.move-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 16px;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-item label {
  font-weight: 500;
  color: #606266;
}

.move-preview {
  margin-top: 10px;
}
</style>