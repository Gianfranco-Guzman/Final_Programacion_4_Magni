import axiosClient from './axiosClient'

export interface CloudinaryUploadResponse {
  secure_url: string
  public_id: string
  width: number
  height: number
  format: string
  resource_type: string
}

export const uploadsApi = {
  uploadImagen: async (file: File, folder = 'foodstore/productos'): Promise<CloudinaryUploadResponse> => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('folder', folder)

    const response = await axiosClient.post<CloudinaryUploadResponse>('/uploads/imagen', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  deleteImagen: async (publicId: string): Promise<void> => {
    await axiosClient.delete(`/uploads/imagen/${encodeURIComponent(publicId)}`)
  },
}
