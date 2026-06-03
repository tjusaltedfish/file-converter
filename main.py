"""
文件转换服务（轻量版）
使用基础库实现，构建更快
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
import subprocess
import json

app = FastAPI(title="文件转换服务")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def health_check():
    """健康检查"""
    return {"status": "ok", "service": "file-converter"}

@app.post("/convert/file")
async def convert_file(file: UploadFile = File(...)):
    """上传文件并转换为 Markdown"""
    try:
        # 检查文件类型
        allowed_extensions = {
            '.txt', '.md', '.csv', '.json', '.xml', '.html', '.htm'
        }

        file_ext = os.path.splitext(file.filename or '')[1].lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"轻量版只支持文本格式: {', '.join(allowed_extensions)}"
            )

        # 读取文件内容
        content = await file.read()
        text = content.decode('utf-8', errors='ignore')

        # 简单转换为 Markdown
        if file_ext in ['.html', '.htm']:
            # 简单去除 HTML 标签
            import re
            text = re.sub(r'<[^>]+>', '', text)
            text = re.sub(r'\s+', ' ', text).strip()

        markdown = f"# {file.filename}\n\n{text}"

        return {
            "success": True,
            "filename": file.filename,
            "markdown": markdown,
            "format": file_ext
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"转换失败: {str(e)}")

@app.post("/convert/url")
async def convert_url(url: str):
    """将网页 URL 转换为 Markdown"""
    try:
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()

        # 简单去除 HTML 标签
        import re
        text = re.sub(r'<[^>]+>', '', response.text)
        text = re.sub(r'\s+', ' ', text).strip()

        markdown = f"# {url}\n\n{text}"

        return {
            "success": True,
            "url": url,
            "markdown": markdown,
            "format": "html"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"转换失败: {str(e)}")

@app.post("/convert/batch")
async def convert_batch(files: list[UploadFile] = File(...)):
    """批量转换多个文件"""
    results = []

    for file in files:
        try:
            # 检查文件类型
            allowed_extensions = {
                '.txt', '.md', '.csv', '.json', '.xml', '.html', '.htm'
            }

            file_ext = os.path.splitext(file.filename or '')[1].lower()
            if file_ext not in allowed_extensions:
                results.append({
                    "success": False,
                    "filename": file.filename,
                    "error": f"轻量版只支持文本格式"
                })
                continue

            # 读取文件内容
            content = await file.read()
            text = content.decode('utf-8', errors='ignore')

            # 简单转换为 Markdown
            if file_ext in ['.html', '.htm']:
                import re
                text = re.sub(r'<[^>]+>', '', text)
                text = re.sub(r'\s+', ' ', text).strip()

            markdown = f"# {file.filename}\n\n{text}"

            results.append({
                "success": True,
                "filename": file.filename,
                "markdown": markdown,
                "format": file_ext
            })

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
