from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from fastapi import HTTPException, UploadFile


MAX_FILES = 3
MAX_IMAGES = 10
MAX_FILE_BYTES = 2 * 1024 * 1024
SUPPORTED_TEXT_EXTENSIONS = {".txt", ".md", ".csv", ".json"}


@dataclass
class ParsedAssets:
    content: str
    file_count: int
    image_count: int
    notes: list[str]


async def parse_learning_assets(
    text_content: str,
    files: list[UploadFile],
    images: list[UploadFile],
) -> ParsedAssets:
    if len(files) > MAX_FILES:
        raise HTTPException(status_code=400, detail="最多只能上传 3 个文件")
    if len(images) > MAX_IMAGES:
        raise HTTPException(status_code=400, detail="最多只能上传 10 张图片")

    notes: list[str] = []
    chunks: list[str] = []
    if text_content.strip():
        chunks.append(f"User text:\n{text_content.strip()}")

    for upload in files:
        chunks.append(await parse_text_file(upload))

    for image in images:
        chunks.append(await parse_image_file(image))
        notes.append(f"received image: {image.filename or 'unnamed image'}")

    content = "\n\n".join(chunk for chunk in chunks if chunk.strip())
    if not content.strip():
        raise HTTPException(status_code=422, detail="请至少输入文本或上传可解析的文件")

    return ParsedAssets(
        content=content,
        file_count=len(files),
        image_count=len(images),
        notes=notes,
    )


async def parse_text_file(upload: UploadFile) -> str:
    filename = upload.filename or "unnamed-file"
    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED_TEXT_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"暂不支持解析 {suffix or '无扩展名'} 文件，请上传 txt/md/csv/json",
        )

    raw = await upload.read()
    if len(raw) > MAX_FILE_BYTES:
        raise HTTPException(status_code=400, detail=f"{filename} 超过 2MB 限制")

    text = decode_text(raw)
    if not text.strip():
        raise HTTPException(status_code=422, detail=f"{filename} 没有可解析文本")

    return f"File {filename} content:\n{text.strip()}"


async def parse_image_file(upload: UploadFile) -> str:
    validate_image(upload)
    filename = upload.filename or "unnamed-image"
    raw = await upload.read()
    if len(raw) > MAX_FILE_BYTES:
        raise HTTPException(status_code=400, detail=f"{filename} 超过 2MB 限制")

    ocr_text = try_ocr_image(raw)
    if ocr_text.strip():
        return f"Image {filename} OCR text:\n{ocr_text.strip()}"
    return (
        f"Image {filename} was uploaded. OCR is not available or no text was detected. "
        "Use the learner text, file names, and other uploaded text files as the main quiz context."
    )


def validate_image(upload: UploadFile) -> None:
    filename = upload.filename or "unnamed-image"
    content_type = upload.content_type or ""
    if not content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail=f"{filename} 不是图片文件")


def try_ocr_image(raw: bytes) -> str:
    try:
        from PIL import Image
        import pytesseract
    except ImportError:
        return ""

    try:
        image = Image.open(BytesIO(raw))
        return pytesseract.image_to_string(image, lang="chi_sim+eng")
    except Exception:
        return ""


def decode_text(raw: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="ignore")
