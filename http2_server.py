from fastapi import FastAPI, Response, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from hypercorn.config import Config
from hypercorn.asyncio import serve
import asyncio
import os

app = FastAPI()

# 静态文件目录配置
if not os.path.exists("static"):
    os.makedirs("static")
    
    # 创建CSS文件
    with open("static/style.css", "w") as f:
        f.write("body { font-family: Arial; color: #333; background-color: #f5f5f5; }\n")
        f.write(".container { max-width: 800px; margin: 0 auto; padding: 20px; }\n")
        f.write("h1 { color: #0066cc; }\n")
        f.write(".card { background: white; border-radius: 8px; padding: 15px; margin: 15px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }\n")
    
    # 创建JS文件
    with open("static/app.js", "w") as f:
        f.write("console.log('HTTP/2 Server Push Demo')\n")
        f.write("document.addEventListener('DOMContentLoaded', () => {\n")
        f.write("  const timeElement = document.getElementById('load-time')\n")
        f.write("  if (timeElement) {\n")
        f.write("    timeElement.textContent = `页面加载完成时间: ${new Date().toLocaleTimeString()}`\n")
        f.write("  }\n")
        f.write("})\n")

app.mount("/static", StaticFiles(directory="static"), name="static")

# 主页面请求触发资源推送
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>HTTP/2 Server Push Demo</title>
        <link rel="stylesheet" href="/static/style.css">
        <script src="/static/app.js"></script>
    </head>
    <body>
        <div class="container">
            <h1>HTTP/2 服务器推送演示</h1>
            <div class="card">
                <p>这个页面使用HTTP/2服务器推送技术预加载了CSS和JavaScript资源。</p>
                <p>打开开发者工具的Network标签查看推送资源。</p>
                <p id="load-time"></p>
            </div>
            <div class="card">
                <h2>测试链接</h2>
                <ul>
                    <li><a href="/fetch-demo">Fetch API示例</a></li>
                    <li><a href="/sse-demo">EventSource (SSE)示例</a></li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """
    
    # 设置Link头以触发HTTP/2服务器推送
    response = HTMLResponse(content=html_content)
    response.headers["Link"] = "</static/style.css>; rel=preload; as=style, </static/app.js>; rel=preload; as=script"
    return response

# Fetch API示例页面
@app.get("/fetch-demo", response_class=HTMLResponse)
async def fetch_demo():
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Fetch API with HTTP/2</title>
        <link rel="stylesheet" href="/static/style.css">
        <script>
            // 使用Fetch API获取数据
            async function fetchData() {
                try {
                    const response = await fetch('/api/data');
                    const data = await response.json();
                    document.getElementById('result').textContent = JSON.stringify(data, null, 2);
                    document.getElementById('status').textContent = '数据获取成功！';
                } catch (error) {
                    document.getElementById('status').textContent = `错误: ${error.message}`;
                }
            }
        </script>
    </head>
    <body>
        <div class="container">
            <h1>HTTP/2 + Fetch API 示例</h1>
            <div class="card">
                <p>这个示例展示了如何使用Fetch API在HTTP/2环境中获取数据。</p>
                <button onclick="fetchData()">获取数据</button>
                <p id="status">点击按钮获取数据...</p>
                <pre id="result"></pre>
            </div>
            <p><a href="/">返回首页</a></p>
        </div>
    </body>
    </html>
    """)

# SSE (EventSource) 示例页面
@app.get("/sse-demo", response_class=HTMLResponse)
async def sse_demo():
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>EventSource with HTTP/2</title>
        <link rel="stylesheet" href="/static/style.css">
        <script>
            document.addEventListener('DOMContentLoaded', () => {
                const eventSource = new EventSource('/api/events');
                const messagesList = document.getElementById('messages');
                
                eventSource.onmessage = function(event) {
                    const newItem = document.createElement('li');
                    newItem.textContent = event.data;
                    messagesList.appendChild(newItem);
                };
                
                eventSource.onerror = function() {
                    const errorItem = document.createElement('li');
                    errorItem.textContent = '连接错误，尝试重新连接...';
                    errorItem.style.color = 'red';
                    messagesList.appendChild(errorItem);
                };
                
                // 15秒后关闭连接
                setTimeout(() => {
                    eventSource.close();
                    const closeItem = document.createElement('li');
                    closeItem.textContent = '连接已关闭';
                    closeItem.style.fontWeight = 'bold';
                    messagesList.appendChild(closeItem);
                }, 15000);
            });
        </script>
    </head>
    <body>
        <div class="container">
            <h1>HTTP/2 + EventSource (SSE) 示例</h1>
            <div class="card">
                <p>这个示例展示了如何使用EventSource (SSE)在HTTP/2环境中接收服务器发送的事件。</p>
                <p>服务器将每秒发送一条消息，共发送15条：</p>
                <ul id="messages"></ul>
            </div>
            <p><a href="/">返回首页</a></p>
        </div>
    </body>
    </html>
    """)

# API端点 - 用于Fetch示例
@app.get("/api/data")
async def get_data():
    # 模拟API数据
    return {
        "message": "HTTP/2通信成功",
        "timestamp": asyncio.get_event_loop().time(),
        "items": ["项目1", "项目2", "项目3"],
        "status": "success"
    }

# SSE端点 - 用于EventSource示例
@app.get("/api/events")
async def event_stream():
    async def generate():
        for i in range(1, 16):
            # SSE格式: 每条消息以data:开头，以两个换行结束
            yield f"data: 消息 #{i} - 时间: {asyncio.get_event_loop().time():.2f}\n\n"
            await asyncio.sleep(1)
    
    return StreamingResponse(generate(), media_type="text/event-stream")

# 启动HTTP/2服务器
if __name__ == "__main__":
    config = Config()
    config.bind = ["0.0.0.0:8001"]
    config.keyfile = "key.pem"
    config.certfile = "cert.pem"
    config.http2 = True
    
    print("启动HTTP/2服务器在 https://localhost:8001")
    print("注意: 由于使用自签名证书，浏览器可能会显示安全警告，可以选择继续访问。")
    
    asyncio.run(serve(app, config))