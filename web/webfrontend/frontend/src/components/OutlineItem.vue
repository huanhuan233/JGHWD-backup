<template>
  <div class="outline-item1">
    <el-row align="middle" justify="space-between">
      <el-col :span="14">
        <div class="outline-title1" :style="getItemStyle(item)" :class="getLevelClass(item.id_level)">
          <!-- <span class="level-badge">{{ item.id_level }}</span> -->
          {{ item.title }}
        </div>
      </el-col>
      <el-col :span="10" class="outline-actions1">
        <el-button class="icon-btn1" size="small" @click="handleEdit" title="编辑">
          <el-icon><Edit /></el-icon>
        </el-button>
        <el-button class="icon-btn1" size="small" @click="handleAddChild" title="添加子项">
          <el-icon><Plus /></el-icon>
        </el-button>
        <!-- 新增：移动按钮 -->
        <el-button class="icon-btn1" size="small" type="warning" @click="handleMove" title="移动">
          <el-icon><Position /></el-icon>
        </el-button>
        <el-button class="icon-btn1" size="small" type="danger" @click="handleRemove" title="删除">
          <el-icon><Delete /></el-icon>
        </el-button>
      </el-col>
    </el-row>
    <div class="outline-children1">
      <OutlineItem
        v-for="(child, index) in item.children"
        :key="child.id"
        :item="child"
        @edit="$emit('edit', $event)"
        @add-child="$emit('add-child', $event)"
        @remove="() => $emit('remove-child', { parent: item, index })"
        @position-up="$emit('position-up', $event)"
        @position-down="$emit('position-down', $event)"
        @level-up="$emit('level-up', $event)"
        @level-down="$emit('level-down', $event)"
        @move="$emit('move', $event)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue'
import type { OutlineItemType } from './types'
import { Edit, Plus, Delete, Top, Bottom, ArrowUp, ArrowDown, Position } from '@element-plus/icons-vue'
const props = defineProps<{ 
  item: OutlineItemType 
}>()
const emit = defineEmits([
  'edit', 
  'add-child', 
  'remove', 
  'position-up', 
  'position-down', 
  'level-up', 
  'level-down',
  'remove-child',
  'move'  // 新增：移动事件
])

// 根据层级返回不同的样式类
const getLevelClass = (level: number) => {
  return `level-${level}`
}

const getItemStyle = (item: OutlineItemType) => {
  // 根据层级动态调整字体大小
  const baseSizes: Record<number, string> = {
    1: '20px',
    2: '18px', 
    3: '16px',
    4: '14px',
    5: '13px',
    6: '12px'
  }
  
  const baseSize = baseSizes[item.id_level] || '14px'
  
  return {
    fontFamily: item.font,
    fontSize: item.size ? sizeMap[item.size] : baseSize,
    color: item.color,
    fontWeight: item.bold ? 'bold' : 'normal',
    fontStyle: item.italic ? 'italic' : 'normal',
  }
}

const sizeMap: Record<string, string> = {
  '初号': '42px',
  '小初': '36px',
  '一号': '26px',
  '小一': '24px',
  '二号': '22px',
  '小二': '18px',
  '三号': '16px',
  '四号': '14px',
  '五号': '12px',
  '小五': '10.5px',
  '六号': '9px',
  '七号': '7.5px',
}

// 事件处理方法
const handlePositionUp = () => {
  console.log('OutlineItem: 位置上移按钮点击', props.item.title)
  emit('position-up', props.item)
}

const handlePositionDown = () => {
  console.log('OutlineItem: 位置下移按钮点击', props.item.title)
  emit('position-down', props.item)
}

const handleLevelUp = () => {
  console.log('OutlineItem: 层级上移按钮点击', props.item.title, '当前层级:', props.item.id_level)
  emit('level-up', props.item)
}

const handleLevelDown = () => {
  console.log('OutlineItem: 层级下移按钮点击', props.item.title, '当前层级:', props.item.id_level)
  emit('level-down', props.item)
}

const handleEdit = () => {
  emit('edit', props.item)
}

const handleAddChild = () => {
  emit('add-child', props.item)
}

// 新增：移动按钮处理
const handleMove = () => {
  emit('move', props.item)
}

const handleRemove = () => {
  emit('remove')
}
</script>

<style scoped>
.outline-item1 {
  padding: 10px;
  margin-bottom: 10px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  background: #fff;
  transition: all 0.3s ease;
}

.outline-actions1 {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.outline-children1 {
  padding-left: 20px;
  margin-top: 8px;
}

.outline-title1 {
  font-weight: 500;
  line-height: 1.6;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.level-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: #409eff;
  color: white;
  border-radius: 50%;
  font-size: 12px;
  font-weight: bold;
}

/* 不同层级的样式 */
.level-1 .level-badge {
  background: #f56c6c;
}

.level-2 .level-badge {
  background: #e6a23c;
}

.level-3 .level-badge {
  background: #67c23a;
}

.level-4 .level-badge {
  background: #409eff;
}

.level-5 .level-badge {
  background: #909399;
}

.level-6 .level-badge {
  background: #c0c4cc;
}

/* 层级字体大小差异 */
.level-1 {
  font-size: 20px !important;
  font-weight: bold;
}

.level-2 {
  font-size: 18px !important;
  font-weight: bold;
}

.level-3 {
  font-size: 16px !important;
}

.level-4 {
  font-size: 14px !important;
}

.level-5 {
  font-size: 13px !important;
}

.level-6 {
  font-size: 12px !important;
}

.icon-btn1 {
  width: 32px;
  height: 32px;
  padding: 0;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>