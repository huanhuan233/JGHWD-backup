import { defineStore } from 'pinia'

export interface OutlineItem {
  title: string
  content: string
}

export interface DebugPrompt {
  title: string
  prompt: string
}

export interface DebugKnowledge {
  title: string
  kb: string
}

export interface DebugInfo {
  prompts: DebugPrompt[]
  knowledge_snippets: DebugKnowledge[]
}

export const useOutlineStore = defineStore('outline', {
  state: () => ({
    title: '',  // ✅ 新增字段
    articleTitle: '',
    outlineItems: [] as OutlineItem[],
    knowledgeUsed: '',
    debugInfo: {
      prompts: [],
      knowledge_snippets: []
    } as DebugInfo
  }),
  actions: {
    setOutline(title: string, items: OutlineItem[], debug?: DebugInfo) {
      this.articleTitle = title
      this.outlineItems = items
      this.debugInfo = debug || {
        prompts: [],
        knowledge_snippets: []
      }
    },
    setKnowledge(knowledge: string) {
      this.knowledgeUsed = knowledge
    },
    clear() {
      this.articleTitle = ''
      this.outlineItems = []
      this.knowledgeUsed = ''
      this.debugInfo = {
        prompts: [],
        knowledge_snippets: []
      }
    }
  }
})
