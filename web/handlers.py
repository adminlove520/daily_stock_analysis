# -*- coding: utf-8 -*-
"""
===================================
Web 处理器层 - 请求处理
===================================

职责：
1. 处理各类 HTTP 请求
2. 调用服务层执行业务逻辑
3. 返回响应数据

处理器分类：
- PageHandler: 页面请求处理
- ApiHandler: API 接口处理
"""

from __future__ import annotations

import json
import re
import logging
from http import HTTPStatus
from datetime import datetime
from typing import Dict, Any, TYPE_CHECKING

from web.services import get_config_service, get_analysis_service
from web.templates import render_config_page

if TYPE_CHECKING:
    from http.server import BaseHTTPRequestHandler

logger = logging.getLogger(__name__)


# ============================================================
# 响应辅助类
# ============================================================

class Response:
    """HTTP 响应封装"""
    
    def __init__(
        self,
        body: bytes,
        status: HTTPStatus = HTTPStatus.OK,
        content_type: str = "text/html; charset=utf-8"
    ):
        self.body = body
        self.status = status
        self.content_type = content_type
    
    def send(self, handler: 'BaseHTTPRequestHandler') -> None:
        """发送响应到客户端"""
        handler.send_response(self.status)
        handler.send_header("Content-Type", self.content_type)
        handler.send_header("Content-Length", str(len(self.body)))
        handler.end_headers()
        handler.wfile.write(self.body)


class JsonResponse(Response):
    """JSON 响应封装"""
    
    def __init__(
        self,
        data: Dict[str, Any],
        status: HTTPStatus = HTTPStatus.OK
    ):
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        super().__init__(
            body=body,
            status=status,
            content_type="application/json; charset=utf-8"
        )


class HtmlResponse(Response):
    """HTML 响应封装"""
    
    def __init__(
        self,
        body: bytes,
        status: HTTPStatus = HTTPStatus.OK
    ):
        super().__init__(
            body=body,
            status=status,
            content_type="text/html; charset=utf-8"
        )


# ============================================================
# 页面处理器
# ============================================================

class PageHandler:
    """页面请求处理器"""
    
    def __init__(self):
        self.config_service = get_config_service()
    
    def handle_index(self) -> Response:
        """处理首页请求 GET /"""
        stock_list = self.config_service.get_stock_list()
        env_filename = self.config_service.get_env_filename()
        body = render_config_page(stock_list, env_filename)
        return HtmlResponse(body)
    
    def handle_update(self, form_data: Dict[str, list]) -> Response:
        """
        处理配置更新 POST /update
        
        Args:
            form_data: 表单数据
        """
        stock_list = form_data.get("stock_list", [""])[0]
        normalized = self.config_service.set_stock_list(stock_list)
        env_filename = self.config_service.get_env_filename()
        body = render_config_page(normalized, env_filename, message="已保存")
        return HtmlResponse(body)


# ============================================================
# API 处理器
# ============================================================

class ApiHandler:
    """API 请求处理器"""
    
    def __init__(self):
        self.analysis_service = get_analysis_service()
    
    def handle_health(self) -> Response:
        """
        健康检查 GET /health
        
        返回:
            {
                "status": "ok",
                "timestamp": "2026-01-19T10:30:00",
                "service": "stock-analysis-webui"
            }
        """
        data = {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "service": "stock-analysis-webui"
        }
        return JsonResponse(data)
    
    def handle_analysis(self, query: Dict[str, list]) -> Response:
        """
        触发股票分析 GET /analysis?code=xxx
        
        Args:
            query: URL 查询参数
            
        返回:
            {
                "success": true,
                "message": "分析任务已提交",
                "code": "600519",
                "task_id": "600519_20260119_103000"
            }
        """
        # 获取股票代码参数
        code_list = query.get("code", [])
        if not code_list or not code_list[0].strip():
            return JsonResponse(
                {"success": False, "error": "缺少必填参数: code (股票代码)"},
                status=HTTPStatus.BAD_REQUEST
            )
        
        code = code_list[0].strip()
        
        # 验证股票代码格式：A股(6位数字) 或 港股(hk+5位数字)
        code = code.lower()
        is_valid = re.match(r'^\d{6}$', code) or re.match(r'^hk\d{5}$', code)
        if not is_valid:
            return JsonResponse(
                {"success": False, "error": f"无效的股票代码格式: {code} (A股6位数字 或 港股hk+5位数字)"},
                status=HTTPStatus.BAD_REQUEST
            )
        
        # 提交异步分析任务
        try:
            result = self.analysis_service.submit_analysis(code)
            return JsonResponse(result)
        except Exception as e:
            logger.error(f"[ApiHandler] 提交分析任务失败: {e}")
            return JsonResponse(
                {"success": False, "error": f"提交任务失败: {str(e)}"},
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )
    
    def handle_tasks(self, query: Dict[str, list]) -> Response:
        """
        查询任务列表 GET /tasks
        
        Args:
            query: URL 查询参数 (可选 limit)
            
        返回:
            {
                "success": true,
                "tasks": [...]
            }
        """
        limit_list = query.get("limit", ["20"])
        try:
            limit = int(limit_list[0])
        except ValueError:
            limit = 20
        
        tasks = self.analysis_service.list_tasks(limit=limit)
        return JsonResponse({"success": True, "tasks": tasks})
    
    def handle_task_status(self, query: Dict[str, list]) -> Response:
        """
        查询单个任务状态 GET /task?id=xxx
        
        Args:
            query: URL 查询参数
        """
        task_id_list = query.get("id", [])
        if not task_id_list or not task_id_list[0].strip():
            return JsonResponse(
                {"success": False, "error": "缺少必填参数: id (任务ID)"},
                status=HTTPStatus.BAD_REQUEST
            )
        
        task_id = task_id_list[0].strip()
        task = self.analysis_service.get_task_status(task_id)
        
        if task is None:
            return JsonResponse(
                {"success": False, "error": f"任务不存在: {task_id}"},
                status=HTTPStatus.NOT_FOUND
            )
        
        return JsonResponse({"success": True, "task": task})


# ============================================================
# 处理器工厂
# ============================================================

_page_handler: PageHandler | None = None
_api_handler: ApiHandler | None = None


def get_page_handler() -> PageHandler:
    """获取页面处理器实例"""
    global _page_handler
    if _page_handler is None:
        _page_handler = PageHandler()
    return _page_handler


def get_api_handler() -> ApiHandler:
    """获取 API 处理器实例"""
    global _api_handler
    if _api_handler is None:
        _api_handler = ApiHandler()
    return _api_handler
