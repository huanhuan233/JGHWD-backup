// src/api/outline.ts
import { API } from "@/api";
export interface OutlineMeta {
  id: number
  title: string
  model_name: string
  created_at: string
}

export interface OutlineDetail {
  id: number
  title: string
  model_name: string
  template: string 
  structure: OutlineSection[]
  created_at: string
  updated_at: string
  original_structure?: any[]
}

export interface OutlineSection {
  title: string
  content: string
}

// 所有大纲列表
export async function fetchOutlineList(): Promise<OutlineMeta[]> {
  const res = await fetch(API.BASE_URL +'/outlines/',{headers:{
    Authorization: "Token " + localStorage.getItem("token"),
  }})
  if (!res.ok) throw new Error('加载大纲列表失败')
  return await res.json()
}
// 调用后端API生成正文
// export async function autoGenerate(requestData:any){
//   const res = await fetch('/api/contents/auto-generate/', {
//     method: 'POST',
//     headers: { 'Content-Type': 'application/json' },
//       body: JSON.stringify(requestData),
//   })
//   if (!res.ok) throw new Error('创建大纲失败')
//   return await res.json()
// }
// 获取某个大纲详情（包括 structure）
export async function fetchOutlineDetail(id: number): Promise<OutlineDetail> {
  const res = await fetch(API.BASE_URL +`/outlines/${id}/`,{
    headers:{
      Authorization: "Token " + localStorage.getItem("token"),
    }
  })
  if (!res.ok) throw new Error('加载大纲详情失败')
  return await res.json()
}

// 删除某个大纲
export async function deleteOutline(id: number): Promise<void> {
  const res = await fetch(API.BASE_URL +`/outlines/${id}/`, {
    method: 'DELETE',
    headers:{
      Authorization: "Token " + localStorage.getItem("token"),
    }
  })
  if (!res.ok) throw new Error('删除失败')
}

// 新建大纲
export async function createOutline(data: {
  title: string
  model_name: string
  structure: OutlineSection[]
}): Promise<OutlineDetail> {
  const res = await fetch(API.BASE_URL +'/outlines/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json',Authorization: "Token " + localStorage.getItem("token"), },
    body: JSON.stringify(data)
  })
  if (!res.ok) throw new Error('创建大纲失败')
  return await res.json()
}
