import { useMutation } from '@tanstack/react-query'

import { uploadsApi } from '@api/uploadsApi'

export const useUploadImagen = () => {
  return useMutation({
    mutationFn: ({ file, folder }: { file: File; folder?: string }) => uploadsApi.uploadImagen(file, folder),
  })
}

export const useDeleteImagen = () => {
  return useMutation({
    mutationFn: (publicId: string) => uploadsApi.deleteImagen(publicId),
  })
}
