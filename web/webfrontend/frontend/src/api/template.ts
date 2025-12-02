// src/api/template.ts
import { API } from "@/api";
export async function fetchTemplateList(): Promise<any[]> {
  try {
    const response = await fetch(API.BASE_URL+'/templates/list-templates?type=format',{
      headers:{
        Authorization: "Token " + localStorage.getItem("token"),
      }
    })
    if (!response.ok) throw new Error('模板获取失败')
    const result = await response.json()
    return result.templates || []
  } catch (error) {
    console.error('❌ 获取模板列表失败:', error)
    return []
  }
}
