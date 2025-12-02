import { onMounted, ref } from 'vue'
import { fetchKnowledgeOptions } from '@/utils/loadKnowledgeConfigs'

// 定义类型
export interface KnowledgeOption {
  label: string
  value: string
}

export function useKnowledgeOptions() {
  const knowledgeOptions = ref<KnowledgeOption[]>([])

  const loadOptions = async () => {
    try {
      knowledgeOptions.value = await fetchKnowledgeOptions()
    } catch (err) {
      console.error('❌ 加载知识库下拉选项失败:', err)
      knowledgeOptions.value = []
    }
  }

  onMounted(loadOptions)

  return {
    knowledgeOptions,
    loadOptions,
  }
}
