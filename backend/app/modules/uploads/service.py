from fastapi import HTTPException, UploadFile, status

from app.core.config import get_settings

MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}


class UploadsService:
    @staticmethod
    def _get_cloudinary_sdk():
        settings = get_settings()
        if not settings.cloudinary_cloud_name or not settings.cloudinary_api_key or not settings.cloudinary_api_secret:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Cloudinary no configurado en el backend",
            )

        try:
            import cloudinary
            import cloudinary.uploader
        except ImportError as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="SDK de Cloudinary no instalado en el backend",
            ) from exc

        cloudinary.config(
            cloud_name=settings.cloudinary_cloud_name,
            api_key=settings.cloudinary_api_key,
            api_secret=settings.cloudinary_api_secret,
            secure=True,
        )
        return cloudinary

    @staticmethod
    async def subir_imagen(file: UploadFile, folder: str | None = None) -> dict:
        if file.content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de imagen no soportado. Solo jpeg, png y webp.",
            )

        file_bytes = await file.read()
        if not file_bytes:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Archivo vacío")
        if len(file_bytes) > MAX_IMAGE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La imagen supera el tamaño máximo permitido de 5 MB",
            )

        cloudinary = UploadsService._get_cloudinary_sdk()
        upload_result = cloudinary.uploader.upload(
            file_bytes,
            folder=folder or "foodstore/productos",
            resource_type="image",
            overwrite=False,
            unique_filename=True,
        )

        return {
            "secure_url": upload_result["secure_url"],
            "public_id": upload_result["public_id"],
            "width": upload_result.get("width", 0),
            "height": upload_result.get("height", 0),
            "format": upload_result.get("format", ""),
            "resource_type": upload_result.get("resource_type", "image"),
        }

    @staticmethod
    def eliminar_imagen(public_id: str) -> None:
        if not public_id.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="public_id inválido")

        cloudinary = UploadsService._get_cloudinary_sdk()
        result = cloudinary.uploader.destroy(public_id, resource_type="image")
        if result.get("result") not in {"ok", "not found"}:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="No se pudo eliminar la imagen en Cloudinary",
            )
