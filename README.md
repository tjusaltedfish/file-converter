# 文件转换服务

基于 Microsoft MarkItDown 的文件转换微服务，将各种格式转换为 Markdown。

## 支持的格式

- ✅ PowerPoint (.pptx)
- ✅ Word (.docx)
- ✅ Excel (.xlsx)
- ✅ PDF (.pdf)
- ✅ HTML (.html, .htm)
- ✅ CSV (.csv)
- ✅ JSON (.json)
- ✅ XML (.xml)
- ✅ OpenDocument (.odt, .ods, .odp)
- ✅ URL（网页）

## 本地开发

### 1. 安装依赖

```bash
cd python-converter
pip install -r requirements.txt
```

### 2. 启动服务

```bash
python main.py
```

服务将在 http://localhost:8000 启动

### 3. 测试 API

```bash
# 健康检查
curl http://localhost:8000/

# 转换文件
curl -X POST -F "file=@document.docx" http://localhost:8000/convert/file

# 转换 URL
curl -X POST "http://localhost:8000/convert/url?url=https://example.com"
```

## 部署到 Vercel

### 方法一：独立部署

1. 在 Vercel 创建新项目
2. 选择 `python-converter` 目录
3. Vercel 会自动检测 Python 并部署
4. 获得部署 URL，如：`https://your-service.vercel.app`

### 方法二：作为子目录部署

如果你想把这个服务和 Next.js 项目一起部署：

1. 在 Vercel 项目设置中
2. 添加 Root Directory 为 `python-converter`
3. 或者创建独立的 Vercel 项目

## API 文档

启动服务后，访问 http://localhost:8000/docs 查看完整的 API 文档（Swagger UI）

### 主要端点

#### POST /convert/file

上传文件并转换为 Markdown

**请求：**
- Content-Type: multipart/form-data
- Body: file（文件）

**响应：**
```json
{
  "success": true,
  "filename": "document.docx",
  "markdown": "# 标题\n\n内容...",
  "format": ".docx"
}
```

#### POST /convert/url

将网页 URL 转换为 Markdown

**请求：**
- Query 参数: url

**响应：**
```json
{
  "success": true,
  "url": "https://example.com",
  "markdown": "# 页面标题\n\n内容...",
  "format": "html"
}
```

#### POST /convert/batch

批量转换多个文件

**请求：**
- Content-Type: multipart/form-data
- Body: files（多个文件）

**响应：**
```json
{
  "results": [
    {
      "success": true,
      "filename": "file1.docx",
      "markdown": "...",
      "format": ".docx"
    },
    {
      "success": true,
      "filename": "file2.pdf",
      "markdown": "...",
      "format": ".pdf"
    }
  ]
}
```

## 环境变量

无需配置环境变量，开箱即用。

## 依赖

- FastAPI - Web 框架
- MarkItDown - 文件转换库
- uvicorn - ASGI 服务器
- python-multipart - 文件上传支持
- httpx - HTTP 客户端

## 许可证

MIT
