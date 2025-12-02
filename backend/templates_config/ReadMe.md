# 📄 模板配置模块 API 文档（Django + ORM）

本模块用于管理结构化文档模板的 API 接口，提供模板的创建、编辑、删除、查询、导出等能力，数据使用 ORM 模型统一存储在数据库中。

---

## 📦 模块作用概览

| 功能         | 说明                                                                 |
|--------------|----------------------------------------------------------------------|
| 模板结构配置 | 支持新建、编辑、删除、列表展示等功能（数据库存储）                   |
| 模板导出导入 | 可导出为本地 JSON 文件，支持导入回填                                |
| 多端共享配置 | 所有模板持久存储在后端数据库，支持多端复用                          |

---

## 📡 接口总览

接口统一前缀：`http://localhost:8899/api/templates/`

---

## 🟢 1. 获取模板列表

> **方法类型**：GET  
> **接口地址**：`/list-templates?type=format`

### ✅ 示例返回：

```json
{
  "success": true,
  "templates": [
    {
      "id": "1749999999999_青年基金",
      "name": "青年基金",
      "structure": [
        {
          "id": "123456",
          "title": "一、背景需求",
          "font": "宋体",
          "size": "四号",
          "color": "#000000",
          "bold": true,
          "italic": false,
          "children": []
        }
      ]
    }
  ]
}
```

---

## 🟡 2. 保存模板

> **方法类型**：POST  
> **接口地址**：`/save-template`  
> **Content-Type**：application/json

### ✅ 请求参数：

```json
{
  "type": "format",
  "id": "1749999999999_青年基金",
  "name": "青年基金",
  "structure": [
    {
      "id": "xxx",
      "title": "一级标题",
      "font": "宋体",
      "size": "四号",
      "color": "#000000",
      "bold": true,
      "italic": false,
      "children": []
    }
  ]
}
```

### ✅ 返回示例：

```json
{
  "success": true,
  "created": true
}
```

---

## 🔴 3. 删除模板

> **方法类型**：POST  
> **接口地址**：`/delete-template`  
> **Content-Type**：application/json

### ✅ 请求参数：

```json
{
  "type": "format",
  "id": "1749999999999_青年基金"
}
```

### ✅ 成功返回：

```json
{
  "success": true
}
```

### ❌ 失败返回（模板不存在）：

```json
{
  "success": false,
  "error": "Template not found"
}
```

---

## 📁 说明

- 所有接口统一路径为：`/api/templates/`
- 模板 ID 格式建议为：`时间戳_模板名`，确保唯一性和可读性
- `structure` 为模板结构定义，采用树形 JSON 数据格式
- 本模块已适配数据库存储（Django ORM），支持多用户并发安全使用

---

✅ 本文档支持直接复制粘贴至 `README.md` 或接口文档中使用，如需接口扩展（分页、用户绑定、模板类型分类）可继续拓展说明。
如需表结构、模型定义、Swagger 接入文档请联系开发负责人。