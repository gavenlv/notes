// 类型定义文件
export interface User {
  id: number;
  name: string;
  email: string;
}

export interface ApiResponse<T> {
  data: T;
  message: string;
  code: number;
}