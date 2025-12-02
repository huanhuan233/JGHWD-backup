// src/api/request.ts
import axios from 'axios'

const request = axios.create({
  baseURL: '/', // 或 http://localhost:8899/ 如果你前后端不在一个端口
  timeout: 10000,
})

request.interceptors.response.use(
  (res) => res.data,
  (err) => {
    console.error('请求错误:', err)
    return Promise.reject(err)
  }
)

export default request
