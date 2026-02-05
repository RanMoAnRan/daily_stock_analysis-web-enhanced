# -*- coding: utf-8 -*-
"""
===================================
Web 服务层 - 业务逻辑
===================================

职责：
1. 配置管理服务 (ConfigService)
2. 分析任务服务 (AnalysisService)
"""

from __future__ import annotations

import os
import re
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Union, Iterable, Tuple

from src.enums import ReportType
from bot.models import BotMessage

logger = logging.getLogger(__name__)

# ============================================================
# 配置管理服务
# ============================================================

_ENV_PATH = os.getenv("ENV_FILE", ".env")

_STOCK_LIST_RE = re.compile(
    r"^(?P<prefix>\s*STOCK_LIST\s*=\s*)(?P<value>.*?)(?P<suffix>\s*)$"
)


class ConfigService:
    """
    配置管理服务
    
    负责 .env 文件中 STOCK_LIST 的读写操作
    """
    
    def __init__(self, env_path: Optional[str] = None):
        self.env_path = env_path or _ENV_PATH
    
    def read_env_text(self) -> str:
        """读取 .env 文件内容"""
        try:
            with open(self.env_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return ""
    
    def write_env_text(self, text: str) -> None:
        """写入 .env 文件内容"""
        with open(self.env_path, "w", encoding="utf-8") as f:
            f.write(text)

    def set_env_text(self, text: str) -> str:
        """
        全量覆盖写入 .env（用于 WebUI 配置中心）。

        Returns:
            备份文件名（同目录）。
        """
        p = Path(self.env_path)
        p.parent.mkdir(parents=True, exist_ok=True)

        try:
            old = p.read_text(encoding="utf-8")
        except FileNotFoundError:
            old = ""

        # 备份：.env.bak.YYYYMMDD_HHMMSS
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{p.name}.bak.{stamp}"
        backup_path = p.with_name(backup_name)
        try:
            backup_path.write_text(old, encoding="utf-8")
        except Exception:
            # 备份失败不应阻塞保存；但仍继续写入
            pass

        new_text = text if text.endswith("\n") or text == "" else (text + "\n")
        p.write_text(new_text, encoding="utf-8")
        return backup_name
    
    def get_stock_list(self) -> str:
        """获取当前自选股列表字符串"""
        env_text = self.read_env_text()
        return self._extract_stock_list(env_text)
    
    def set_stock_list(self, stock_list: str) -> str:
        """
        设置自选股列表
        
        Args:
            stock_list: 股票代码字符串（逗号或换行分隔）
            
        Returns:
            规范化后的股票列表字符串
        """
        env_text = self.read_env_text()
        normalized = self._normalize_stock_list(stock_list)
        updated = self._update_stock_list(env_text, normalized)
        self.write_env_text(updated)
        return normalized
    
    def get_env_filename(self) -> str:
        """获取 .env 文件名"""
        return os.path.basename(self.env_path)

    def get_env_values(
        self,
        keys: Iterable[Tuple[str, str]],
    ) -> Dict[str, str]:
        """
        从 .env 文件读取指定 key 的值（优先文件，其次 default）。

        Args:
            keys: [(KEY, default_str), ...]
        """
        env_text = self.read_env_text()
        data = self._parse_env_text(env_text)
        out: Dict[str, str] = {}
        for k, default in keys:
            v = data.get(k)
            out[k] = v if v is not None else default
        return out

    def update_env_values(self, updates: Dict[str, str]) -> None:
        """
        更新 .env 中多个 key 的值（保留原有注释/其他行；不存在的 key 追加到末尾）。
        """
        env_text = self.read_env_text()
        updated = self._update_env_kv(env_text, updates)
        self.write_env_text(updated)

    def _extract_stock_list(self, env_text: str) -> str:
        """从环境文件中提取 STOCK_LIST 值"""
        for line in env_text.splitlines():
            m = _STOCK_LIST_RE.match(line)
            if m:
                raw = m.group("value").strip()
                # 去除引号
                if (raw.startswith('"') and raw.endswith('"')) or \
                   (raw.startswith("'") and raw.endswith("'")):
                    raw = raw[1:-1]
                return raw
        return ""
    
    def _normalize_stock_list(self, value: str) -> str:
        """规范化股票列表格式"""
        parts = [p.strip() for p in value.replace("\n", ",").split(",")]
        parts = [p for p in parts if p]
        return ",".join(parts)
    
    def _update_stock_list(self, env_text: str, new_value: str) -> str:
        """更新环境文件中的 STOCK_LIST"""
        lines = env_text.splitlines(keepends=False)
        out_lines: List[str] = []
        replaced = False
        
        for line in lines:
            m = _STOCK_LIST_RE.match(line)
            if not m:
                out_lines.append(line)
                continue
            
            out_lines.append(f"{m.group('prefix')}{new_value}{m.group('suffix')}")
            replaced = True
        
        if not replaced:
            if out_lines and out_lines[-1].strip() != "":
                out_lines.append("")
            out_lines.append(f"STOCK_LIST={new_value}")
        
        trailing_newline = env_text.endswith("\n") if env_text else True
        out = "\n".join(out_lines)
        return out + ("\n" if trailing_newline else "")

    def _parse_env_text(self, env_text: str) -> Dict[str, str]:
        """
        解析 .env 为 dict（非常轻量，忽略注释行；支持简单引号/双引号）。
        """
        out: Dict[str, str] = {}
        for raw_line in (env_text or "").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip()
            if not k:
                continue
            if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                v = v[1:-1]
            out[k] = v
        return out

    def _update_env_kv(self, env_text: str, updates: Dict[str, str]) -> str:
        """
        在保持原始行结构的前提下更新 KEY=VALUE（仅更新非注释行）。
        """
        lines = (env_text or "").splitlines(keepends=False)
        out_lines: List[str] = []
        replaced: set[str] = set()

        # 针对每个更新 key 做一次正则，保留 prefix/suffix
        patterns: Dict[str, re.Pattern[str]] = {}
        for k in updates.keys():
            patterns[k] = re.compile(rf"^(?P<prefix>\s*{re.escape(k)}\s*=\s*)(?P<value>.*?)(?P<suffix>\s*)$")

        for line in lines:
            stripped = line.lstrip()
            if stripped.startswith("#") or "=" not in line:
                out_lines.append(line)
                continue

            hit = False
            for k, pat in patterns.items():
                m = pat.match(line)
                if not m:
                    continue
                out_lines.append(f"{m.group('prefix')}{updates.get(k, '')}{m.group('suffix')}")
                replaced.add(k)
                hit = True
                break

            if not hit:
                out_lines.append(line)

        # 追加缺失的 key
        missing = [k for k in updates.keys() if k not in replaced]
        if missing:
            if out_lines and out_lines[-1].strip() != "":
                out_lines.append("")
            for k in missing:
                out_lines.append(f"{k}={updates.get(k, '')}")

        trailing_newline = env_text.endswith("\n") if env_text else True
        out = "\n".join(out_lines)
        return out + ("\n" if trailing_newline else "")


# ============================================================
# 分析任务服务
# ============================================================

class AnalysisService:
    """
    分析任务服务
    
    负责：
    1. 管理异步分析任务
    2. 执行股票分析
    3. 触发通知推送
    """
    
    _instance: Optional['AnalysisService'] = None
    _lock = threading.Lock()
    
    def __init__(self, max_workers: int = 3):
        self._executor: Optional[ThreadPoolExecutor] = None
        self._max_workers = max_workers
        self._tasks: Dict[str, Dict[str, Any]] = {}
        self._tasks_lock = threading.Lock()
        self._max_task_logs = 200
    
    @classmethod
    def get_instance(cls) -> 'AnalysisService':
        """获取单例实例"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    @property
    def executor(self) -> ThreadPoolExecutor:
        """获取或创建线程池"""
        if self._executor is None:
            self._executor = ThreadPoolExecutor(
                max_workers=self._max_workers,
                thread_name_prefix="analysis_"
            )
        return self._executor
    
    def submit_analysis(
        self, 
        code: str, 
        report_type: Union[ReportType, str] = ReportType.SIMPLE,
        source_message: Optional[BotMessage] = None,
        send_notification: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        提交异步分析任务
        
        Args:
            code: 股票代码
            report_type: 报告类型枚举
            
        Returns:
            任务信息字典
        """
        # 确保 report_type 是枚举类型
        if isinstance(report_type, str):
            report_type = ReportType.from_str(report_type)

        # 默认行为：
        # - WebUI 触发（无 source_message）：不推送任何通知，只在 WebUI 展示结果
        # - Bot 命令触发（有 source_message）：分析完成后推送到会话/已配置渠道
        if send_notification is None:
            send_notification = source_message is not None
        
        task_id = f"{code}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # 提交到线程池
        self.executor.submit(self._run_analysis, code, task_id, report_type, source_message, bool(send_notification))
        
        logger.info(f"[AnalysisService] 已提交股票 {code} 的分析任务, task_id={task_id}, report_type={report_type.value}")
        
        return {
            "success": True,
            "message": "分析任务已提交，将异步执行并展示结果" if not send_notification else "分析任务已提交，将异步执行并推送通知",
            "code": code,
            "task_id": task_id,
            "report_type": report_type.value,
            "send_notification": bool(send_notification)
        }

    def submit_market_review(self) -> Dict[str, Any]:
        """
        提交异步“大盘复盘”任务（WebUI 专用：默认不推送通知）。
        """
        task_id = f"market_review_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        self.executor.submit(self._run_market_review, task_id)
        logger.info(f"[AnalysisService] 已提交大盘复盘任务, task_id={task_id}")
        return {
            "success": True,
            "message": "大盘复盘任务已提交，将异步执行并在 WebUI 展示",
            "task_id": task_id
        }
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        with self._tasks_lock:
            return self._tasks.get(task_id)
    
    def list_tasks(self, limit: int = 20) -> List[Dict[str, Any]]:
        """列出最近的任务"""
        with self._tasks_lock:
            tasks = list(self._tasks.values())
        # 按开始时间倒序
        tasks.sort(key=lambda x: x.get('start_time', ''), reverse=True)
        return tasks[:limit]

    def _append_task_log(
        self,
        task_id: str,
        level: str,
        message: str,
        stage: Optional[str] = None,
        progress: Optional[int] = None
    ) -> None:
        """追加任务日志（用于 WebUI 实时展示）。"""
        entry = {
            "ts": datetime.now().isoformat(),
            "level": level,
            "msg": message,
        }

        with self._tasks_lock:
            task = self._tasks.get(task_id)
            if not task:
                return

            logs = task.get("logs")
            if not isinstance(logs, list):
                logs = []
            logs.append(entry)
            if len(logs) > self._max_task_logs:
                logs = logs[-self._max_task_logs:]
            task["logs"] = logs

            if stage is not None:
                task["stage"] = stage
            if progress is not None:
                task["progress"] = int(progress)
    
    def _run_analysis(
        self, 
        code: str, 
        task_id: str, 
        report_type: ReportType = ReportType.SIMPLE,
        source_message: Optional[BotMessage] = None,
        send_notification: bool = False
    ) -> Dict[str, Any]:
        """
        执行单只股票分析
        
        内部方法，在线程池中运行
        
        Args:
            code: 股票代码
            task_id: 任务ID
            report_type: 报告类型枚举
        """
        # 初始化任务状态
        with self._tasks_lock:
            self._tasks[task_id] = {
                "task_id": task_id,
                "code": code,
                "status": "running",
                "start_time": datetime.now().isoformat(),
                "result": None,
                "error": None,
                "report_type": report_type.value,
                "send_notification": bool(send_notification),
                "stage": "init",
                "progress": 0,
                "logs": [],
            }

        self._append_task_log(task_id, "INFO", f"任务开始：{code}", stage="init", progress=3)
        
        try:
            # 延迟导入避免循环依赖
            from src.config import get_config
            from src.core.pipeline import StockAnalysisPipeline
            
            logger.info(f"[AnalysisService] 开始分析股票: {code}")
            self._append_task_log(task_id, "INFO", "初始化分析管道...", stage="init", progress=8)
            
            # 创建分析管道
            config = get_config()
            pipeline = StockAnalysisPipeline(
                config=config,
                max_workers=1,
                source_message=source_message
            )

            # Step 1: 获取并保存数据
            self._append_task_log(task_id, "INFO", "Step 1/3 获取并保存行情数据...", stage="fetch_data", progress=18)
            success, error = pipeline.fetch_and_save_stock_data(code)
            if success:
                self._append_task_log(task_id, "INFO", "行情数据已就绪", stage="fetch_data", progress=35)
            else:
                # 允许继续：pipeline 内部会尝试使用已有数据继续分析
                self._append_task_log(task_id, "WARNING", f"行情数据获取失败：{error}（将尝试使用已有数据继续）", stage="fetch_data", progress=35)

            # Step 2: AI 分析
            self._append_task_log(task_id, "INFO", "Step 2/3 执行趋势/情报/AI 综合分析...", stage="analyze", progress=55)
            result = pipeline.analyze_stock(code)
            
            if result:
                # WebUI 展示：尽量保留完整结果字段，方便前端展示更多细节
                result_data = result.to_dict()
                # 尽早写入一次中间结果，便于 WebUI 提前展示摘要/评分等
                with self._tasks_lock:
                    self._tasks[task_id]["result"] = result_data

                # 生成报告内容（Markdown），用于 WebUI 展示（不等于推送）
                self._append_task_log(task_id, "INFO", "Step 3/3 生成报告内容...", stage="render_report", progress=85)
                try:
                    if report_type == ReportType.FULL:
                        result_data["report_markdown"] = pipeline.notifier.generate_dashboard_report([result])
                    else:
                        result_data["report_markdown"] = pipeline.notifier.generate_single_stock_report(result)
                except Exception as e:
                    logger.warning(f"[AnalysisService] 生成 WebUI 报告内容失败: {e}")
                    result_data["report_markdown"] = ""

                # 生成报告 HTML（Markdown 预览用）。markdown2 为可选依赖：未安装则跳过。
                report_md = result_data.get("report_markdown") or ""
                try:
                    import markdown2  # type: ignore

                    report_html = markdown2.markdown(
                        report_md,
                        safe_mode="escape",
                        extras=["fenced-code-blocks", "tables"]
                    )

                    # 防御性处理：避免 javascript: 链接
                    report_html = re.sub(r'href\\s*=\\s*\"\\s*javascript:[^\"]*\"', 'href=\"#\"', str(report_html), flags=re.IGNORECASE)
                    report_html = re.sub(r"href\\s*=\\s*'\\s*javascript:[^']*'", "href='#'", str(report_html), flags=re.IGNORECASE)

                    result_data["report_html"] = str(report_html)
                except Exception as e:
                    logger.debug(f"[AnalysisService] 生成 Markdown 预览 HTML 失败（可忽略）: {e}")
                    result_data["report_html"] = ""
                # 再次写入（包含 report_markdown）
                with self._tasks_lock:
                    self._tasks[task_id]["result"] = result_data
                self._append_task_log(task_id, "INFO", "报告已生成", stage="render_report", progress=92)

                # 可选：推送（Bot 触发时）
                if send_notification and pipeline.notifier.is_available():
                    self._append_task_log(task_id, "INFO", "推送通知中...", stage="notify", progress=95)
                    try:
                        report_content = result_data.get("report_markdown") or ""
                        sent_ok = pipeline.notifier.send(report_content) if report_content else False
                        if sent_ok:
                            self._append_task_log(task_id, "INFO", "推送成功", stage="notify", progress=97)
                        else:
                            self._append_task_log(task_id, "WARNING", "推送失败或未配置有效渠道", stage="notify", progress=97)
                    except Exception as e:
                        self._append_task_log(task_id, "ERROR", f"推送异常：{e}", stage="notify", progress=97)
                
                with self._tasks_lock:
                    self._tasks[task_id].update({
                        "status": "completed",
                        "end_time": datetime.now().isoformat(),
                        "result": result_data
                    })
                
                logger.info(f"[AnalysisService] 股票 {code} 分析完成: {result.operation_advice}")
                self._append_task_log(task_id, "INFO", "任务完成", stage="done", progress=100)
                return {"success": True, "task_id": task_id, "result": result_data}
            else:
                with self._tasks_lock:
                    self._tasks[task_id].update({
                        "status": "failed",
                        "end_time": datetime.now().isoformat(),
                        "error": "分析返回空结果"
                    })
                
                logger.warning(f"[AnalysisService] 股票 {code} 分析失败: 返回空结果")
                self._append_task_log(task_id, "ERROR", "分析失败：返回空结果", stage="failed", progress=100)
                return {"success": False, "task_id": task_id, "error": "分析返回空结果"}
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"[AnalysisService] 股票 {code} 分析异常: {error_msg}")
            
            with self._tasks_lock:
                self._tasks[task_id].update({
                    "status": "failed",
                    "end_time": datetime.now().isoformat(),
                    "error": error_msg
                })
            self._append_task_log(task_id, "ERROR", f"任务异常：{error_msg}", stage="failed", progress=100)
            return {"success": False, "task_id": task_id, "error": error_msg}

    def _run_market_review(self, task_id: str) -> Dict[str, Any]:
        """
        执行大盘复盘分析（用于 WebUI 展示，不推送）。
        """
        with self._tasks_lock:
            self._tasks[task_id] = {
                "task_id": task_id,
                "code": "market",
                "kind": "market_review",
                "status": "running",
                "start_time": datetime.now().isoformat(),
                "result": None,
                "error": None,
                "report_type": "full",
                "send_notification": False,
                "stage": "market_review",
                "progress": 0,
                "logs": [],
            }

        self._append_task_log(task_id, "INFO", "任务开始：大盘复盘", stage="market_review", progress=5)

        try:
            # 延迟导入，避免 WebUI-only 启动时无关依赖阻塞
            from src.config import get_config
            from src.core.market_review import run_market_review

            cfg = get_config()

            # WebUI 不推送：提供一个只负责落盘的 notifier（让 run_market_review 能保存报告）
            class _WebUINotifier:
                def save_report_to_file(self, content: str, filename: Optional[str] = None) -> str:
                    from datetime import datetime as _dt
                    from pathlib import Path as _Path
                    if filename is None:
                        date_str = _dt.now().strftime('%Y%m%d')
                        filename = f"market_review_{date_str}.md"
                    reports_dir = _Path(__file__).parent.parent / 'reports'
                    reports_dir.mkdir(parents=True, exist_ok=True)
                    filepath = reports_dir / filename
                    filepath.write_text(content, encoding='utf-8')
                    return str(filepath)

                def is_available(self) -> bool:
                    return False

                def send(self, _content: str) -> bool:
                    return False

            # 可选：搜索与 AI
            analyzer = None
            search_service = None
            try:
                from src.search_service import SearchService
                if cfg.bocha_api_keys or cfg.tavily_api_keys or cfg.serpapi_keys:
                    search_service = SearchService(
                        bocha_keys=cfg.bocha_api_keys,
                        tavily_keys=cfg.tavily_api_keys,
                        serpapi_keys=cfg.serpapi_keys
                    )
            except Exception as e:
                self._append_task_log(task_id, "WARNING", f"搜索服务初始化失败（将继续）：{e}")

            try:
                from src.analyzer import GeminiAnalyzer
                if cfg.gemini_api_key:
                    analyzer = GeminiAnalyzer(api_key=cfg.gemini_api_key)
            except Exception as e:
                self._append_task_log(task_id, "WARNING", f"AI 分析器初始化失败（将继续）：{e}")

            self._append_task_log(task_id, "INFO", "执行大盘复盘分析中...", stage="market_review", progress=35)
            review = run_market_review(_WebUINotifier(), analyzer=analyzer, search_service=search_service)

            if not review:
                with self._tasks_lock:
                    self._tasks[task_id].update({
                        "status": "failed",
                        "end_time": datetime.now().isoformat(),
                        "error": "大盘复盘返回空结果"
                    })
                self._append_task_log(task_id, "ERROR", "大盘复盘失败：返回空结果", stage="failed", progress=100)
                return {"success": False, "task_id": task_id, "error": "大盘复盘返回空结果"}

            report_md = f"# 🎯 大盘复盘\n\n{review}"
            result_data: Dict[str, Any] = {
                "name": "大盘复盘",
                "report_markdown": report_md,
                "analysis_summary": "",
                "trend_prediction": "",
                "operation_advice": "",
            }

            # Markdown 预览（可选依赖 markdown2）
            try:
                import markdown2  # type: ignore
                report_html = markdown2.markdown(
                    report_md,
                    safe_mode="escape",
                    extras=["fenced-code-blocks", "tables"]
                )
                report_html = re.sub(r'href\\s*=\\s*\"\\s*javascript:[^\"]*\"', 'href=\"#\"', str(report_html), flags=re.IGNORECASE)
                report_html = re.sub(r"href\\s*=\\s*'\\s*javascript:[^']*'", "href='#'", str(report_html), flags=re.IGNORECASE)
                result_data["report_html"] = str(report_html)
            except Exception:
                result_data["report_html"] = ""

            with self._tasks_lock:
                self._tasks[task_id].update({
                    "status": "completed",
                    "end_time": datetime.now().isoformat(),
                    "result": result_data
                })

            self._append_task_log(task_id, "INFO", "任务完成：大盘复盘", stage="done", progress=100)
            return {"success": True, "task_id": task_id, "result": result_data}

        except Exception as e:
            err = str(e)
            with self._tasks_lock:
                self._tasks[task_id].update({
                    "status": "failed",
                    "end_time": datetime.now().isoformat(),
                    "error": err
                })
            self._append_task_log(task_id, "ERROR", f"任务异常：{err}", stage="failed", progress=100)
            return {"success": False, "task_id": task_id, "error": err}


# ============================================================
# 便捷函数
# ============================================================

def get_config_service() -> ConfigService:
    """获取配置服务实例"""
    return ConfigService()


def get_analysis_service() -> AnalysisService:
    """获取分析服务单例"""
    return AnalysisService.get_instance()
