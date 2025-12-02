# 📘 知识库配置模块 API 接口文档（Django + ORM）

本模块用于管理大模型调用时所使用的知识库 API 配置。
包含前端页面配置、数据库存储、调用模板生成（自动写入 JSON 文件）等完整功能。

---

## 📁 模块作用概览

| 功能 | 说明 |
|------|------|
| 知识库配置管理 | 支持新增、编辑、删除、列表展示（数据库 ORM） |
| 知识库调用模板生成 | 每次保存配置会自动生成 JSON 请求模板文件（文件存储） |
| 多端共用配置 | 前端多个页面通过统一接口读取知识库下拉选项 |

---

## ✅ 接口总览

接口统一前缀：`http://localhost:8899/api/knowledge/configs/`

### 📌 1. 获取所有配置

- **方法**：GET
- **路径**：`/api/knowledge/configs/`
- **返回示例**：

```json
[
  {
    "id": 1,
    "name": "项目知识库",
    "type": "dify",
    "api_key": "app-xxxxx",
    "created_at": "2025-05-17T08:30:00Z"
  },
  ...
]
```

---

### 📌 2. 新建配置

- **方法**：POST
- **路径**：`/api/knowledge/configs/`
- **请求头**：`Content-Type: application/json`
- **请求体**：

```json
{
  "name": "项目知识库",
  "type": "dify",
  "api_key": "app-xxxxx"
}
```

- **成功响应**：

```json
{
  "success": true,
  "data": {
    "id": 3,
    "name": "项目知识库",
    "type": "dify",
    "api_key": "app-xxxxx"
  }
}
```

---

### 📌 3. 更新配置（编辑）

- **方法**：PUT
- **路径**：`/api/knowledge/configs/<id>/`
- **请求体**：同新增

---

### 📌 4. 删除配置

- **方法**：DELETE
- **路径**：`/api/knowledge/configs/?id=<id>`
- **示例**：

```
DELETE /api/knowledge/configs/?id=3
```

- **响应**：

```json
{
  "success": true,
  "message": "配置已删除"
}
```

---

## 📂 调用模板自动生成说明

每次新增 / 修改配置后，会根据知识库类型自动生成一份调用模板文件。

- **保存路径**：

```
backend/template_storage/knowledge_templates/<type>_<name>_<时间戳>.json
```

- **文件内容示例（type=dify）**：

```json
{
  "method": "POST",
  "url": "http://localhost:8080/v1/completion-messages",
  "headers": {
    "Authorization": "Bearer app-xxxxx",
    "Content-Type": "application/json"
  },
  "body": {
    "inputs": {
      "query": "请输入您的问题"
    },
    "response_mode": "streaming",
    "user": "abc-123"
  }
}
```

---

## 📄 前端使用建议

### 📌 获取知识库下拉列表

前端页面如 HomePage.vue、GenerateDialog.vue 可通过以下方式复用：

```ts
const { knowledgeOptions } = useKnowledgeOptions()
```

```html
<el-select v-model="selectedKnowledgeBase">
  <el-option
    v-for="item in knowledgeOptions"
    :key="item.value"
    :label="item.label"
    :value="item.value"
  />
</el-select>
```

---

### 📌 编辑配置（点击左侧配置加载到表单）

```ts
function selectConfig(index: number) {
  const config = savedConfigs.value[index]
  currentId.value = config.id
  form.value = {
    name: config.name,
    type: config.type,
    api_key: config.api_key
  }
}
```

---

## ✅ 模块优势

- 🔄 支持完整增删改查
- 🧩 可扩展支持多种类型知识库（如 Dify、Milvus、FAISS）
- 📁 文件模板便于独立调试调用结构
- 🔗 与 Vue 3 + Element Plus 高度集成

---
