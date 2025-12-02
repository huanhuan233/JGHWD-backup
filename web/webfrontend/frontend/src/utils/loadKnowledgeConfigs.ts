import { onMounted, ref } from 'vue'
import { API } from '@/api'
// 声明类型结构
interface KnowledgeOption {
  label: string
  value: string
}

const knowledgeOptions = ref<KnowledgeOption[]>([])

export async function fetchKnowledgeOptions(): Promise<KnowledgeOption[]> {
  try {
    const response = await fetch(API.BASE_URL+'/knowledge/configs/',{headers:{Authorization: "Token " + localStorage.getItem("token")}})
    const result = await response.json()

    if (!Array.isArray(result.configs)) {
      console.error('❌ 返回格式错误：', result)
      return []
    }

    return result.configs.map((conf: any) => {
      const base = `${conf.type}_${conf.name.replace(/\s/g, '_')}`
      return {
        label: `${conf.name} (${conf.type})`,
        value: base
      }
    })
  } catch (err) {
    console.error('❌ 加载知识库配置失败:', err)
    return []
  }
}


// 导出给组件使用
export { knowledgeOptions }
