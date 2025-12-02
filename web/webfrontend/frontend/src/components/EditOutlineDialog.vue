<template>
  <el-dialog v-model="visible" title="编辑标题">
    <el-form label-width="80px">
      <el-form-item label="标题">
        <el-input v-model="localItem.title" />
      </el-form-item>
      <el-form-item label="字体">
        <!-- <el-select v-model="localItem.font">
          <el-option v-for="f in fonts" :key="f" :label="f" :value="f" />
        </el-select> -->
        <el-select v-model="localItem.font"  >
          <el-option-group
            v-for="group in fonts"
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
      <el-form-item label="字号">
        <el-select v-model="localItem.size">
          <el-option v-for="s in sizes" :key="s.value" :label="s.name" :value="s.value" />
        </el-select>
      </el-form-item>
      <el-form-item label="颜色"> 
        <el-color-picker v-model="localItem.color" color-format="rgb"  />
      </el-form-item>
      <el-form-item label="样式">
        <el-checkbox v-model="localItem.bold">加粗</el-checkbox>
        <el-checkbox v-model="localItem.italic">斜体</el-checkbox>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="$emit('cancel')">取消</el-button>
      <el-button type="primary" @click="onConfirm">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch, defineProps, defineEmits } from "vue";
import type { OutlineItemType } from "./types";

const props = defineProps<{
  modelValue: boolean;
  item: OutlineItemType;
  fonts: any[];
  sizes: any[];
}>();
const emit = defineEmits(["update:modelValue", "confirm", "cancel"]);

const visible = ref(props.modelValue);
watch(
  () => props.modelValue,
  (val) => (visible.value = val)
);
watch(visible, (val) => emit("update:modelValue", val));

const localItem = ref({ ...props.item });
watch(
  () => props.item,
  (val) => (localItem.value = { ...val })
);

const onConfirm = () => {
  emit("confirm", { ...localItem.value });
  visible.value = false;
};
</script>

<style scoped>
.el-form-item {
  margin-bottom: 16px;
}
</style>
