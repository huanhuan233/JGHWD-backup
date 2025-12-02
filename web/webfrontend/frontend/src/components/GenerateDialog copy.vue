<!-- 大纲编辑页面弹窗组件 -->
<template>
  <el-dialog
    v-model="dialogVisible"
    title="生成正文设置"
    width="600px"
    @close="$emit('cancel')"
  >
    <el-form label-width="120px">
      <el-form-item label="选择模型">
        <el-select v-model="model" placeholder="请选择模型">
          <el-option
            v-for="item in modelOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="最小字数">
        <el-select v-model="minWords" placeholder="选择字数">
          <el-option v-for="num in [500, 1000, 1500, 2000, 2500, 3000, 3500, 4000]" :key="num" :label="num + '字'" :value="num" />
        </el-select>
      </el-form-item>

      <!-- <el-form-item label="正文字体">
        <el-select v-model="fontFamily" placeholder="选择字体">
          <el-option v-for="font in wordFonts" :key="font" :label="font" :value="font" />
        </el-select>
      </el-form-item>

      <el-form-item label="字体颜色">
        <el-color-picker v-model="fontColor" show-alpha />
        <el-input v-model="fontColor" placeholder="输入十六进制颜色值" style="margin-left: 12px; width: 140px" />
      </el-form-item>

      <el-form-item label="字体样式">
        <el-checkbox v-model="isBold">加粗</el-checkbox>
        <el-checkbox v-model="isItalic">斜体</el-checkbox>
      </el-form-item> -->

      <!-- <el-form-item label="标头样式">
        <el-select v-model="letterStyle" placeholder="选择标头样式">
          <el-option v-for="style in letterStyles" :key="style" :label="style" :value="style" />
        </el-select>
      </el-form-item> -->

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
      </el-form-item>

      <el-form-item label="自定义提示词">
        <el-input type="textarea" v-model="customPrompt" placeholder="可选提示词..." rows="3" />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="$emit('cancel')">取消</el-button>
      <el-button type="primary" @click="submitGenerate">开始生成</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { defineProps, defineEmits } from 'vue'
import { useKnowledgeOptions } from '@/composables/useKnowledgeOptions'
import { API } from "@/api";
import { onMounted } from 'vue' 
const props = defineProps<{ section: any }>()
const emit = defineEmits(['cancel', 'confirm'])

const dialogVisible = ref(true)

const model = ref('')
const modelOptions = ref<{ label: string; value: string }[]>([])

const minWords = ref(1000)
const wordFonts = ['宋体', '黑体', '微软雅黑', 'Times New Roman', 'Arial']
const fontFamily = ref('宋体')
const fontColor = ref('#000000')
const isBold = ref(false)
const isItalic = ref(false)

// const letterStyles = ['默认信纸', '红头文件', '简约蓝', '军工风']
// const letterStyle = ref('默认信纸')

const enableKnowledge = ref(false)
const { knowledgeOptions: knowledgeBases } = useKnowledgeOptions()
const selectedKB = ref('')
const customPrompt = ref('')

const submitGenerate = () => {
  emit('confirm', {
    model: model.value,
    minWords: minWords.value,
    fontFamily: fontFamily.value,
    fontColor: fontColor.value,
    isBold: isBold.value,
    isItalic: isItalic.value,
  //  letterStyle: letterStyle.value,
    enableKnowledge: enableKnowledge.value,
    selectedKB: selectedKB.value,
    customPrompt: customPrompt.value,
    section: props.section,
  })
}
const fetchModelOptions = async () => {
  try {
    const res = await fetch(API.BASE_URL+'/contents/models/',{headers:{Authorization: "Token " + localStorage.getItem("token"),}})
    const result = await res.json()
    if (result.success) {
      modelOptions.value = result.models.map((m: string) => ({
        label: m,
        value: m,
      }))
    } else {
      console.warn('模型列表获取失败：', result)
    }
  } catch (error) {
    console.error('❌ 获取模型列表失败:', error)
  }
}

onMounted(() => {
  fetchModelOptions()
})
</script>

<style scoped>
.el-form-item {
  margin-bottom: 18px;
}
</style>
