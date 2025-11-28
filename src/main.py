"""
DevSecOps Unified Monitor Platform - Main Web Application
SOC Dashboard for Kubernetes monitoring and security log analysis
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import uvicorn
import json
from pathlib import Path
from typing import Optional, Dict, Any
import logging

# 導入 Elasticsearch 客戶端
from .security.elasticsearch_client import get_elasticsearch_client

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="DevSecOps Unified Monitor Platform",
    description="SOC Dashboard for K8S monitoring and security log analysis",
    version="1.0.0"
)

# Setup templates and static files
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Create static directory if it doesn't exist
static_dir = BASE_DIR / "static"
static_dir.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# 7 大日誌源配置
LOG_SOURCES = {
    "palo_alto": {
        "name": "Palo Alto Firewall",
        "description": "外部/南北向流量防護",
        "type": "perimeter",
        "color": "#FF6B35"
    },
    "fortigate": {
        "name": "FortiGate Firewall",
        "description": "內部/東西向流量區隔",
        "type": "internal_segmentation",
        "color": "#004E89"
    },
    "spam_filter": {
        "name": "SPAM Filter",
        "description": "郵件第一道過濾",
        "type": "email_security",
        "color": "#F77F00"
    },
    "trend_email": {
        "name": "Trend Micro Email Security",
        "description": "郵件第二道過濾 (進階威脅/APT)",
        "type": "email_security",
        "color": "#FCBF49"
    },
    "trend_apex": {
        "name": "Trend Apex Central",
        "description": "端點防護 (EDR/Antivirus)",
        "type": "endpoint_protection",
        "color": "#003049"
    },
    "windows_events": {
        "name": "Windows Event Logs",
        "description": "身份認證 (AD)、GPO、系統登入",
        "type": "identity_access",
        "color": "#669BBC"
    },
    "manage_engine": {
        "name": "ManageEngine",
        "description": "IT 資產管理與運維審計",
        "type": "asset_management",
        "color": "#C1121F"
    }
}

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """SOC 主儀表板"""
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "log_sources": LOG_SOURCES,
        "page_title": "SOC Dashboard"
    })

@app.get("/threat-hunting", response_class=HTMLResponse)
async def threat_hunting(request: Request):
    """威脅獵捕分析頁面"""
    return templates.TemplateResponse("threat_hunting.html", {
        "request": request,
        "log_sources": LOG_SOURCES,
        "page_title": "Threat Hunting"
    })

@app.get("/api/health")
async def health_check():
    """健康檢查端點"""
    return {"status": "healthy", "service": "SOC Dashboard"}

# Pydantic 模型定義
class ThreatHuntingQuery(BaseModel):
    query_dsl: Dict[str, Any]
    log_source: Optional[str] = None
    time_range: str = "24h"
    size: int = 1000

class SecurityMetricsRequest(BaseModel):
    time_range: str = "24h"

@app.get("/api/log-sources")
async def get_log_sources():
    """取得日誌源配置"""
    return LOG_SOURCES

@app.get("/api/elasticsearch/health")
async def elasticsearch_health():
    """檢查 Elasticsearch 連線狀態"""
    try:
        es_client = await get_elasticsearch_client()
        is_connected = await es_client.check_connection()

        if is_connected:
            cluster_health = await es_client.get_cluster_health()
            return {
                "status": "connected",
                "cluster_health": cluster_health
            }
        else:
            return JSONResponse(
                status_code=503,
                content={"status": "disconnected", "error": "Unable to connect to Elasticsearch"}
            )
    except Exception as e:
        logger.error(f"Elasticsearch health check failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "error": str(e)}
        )

@app.post("/api/threat-hunting")
async def execute_threat_hunting(query: ThreatHuntingQuery):
    """執行威脅獵捕查詢"""
    try:
        es_client = await get_elasticsearch_client()

        # 執行威脅獵捕查詢
        result = await es_client.threat_hunting_query(
            query_dsl=query.query_dsl,
            log_source=query.log_source,
            time_range=query.time_range,
            size=query.size
        )

        if "error" in result:
            return JSONResponse(
                status_code=400,
                content=result
            )

        return result

    except json.JSONDecodeError:
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid JSON in query DSL"}
        )
    except Exception as e:
        logger.error(f"Threat hunting query failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Internal server error: {str(e)}"}
        )

@app.post("/api/security-metrics")
async def get_security_metrics(request: SecurityMetricsRequest):
    """取得安全指標統計"""
    try:
        es_client = await get_elasticsearch_client()

        # 取得安全指標
        metrics = await es_client.get_security_metrics(
            time_range=request.time_range
        )

        if "error" in metrics:
            return JSONResponse(
                status_code=400,
                content=metrics
            )

        return metrics

    except Exception as e:
        logger.error(f"Security metrics query failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Internal server error: {str(e)}"}
        )

@app.get("/api/dashboard-data")
async def get_dashboard_data():
    """取得儀表板數據（模擬數據 + 實際 ES 數據混合）"""
    try:
        es_client = await get_elasticsearch_client()

        # 嘗試從 Elasticsearch 取得實際數據
        is_connected = await es_client.check_connection()

        if is_connected:
            # 取得實際的安全指標
            metrics = await es_client.get_security_metrics("24h")

            # 如果有實際數據，使用實際數據；否則使用模擬數據
            if metrics.get("total_events", 0) > 0:
                dashboard_data = {
                    "threat_overview": {
                        "high_threats": len([x for x, y in metrics.get("threat_levels", {}).items()
                                           if "high" in x.lower() or "critical" in x.lower()]),
                        "medium_alerts": len([x for x, y in metrics.get("threat_levels", {}).items()
                                            if "medium" in x.lower() or "warning" in x.lower()]),
                        "low_events": len([x for x, y in metrics.get("threat_levels", {}).items()
                                         if "low" in x.lower() or "info" in x.lower()]),
                        "resolved": metrics.get("total_events", 0) - sum(metrics.get("threat_levels", {}).values())
                    },
                    "log_sources_status": metrics.get("log_sources", {}),
                    "timeline_data": metrics.get("timeline", [])
                }
            else:
                # 使用模擬數據
                dashboard_data = generate_mock_dashboard_data()
        else:
            # Elasticsearch 未連線，使用模擬數據
            dashboard_data = generate_mock_dashboard_data()

        return dashboard_data

    except Exception as e:
        logger.error(f"Dashboard data query failed: {e}")
        # 發生錯誤時返回模擬數據
        return generate_mock_dashboard_data()

def generate_mock_dashboard_data():
    """生成模擬儀表板數據"""
    import random
    from datetime import datetime, timedelta

    return {
        "threat_overview": {
            "high_threats": random.randint(15, 30),
            "medium_alerts": random.randint(100, 200),
            "low_events": random.randint(1000, 2000),
            "resolved": random.randint(8000, 10000)
        },
        "log_sources_status": {
            source_id: {
                "events_count": random.randint(50, 1000),
                "status": "online",
                "activity_percentage": random.randint(80, 100)
            }
            for source_id in LOG_SOURCES.keys()
        },
        "timeline_data": [
            {
                "timestamp": (datetime.now() - timedelta(hours=i)).isoformat(),
                "count": random.randint(10, 100)
            }
            for i in range(24, 0, -1)
        ]
    }

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )