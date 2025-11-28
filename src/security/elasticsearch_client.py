"""
Elasticsearch Client for SOC Dashboard
高效能的 ELK 數據查詢與聚合分析模組
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import ConnectionError, NotFoundError
import logging

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityElasticsearchClient:
    """
    資安專用 Elasticsearch 客戶端
    專注於 SOC 威脅獵捕與日誌分析
    """

    def __init__(self,
                 hosts: List[str] = ["http://localhost:9200"],
                 username: str = None,
                 password: str = None,
                 verify_certs: bool = True):
        """
        初始化 Elasticsearch 連線

        Args:
            hosts: Elasticsearch 主機列表
            username: 認證用戶名
            password: 認證密碼
            verify_certs: 是否驗證 SSL 憑證
        """
        self.hosts = hosts

        # 建立連線配置
        auth_config = {}
        if username and password:
            auth_config = {"basic_auth": (username, password)}

        self.client = AsyncElasticsearch(
            hosts=hosts,
            verify_certs=verify_certs,
            **auth_config
        )

        # 7 大日誌源索引映射
        self.log_source_indices = {
            "palo_alto": "paloalto-*",
            "fortigate": "fortigate-*",
            "spam_filter": "spam-filter-*",
            "trend_email": "trend-email-*",
            "trend_apex": "trend-apex-*",
            "windows_events": "winlogbeat-*",
            "manage_engine": "manageengine-*"
        }

    async def check_connection(self) -> bool:
        """檢查 Elasticsearch 連線狀態"""
        try:
            info = await self.client.info()
            logger.info(f"Connected to Elasticsearch: {info['version']['number']}")
            return True
        except ConnectionError as e:
            logger.error(f"Failed to connect to Elasticsearch: {e}")
            return False

    async def get_cluster_health(self) -> Dict[str, Any]:
        """取得叢集健康狀態"""
        try:
            health = await self.client.cluster.health()
            return {
                "status": health["status"],
                "cluster_name": health["cluster_name"],
                "number_of_nodes": health["number_of_nodes"],
                "number_of_data_nodes": health["number_of_data_nodes"],
                "active_primary_shards": health["active_primary_shards"],
                "active_shards": health["active_shards"],
                "relocating_shards": health["relocating_shards"],
                "initializing_shards": health["initializing_shards"],
                "unassigned_shards": health["unassigned_shards"]
            }
        except Exception as e:
            logger.error(f"Failed to get cluster health: {e}")
            return {"status": "unknown", "error": str(e)}

    async def threat_hunting_query(self,
                                   query_dsl: Dict[str, Any],
                                   log_source: str = None,
                                   time_range: str = "24h",
                                   size: int = 1000) -> Dict[str, Any]:
        """
        執行威脅獵捕查詢

        Args:
            query_dsl: Elasticsearch DSL 查詢
            log_source: 指定日誌源 (可選)
            time_range: 時間範圍 (1h, 6h, 24h, 7d, 30d)
            size: 返回結果數量限制

        Returns:
            查詢結果與統計資訊
        """
        try:
            # 確定查詢的索引
            if log_source and log_source in self.log_source_indices:
                index = self.log_source_indices[log_source]
            else:
                # 查詢所有日誌源
                index = ",".join(self.log_source_indices.values())

            # 添加時間範圍過濾器
            if "bool" not in query_dsl.get("query", {}):
                query_dsl["query"] = {"bool": {"must": [query_dsl.get("query", {"match_all": {}})]}}

            # 時間範圍轉換
            time_filter = {
                "range": {
                    "@timestamp": {
                        "gte": f"now-{time_range}",
                        "lte": "now"
                    }
                }
            }

            if "filter" not in query_dsl["query"]["bool"]:
                query_dsl["query"]["bool"]["filter"] = []
            query_dsl["query"]["bool"]["filter"].append(time_filter)

            # 設定查詢參數
            query_dsl["size"] = size
            query_dsl["sort"] = [{"@timestamp": {"order": "desc"}}]

            start_time = datetime.now()

            # 執行查詢
            response = await self.client.search(
                index=index,
                body=query_dsl,
                request_timeout=30
            )

            query_time = (datetime.now() - start_time).total_seconds() * 1000

            # 處理結果
            hits = response["hits"]["hits"]
            total_count = response["hits"]["total"]["value"]

            # 提取關鍵資訊
            events = []
            for hit in hits:
                source_data = hit["_source"]
                events.append({
                    "timestamp": source_data.get("@timestamp"),
                    "index": hit["_index"],
                    "source": self._map_index_to_source(hit["_index"]),
                    "severity": self._extract_severity(source_data),
                    "message": self._extract_message(source_data),
                    "raw_data": source_data
                })

            # 處理聚合結果
            aggregations = {}
            if "aggregations" in response:
                aggregations = self._process_aggregations(response["aggregations"])

            return {
                "total_hits": total_count,
                "query_time_ms": round(query_time),
                "events": events,
                "aggregations": aggregations,
                "indices_searched": index.split(",") if "," in index else [index]
            }

        except Exception as e:
            logger.error(f"Threat hunting query failed: {e}")
            return {
                "error": str(e),
                "total_hits": 0,
                "query_time_ms": 0,
                "events": [],
                "aggregations": {}
            }

    async def get_security_metrics(self, time_range: str = "24h") -> Dict[str, Any]:
        """
        取得安全指標統計

        Args:
            time_range: 時間範圍

        Returns:
            安全指標數據
        """
        try:
            # 威脅等級聚合查詢
            threat_query = {
                "query": {
                    "bool": {
                        "filter": [
                            {"range": {"@timestamp": {"gte": f"now-{time_range}"}}}
                        ]
                    }
                },
                "size": 0,
                "aggs": {
                    "threat_levels": {
                        "terms": {
                            "field": "threat.severity.keyword",
                            "size": 10
                        }
                    },
                    "log_sources": {
                        "terms": {
                            "field": "_index",
                            "size": 10
                        }
                    },
                    "timeline": {
                        "date_histogram": {
                            "field": "@timestamp",
                            "calendar_interval": "1h",
                            "min_doc_count": 0
                        }
                    }
                }
            }

            # 執行所有日誌源的統計查詢
            index = ",".join(self.log_source_indices.values())
            response = await self.client.search(
                index=index,
                body=threat_query,
                request_timeout=10
            )

            # 處理聚合結果
            aggs = response.get("aggregations", {})

            # 威脅等級分佈
            threat_levels = {}
            for bucket in aggs.get("threat_levels", {}).get("buckets", []):
                threat_levels[bucket["key"]] = bucket["doc_count"]

            # 日誌源分佈
            log_sources = {}
            for bucket in aggs.get("log_sources", {}).get("buckets", []):
                source_name = self._map_index_to_source(bucket["key"])
                log_sources[source_name] = bucket["doc_count"]

            # 時間線數據
            timeline = []
            for bucket in aggs.get("timeline", {}).get("buckets", []):
                timeline.append({
                    "timestamp": bucket["key"],
                    "count": bucket["doc_count"]
                })

            return {
                "total_events": response["hits"]["total"]["value"],
                "threat_levels": threat_levels,
                "log_sources": log_sources,
                "timeline": timeline,
                "time_range": time_range
            }

        except Exception as e:
            logger.error(f"Failed to get security metrics: {e}")
            return {
                "total_events": 0,
                "threat_levels": {},
                "log_sources": {},
                "timeline": [],
                "error": str(e)
            }

    def _map_index_to_source(self, index_name: str) -> str:
        """將索引名稱映射到日誌源名稱"""
        for source, pattern in self.log_source_indices.items():
            if pattern.replace("*", "") in index_name:
                return source
        return "unknown"

    def _extract_severity(self, source_data: Dict[str, Any]) -> str:
        """從日誌資料中提取嚴重性等級"""
        # 常見的嚴重性欄位
        severity_fields = [
            "threat.severity", "severity", "level", "priority",
            "event.severity", "alert.severity", "log.level"
        ]

        for field in severity_fields:
            if "." in field:
                # 處理嵌套欄位 (如 threat.severity)
                keys = field.split(".")
                value = source_data
                try:
                    for key in keys:
                        value = value[key]
                    if value:
                        return str(value).lower()
                except (KeyError, TypeError):
                    continue
            else:
                # 處理直接欄位
                if field in source_data and source_data[field]:
                    return str(source_data[field]).lower()

        # 預設為低危
        return "低危"

    def _extract_message(self, source_data: Dict[str, Any]) -> str:
        """從日誌資料中提取訊息內容"""
        # 常見的訊息欄位
        message_fields = [
            "message", "description", "event.original",
            "log.message", "event.description", "summary"
        ]

        for field in message_fields:
            if "." in field:
                # 處理嵌套欄位
                keys = field.split(".")
                value = source_data
                try:
                    for key in keys:
                        value = value[key]
                    if value:
                        return str(value)[:200]  # 限制長度
                except (KeyError, TypeError):
                    continue
            else:
                # 處理直接欄位
                if field in source_data and source_data[field]:
                    return str(source_data[field])[:200]  # 限制長度

        # 如果找不到訊息欄位，返回索引名稱
        return "Security event detected"

    def _process_aggregations(self, aggs: Dict[str, Any]) -> Dict[str, Any]:
        """處理聚合查詢結果"""
        processed = {}

        for agg_name, agg_data in aggs.items():
            if "buckets" in agg_data:  # Terms aggregation
                processed[agg_name] = [
                    {"key": bucket["key"], "count": bucket["doc_count"]}
                    for bucket in agg_data["buckets"]
                ]
            elif "value" in agg_data:  # Metric aggregation
                processed[agg_name] = agg_data["value"]
            else:
                processed[agg_name] = agg_data

        return processed

    async def close(self):
        """關閉 Elasticsearch 連線"""
        if self.client:
            await self.client.close()

# 全域實例（延遲初始化）
_es_client = None

async def get_elasticsearch_client() -> SecurityElasticsearchClient:
    """取得 Elasticsearch 客戶端實例（延遲初始化）"""
    global _es_client
    if _es_client is None:
        try:
            _es_client = SecurityElasticsearchClient()
        except Exception as e:
            logger.warning(f"Failed to initialize Elasticsearch client: {e}")
            # 如果無法連接到 Elasticsearch，返回一個模擬客戶端
            _es_client = MockElasticsearchClient()
    return _es_client

class MockElasticsearchClient:
    """模擬 Elasticsearch 客戶端，用於無 Elasticsearch 環境"""

    async def check_connection(self) -> bool:
        return False

    async def get_cluster_health(self) -> Dict[str, Any]:
        return {"status": "mock", "error": "Elasticsearch not available"}

    async def threat_hunting_query(self, query_dsl: Dict[str, Any], log_source: str = None,
                                 time_range: str = "24h", size: int = 1000) -> Dict[str, Any]:
        return {
            "total_hits": 0,
            "query_time_ms": 0,
            "events": [],
            "aggregations": {},
            "error": "Elasticsearch not available - using mock data"
        }

    async def get_security_metrics(self, time_range: str = "24h") -> Dict[str, Any]:
        return {
            "total_events": 0,
            "threat_levels": {},
            "log_sources": {},
            "timeline": [],
            "error": "Elasticsearch not available"
        }

    async def close(self):
        pass