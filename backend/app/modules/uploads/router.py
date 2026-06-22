from fastapi import APIRouter, Depends, Form, Response, UploadFile, status

from app.core.dependencies import require_role
from app.modules.auth.model import Usuario
from app.modules.uploads.schemas import CloudinaryResponse
from app.modules.uploads.service import UploadsService

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.post(
    "/imagen",
    response_model=CloudinaryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Subir imagen a Cloudinary",
)
async def subir_imagen(
    file: UploadFile,
    folder: str | None = Form(default=None),
    _user: Usuario = Depends(require_role(["ADMIN"])),
) -> CloudinaryResponse:
    result = await UploadsService.subir_imagen(file, folder)
    return CloudinaryResponse.model_validate(result)


@router.delete(
    "/imagen/{public_id:path}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar imagen de Cloudinary por public_id",
)
async def eliminar_imagen(
    public_id: str,
    _user: Usuario = Depends(require_role(["ADMIN"])),
) -> Response:
    UploadsService.eliminar_imagen(public_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
