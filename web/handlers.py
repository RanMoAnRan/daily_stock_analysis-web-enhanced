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
from web.templates import render_config_page, render_env_editor_page, render_error_page
from src.enums import ReportType

if TYPE_CHECKING:
    from http.server import BaseHTTPRequestHandler

logger = logging.getLogger(__name__)

_LOOPBACK_IPS = {"127.0.0.1", "::1"}


def _is_loopback_request(handler: "BaseHTTPRequestHandler") -> bool:
    """仅允许本机访问敏感页面（例如 .env 编辑）。"""
    try:
        ip = handler.client_address[0]
        return ip in _LOOPBACK_IPS
    except Exception:
        return False


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
    
    def handle_index(self, request_handler: "BaseHTTPRequestHandler") -> Response:
        """处理首页请求 GET /"""
        stock_list = self.config_service.get_stock_list()
        env_filename = self.config_service.get_env_filename()
        common = self.config_service.get_env_values(
            [
                ("SCHEDULE_ENABLED", "false"),
                ("SCHEDULE_TIME", "18:00"),
                ("MARKET_REVIEW_ENABLED", "true"),
            ]
        )
        body = render_config_page(stock_list, env_filename, common_config=common)
        return HtmlResponse(body)
    
    def handle_update(self, request_handler: "BaseHTTPRequestHandler", form_data: Dict[str, list]) -> Response:
        """
        处理配置更新 POST /update
        
        Args:
            form_data: 表单数据
        """
        stock_list = form_data.get("stock_list", [""])[0]
        normalized = self.config_service.set_stock_list(stock_list)
        env_filename = self.config_service.get_env_filename()
        common = self.config_service.get_env_values(
            [
                ("SCHEDULE_ENABLED", "false"),
                ("SCHEDULE_TIME", "18:00"),
                ("MARKET_REVIEW_ENABLED", "true"),
            ]
        )
        body = render_config_page(normalized, env_filename, message="已保存", common_config=common)
        return HtmlResponse(body)

    def handle_common_update(self, request_handler: "BaseHTTPRequestHandler", form_data: Dict[str, list]) -> Response:
        """更新常用配置 POST /common/update（仅允许本机回环地址访问）。"""
        if not _is_loopback_request(request_handler):
            body = render_error_page(403, "禁止访问", "该操作仅允许本机访问（127.0.0.1 / ::1）")
            return HtmlResponse(body, status=HTTPStatus.FORBIDDEN)

        def _get(name: str, default: str = "") -> str:
            return (form_data.get(name, [default])[0] or "").strip()

        def _get_bool(name: str) -> str:
            # checkbox: checked => "on", unchecked => absent
            return "true" if name in form_data else "false"

        # 读当前值作为兜底
        current = self.config_service.get_env_values(
            [
                ("SCHEDULE_ENABLED", "false"),
                ("SCHEDULE_TIME", "18:00"),
                ("MARKET_REVIEW_ENABLED", "true"),
            ]
        )

        # 基本校验
        errors: List[str] = []

        st = _get("SCHEDULE_TIME", current["SCHEDULE_TIME"])
        if not re.match(r"^(?:[01]\\d|2[0-3]):[0-5]\\d$", st):
            errors.append("SCHEDULE_TIME 格式需为 HH:MM（24 小时制）")

        if errors:
            env_filename = self.config_service.get_env_filename()
            stock_list = self.config_service.get_stock_list()
            body = render_config_page(stock_list, env_filename, message="保存失败：" + "；".join(errors), common_config=current)
            return HtmlResponse(body, status=HTTPStatus.BAD_REQUEST)

        updates = {
            "SCHEDULE_ENABLED": _get_bool("SCHEDULE_ENABLED"),
            "SCHEDULE_TIME": st,
            "MARKET_REVIEW_ENABLED": _get_bool("MARKET_REVIEW_ENABLED"),
        }

        self.config_service.update_env_values(updates)

        env_filename = self.config_service.get_env_filename()
        stock_list = self.config_service.get_stock_list()
        common = self.config_service.get_env_values(
            [
                ("SCHEDULE_ENABLED", "false"),
                ("SCHEDULE_TIME", "18:00"),
                ("MARKET_REVIEW_ENABLED", "true"),
            ]
        )
        body = render_config_page(
            stock_list,
            env_filename,
            message="常用配置已保存（部分配置需重启生效）",
            common_config=common,
        )
        return HtmlResponse(body)

    def handle_env_editor(self, request_handler: "BaseHTTPRequestHandler") -> Response:
        """处理 .env 编辑器页面 GET /env（仅允许本机回环地址访问）。"""
        if not _is_loopback_request(request_handler):
            body = render_error_page(403, "禁止访问", "该页面仅允许本机访问（127.0.0.1 / ::1）")
            return HtmlResponse(body, status=HTTPStatus.FORBIDDEN)

        env_text = self.config_service.read_env_text()
        env_filename = self.config_service.get_env_filename()
        body = render_env_editor_page(env_text, env_filename)
        return HtmlResponse(body)

    def handle_env_update(self, request_handler: "BaseHTTPRequestHandler", form_data: Dict[str, list]) -> Response:
        """保存 .env 全量内容 POST /env/update（仅允许本机回环地址访问）。"""
        if not _is_loopback_request(request_handler):
            body = render_error_page(403, "禁止访问", "该操作仅允许本机访问（127.0.0.1 / ::1）")
            return HtmlResponse(body, status=HTTPStatus.FORBIDDEN)

        env_text = form_data.get("env_text", [""])[0]
        try:
            backup_name = self.config_service.set_env_text(env_text)
            env_filename = self.config_service.get_env_filename()
            body = render_env_editor_page(env_text, env_filename, message=f"已保存（已自动备份：{backup_name}）")
            return HtmlResponse(body)
        except Exception as e:
            env_filename = self.config_service.get_env_filename()
            body = render_env_editor_page(env_text, env_filename, message=f"保存失败：{e}")
            return HtmlResponse(body, status=HTTPStatus.INTERNAL_SERVER_ERROR)


# ============================================================
# API 处理器
# ============================================================

class ApiHandler:
    """API 请求处理器"""
    
    def __init__(self):
        self.analysis_service = get_analysis_service()
    
    def handle_health(self, request_handler: "BaseHTTPRequestHandler") -> Response:
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
    
    def handle_analysis(self, request_handler: "BaseHTTPRequestHandler", query: Dict[str, list]) -> Response:
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

        # 验证股票代码格式：A股(6位数字) / 港股(hk+5位数字) / 美股(1-5个大写字母)
        code = code.lower()
        is_a_stock = re.match(r'^\d{6}$', code)
        is_hk_stock = re.match(r'^hk\d{5}$', code)
        is_us_stock = re.match(r'^[A-Z]{1,5}(\.[A-Z])?$', code.upper())

        # 兼容策略：01xxxx 通常为场外基金代码（净值），当前 WebUI 不支持，避免误分析
        if is_a_stock and re.match(r'^01\d{4}$', code):
            return JsonResponse(
                {"success": False, "error": f"暂不支持场外基金代码: {code}（请使用场内 ETF 代码，如 510300 / 159915）"},
                status=HTTPStatus.BAD_REQUEST
            )

        if not (is_a_stock or is_hk_stock or is_us_stock):
            return JsonResponse(
                {"success": False, "error": f"无效的股票代码格式: {code} (A股6位数字 / 港股hk+5位数字 / 美股1-5个字母)"},
                status=HTTPStatus.BAD_REQUEST
            )
        
        # 获取报告类型参数（默认精简报告）
        report_type_str = query.get("report_type", ["simple"])[0]
        report_type = ReportType.from_str(report_type_str)
        
        # 提交异步分析任务
        try:
            result = self.analysis_service.submit_analysis(code, report_type=report_type)
            return JsonResponse(result)
        except Exception as e:
            logger.error(f"[ApiHandler] 提交分析任务失败: {e}")
            return JsonResponse(
                {"success": False, "error": f"提交任务失败: {str(e)}"},
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )
    
    def handle_tasks(self, request_handler: "BaseHTTPRequestHandler", query: Dict[str, list]) -> Response:
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
    
    def handle_task_status(self, request_handler: "BaseHTTPRequestHandler", query: Dict[str, list]) -> Response:
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

    def handle_market_review(self, request_handler: "BaseHTTPRequestHandler", query: Dict[str, list]) -> Response:
        """
        触发大盘复盘 GET /market-review

        返回:
            {"success": true, "task_id": "...", "message": "..."}
        """
        try:
            result = self.analysis_service.submit_market_review()
            return JsonResponse(result)
        except Exception as e:
            logger.error(f"[ApiHandler] 提交大盘复盘任务失败: {e}")
            return JsonResponse(
                {"success": False, "error": f"提交任务失败: {str(e)}"},
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )


# ============================================================
# Bot Webhook 处理器
# ============================================================

class BotHandler:
    """
    机器人 Webhook 处理器
    
    处理各平台的机器人回调请求。
    """
    
    def handle_webhook(self, platform: str, form_data: Dict[str, list], headers: Dict[str, str], body: bytes) -> Response:
        """
        处理 Webhook 请求
        
        Args:
            platform: 平台名称 (feishu, dingtalk, wecom, telegram)
            form_data: POST 数据（已解析）
            headers: HTTP 请求头
            body: 原始请求体
            
        Returns:
            Response 对象
        """
        try:
            from bot.handler import handle_webhook
            from bot.models import WebhookResponse
            
            # 调用 bot 模块处理
            webhook_response = handle_webhook(platform, headers, body)
            
            # 转换为 web 响应
            return JsonResponse(
                webhook_response.body,
                status=HTTPStatus(webhook_response.status_code)
            )
            
        except ImportError as e:
            logger.error(f"[BotHandler] Bot 模块未正确安装: {e}")
            return JsonResponse(
                {"error": "Bot module not available"},
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.error(f"[BotHandler] 处理 {platform} Webhook 失败: {e}")
            return JsonResponse(
                {"error": str(e)},
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )


# ============================================================
# 处理器工厂
# ============================================================

_page_handler: PageHandler | None = None
_api_handler: ApiHandler | None = None
_bot_handler: BotHandler | None = None


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


def get_bot_handler() -> BotHandler:
    """获取 Bot 处理器实例"""
    global _bot_handler
    if _bot_handler is None:
        _bot_handler = BotHandler()
    return _bot_handler
