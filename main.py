"""
文件转换服务
基于 Microsoft MarkItDown 将各种格式转换为 Markdown
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from markitdown import MarkItDown
import tempfile
import os
from typing import Optional
import httpx

app = FastAPI(title="文件转换服务")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化 MarkItDown
converter = MarkItDown()

@app.get("/")
async def health_check():
    """健康检查"""
    return {"status": "ok", "service": "file-converter"}

@app.post("/convert/file")
async def convert_file(file: UploadFile = File(...)):
    """
    上传文件并转换为 Markdown
    支持格式：pptx, docx, xlsx, pdf, html, csv, json, xml
    """
    try:
        # 检查文件类型
        allowed_extensions = {
            '.pptx', '.docx', '.xlsx', '.pdf', '.html', '.htm',
            '.csv', '.json', '.xml', '.txt', '.odt', '.ods', '.odp'
        }

        file_ext = os.path.splitext(file.filename or '')[1].lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件格式: {file_ext}。支持的格式: {', '.join(allowed_extensions)}"
            )

        # 保存到临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        try:
            # 转换文件
            result = converter.convert(tmp_path)

            return {
                "success": True,
                "filename": file.filename,
                "markdown": result.text_content,
                "format": file_ext
            }
        finally:
            # 清理临时文件
            os.unlink(tmp_path)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"转换失败: {str(e)}")

@app.post("/convert/url")
async def convert_url(url: str):
    """
    将网页 URL 转换为 Markdown
    """
    try:
        # 转换 URL
        result = converter.convert(url)

        return {
            "success": True,
            "url": url,
            "markdown": result.text_content,
            "format": "html"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"转换失败: {str(e)}")

@app.post("/convert/batch")
async def convert_batch(files: list[UploadFile] = File(...)):
    """
    批量转换多个文件
    """
    results = []

    for file in files:
        try:
            # 保存到临时文件
            file_ext = os.path.splitext(file.filename or '')[1].lower()
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
                content = await file.read()
                tmp.write(content)
                tmp_path = tmp.name

            try:
                # 转换文件
                result = converter.convert(tmp_path)
                results.append({
                    "success": True,
                    "filename": file.filename,
                    "markdown": result.text_content,
                    "format": file_ext
                })
            finally:
                # 清理临时文件
                os.unlink(tmp_path)

        except Exception as e:
            results.append({
                "success": False,
                "filename": file.filename,
                "error": str(e)
            })

    return {"results": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
