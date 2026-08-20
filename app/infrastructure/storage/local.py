from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile


class LocalStorage:

    def __init__(self, base_path: str = "storage"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def save(
        self,
        file: UploadFile,
        folder: str,
    ) -> tuple[str , int]:
        

        folder_path = self.base_path / folder
        folder_path.mkdir(parents=True, exist_ok=True)

        file_extension = Path(file.filename).suffix
        unique_name = f"{uuid4()}{file_extension}"

        file_path = folder_path / unique_name

        with file_path.open("wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                buffer.write(chunk)
                file_size += len(chunk)

        return str(file_path) , file_size







    def delete(self, storage_key: str) -> None:

        file_path = Path(storage_key)

        if file_path.exists():
            file_path.unlink()

    def exists(self, storage_key: str) -> bool:

        return Path(storage_key).exists()