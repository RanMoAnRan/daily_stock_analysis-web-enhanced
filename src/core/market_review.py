# -*- coding: utf-8 -*-
"""
===================================
A股自选股智能分析系统 - 大盘复盘模块
===================================

职责：
1. 执行大盘复盘分析
2. 生成复盘报告
3. 保存和发送复盘报告
"""

import logging
from datetime import datetime
from typing import Optional

from src.notification import NotificationService
from src.market_analyzer import MarketAnalyzer
from src.search_service import SearchService
from src.analyzer import GeminiAnalyzer


logger = logging.getLogger(__name__)


def run_market_review(
    notifier: NotificationService, 
    analyzer: Optional[GeminiAnalyzer] = None, 
    search_service: Optional[SearchService] = None
) -> Optional[str]:
    """
    执行大盘复盘分析
    
    Args:
        notifier: 通知服务
        analyzer: AI分析器（可选）
        search_service: 搜索服务（可选）
    
    Returns:
        复盘报告文本
    """
    logger.info("开始执行大盘复盘分析...")
    
    try:
        market_analyzer = MarketAnalyzer(
            search_service=search_service,
            analyzer=analyzer
        )
        
        # 执行复盘
        review_report = market_analyzer.run_daily_review()
        
        if review_report:
            overview = getattr(market_analyzer, "last_overview", None)
            snapshot_md = ""
            if overview is not None:
                try:
                    snapshot_md = market_analyzer.format_overview_markdown(overview)
                except Exception as e:
                    logger.warning(f"生成市场数据快照失败，将仅保存复盘正文: {e}")

            # 拼接“数据快照 + 复盘正文”
            if snapshot_md:
                full_report = f"{snapshot_md}\n\n---\n\n{review_report}"
            else:
                full_report = review_report

            # 保存报告到文件
            date_str = datetime.now().strftime('%Y%m%d')
            report_filename = f"market_review_{date_str}.md"
            filepath = notifier.save_report_to_file(
                f"# 🎯 大盘复盘\n\n{full_report}",
                report_filename
            )
            logger.info(f"大盘复盘报告已保存: {filepath}")
            
            # 推送通知
            if notifier.is_available():
                # 添加标题
                report_content = f"🎯 大盘复盘\n\n{full_report}"
                
                success = notifier.send(report_content)
                if success:
                    logger.info("大盘复盘推送成功")
                else:
                    logger.warning("大盘复盘推送失败")
            
            # 返回完整 Markdown（含数据快照），便于 WebUI 展示与上层复用
            return full_report
        
    except Exception as e:
        logger.error(f"大盘复盘分析失败: {e}")
    
    return None
