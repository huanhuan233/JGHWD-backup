// src/api/index.ts

const BASE_URL = import.meta.env.VITE_API_BASE || 'http://192.168.0.9:8899/api'

export const API = {
  MODELS: `${BASE_URL}/list-models/`,
  TEMPLATES: `${BASE_URL}/list-templates?type=format`,
  GENERATE_OUTLINE_ITEMS: `${BASE_URL}/generate-outline-items/`,

  // 👇 FormatPage.vue 用到的 API
  SAVE_TEMPLATE: `${BASE_URL}/templates/save-template`,
  DELETE_TEMPLATE: `${BASE_URL}/templates/delete-template`,

  // 👇 KnowledgeConfigPage.vue 用到的 API
  GET_KNOWLEDGE_CONFIGS: `${BASE_URL}/knowledge/configs/`,
  SAVE_KNOWLEDGE_CONFIG: `${BASE_URL}/knowledge/save-config`,
  DELETE_KNOWLEDGE_CONFIG: `${BASE_URL}/knowledge/configs/`,
  GET_KNOWLEDGE_CONFIG_DETAIL: (id?: string) =>
  id ? `${BASE_URL}/knowledge/configs/${id}/` : `${BASE_URL}/knowledge/configs/`,
  DELETE_ORPHAN_FILE: `${BASE_URL}/delete-orphan-file/`,
  // outlines
  OUTLINES: '/api/outlines/',
  BASE_URL:BASE_URL,
  GET_OUTLINE_DETAIL: (id: number) => `/api/outlines/${id}/`,
  DELETE_OUTLINE: (id: number) => `/api/outlines/${id}/`,
}
