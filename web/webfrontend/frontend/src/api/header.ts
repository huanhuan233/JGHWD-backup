import request from './request'

export function getHeaders() {
  return request.get('/api/headers/')
}

export function deleteHeader(id: number) {
  return request.delete(`/api/headers/${id}/`)
}

export function uploadHeader(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/api/headers/upload/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}
