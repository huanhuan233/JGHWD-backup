<template>
  <div class="header-upload-page">
    <el-card class="upload-card">
      <template #header>
        <div class="card-header">
          <span>上传标头信纸</span>
        </div>
      </template>

      <el-upload
        class="upload-area"
        action="/api/headers/upload/"
        :on-success="handleUploadSuccess"
        :on-remove="handleRemove"
        :file-list="headerFiles"
        :limit="5"
        list-type="picture-card"
        :auto-upload="true"
      >
        <template #file="{ file }">
          <div class="file-preview">
            <img v-if="file.url?.endsWith('.png') || file.url?.endsWith('.jpg')" :src="file.url" class="image-preview" />
            <span class="file-name">{{ file.name }}</span>
          </div>
        </template>
      </el-upload>
    </el-card>

    <el-card class="saved-list" style="margin-top: 20px;">
      <template #header>
        <span>已保存标头</span>
      </template>
      <el-table :data="savedHeaders" border>
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="uploadTime" label="上传时间" />
        <el-table-column label="操作" width="180">
          <template #default="scope">
            <el-button type="text" size="small" @click="handlePreview(scope.row)">预览</el-button>
            <el-button type="danger" size="small" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="previewVisible" title="标头预览" width="50%">
      <div v-if="isImage(previewImage)">
        <img :src="previewImage" alt="预览图片" style="width: 100%;" />
      </div>
      <p v-else>该文件暂不支持预览</p>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getHeaders, deleteHeader } from '@/api/header'

const headerFiles = ref<any[]>([])
const savedHeaders = ref<any[]>([])
const previewVisible = ref(false)
const previewImage = ref('')

const handleUploadSuccess = () => {
  ElMessage.success('上传成功')
  fetchSavedHeaders()
}

const handleRemove = () => {
  ElMessage.info('已从上传列表中移除')
}

const handlePreview = (row: any) => {
  previewImage.value = row.url
  previewVisible.value = true
}

const handleDelete = async (row: any) => {
  await deleteHeader(row.id)
  ElMessage.success('删除成功')
  fetchSavedHeaders()
}

const fetchSavedHeaders = async () => {
  const res = await getHeaders()
  savedHeaders.value = res
}

const isImage = (url: string) => {
  return url.endsWith('.png') || url.endsWith('.jpg') || url.endsWith('.jpeg')
}

onMounted(() => {
  fetchSavedHeaders()
})
</script>

<style scoped>
.header-upload-page {
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.image-preview {
  width: 100%;
  border-radius: 4px;
}
.file-name {
  display: block;
  text-align: center;
  margin-top: 4px;
}
</style>
