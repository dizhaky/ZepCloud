"""Simple demo server for browser automation testing"""
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI(title="M365 RAG System - Demo")

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>M365 RAG System - Setup</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 { color: #0066cc; }
            .status { 
                padding: 15px;
                background: #e8f5e9;
                border-left: 4px solid #4caf50;
                margin: 20px 0;
            }
            button {
                background: #0066cc;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                margin: 10px 5px;
            }
            button:hover { background: #0052a3; }
            input {
                width: 100%;
                padding: 10px;
                margin: 10px 0;
                border: 1px solid #ddd;
                border-radius: 5px;
                box-sizing: border-box;
            }
            .form-group {
                margin: 20px 0;
            }
            label {
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 M365 RAG System - Initial Setup</h1>
            
            <div class="status">
                <strong>✅ Server Status:</strong> Running on http://localhost:8000
            </div>
            
            <h2>Configuration</h2>
            <form id="setupForm">
                <div class="form-group">
                    <label for="m365ClientId">Microsoft 365 Client ID:</label>
                    <input type="text" id="m365ClientId" name="m365ClientId" 
                           placeholder="Enter your Azure AD Client ID">
                </div>
                
                <div class="form-group">
                    <label for="m365ClientSecret">Microsoft 365 Client Secret:</label>
                    <input type="password" id="m365ClientSecret" name="m365ClientSecret" 
                           placeholder="Enter your Azure AD Client Secret">
                </div>
                
                <div class="form-group">
                    <label for="m365TenantId">Microsoft 365 Tenant ID:</label>
                    <input type="text" id="m365TenantId" name="m365TenantId" 
                           placeholder="Enter your Azure AD Tenant ID">
                </div>
                
                <div class="form-group">
                    <label for="openaiKey">OpenAI API Key:</label>
                    <input type="password" id="openaiKey" name="openaiKey" 
                           placeholder="Enter your OpenAI API key">
                </div>
                
                <button type="submit" id="saveBtn">💾 Save Configuration</button>
                <button type="button" id="testBtn">🧪 Test Connection</button>
                <button type="button" id="deployBtn">🚀 Deploy System</button>
            </form>
            
            <div id="result" style="margin-top: 20px; padding: 15px; display: none;"></div>
        </div>
        
        <script>
            document.getElementById('setupForm').addEventListener('submit', function(e) {
                e.preventDefault();
                const result = document.getElementById('result');
                result.style.display = 'block';
                result.style.background = '#e8f5e9';
                result.style.borderLeft = '4px solid #4caf50';
                result.innerHTML = '<strong>✅ Configuration Saved!</strong><br>Ready to deploy the system.';
            });
            
            document.getElementById('testBtn').addEventListener('click', function() {
                const result = document.getElementById('result');
                result.style.display = 'block';
                result.style.background = '#fff3e0';
                result.style.borderLeft = '4px solid #ff9800';
                result.innerHTML = '<strong>🧪 Testing Connection...</strong><br>Verifying credentials...';
                
                setTimeout(() => {
                    result.style.background = '#e8f5e9';
                    result.style.borderLeft = '4px solid #4caf50';
                    result.innerHTML = '<strong>✅ Connection Successful!</strong><br>All credentials verified.';
                }, 2000);
            });
            
            document.getElementById('deployBtn').addEventListener('click', function() {
                const result = document.getElementById('result');
                result.style.display = 'block';
                result.style.background = '#e3f2fd';
                result.style.borderLeft = '4px solid #2196f3';
                result.innerHTML = '<strong>🚀 Deployment Started!</strong><br>Initializing services...';
                
                setTimeout(() => {
                    result.innerHTML += '<br>📦 Starting Docker containers...';
                }, 1000);
                
                setTimeout(() => {
                    result.innerHTML += '<br>🔐 Configuring SSL certificates...';
                }, 2000);
                
                setTimeout(() => {
                    result.innerHTML += '<br>🗄️ Initializing databases...';
                }, 3000);
                
                setTimeout(() => {
                    result.style.background = '#e8f5e9';
                    result.style.borderLeft = '4px solid #4caf50';
                    result.innerHTML = '<strong>✅ Deployment Complete!</strong><br>' +
                                      'System is ready at:<br>' +
                                      '• API: <a href="http://localhost:8000/docs">http://localhost:8000/docs</a><br>' +
                                      '• RAGFlow: <a href="http://localhost">http://localhost</a><br>' +
                                      '• Grafana: <a href="http://localhost:3000">http://localhost:3000</a>';
                }, 4000);
            });
        </script>
    </body>
    </html>
    """

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "M365 RAG System Demo Server"}

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 M365 RAG System - Demo Server Starting...")
    print("="*60)
    print("\n📍 Server URL: http://localhost:8000")
    print("📖 Setup Page: http://localhost:8000")
    print("\n✨ Ready for browser automation testing!")
    print("\nPress CTRL+C to stop\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

