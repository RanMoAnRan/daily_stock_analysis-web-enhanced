# -*- coding: utf-8 -*-
"""
===================================
Web 模板层 - HTML 页面生成
===================================

职责：
1. 生成 HTML 页面
2. 管理 CSS 样式
3. 提供可复用的页面组件
"""

from __future__ import annotations

import html
from typing import Optional


# ============================================================
# CSS 样式定义
# ============================================================

BASE_CSS = """
:root { color-scheme: light; }

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --primary: #2563eb;
    --primary-hover: #1d4ed8;
    --bg: #f8fafc;
    --card: #ffffff;
    --text: #1e293b;
    --text-light: #64748b;
    --border: #e2e8f0;
    --success: #10b981;
    --error: #ef4444;
    --warning: #f59e0b;
    --shadow: 0 10px 25px rgba(15, 23, 42, 0.08);
    --shadow-sm: 0 4px 12px rgba(15, 23, 42, 0.08);
    --radius-lg: 16px;
    --radius-md: 12px;
    --ring: 0 0 0 4px rgba(37, 99, 235, 0.14);
    --page-pad: 12px;
    --shell-gap: 14px;
    --app-header-h: 76px; /* JS 会在运行时覆盖为真实高度 */
}

* {
    box-sizing: border-box;
}

code {
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
    font-size: 12px;
    background: rgba(15, 23, 42, 0.06);
    border: 1px solid rgba(226, 232, 240, 0.9);
    padding: 2px 6px;
    border-radius: 8px;
}

body {
    font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    background:
        radial-gradient(1200px 600px at 20% 0%, rgba(37, 99, 235, 0.10), transparent 60%),
        radial-gradient(900px 500px at 90% 20%, rgba(16, 185, 129, 0.08), transparent 55%),
        radial-gradient(700px 450px at 55% 100%, rgba(245, 158, 11, 0.07), transparent 55%),
        var(--bg);
    color: var(--text);
    min-height: 100vh;
    margin: 0;
    padding: var(--page-pad);
    /* 单页滑动：页面不随内容撑开，改为面板内滚动 */
    height: 100dvh;
    overflow: hidden;
}

.text-error {
    color: rgba(220, 38, 38, 0.92);
}

.input-error {
    border-color: rgba(239, 68, 68, 0.65) !important;
    box-shadow: 0 0 0 4px rgba(239, 68, 68, 0.12) !important;
}

.app-shell {
    width: 100%;
    max-width: none;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: var(--shell-gap);
    height: calc(100dvh - (var(--page-pad) * 2));
    min-height: 0;
}

.app-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 16px;
    border-radius: var(--radius-lg);
    background: rgba(255, 255, 255, 0.78);
    border: 1px solid rgba(226, 232, 240, 0.85);
    box-shadow: var(--shadow-sm);
    backdrop-filter: blur(10px);
}

.header-right {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 6px;
}

.header-actions {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
}

.nav-link {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 8px 10px;
    border-radius: 999px;
    border: 1px solid rgba(226, 232, 240, 0.9);
    background: rgba(255, 255, 255, 0.9);
    color: rgba(15, 23, 42, 0.92);
    text-decoration: none;
    font-size: 12px;
    font-weight: 800;
    transition: background 120ms ease, border-color 120ms ease, box-shadow 120ms ease;
}

.nav-link:hover {
    background: rgba(255, 255, 255, 1);
    border-color: rgba(148, 163, 184, 0.65);
}

.nav-link.active {
    border-color: rgba(37, 99, 235, 0.55);
    box-shadow: var(--ring);
}

.settings-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 10px;
    margin-top: 10px;
}

.settings-section {
    padding: 10px;
    border-radius: 14px;
    border: 1px solid rgba(226, 232, 240, 0.9);
    background: rgba(255, 255, 255, 0.65);
}

.settings-section-title {
    font-size: 12px;
    font-weight: 900;
    color: rgba(15, 23, 42, 0.92);
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
}

.settings-row {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 10px;
    padding: 6px 0;
    flex-wrap: wrap; /* 左侧栏较窄时自动换行，避免溢出 */
}

.settings-row + .settings-row {
    border-top: 1px dashed rgba(226, 232, 240, 0.95);
}

.settings-label {
    font-size: 12px;
    font-weight: 800;
    color: rgba(15, 23, 42, 0.90);
}

.settings-desc {
    font-size: 12px;
    color: rgba(100, 116, 139, 0.95);
    margin-top: 2px;
    line-height: 1.4;
}

.settings-control {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-shrink: 0;
    max-width: 100%;
}

.input-sm {
    width: 160px;
    max-width: 100%;
    padding: 10px 10px;
    border-radius: 12px;
    border: 1px solid rgba(226, 232, 240, 0.95);
    background: rgba(255, 255, 255, 0.92);
    color: rgba(15, 23, 42, 0.92);
    font-size: 12px;
}

.input-sm:focus-visible {
    outline: none;
    box-shadow: var(--ring);
    border-color: rgba(37, 99, 235, 0.65);
}

.switch {
    position: relative;
    width: 44px;
    height: 26px;
    flex-shrink: 0;
}

.switch input {
    position: absolute;
    opacity: 0;
    width: 0;
    height: 0;
}

.switch-track {
    position: absolute;
    inset: 0;
    border-radius: 999px;
    background: rgba(148, 163, 184, 0.35);
    border: 1px solid rgba(226, 232, 240, 0.95);
    transition: background 140ms ease, border-color 140ms ease;
}

.switch-thumb {
    position: absolute;
    top: 3px;
    left: 3px;
    width: 20px;
    height: 20px;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.95);
    border: 1px solid rgba(226, 232, 240, 0.95);
    box-shadow: 0 8px 18px rgba(15, 23, 42, 0.10);
    transition: transform 140ms ease;
}

.switch input:checked + .switch-track {
    background: rgba(16, 185, 129, 0.35);
    border-color: rgba(16, 185, 129, 0.45);
}

.switch input:checked + .switch-track .switch-thumb {
    transform: translateX(18px);
}

.brand-line {
    display: flex;
    align-items: center;
    gap: 10px;
    min-width: 0;
}

.brand-mark {
    width: 28px;
    height: 28px;
    border-radius: 10px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, rgba(37, 99, 235, 0.18), rgba(16, 185, 129, 0.14));
    border: 1px solid rgba(226, 232, 240, 0.85);
    flex-shrink: 0;
}

.brand-mark svg {
    width: 16px;
    height: 16px;
    stroke: rgba(30, 41, 59, 0.95);
}

.brand {
    display: flex;
    flex-direction: column;
    gap: 2px;
    min-width: 0;
}

.brand-title {
    font-size: 16px;
    font-weight: 800;
    letter-spacing: 0.2px;
}

.brand-subtitle {
    font-size: 12px;
    color: var(--text-light);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.app-grid {
    display: grid;
    /* 左侧配置更窄，给右侧结果更多空间 */
    grid-template-columns: 280px 1fr;
    gap: 14px;
    flex: 1;
    min-height: 0;
    overflow: hidden;
}

.panel {
    display: flex;
    flex-direction: column;
    gap: 14px;
    min-width: 0;
    min-height: 0;
    overflow: hidden;
}

.app-grid > .panel:first-child {
    /* 左侧：内容过多时单独滚动 */
    overflow: auto;
    padding-right: 2px;
}

.app-grid > .panel:last-child {
    /* 右侧：内部拆分区域滚动 */
    overflow: hidden;
}

.card {
    background: rgba(255, 255, 255, 0.85);
    border: 1px solid rgba(226, 232, 240, 0.85);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow);
    backdrop-filter: blur(10px);
    padding: 16px;
}

.sticky-card {
    position: sticky;
    top: 0;
    z-index: 30;
}

.card:hover {
    border-color: rgba(148, 163, 184, 0.55);
}

.results-card {
    display: flex;
    flex-direction: column;
    min-height: 0;
    flex: 1;
}

.card-title {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    margin-bottom: 10px;
}

.card-title h2, .card-title h3 {
    margin: 0;
    font-size: 14px;
    font-weight: 800;
}

.section-title {
    display: inline-flex;
    align-items: center;
    gap: 8px;
}

.section-icon {
    width: 18px;
    height: 18px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 8px;
    background: rgba(148, 163, 184, 0.12);
    border: 1px solid rgba(226, 232, 240, 0.9);
    flex-shrink: 0;
}

.section-icon svg {
    width: 14px;
    height: 14px;
    stroke: rgba(30, 41, 59, 0.9);
}

.card-hint {
    font-size: 12px;
    color: var(--text-light);
}

.container {
    /* 向后兼容：旧结构仍可用 */
    width: 100%;
}

h2 {
    margin-top: 0;
    color: var(--text);
    font-size: 1.5rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.subtitle {
    color: var(--text-light);
    font-size: 0.875rem;
    margin-bottom: 2rem;
    line-height: 1.5;
}

.code-badge {
    background: #f1f5f9;
    padding: 0.2rem 0.4rem;
    border-radius: 0.25rem;
    font-family: monospace;
    color: var(--primary);
}

.form-group {
    margin-bottom: 1.5rem;
}

label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: var(--text);
}

textarea, input[type="text"] {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid rgba(226, 232, 240, 0.95);
    border-radius: var(--radius-md);
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
    font-size: 0.875rem;
    line-height: 1.5;
    resize: vertical;
    transition: border-color 0.2s, box-shadow 0.2s;
    background: rgba(255, 255, 255, 0.95);
}

#analysis_codes {
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: 0.2px;
    resize: vertical;
    min-height: 84px;
}

textarea:focus, input[type="text"]:focus {
    outline: none;
    border-color: var(--primary);
    box-shadow: var(--ring);
}

button {
    background: linear-gradient(180deg, rgba(37, 99, 235, 0.98), rgba(37, 99, 235, 0.86));
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: var(--radius-md);
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    width: 100%;
    font-size: 1rem;
    box-shadow: 0 8px 18px rgba(37, 99, 235, 0.18);
}

button:hover {
    background: linear-gradient(180deg, rgba(29, 78, 216, 0.98), rgba(29, 78, 216, 0.86));
}

button:active {
    transform: translateY(1px);
}

button:focus-visible {
    outline: none;
    box-shadow: var(--ring), 0 8px 18px rgba(37, 99, 235, 0.18);
}

.btn-secondary {
    background-color: var(--text-light);
}

.btn-secondary:hover {
    background-color: var(--text);
}

.footer {
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border);
    color: var(--text-light);
    font-size: 0.75rem;
    text-align: center;
}

/* Toast Notification */
.toast {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%) translateY(100px);
    background: white;
    border-left: 4px solid var(--success);
    padding: 1rem 1.5rem;
    border-radius: 0.5rem;
    box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1);
    display: flex;
    align-items: center;
    gap: 0.75rem;
    transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    opacity: 0;
    z-index: 1000;
}

.toast.show {
    transform: translateX(-50%) translateY(0);
    opacity: 1;
}

.toast.error {
    border-left-color: var(--error);
}

.toast.warning {
    border-left-color: var(--warning);
}

.toast-dot {
    width: 10px;
    height: 10px;
    border-radius: 999px;
    background: var(--success);
    box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.14);
    flex-shrink: 0;
}

.toast.error .toast-dot {
    background: var(--error);
    box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.14);
}

.toast.warning .toast-dot {
    background: var(--warning);
    box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.14);
}

/* Helper classes */
.text-muted {
    font-size: 0.75rem;
    color: var(--text-light);
    margin-top: 0.5rem;
}

.mt-2 { margin-top: 0.5rem; }
.mt-4 { margin-top: 1rem; }
.mb-2 { margin-bottom: 0.5rem; }
.mb-4 { margin-bottom: 1rem; }

/* Section divider */
.section-divider {
    margin: 2rem 0;
    border: none;
    border-top: 1px solid var(--border);
}

/* Analysis section */
.analysis-section {
    margin-top: 1.5rem;
    padding-top: 1.5rem;
    border-top: 1px solid var(--border);
}

.analysis-section h3 {
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 1rem;
    color: var(--text);
}

.input-group {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
}

.input-group textarea,
.input-group input {
    flex: 1;
    resize: none;
    min-width: 190px;
}

.input-group textarea::placeholder {
    color: rgba(100, 116, 139, 0.72); /* 更像“提示文字” */
    font-size: 12px;
}

.input-group textarea:focus::placeholder {
    color: rgba(100, 116, 139, 0.55);
}

.input-group button {
    width: auto;
    padding: 0.75rem 1.25rem;
    white-space: nowrap;
}

.report-select {
    appearance: none;
    -webkit-appearance: none;
    -moz-appearance: none;
    padding: 0.75rem 0.5rem;
    border: 1px solid rgba(226, 232, 240, 0.95);
    border-radius: var(--radius-md);
    font-size: 0.8rem;
    background: rgba(255, 255, 255, 0.95);
    color: var(--text);
    cursor: pointer;
    min-width: 110px;
    transition: border-color 0.2s, box-shadow 0.2s;
}

.report-select:focus {
    outline: none;
    border-color: var(--primary);
    box-shadow: var(--ring);
}

.select-wrap {
    position: relative;
    display: inline-flex;
    align-items: center;
    flex-shrink: 0;
}

.select-wrap .report-select {
    padding-right: 34px; /* room for chevron */
    background: rgba(255, 255, 255, 0.92);
}

.select-icon {
    position: absolute;
    right: 10px;
    width: 16px;
    height: 16px;
    pointer-events: none;
    stroke: rgba(71, 85, 105, 0.95);
    opacity: 0.9;
}

.segmented {
    display: inline-flex;
    align-items: center;
    padding: 4px;
    border-radius: 999px;
    background: rgba(15, 23, 42, 0.04);
    border: 1px solid rgba(226, 232, 240, 0.95);
    flex-shrink: 0;
}

.seg-btn {
    appearance: none;
    border: 0;
    background: transparent;
    color: rgba(30, 41, 59, 0.85);
    font-size: 12px;
    font-weight: 800;
    padding: 10px 12px;
    border-radius: 999px;
    cursor: pointer;
    transition: background 120ms ease, color 120ms ease, box-shadow 120ms ease;
    white-space: nowrap;
}

.seg-btn:hover {
    background: rgba(37, 99, 235, 0.10);
    color: rgba(30, 41, 59, 0.95);
}

.seg-btn.active {
    background: rgba(255, 255, 255, 0.92);
    color: rgba(15, 23, 42, 0.95);
    box-shadow: 0 10px 22px rgba(15, 23, 42, 0.10);
    border: 1px solid rgba(226, 232, 240, 0.95);
}

.seg-btn:focus-visible {
    outline: none;
    box-shadow: var(--ring);
}

.btn-analysis {
    background: linear-gradient(180deg, rgba(16, 185, 129, 0.98), rgba(16, 185, 129, 0.86));
    box-shadow: 0 8px 18px rgba(16, 185, 129, 0.18);
}

.btn-market {
    background: linear-gradient(180deg, rgba(245, 158, 11, 0.98), rgba(245, 158, 11, 0.84));
    color: rgba(255, 255, 255, 0.98);
    border: 1px solid rgba(245, 158, 11, 0.55);
    box-shadow: 0 10px 22px rgba(245, 158, 11, 0.22);
}

.btn-market:hover {
    background: linear-gradient(180deg, rgba(217, 119, 6, 0.98), rgba(217, 119, 6, 0.84));
}

.btn-market:disabled {
    opacity: 0.7;
    cursor: not-allowed;
    box-shadow: none;
}

.btn-analysis:hover {
    background: linear-gradient(180deg, rgba(5, 150, 105, 0.98), rgba(5, 150, 105, 0.86));
}

.btn-analysis:disabled {
    background-color: var(--text-light);
    cursor: not-allowed;
    transform: none;
}

/* Result box */
.result-box {
    margin-top: 1rem;
    padding: 1rem;
    border-radius: 0.5rem;
    font-size: 0.875rem;
    display: none;
}

.result-box.show {
    display: block;
}

.result-box.success {
    background-color: #ecfdf5;
    border: 1px solid #a7f3d0;
    color: #065f46;
}

.result-box.error {
    background-color: #fef2f2;
    border: 1px solid #fecaca;
    color: #991b1b;
}

.result-box.loading {
    background-color: #eff6ff;
    border: 1px solid #bfdbfe;
    color: #1e40af;
}

.spinner {
    display: inline-block;
    width: 14px;
    height: 14px;
    border: 2px solid currentColor;
    border-right-color: transparent;
    border-radius: 50%;
    animation: spin 0.75s linear infinite;
    margin-right: 0.5rem;
    vertical-align: middle;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

/* Task List Container */
.task-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    max-height: none;
    height: 100%;
    overflow-y: auto;
    padding-right: 2px;
    min-height: 0;
}

.task-list:empty::after {
    content: '暂无任务';
    display: block;
    text-align: center;
    color: var(--text-light);
    font-size: 0.8rem;
    padding: 1rem;
}

/* Task Card - Compact */
.task-card {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.6rem 0.75rem;
    background: var(--bg);
    border-radius: 0.5rem;
    border: 1px solid var(--border);
    font-size: 0.8rem;
    transition: all 0.2s;
    cursor: pointer;
}

.task-card:hover {
    border-color: var(--primary);
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.task-card.selected {
    border-color: rgba(37, 99, 235, 0.7);
    background: linear-gradient(135deg, rgba(37, 99, 235, 0.08) 0%, rgba(248, 250, 252, 1) 100%);
}

.task-card.running {
    border-color: var(--primary);
    background: linear-gradient(135deg, #eff6ff 0%, #f8fafc 100%);
}

.task-card.completed {
    border-color: var(--success);
    background: linear-gradient(135deg, #ecfdf5 0%, #f8fafc 100%);
}

.task-card.failed {
    border-color: var(--error);
    background: linear-gradient(135deg, #fef2f2 0%, #f8fafc 100%);
}

/* Task Status Icon */
.task-status {
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    flex-shrink: 0;
    font-size: 0.9rem;
}

.task-status svg {
    width: 14px;
    height: 14px;
    stroke: currentColor;
}

.task-card.running .task-status {
    background: var(--primary);
    color: white;
}

.task-card.completed .task-status {
    background: var(--success);
    color: white;
}

.task-card.failed .task-status {
    background: var(--error);
    color: white;
}

.task-card.pending .task-status {
    background: var(--border);
    color: var(--text-light);
}

/* Task Main Info */
.task-main {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
}

.task-title {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-weight: 600;
    color: var(--text);
}

.task-title .code {
    font-family: monospace;
    background: rgba(0,0,0,0.05);
    padding: 0.1rem 0.3rem;
    border-radius: 0.25rem;
}

.task-title .name {
    color: var(--text-light);
    font-weight: 400;
    font-size: 0.75rem;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.task-meta {
    display: flex;
    gap: 0.75rem;
    font-size: 0.7rem;
    color: var(--text-light);
}

.task-meta span {
    display: flex;
    align-items: center;
    gap: 0.2rem;
}

/* Task Result Badge */
.task-result {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 0.15rem;
    flex-shrink: 0;
}

.task-advice {
    font-weight: 900;
    font-size: 0.82rem;
    padding: 0.18rem 0.5rem;
    border-radius: 0.25rem;
    background: var(--primary);
    color: white;
}

.task-advice.buy { background: #059669; }     /* 买入 */
.task-advice.add { background: #047857; }     /* 加仓 */
.task-advice.hold { background: #475569; }    /* 持有 */
.task-advice.reduce { background: #d97706; }  /* 减仓 */
.task-advice.sell { background: #dc2626; }    /* 卖出 */
.task-advice.wait { background: #6b7280; }    /* 观望 */

.task-score {
    font-size: 0.7rem;
    color: var(--text-light);
}

/* Task Actions */
.task-actions {
    display: flex;
    gap: 0.25rem;
    flex-shrink: 0;
}

.task-btn {
    width: 24px;
    height: 24px;
    padding: 0;
    border-radius: 0.25rem;
    background: transparent;
    color: var(--text-light);
    font-size: 0.75rem;
    display: flex;
    align-items: center;
    justify-content: center;
}

.task-btn:hover {
    background: rgba(0,0,0,0.05);
    color: var(--text);
    transform: none;
}

/* Spinner in task */
.task-card .spinner {
    width: 12px;
    height: 12px;
    border-width: 1.5px;
    margin: 0;
}

/* Empty state hint */
.task-hint {
    text-align: center;
    padding: 0.75rem;
    color: var(--text-light);
    font-size: 0.75rem;
    background: var(--bg);
    border-radius: 0.375rem;
}

/* Task detail expand */
.task-detail {
    display: none;
    padding: 0.5rem 0.75rem;
    padding-left: 3rem;
    background: rgba(0,0,0,0.02);
    border-radius: 0 0 0.5rem 0.5rem;
    margin-top: -0.5rem;
    font-size: 0.75rem;
    border: 1px solid var(--border);
    border-top: none;
}

.task-detail.show {
    display: block;
}

.task-detail-row {
    display: flex;
    justify-content: space-between;
    padding: 0.25rem 0;
}

.task-detail-row .label {
    color: var(--text-light);
}

.task-detail-summary {
    margin-top: 0.5rem;
    padding: 0.5rem;
    background: white;
    border-radius: 0.25rem;
    line-height: 1.4;
}

.task-detail-report-title {
    margin-top: 0.75rem;
    color: var(--text-light);
    font-weight: 600;
}

.task-report {
    margin-top: 0.35rem;
    padding: 0.6rem 0.75rem;
    background: rgba(248, 250, 252, 0.9);
    color: rgba(15, 23, 42, 0.92);
    border-radius: 0.25rem;
    border: 1px solid rgba(226, 232, 240, 0.9);
    overflow: auto;
    max-height: 60vh;
    white-space: pre-wrap;
    word-break: break-word;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
    line-height: 1.45;
}

.results-split {
    display: grid;
    /* 任务列表更宽，避免信息挤在一起 */
    grid-template-columns: var(--task-col-w, 300px) 10px 1fr;
    gap: 12px;
    min-height: 0;
    align-items: stretch;
    flex: 1;
}

.splitter {
    width: 10px;
    cursor: col-resize;
    border-radius: 999px;
    background: rgba(226, 232, 240, 0.35);
    border: 1px solid rgba(226, 232, 240, 0.65);
    align-self: stretch;
}

.splitter:hover {
    background: rgba(37, 99, 235, 0.12);
    border-color: rgba(37, 99, 235, 0.25);
}

.splitter:active {
    background: rgba(37, 99, 235, 0.18);
    border-color: rgba(37, 99, 235, 0.35);
}

.detail-pane {
    border: 1px solid rgba(226, 232, 240, 0.9);
    border-radius: 12px;
    background: rgba(248, 250, 252, 0.65);
    padding: 0;
    overflow: auto;
    min-height: 0;
}

.detail-body {
    padding: 12px;
}

.hero-card {
    border: 1px solid rgba(226, 232, 240, 0.9);
    border-radius: 14px;
    background: rgba(255, 255, 255, 0.92);
    box-shadow: 0 10px 25px rgba(15, 23, 42, 0.08);
    padding: 14px;
    margin-bottom: 12px;
}

.hero-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    margin-bottom: 10px;
}

.hero-title {
    font-weight: 900;
    font-size: 13px;
    color: rgba(15, 23, 42, 0.92);
}

.hero-grid {
    display: grid;
    grid-template-columns: 1.15fr 1fr;
    gap: 12px;
    min-width: 0;
}

.hero-primary {
    min-width: 0;
}

.hero-big {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 8px;
}

.hero-big .hero-strong {
    font-size: 18px;
    font-weight: 1000;
    letter-spacing: 0.2px;
    color: rgba(15, 23, 42, 0.95);
}

.hero-sub {
    font-size: 12px;
    color: rgba(100, 116, 139, 0.95);
    line-height: 1.45;
}

.hero-points {
    display: grid;
    grid-template-columns: 1fr;
    gap: 8px;
}

.hero-points-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
}

.hero-point {
    border: 1px solid rgba(226, 232, 240, 0.9);
    border-radius: 12px;
    background: rgba(248, 250, 252, 0.9);
    padding: 10px;
    min-width: 0;
}

.hero-point .k {
    font-size: 11px;
    font-weight: 900;
    color: rgba(71, 85, 105, 0.95);
    margin-bottom: 6px;
}

.hero-point .v {
    font-size: 12px;
    color: rgba(15, 23, 42, 0.92);
    line-height: 1.45;
    word-break: break-word;
}

.hero-point .v strong {
    font-weight: 1000;
    color: rgba(15, 23, 42, 0.95);
}

@media (max-width: 980px) {
    .hero-grid { grid-template-columns: 1fr; }
    .hero-points-grid { grid-template-columns: 1fr; }
}

.detail-sticky {
    position: sticky;
    top: 0;
    z-index: 10;
    margin: 0;
    padding: 12px;
    background: rgba(248, 250, 252, 0.86);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid rgba(226, 232, 240, 0.85);
    border-top-left-radius: 12px;
    border-top-right-radius: 12px;
}

.detail-actions {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
}

.btn-inline {
    width: auto;
    padding: 8px 10px;
    font-size: 12px;
    border-radius: 10px;
    background: rgba(255, 255, 255, 0.9);
    color: rgba(15, 23, 42, 0.9);
    border: 1px solid rgba(226, 232, 240, 0.9);
    box-shadow: none;
}

.btn-inline.btn-market {
    background: linear-gradient(180deg, rgba(245, 158, 11, 0.98), rgba(245, 158, 11, 0.84));
    color: rgba(255, 255, 255, 0.98);
    border: 1px solid rgba(245, 158, 11, 0.55);
    box-shadow: 0 10px 22px rgba(245, 158, 11, 0.22);
}

.btn-inline:hover {
    background: rgba(255, 255, 255, 1);
    border-color: rgba(148, 163, 184, 0.65);
}

.btn-inline.btn-market:hover {
    background: linear-gradient(180deg, rgba(217, 119, 6, 0.98), rgba(217, 119, 6, 0.84));
    border-color: rgba(217, 119, 6, 0.65);
}

.btn-inline.btn-market:disabled {
    opacity: 0.7;
    cursor: not-allowed;
    box-shadow: none;
}

.btn-inline:focus-visible {
    outline: none;
    box-shadow: var(--ring);
}

.toc-select {
    width: auto;
    padding: 8px 10px;
    font-size: 12px;
    border-radius: 10px;
    background: rgba(255, 255, 255, 0.9);
    color: rgba(15, 23, 42, 0.9);
    border: 1px solid rgba(226, 232, 240, 0.9);
}

.toc-select:focus-visible {
    outline: none;
    box-shadow: var(--ring);
}

.toc-pop {
    position: relative;
}

.toc-pop > summary {
    list-style: none;
}
.toc-pop > summary::-webkit-details-marker { display: none; }

.toc-panel {
    position: absolute;
    right: 0;
    top: calc(100% + 8px);
    width: min(320px, 70vw);
    max-height: 300px;
    overflow: auto;
    padding: 10px;
    border-radius: 12px;
    border: 1px solid rgba(226, 232, 240, 0.9);
    background: rgba(255, 255, 255, 0.92);
    box-shadow: var(--shadow);
    z-index: 40;
}

.report-split {
    display: grid;
    grid-template-columns: 200px 1fr;
    gap: 12px;
    align-items: start;
}

.report-toc {
    position: sticky;
    top: 58px; /* below sticky header */
    align-self: start;
    max-height: 60vh;
    overflow: auto;
    padding: 10px;
    border-radius: 12px;
    border: 1px solid rgba(226, 232, 240, 0.9);
    background: rgba(255, 255, 255, 0.75);
}

.toc-title {
    font-weight: 800;
    font-size: 12px;
    color: rgba(15, 23, 42, 0.9);
    margin-bottom: 8px;
}

.toc-item {
    display: block;
    color: rgba(30, 41, 59, 0.9);
    text-decoration: none;
    font-size: 12px;
    line-height: 1.45;
    padding: 4px 6px;
    border-radius: 8px;
    border: 1px solid transparent;
}

.toc-item:hover {
    background: rgba(37, 99, 235, 0.06);
    border-color: rgba(37, 99, 235, 0.14);
}

.toc-item.active {
    background: rgba(37, 99, 235, 0.10);
    border-color: rgba(37, 99, 235, 0.22);
}

.toc-l2 { padding-left: 14px; }
.toc-l3 { padding-left: 24px; }

.report-body {
    min-width: 0;
}

.md-preview {
    padding: 12px;
    border-radius: 12px;
    border: 1px solid rgba(226, 232, 240, 0.9);
    background: rgba(255, 255, 255, 0.85);
    color: rgba(15, 23, 42, 0.92);
    line-height: 1.7;
    font-size: 14px;
}

.md-preview h1, .md-preview h2, .md-preview h3 {
    margin: 0.6em 0 0.35em;
    line-height: 1.25;
}
.md-preview h1 { font-size: 18px; }
.md-preview h2 { font-size: 16px; }
.md-preview h3 { font-size: 14px; }

.md-preview p { margin: 0.35em 0; }
.md-preview ul, .md-preview ol { margin: 0.35em 0 0.35em 1.2em; }
.md-preview li { margin: 0.15em 0; }

.md-preview blockquote {
    margin: 0.5em 0;
    padding: 0.5em 0.75em;
    border-left: 3px solid rgba(37, 99, 235, 0.45);
    background: rgba(37, 99, 235, 0.06);
    border-radius: 8px;
    color: rgba(30, 41, 59, 0.95);
}

.md-preview code {
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
    font-size: 12px;
    background: rgba(15, 23, 42, 0.06);
    border: 1px solid rgba(226, 232, 240, 0.9);
    padding: 1px 4px;
    border-radius: 6px;
}

.md-preview pre {
    margin: 0.6em 0;
    padding: 10px 12px;
    overflow: auto;
    border-radius: 10px;
    background: rgba(15, 23, 42, 0.04);
    border: 1px solid rgba(226, 232, 240, 0.9);
}
.md-preview pre code {
    background: transparent;
    border: none;
    padding: 0;
}

.md-preview table {
    width: 100%;
    border-collapse: collapse;
    margin: 0.6em 0;
    font-size: 12px;
}
.md-preview th, .md-preview td {
    border: 1px solid rgba(226, 232, 240, 0.9);
    padding: 6px 8px;
    text-align: left;
    vertical-align: top;
}
.md-preview th {
    background: rgba(248, 250, 252, 0.95);
    font-weight: 800;
}

.md-preview a {
    color: rgba(37, 99, 235, 0.95);
    text-decoration: none;
}
.md-preview a:hover { text-decoration: underline; }

.detail-empty {
    color: var(--text-light);
    font-size: 13px;
    line-height: 1.6;
    padding: 10px;
    white-space: pre-wrap;
}

.detail-header {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    margin-bottom: 10px;
}

.detail-title {
    display: flex;
    flex-direction: column;
    gap: 2px;
    min-width: 0;
}

.detail-title .code {
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
    font-weight: 800;
}

.detail-title .name {
    color: var(--text-light);
    font-size: 12px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 380px;
}

.badge-row {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
}

.badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 8px;
    border-radius: 999px;
    font-size: 12px;
    border: 1px solid rgba(226, 232, 240, 0.9);
    background: rgba(255, 255, 255, 0.8);
}

.badge.focus {
    font-size: 13px;
    font-weight: 900;
    padding: 6px 10px;
    letter-spacing: 0.2px;
}

.badge.positive { border-color: rgba(16, 185, 129, 0.35); }
.badge.warning { border-color: rgba(245, 158, 11, 0.35); }
.badge.negative { border-color: rgba(239, 68, 68, 0.35); }
.badge.neutral { border-color: rgba(100, 116, 139, 0.45); }

.kv {
    display: grid;
    grid-template-columns: 90px 1fr;
    gap: 6px 10px;
    font-size: 12px;
    color: var(--text);
    margin-bottom: 10px;
}

.kv .k { color: var(--text-light); }
.kv .v { word-break: break-word; }

.detail-section-title {
    margin: 10px 0 6px;
    font-weight: 800;
    font-size: 12px;
    color: var(--text);
}

.detail-summary {
    padding: 10px;
    border-radius: 10px;
    border: 1px solid rgba(226, 232, 240, 0.9);
    background: rgba(255, 255, 255, 0.85);
    font-size: 13px;
    line-height: 1.6;
}

.progress {
    width: 100%;
    height: 10px;
    border-radius: 999px;
    background: rgba(148, 163, 184, 0.25);
    overflow: hidden;
    border: 1px solid rgba(226, 232, 240, 0.9);
}

.progress-bar {
    height: 100%;
    width: 0%;
    background: linear-gradient(90deg, rgba(37, 99, 235, 0.9), rgba(16, 185, 129, 0.9));
    transition: width 0.3s ease;
}

.log-box {
    margin-top: 8px;
    padding: 10px;
    border-radius: 10px;
    border: 1px solid rgba(226, 232, 240, 0.9);
    background: rgba(255, 255, 255, 0.75);
    max-height: 220px;
    overflow: auto;
    white-space: pre-wrap;
    word-break: break-word;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
    font-size: 12px;
    line-height: 1.45;
    color: rgba(15, 23, 42, 0.9);
}

@media (max-width: 980px) {
    .app-grid { grid-template-columns: 1fr; overflow: auto; }
    .results-split { grid-template-columns: 1fr; min-height: auto; }
    .splitter { display: none; }
    .task-list { max-height: 300px; }
    .report-split { grid-template-columns: 1fr; }
    .report-toc { position: relative; top: 0; max-height: 220px; }
}
"""


# ============================================================
# 页面模板
# ============================================================

def render_base(
    title: str,
    content: str,
    extra_css: str = "",
    extra_js: str = ""
) -> str:
    """
    渲染基础 HTML 模板
    
    Args:
        title: 页面标题
        content: 页面内容 HTML
        extra_css: 额外的 CSS 样式
        extra_js: 额外的 JavaScript
    """
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html.escape(title)}</title>
  <style>{BASE_CSS}{extra_css}</style>
</head>
<body>
  {content}
  {extra_js}
</body>
</html>"""


def render_toast(message: str, toast_type: str = "success") -> str:
    """
    渲染 Toast 通知
    
    Args:
        message: 通知消息
        toast_type: 类型 (success, error, warning)
    """
    type_class = f" {toast_type}" if toast_type != "success" else ""
    
    return f"""
    <div id="toast" class="toast show{type_class}">
        <span class="toast-dot"></span>
        <span>{html.escape(message)}</span>
    </div>
    <script>
        setTimeout(() => {{
            document.getElementById('toast').classList.remove('show');
        }}, 3000);
    </script>
    """


def render_config_page(
    stock_list: str,
    env_filename: str,
    message: Optional[str] = None,
    common_config: Optional[dict] = None,
) -> bytes:
    """
    渲染配置页面
    
    Args:
        stock_list: 当前自选股列表
        env_filename: 环境文件名
        message: 可选的提示消息
    """
    safe_value = html.escape(stock_list)
    toast_html = render_toast(message) if message else ""
    common_config = common_config or {}

    def _get(key: str, default: str) -> str:
        v = common_config.get(key)
        return str(v) if v is not None else default

    def _is_true(key: str, default: str = "false") -> bool:
        v = _get(key, default).strip().lower()
        return v == "true" or v == "1" or v == "yes" or v == "on"

    schedule_time = html.escape(_get("SCHEDULE_TIME", "18:00"))

    schedule_enabled_checked = "checked" if _is_true("SCHEDULE_ENABLED") else ""
    market_review_checked = "checked" if _is_true("MARKET_REVIEW_ENABLED", "true") else ""

    # 首页“常用配置”先只保留：定时任务相关
    
    # 分析组件的 JavaScript - 支持多任务
    analysis_js = """
<script>
	(function() {
		    const codeInput = document.getElementById('analysis_codes');
	    const submitBtn = document.getElementById('analysis_btn');
	    const marketReviewBtn = document.getElementById('market_review_btn');
	    const taskList = document.getElementById('task_list');
	    const taskSplitter = document.getElementById('task_splitter');
	    const detailPane = document.getElementById('task_detail_view');
	    const reportTypeSelect = document.getElementById('report_type');
	    const codeHint = document.getElementById('analysis_codes_hint');

	    function syncLayoutVars() {
	        try {
	            const header = document.querySelector('.app-header');
	            if (header) {
	                const h = Math.ceil(header.getBoundingClientRect().height);
	                document.documentElement.style.setProperty('--app-header-h', String(h) + 'px');
	            }
	        } catch (e) {}
	    }

	    function setupTaskSplitter() {
	        if (!taskSplitter) return;
	        const container = taskSplitter.parentElement;
	        if (!container) return;

	        // 恢复上次宽度
	        try {
	            const saved = localStorage.getItem('task_col_w');
	            if (saved && /^[0-9]+$/.test(saved)) {
	                container.style.setProperty('--task-col-w', String(saved) + 'px');
	            }
	        } catch (e) {}

	        let dragging = false;
	        let startX = 0;
	        let startW = 0;

	        function clamp(v, min, max) { return Math.max(min, Math.min(max, v)); }

	        function onMove(ev) {
	            if (!dragging) return;
	            const x = ev.clientX;
	            const dx = x - startX;
	            const w = clamp(startW + dx, 220, 560);
	            container.style.setProperty('--task-col-w', String(w) + 'px');
	            try { localStorage.setItem('task_col_w', String(Math.round(w))); } catch (e) {}
	        }

	        function onUp() {
	            if (!dragging) return;
	            dragging = false;
	            document.body.style.cursor = '';
	            document.body.style.userSelect = '';
	            window.removeEventListener('mousemove', onMove);
	            window.removeEventListener('mouseup', onUp);
	        }

	        taskSplitter.addEventListener('mousedown', function(ev) {
	            ev.preventDefault();
	            dragging = true;
	            startX = ev.clientX;
	            // 第一列当前宽度
	            const col = container.querySelector('.task-list');
	            startW = col ? col.getBoundingClientRect().width : 300;
	            document.body.style.cursor = 'col-resize';
	            document.body.style.userSelect = 'none';
	            window.addEventListener('mousemove', onMove);
	            window.addEventListener('mouseup', onUp);
	        });
	    }
    
    // 任务管理
    const tasks = new Map(); // taskId -> {task, pollCount}
    let pollInterval = null;
		    const MAX_POLL_COUNT = 120; // 6 分钟超时：120 * 3000ms = 360000ms
		    const POLL_INTERVAL_MS = 3000;
		    const MAX_TASKS_DISPLAY = 10;
		    let selectedTaskId = null;
		    let lastTocTaskId = null;

    // 简单转义，避免把 AI 输出/用户输入直接注入 HTML
	    function escapeHtml(str) {
	        if (str === null || str === undefined) return '';
	        return String(str)
	            .replace(/&/g, '&amp;')
	            .replace(/</g, '&lt;')
	            .replace(/>/g, '&gt;')
	            .replace(/\"/g, '&quot;')
	            .replace(/'/g, '&#39;');
	    }

	    // 报告类型由下拉框选择（reportTypeSelect）

	    function ensureTaskUi(taskId) {
	        if (!taskId || !tasks.has(taskId)) return { showLogs: false };
	        const td = tasks.get(taskId);
	        if (!td.ui) td.ui = { showLogs: false, tocMode: 'off' };
	        if (td.ui.showLogs === undefined) td.ui.showLogs = false;
	        if (td.ui.tocMode === undefined) td.ui.tocMode = 'off';
	        return td.ui;
	    }

	    async function copyText(text) {
	        const value = String(text || '');
	        try {
	            if (navigator.clipboard && navigator.clipboard.writeText) {
	                await navigator.clipboard.writeText(value);
	                return true;
	            }
	        } catch (e) {}

	        try {
	            const ta = document.createElement('textarea');
	            ta.value = value;
	            ta.style.position = 'fixed';
	            ta.style.left = '-9999px';
	            document.body.appendChild(ta);
	            ta.select();
	            const ok = document.execCommand('copy');
	            document.body.removeChild(ta);
	            return ok;
	        } catch (e) {
	            return false;
	        }
	    }

	    function downloadText(filename, text) {
	        const blob = new Blob([String(text || '')], { type: 'text/plain;charset=utf-8' });
	        const url = URL.createObjectURL(blob);
	        const a = document.createElement('a');
	        a.href = url;
	        a.download = filename || 'report.md';
	        document.body.appendChild(a);
	        a.click();
	        document.body.removeChild(a);
	        setTimeout(() => URL.revokeObjectURL(url), 2000);
	    }

	    window.toggleLogs = function(taskId) {
	        const ui = ensureTaskUi(taskId);
	        ui.showLogs = !ui.showLogs;
	        renderDetail();
	    };

	    window.setTocMode = function(taskId, mode) {
	        const ui = ensureTaskUi(taskId);
	        const v = String(mode || 'off');
	        ui.tocMode = (v === 'top' || v === 'left') ? v : 'off';
	        renderDetail();
	    };

	    window.copySummary = async function(taskId) {
	        const td = tasks.get(taskId);
	        const summary = td && td.task && td.task.result ? (td.task.result.analysis_summary || '') : '';
	        const ok = await copyText(summary);
	        if (!ok) alert('复制失败');
	    };

	    window.copyMarkdown = async function(taskId) {
	        const td = tasks.get(taskId);
	        const md = td && td.task && td.task.result ? (td.task.result.report_markdown || '') : '';
	        const ok = await copyText(md);
	        if (!ok) alert('复制失败');
	    };

	    window.downloadMarkdown = function(taskId) {
	        const td = tasks.get(taskId);
	        if (!td || !td.task) return;
	        const code = (td.task.code || taskId.split('_')[0] || 'report').toString();
	        const md = td.task.result ? (td.task.result.report_markdown || '') : '';
	        const date = new Date().toISOString().slice(0, 10);
	        downloadText(code + '_' + date + '.md', md);
	    };

	    // 报告类型：无需额外绑定，直接读 reportTypeSelect.value
    
	    // 批量输入：允许逗号/空格/换行分隔；只转小写
		    codeInput.addEventListener('input', function(e) {
		        this.value = this.value.toLowerCase();
		        updateButtonState();
		    });
    
	    // Textarea 内回车用于换行；Ctrl/Cmd + Enter 提交
	    codeInput.addEventListener('keydown', function(e) {
	        if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
	            e.preventDefault();
	            if (!submitBtn.disabled) {
	                submitAnalysis();
	            }
	        }
	    });

	    function parseCodes(raw) {
	        const parts = String(raw || '')
	            .toLowerCase()
	            .split(/[\\s,，、;；|]+/g)
	            .map(s => s.trim())
	            .filter(Boolean);

	        // 去重（保留顺序）
	        const seen = new Set();
	        const codes = [];
	        for (const p of parts) {
	            if (!seen.has(p)) {
	                seen.add(p);
	                codes.push(p);
	            }
	        }
	        return codes;
	    }

	    function isValidCode(code) {
	        // A股: 600519（注意：01xxxx 常见为场外基金代码，这里先按“暂不支持”处理）
	        const isAStock = /^\\d{6}$/.test(code) && !/^01\\d{4}$/.test(code);
	        const isHKStock = /^hk\\d{5}$/.test(code);              // 港股: hk00700
	        const isUSStock = /^[a-z]{1,5}(\\.[a-z])?$/.test(code); // 美股: aapl / brk.b
	        return isAStock || isHKStock || isUSStock;
	    }
    
	    // 更新按钮状态：
	    // - 至少存在 1 个合法代码
	    // - 且不包含非法代码（避免误分析）
	    function updateButtonState() {
	        const codes = parseCodes(codeInput.value);
	        const valid = codes.filter(isValidCode);
	        const invalid = codes.filter(c => !isValidCode(c));

	        if (codeHint) {
	            if (codes.length === 0) {
	                codeHint.classList.remove('text-error');
	                codeHint.textContent = '支持批量输入；按 Ctrl/Cmd + Enter 可快速提交。格式：A股 6 位数字（600519）；港股 hk+5 位（hk00700）；美股 1-5 字母，可选 .x（aapl / brk.b）。';
	            } else if (invalid.length > 0) {
	                codeHint.classList.add('text-error');
	                codeHint.textContent = '检测到无效代码：' + invalid.slice(0, 8).join(', ') + (invalid.length > 8 ? ' ...' : '') + '。请修正后再提交。';
	            } else {
	                codeHint.classList.remove('text-error');
	                codeHint.textContent = '已识别 ' + valid.length + ' 只股票：' + valid.slice(0, 8).join(', ') + (valid.length > 8 ? ' ...' : '') + '。';
	            }
	        }

	        if (invalid.length > 0) codeInput.classList.add('input-error');
	        else codeInput.classList.remove('input-error');

	        submitBtn.disabled = (valid.length === 0) || (invalid.length > 0);
	    }
    
    // 格式化时间
    function formatTime(isoString) {
        if (!isoString) return '-';
        const date = new Date(isoString);
        return date.toLocaleTimeString('zh-CN', {hour: '2-digit', minute: '2-digit', second: '2-digit'});
    }
    
    // 计算耗时
    function calcDuration(start, end) {
        if (!start) return '-';
        const startTime = new Date(start).getTime();
        const endTime = end ? new Date(end).getTime() : Date.now();
        const seconds = Math.floor((endTime - startTime) / 1000);
        if (seconds < 60) return seconds + 's';
        const minutes = Math.floor(seconds / 60);
        const remainSec = seconds % 60;
        return minutes + 'm' + remainSec + 's';
    }

    function getStageLabel(stage) {
        const map = {
            'init': '初始化',
            'fetch_data': '获取数据',
            'analyze': 'AI 分析',
            'render_report': '生成报告',
            'notify': '推送通知',
            'done': '完成',
            'failed': '失败'
        };
        return map[stage] || (stage || '处理中');
    }

	    function renderLogs(logs) {
	        if (!Array.isArray(logs) || logs.length === 0) {
	            return '<div class="log-box">暂无日志</div>';
	        }
        const maxLines = 120;
        const lines = logs.slice(-maxLines).map((e) => {
            const ts = e && e.ts ? formatTime(e.ts) : '-';
            const level = e && e.level ? String(e.level) : 'INFO';
            const msg = e && e.msg ? String(e.msg) : '';
            return '[' + ts + '] ' + level + ' ' + msg;
        });
	        return '<div class="log-box">' + escapeHtml(lines.join('\\n')) + '</div>';
	    }

	    function iconCheck() {
	        return '<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6L9 17l-5-5"></path></svg>';
	    }
	    function iconX() {
	        return '<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6L6 18"></path><path d="M6 6l12 12"></path></svg>';
	    }
	    function iconDot() {
	        return '<svg viewBox="0 0 24 24" fill="none" stroke-width="2"><circle cx="12" cy="12" r="3"></circle></svg>';
	    }
    
    // 获取建议样式类
	    function getAdviceClass(advice) {
	        if (!advice) return '';
	        // 匹配顺序很重要：先匹配更具体的词
	        if (advice.includes('加仓')) return 'add';
	        if (advice.includes('减仓')) return 'reduce';
	        if (advice.includes('买')) return 'buy';
	        if (advice.includes('卖')) return 'sell';
	        if (advice.includes('持有')) return 'hold';
	        return 'wait';
	    }

	    function getBadgeTone(advice) {
	        if (!advice) return 'warning';
	        if (advice.includes('买') || advice.includes('加仓')) return 'positive';
	        if (advice.includes('卖')) return 'negative';
	        if (advice.includes('减仓')) return 'warning';
	        if (advice.includes('持有')) return 'neutral';
	        if (advice.includes('观望') || advice.includes('等待')) return 'warning';
	        return 'warning';
	    }

	    function getTrendTone(trend, advice) {
	        const t = String(trend || '');
	        const a = String(advice || '');

	        // 基于“趋势预测”本身的颜色
	        let tone = 'neutral';
	        if (t.includes('强烈看多')) tone = 'positive';
	        else if (t.includes('看多')) tone = 'positive';
	        else if (t.includes('震荡')) tone = 'neutral';
	        else if (t.includes('强烈看空')) tone = 'negative';
	        else if (t.includes('看空')) tone = 'warning';

	        // 与操作建议做一致性校验：明显冲突时用 warning 提示
	        const bullish = t.includes('看多');
	        const bearish = t.includes('看空');
	        const buyish = a.includes('买') || a.includes('加仓');
	        const sellish = a.includes('卖') || a.includes('减仓');
	        if ((bullish && sellish) || (bearish && buyish)) {
	            tone = 'warning';
	        }
	        return tone;
	    }

	    function renderHeroCard(result, tone, trendTone) {
	        const dash = (result && result.dashboard) ? result.dashboard : null;
	        const sniper = dash && dash.battle_plan && dash.battle_plan.sniper_points ? dash.battle_plan.sniper_points : null;
	        const pricePos = dash && dash.data_perspective && dash.data_perspective.price_position ? dash.data_perspective.price_position : null;

	        const adviceText = escapeHtml(result.operation_advice || '-');
	        const trendText = escapeHtml(result.trend_prediction || '-');
	        const scoreText = escapeHtml(result.sentiment_score ?? '-');
	        const confText = escapeHtml(result.confidence_level || '-');
	        const reasonText = escapeHtml(result.buy_reason || '');

	        function valOrDash(v) {
	            if (v === undefined || v === null) return '-';
	            const s = String(v).trim();
	            return s ? escapeHtml(s) : '-';
	        }

	        const items = [];
	        if (sniper) {
	            items.push({ k: '理想买入', v: valOrDash(sniper.ideal_buy) });
	            items.push({ k: '次优买入', v: valOrDash(sniper.secondary_buy) });
	            items.push({ k: '止损', v: valOrDash(sniper.stop_loss) });
	            items.push({ k: '目标位', v: valOrDash(sniper.take_profit) });
	        }
	        // fallback：没有结构化点位时，先不硬解析，保持简洁

	        const extra = [];
	        if (pricePos && (pricePos.support_level !== undefined || pricePos.resistance_level !== undefined || pricePos.bias_ma5 !== undefined)) {
	            if (pricePos.support_level !== undefined) extra.push('<span class="badge neutral">支撑 ' + valOrDash(pricePos.support_level) + '</span>');
	            if (pricePos.resistance_level !== undefined) extra.push('<span class="badge neutral">压力 ' + valOrDash(pricePos.resistance_level) + '</span>');
	            if (pricePos.bias_ma5 !== undefined) extra.push('<span class="badge neutral">乖离 ' + valOrDash(pricePos.bias_ma5) + '%</span>');
	        }

	        const pointsHtml = items.length > 0
	            ? (
	                '<div class="hero-points-grid">' +
	                    items.map((it) => (
	                        '<div class="hero-point">' +
	                            '<div class="k">' + it.k + '</div>' +
	                            '<div class="v"><strong>' + it.v + '</strong></div>' +
	                        '</div>'
	                    )).join('') +
	                '</div>'
	            )
	            : '<div class="detail-empty" style="padding: 0;">暂无结构化关键价位（可在报告中查看）。</div>';

	        return (
	            '<div class="hero-card">' +
	                '<div class="hero-head">' +
	                    '<div class="hero-title">关键结论</div>' +
	                    '<div class="badge-row">' +
	                        '<span class="badge focus ' + tone + '">' + adviceText + '</span>' +
	                        '<span class="badge focus ' + trendTone + '">' + trendText + '</span>' +
	                    '</div>' +
	                '</div>' +
	                '<div class="hero-grid">' +
	                    '<div class="hero-primary">' +
	                        '<div class="hero-big">' +
	                            '<div class="hero-strong">' + adviceText + '</div>' +
	                            '<span class="badge ' + trendTone + '">趋势 ' + trendText + '</span>' +
	                            '<span class="badge">评分 ' + scoreText + '</span>' +
	                            '<span class="badge neutral">置信度 ' + confText + '</span>' +
	                        '</div>' +
	                        (extra.length ? ('<div class="badge-row" style="margin-bottom:8px;">' + extra.join('') + '</div>') : '') +
	                        (reasonText ? ('<div class="hero-sub"><strong>理由：</strong>' + reasonText + '</div>') : '<div class="hero-sub">从“狙击点位/风控/趋势”三个角度快速把握重点。</div>') +
	                    '</div>' +
	                    '<div class="hero-points">' +
	                        pointsHtml +
	                    '</div>' +
	                '</div>' +
	            '</div>'
	        );
	    }
    
	    // 渲染单个任务卡片
		    function renderTaskCard(taskId, taskData) {
	        const task = taskData.task || {};
	        const status = task.status || 'pending';
	        const code = task.code || taskId.split('_')[0];
	        const result = task.result || {};

	        const codeSafe = escapeHtml(code);
	        const nameSafe = escapeHtml(result.name || code);
	        
		        let statusIcon = iconDot();
		        let statusText = '等待中';
		        if (status === 'running') { statusIcon = '<span class="spinner"></span>'; statusText = '分析中'; }
		        else if (status === 'completed') { statusIcon = iconCheck(); statusText = '完成'; }
		        else if (status === 'failed') { statusIcon = iconX(); statusText = '失败'; }
	        
	        let resultHtml = '';
	        if (status === 'completed' && result.operation_advice) {
	            const adviceClass = getAdviceClass(result.operation_advice);
	            resultHtml = '<div class="task-result">' +
	                '<span class="task-advice ' + adviceClass + '">' + escapeHtml(result.operation_advice) + '</span>' +
	                '<span class="task-score">' + escapeHtml((result.sentiment_score ?? '-')) + '分</span>' +
	                '</div>';
	        } else if (status === 'failed') {
	            resultHtml = '<div class="task-result"><span class="task-advice sell">失败</span></div>';
	        }

	        const selectedClass = (taskId === selectedTaskId) ? ' selected' : '';
	        return '<div class="task-card ' + status + selectedClass + '" id="task_' + taskId + '" onclick="selectTask(\\''+taskId+'\\')">' +
	            '<div class="task-status">' + statusIcon + '</div>' +
	            '<div class="task-main">' +
	                '<div class="task-title">' +
	                    '<span class="code">' + codeSafe + '</span>' +
	                    '<span class="name">' + nameSafe + '</span>' +
	                '</div>' +
		                '<div class="task-meta">' +
		                    '<span>开始 ' + formatTime(task.start_time) + '</span>' +
		                    '<span>耗时 ' + calcDuration(task.start_time, task.end_time) + '</span>' +
		                    '<span>' + (task.report_type === 'full' ? '完整' : '精简') + '</span>' +
		                '</div>' +
		            '</div>' +
	            resultHtml +
	            '<div class="task-actions">' +
	                '<button class="task-btn" onclick="event.stopPropagation();removeTask(\\''+taskId+'\\')">×</button>' +
	            '</div>' +
	        '</div>';
		    }

		    function buildReportToc() {
		        if (!detailPane || !selectedTaskId) return;
		        const toc = detailPane.querySelector('#toc_list');
		        const report = detailPane.querySelector('#report_content');
		        if (!toc || !report) {
		            lastTocTaskId = null;
		            return;
		        }

		        // 仅在“当前任务”或内容变化时重建
		        const tocCtx = toc && toc.parentElement ? (toc.parentElement.className || '') : '';
		        const marker = selectedTaskId + ':' + String(report.innerHTML.length) + ':' + tocCtx;
		        if (lastTocTaskId === marker) return;
		        lastTocTaskId = marker;

		        const headings = Array.from(report.querySelectorAll('h1, h2, h3'));
		        if (headings.length === 0) {
		            toc.innerHTML = '<div class="card-hint">暂无目录</div>';
		            return;
		        }

		        function safeId(i) { return 'sec_' + selectedTaskId.replace(/[^a-zA-Z0-9_]/g, '_') + '_' + i; }

		        const items = [];
		        headings.forEach((h, idx) => {
		            const text = (h.textContent || '').trim();
		            if (!text) return;
		            if (!h.id) h.id = safeId(idx);
		            const level = Number(String(h.tagName).replace('H', '')) || 1;
		            const cls = level === 1 ? 'toc-item' : (level === 2 ? 'toc-item toc-l2' : 'toc-item toc-l3');
		            items.push('<a class="' + cls + '" href="#' + h.id + '" data-target="' + h.id + '">' + escapeHtml(text) + '</a>');
		        });
		        toc.innerHTML = items.join('');

		        toc.onclick = function(e) {
		            const a = e.target && e.target.closest ? e.target.closest('a[data-target]') : null;
		            if (!a) return;
		            e.preventDefault();
		            const id = a.getAttribute('data-target');
		            const el = report.querySelector('#' + CSS.escape(id));
		            if (el) {
		                el.scrollIntoView({ behavior: 'smooth', block: 'start' });
		                // 轻微上移，避免被 sticky header 压住
		                setTimeout(() => { detailPane.scrollTop = Math.max(0, detailPane.scrollTop - 70); }, 50);
		            }
		            toc.querySelectorAll('.toc-item.active').forEach(n => n.classList.remove('active'));
		            a.classList.add('active');
		        };
		    }

		    function setDetail(html) {
		        detailPane.innerHTML = html;
		        buildReportToc();
		    }

		    function renderDetail() {
		        if (!detailPane) return;
		        if (!selectedTaskId || !tasks.has(selectedTaskId)) {
		            setDetail('<div class="detail-body"><div class="detail-empty">在左侧输入股票代码后点击“开始分析”。\\n\\n右侧会显示任务列表，点击任意任务即可在这里查看完整结果。</div></div>');
		            return;
		        }

	        const taskData = tasks.get(selectedTaskId) || {};
	        const task = taskData.task || {};
	        const status = task.status || 'pending';
	        const code = escapeHtml(task.code || selectedTaskId.split('_')[0]);
	        const result = task.result || {};
	        const name = escapeHtml(result.name || '-');
	        const stage = task.stage || (status === 'completed' ? 'done' : (status === 'failed' ? 'failed' : ''));
	        const progress = (task.progress !== undefined && task.progress !== null) ? Number(task.progress) : (status === 'completed' ? 100 : 0);
	        const logsHtml = renderLogs(task.logs || []);

		        const stageText = escapeHtml(getStageLabel(stage));
		        const progressText = isNaN(progress) ? '-' : String(Math.max(0, Math.min(100, progress)));
		        const progressHtml = '<div class="progress"><div class="progress-bar" style="width:' + progressText + '%"></div></div>';
		        const ui = ensureTaskUi(selectedTaskId);
		        const showLogs = ui.showLogs === true;
		        const logsToggleText = showLogs ? '隐藏日志' : '显示日志';
		        const logsSection = showLogs ? ('<div class="detail-section-title">实时日志</div>' + logsHtml) : '';

		        // 大盘复盘：单独渲染（不展示“操作建议/趋势预测”）
		        if (task.kind === 'market_review') {
		            const title = '大盘复盘';
		            const stageText2 = escapeHtml(getStageLabel(stage));
		            const header =
		                '<div class="detail-sticky">' +
		                    '<div class="detail-header">' +
		                        '<div class="detail-title"><div class="code">' + escapeHtml(title) + '</div><div class="name">市场概览与热点</div></div>' +
		                        '<div class="badge-row">' +
		                            (status === 'completed' ? '<span class="badge positive">完成</span>' : (status === 'failed' ? '<span class="badge negative">失败</span>' : '<span class="badge warning">运行中</span>')) +
		                            '<span class="badge">阶段 ' + stageText2 + '</span>' +
		                            '<span class="badge">进度 ' + progressText + '%</span>' +
		                        '</div>' +
		                    '</div>' +
		                    '<div class="detail-actions">' +
		                        '<button class="btn-inline" type="button" onclick="toggleLogs(\\'' + selectedTaskId + '\\')">' + logsToggleText + '</button>' +
		                        '<button class="btn-inline" type="button" onclick="copyMarkdown(\\'' + selectedTaskId + '\\')">复制MD</button>' +
		                        '<button class="btn-inline" type="button" onclick="downloadMarkdown(\\'' + selectedTaskId + '\\')">下载MD</button>' +
		                    '</div>' +
		                    progressHtml +
		                '</div>';

		            if (status === 'failed') {
		                const err = escapeHtml(task.error || '未知错误');
		                setDetail(header + '<div class="detail-body"><div class="detail-section-title">错误信息</div><div class="detail-summary">' + err + '</div>' + logsSection + '</div>');
		                return;
		            }

		            const report = escapeHtml(result.report_markdown || '');
		            const reportHtml = String(result.report_html || '');
		            const body =
		                '<div class="detail-body">' +
		                    (reportHtml
		                        ? '<div class="detail-section-title">报告（Markdown 预览）</div><div id="report_content" class="md-preview">' + reportHtml + '</div>'
		                        : (report ? '<div class="detail-section-title">报告（原始 Markdown）</div><pre class="task-report">' + report + '</pre>' : '<div class="detail-empty">暂无可展示的报告内容。</div>')
		                    ) +
		                    logsSection +
		                '</div>';

		            setDetail(header + body);
		            return;
		        }

		        if (status === 'failed') {
		            const err = escapeHtml(task.error || '未知错误');
		            setDetail(
		                '<div class="detail-sticky">' +
		                    '<div class="detail-header">' +
		                        '<div class="detail-title"><div class="code">' + code + '</div><div class="name">' + name + '</div></div>' +
		                        '<div class="badge-row"><span class="badge negative">失败</span><span class="badge">阶段 ' + stageText + '</span></div>' +
		                    '</div>' +
		                    '<div class="detail-actions">' +
		                        '<button class="btn-inline" type="button" onclick="toggleLogs(\\'' + selectedTaskId + '\\')">' + logsToggleText + '</button>' +
		                    '</div>' +
		                    progressHtml +
		                '</div>' +
		                '<div class="detail-body">' +
		                    '<div class="detail-section-title">错误信息</div><div class="detail-summary">' + err + '</div>' +
		                    logsSection +
		                '</div>'
		            );
		            return;
		        }

		        if (status !== 'completed') {
	            const hasPartial = result && (result.operation_advice || result.analysis_summary || result.sentiment_score !== undefined);
	            const advicePartial = escapeHtml(result.operation_advice || '-');
	            const scorePartial = escapeHtml(result.sentiment_score ?? '-');
	            const tonePartial = getBadgeTone(result.operation_advice || '');
	            const summaryPartial = escapeHtml(result.analysis_summary || '');

		            setDetail(
		                '<div class="detail-sticky">' +
		                    '<div class="detail-header">' +
		                        '<div class="detail-title"><div class="code">' + code + '</div><div class="name">' + name + '</div></div>' +
		                        '<div class="badge-row">' +
		                            '<span class="badge warning">分析中</span>' +
		                            '<span class="badge">阶段 ' + stageText + '</span>' +
		                            '<span class="badge">进度 ' + progressText + '%</span>' +
		                        '</div>' +
		                    '</div>' +
		                    '<div class="detail-actions">' +
		                        '<button class="btn-inline" type="button" onclick="toggleLogs(\\'' + selectedTaskId + '\\')">' + logsToggleText + '</button>' +
		                    '</div>' +
		                    progressHtml +
		                '</div>' +
		                '<div class="detail-body">' +
		                    (hasPartial ? (
		                        '<div class="detail-section-title">阶段性结果</div>' +
		                        '<div class="badge-row" style="margin-bottom:8px;">' +
		                            '<span class="badge focus ' + tonePartial + '">' + advicePartial + '</span>' +
		                            '<span class="badge">评分 ' + scorePartial + '</span>' +
		                        '</div>' +
		                        (summaryPartial ? '<div class="detail-summary">' + summaryPartial + '</div>' : '')
		                    ) : '<div class="detail-empty">任务正在运行，请稍候…</div>') +
		                    logsSection +
		                '</div>'
		            );
		            return;
		        }

	        const advice = escapeHtml(result.operation_advice || '-');
	        const score = escapeHtml(result.sentiment_score ?? '-');
	        const trendRaw = String(result.trend_prediction || '');
	        const trend = escapeHtml(trendRaw || '-');
	        const summary = escapeHtml(result.analysis_summary || '');
        const report = escapeHtml(result.report_markdown || '');
        const reportHtml = String(result.report_html || '');
	        const tone = getBadgeTone(result.operation_advice);
	        const trendTone = getTrendTone(trendRaw, String(result.operation_advice || ''));

	        const notifyText = (task.send_notification === true) ? '将推送' : '仅页面展示';
	        const tocMode = ui.tocMode || 'off';
	        const tocSelect =
	            '<select class="toc-select" onchange="setTocMode(\\'' + selectedTaskId + '\\', this.value)" title="目录位置">' +
	                '<option value="off"' + (tocMode === 'off' ? ' selected' : '') + '>目录：关闭</option>' +
	                '<option value="top"' + (tocMode === 'top' ? ' selected' : '') + '>目录：右上</option>' +
	                '<option value="left"' + (tocMode === 'left' ? ' selected' : '') + '>目录：左侧</option>' +
	            '</select>';
		
	        const tocTop = (tocMode === 'top')
	            ? ('<details class="toc-pop">' +
	                    '<summary class="btn-inline">目录</summary>' +
	                    '<div class="toc-panel"><div id="toc_list"></div></div>' +
	                '</details>')
	            : '';

		        setDetail(
		            '<div class="detail-sticky">' +
		                '<div class="detail-header">' +
		                    '<div class="detail-title"><div class="code">' + code + '</div><div class="name">' + name + '</div></div>' +
		                    '<div class="badge-row">' +
		                        '<span class="badge focus ' + tone + '">' + advice + '</span>' +
		                        '<span class="badge">评分 ' + score + '</span>' +
		                        '<span class="badge focus ' + trendTone + '">趋势 ' + trend + '</span>' +
		                        '<span class="badge">' + escapeHtml(notifyText) + '</span>' +
		                        '<span class="badge">阶段 ' + stageText + '</span>' +
		                    '</div>' +
		                '</div>' +
		                '<div class="detail-actions">' +
		                    '<button class="btn-inline" type="button" onclick="toggleLogs(\\'' + selectedTaskId + '\\')">' + logsToggleText + '</button>' +
		                    '<button class="btn-inline" type="button" onclick="copySummary(\\'' + selectedTaskId + '\\')">复制摘要</button>' +
		                    '<button class="btn-inline" type="button" onclick="copyMarkdown(\\'' + selectedTaskId + '\\')">复制MD</button>' +
		                    '<button class="btn-inline" type="button" onclick="downloadMarkdown(\\'' + selectedTaskId + '\\')">下载MD</button>' +
		                    tocSelect +
		                    tocTop +
		                '</div>' +
		                progressHtml +
		            '</div>' +
		            '<div class="detail-body">' +
		                renderHeroCard(result, tone, trendTone) +
		                '<div class="kv">' +
		                    '<div class="k">状态</div><div class="v">完成</div>' +
		                    '<div class="k">趋势</div><div class="v">' + trend + '</div>' +
		                    '<div class="k">报告类型</div><div class="v">' + escapeHtml(task.report_type === 'full' ? '完整' : '精简') + '</div>' +
		                    '<div class="k">开始时间</div><div class="v">' + escapeHtml(formatTime(task.start_time)) + '</div>' +
		                    '<div class="k">耗时</div><div class="v">' + escapeHtml(calcDuration(task.start_time, task.end_time)) + '</div>' +
		                '</div>' +
		                (summary ? '<div class="detail-section-title">摘要</div><div class="detail-summary">' + summary + '</div>' : '') +
		                (reportHtml ? (
		                    '<div class="detail-section-title">报告（Markdown 预览）</div>' +
		                    (tocMode === 'left'
		                        ? ('<div class="report-split">' +
		                            '<div class="report-toc"><div class="toc-title">目录</div><div id="toc_list"></div></div>' +
		                            '<div class="report-body"><div id="report_content" class="md-preview">' + reportHtml + '</div></div>' +
		                          '</div>')
		                        : ('<div id="report_content" class="md-preview">' + reportHtml + '</div>')
		                    )
		                ) : (
		                    report ? '<div class="detail-section-title">报告（原始 Markdown）</div><pre class="task-report">' + report + '</pre>' : '<div class="detail-empty">暂无可展示的报告内容。</div>'
		                )) +
		                logsSection +
		            '</div>'
		        );
		    }
    
	    // 渲染所有任务
	    function renderAllTasks() {
	        if (tasks.size === 0) {
	            taskList.innerHTML = '<div class="task-hint">暂无任务：在左侧输入股票代码开始分析</div>';
	            renderDetail();
	            return;
	        }
        
        let html = '';
        const sortedTasks = Array.from(tasks.entries())
            .sort((a, b) => (b[1].task?.start_time || '').localeCompare(a[1].task?.start_time || ''));
        
        sortedTasks.slice(0, MAX_TASKS_DISPLAY).forEach(([taskId, taskData]) => {
            html += renderTaskCard(taskId, taskData);
        });
        
        if (sortedTasks.length > MAX_TASKS_DISPLAY) {
            html += '<div class="task-hint">... 还有 ' + (sortedTasks.length - MAX_TASKS_DISPLAY) + ' 个任务</div>';
        }
        
	        taskList.innerHTML = html;
	        renderDetail();
	    }

	    // 选择任务（在右侧详情展示）
	    window.selectTask = function(taskId) {
	        selectedTaskId = taskId;
	        renderAllTasks();
	    };
    
	    // 移除任务
	    window.removeTask = function(taskId) {
	        tasks.delete(taskId);
	        if (selectedTaskId === taskId) {
	            selectedTaskId = null;
	        }
	        renderAllTasks();
	        checkStopPolling();
	    };
    
    // 轮询所有运行中的任务
    function pollAllTasks() {
        let hasRunning = false;
        
        tasks.forEach((taskData, taskId) => {
            const status = taskData.task?.status;
            if (status === 'running' || status === 'pending' || !status) {
                hasRunning = true;
                taskData.pollCount = (taskData.pollCount || 0) + 1;
                
                if (taskData.pollCount > MAX_POLL_COUNT) {
                    taskData.task = taskData.task || {};
                    taskData.task.status = 'failed';
                    taskData.task.error = '轮询超时';
                    return;
                }
                
                fetch('/task?id=' + encodeURIComponent(taskId))
                    .then(r => r.json())
                    .then(data => {
                        if (data.success && data.task) {
                            taskData.task = data.task;
                            renderAllTasks();
                        }
                    })
                    .catch(() => {});
            }
        });
        
        if (!hasRunning) {
            checkStopPolling();
        }
    }
    
    // 检查是否需要停止轮询
    function checkStopPolling() {
        let hasRunning = false;
        tasks.forEach((taskData) => {
            const status = taskData.task?.status;
            if (status === 'running' || status === 'pending' || !status) {
                hasRunning = true;
            }
        });
        
        if (!hasRunning && pollInterval) {
            clearInterval(pollInterval);
            pollInterval = null;
        }
    }
    
    // 开始轮询
    function startPolling() {
        if (!pollInterval) {
            pollInterval = setInterval(pollAllTasks, POLL_INTERVAL_MS);
        }
    }
    
	    // 提交分析（支持批量；逗号/空格/换行分隔）
	    window.submitAnalysis = async function() {
	        const raw = codeInput.value || '';
	        const allCodes = parseCodes(raw);
	        const validCodes = allCodes.filter(isValidCode);
	        const invalidCodes = allCodes.filter(c => !isValidCode(c));

	        if (allCodes.length === 0) return;
	        if (invalidCodes.length > 0) {
	            alert('请先修正无效代码后再提交：' + invalidCodes.slice(0, 10).join(', ') + (invalidCodes.length > 10 ? ' ...' : ''));
	            codeInput.focus();
	            updateButtonState();
	            return;
	        }
	        if (validCodes.length === 0) return;

	        // 简单限流：一次最多提交 20 只，避免把本地/接口压爆
	        const codes = validCodes.slice(0, 20);
	        if (validCodes.length > 20) {
	            alert('一次最多提交 20 只股票，本次将只提交前 20 只。');
	        }
	        // invalidCodes 必为空：上方已强校验阻止提交

	        submitBtn.disabled = true;
	        submitBtn.textContent = '提交中...';

	        const reportType = reportTypeSelect.value;

	        try {
	            for (const code of codes) {
	                const resp = await fetch('/analysis?code=' + encodeURIComponent(code) + '&report_type=' + encodeURIComponent(reportType));
	                const data = await resp.json();
	                if (data && data.success) {
	                    const taskId = data.task_id;
	                    tasks.set(taskId, {
	                        task: {
	                            code: code,
	                            status: 'running',
	                            start_time: new Date().toISOString(),
	                            report_type: reportType,
	                            send_notification: data.send_notification
	                        },
	                        pollCount: 0
	                    });

	                    selectedTaskId = taskId;
	                    renderAllTasks();
	                    startPolling();

	                    // 提交后轻微间隔，降低触发限流/并发问题的概率
	                    await new Promise(r => setTimeout(r, 150));
	                } else {
	                    alert('提交失败（' + code + '）: ' + ((data && (data.error || data.message)) || '未知错误'));
	                }
	            }
	        } catch (e) {
	            alert('请求失败: ' + (e && e.message ? e.message : String(e)));
	        } finally {
	            submitBtn.disabled = false;
	            submitBtn.textContent = '开始分析';
	            updateButtonState();
	        }
	    };

	    window.submitMarketReview = async function() {
	        if (marketReviewBtn) {
	            marketReviewBtn.disabled = true;
	            marketReviewBtn.textContent = '复盘中...';
	        }
	        try {
	            const resp = await fetch('/market-review');
	            const data = await resp.json();
	            if (data && data.success && data.task_id) {
	                const taskId = data.task_id;
	                tasks.set(taskId, {
	                    task: {
	                        code: 'market',
	                        kind: 'market_review',
	                        status: 'running',
	                        start_time: new Date().toISOString(),
	                        report_type: 'full',
	                        send_notification: false
	                    },
	                    pollCount: 0
	                });
	                selectedTaskId = taskId;
	                renderAllTasks();
	                startPolling();
	            } else {
	                alert('提交失败：' + ((data && (data.error || data.message)) || '未知错误'));
	            }
	        } catch (e) {
	            alert('请求失败: ' + (e && e.message ? e.message : String(e)));
	        } finally {
	            if (marketReviewBtn) {
	                marketReviewBtn.disabled = false;
	                marketReviewBtn.textContent = '大盘复盘';
	            }
	        }
	    };

	    // 页面加载：拉取最近任务（容器/服务重启后也能看到最近记录）
	    function loadRecentTasks() {
	        fetch('/tasks?limit=' + encodeURIComponent(String(MAX_TASKS_DISPLAY)))
	            .then(r => r.json())
	            .then(data => {
	                if (!data || !data.success || !Array.isArray(data.tasks)) return;
	                data.tasks.forEach((t) => {
	                    if (!t || !t.task_id) return;
	                    tasks.set(t.task_id, { task: t, pollCount: 0 });
	                });
	                if (!selectedTaskId && data.tasks.length > 0) {
	                    selectedTaskId = data.tasks[0].task_id;
	                }
	                renderAllTasks();
	                startPolling();
	            })
	            .catch(() => {});
	    }
	    
	    // 初始化
	    syncLayoutVars();
	    setupTaskSplitter();
	    window.addEventListener('resize', function() {
	        // 简单防抖
	        clearTimeout(window.__syncLayoutVarsT);
	        window.__syncLayoutVarsT = setTimeout(syncLayoutVars, 120);
	    });
	    updateButtonState();
	    renderAllTasks();
	    loadRecentTasks();
	})();
	</script>
"""
    
    content = f"""
	  <div class="app-shell">
	    <div class="app-header">
	      <div class="brand-line">
	        <span class="brand-mark" aria-hidden="true">
	          <svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
	            <path d="M4 18V6"></path>
	            <path d="M4 18H20"></path>
	            <path d="M7 14l3-3 3 2 4-5"></path>
	            <path d="M17 8h3v3"></path>
	          </svg>
	        </span>
	        <div class="brand">
		          <div class="brand-title">股票智能分析</div>
	          <div class="brand-subtitle">手动触发分析并在页面展示结果（默认不推送通知）</div>
	        </div>
	      </div>
	      <div class="header-right">
	        <div class="header-actions">
	          <a class="nav-link active" href="/">分析</a>
	          <a class="nav-link" href="/env">.env 配置</a>
	        </div>
	        <div class="card-hint">API: <code>/health</code> · <code>/analysis</code> · <code>/tasks</code></div>
	      </div>
	    </div>

    <div class="app-grid">
      <!-- 左侧：输入 + 配置 -->
      <div class="panel">
	        <div class="card sticky-card">
	          <div class="card-title">
	            <h3 class="section-title">
	              <span class="section-icon" aria-hidden="true">
	                <svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
	                  <path d="M12 2v6"></path>
	                  <path d="M12 22v-2"></path>
	                  <path d="M4.93 4.93l4.24 4.24"></path>
	                  <path d="M19.07 19.07l-2.12-2.12"></path>
	                  <path d="M2 12h6"></path>
	                  <path d="M22 12h-2"></path>
	                  <path d="M4.93 19.07l4.24-4.24"></path>
	                  <path d="M19.07 4.93l-2.12 2.12"></path>
	                </svg>
	              </span>
	              快速分析
	            </h3>
	            <div class="card-hint">支持 A/H/美股</div>
	          </div>
          <div class="form-group" style="margin-bottom: 0;">
	            <label for="analysis_codes">股票代码</label>
            <div class="input-group">
              <textarea
                  id="analysis_codes"
                  placeholder="支持批量：每行一只"
                  rows="3"
                  maxlength="500"
                  autocomplete="off"
              ></textarea>
              <div class="select-wrap" title="选择报告类型">
                <select id="report_type" class="report-select">
                  <option value="simple">精简</option>
                  <option value="full" selected>完整</option>
                </select>
                <svg class="select-icon" viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                  <path d="M6 9l6 6 6-6"></path>
                </svg>
              </div>
              <button type="button" id="analysis_btn" class="btn-analysis" onclick="submitAnalysis()" disabled>
                开始分析
              </button>
            </div>
            <div class="header-actions" style="margin-top: 10px;">
              <button type="button" class="btn-inline btn-market" id="market_review_btn" onclick="submitMarketReview()">大盘复盘</button>
              <div class="card-hint">生成市场概览报告（不推送，仅页面展示）</div>
            </div>
            <div class="text-muted mt-2" id="analysis_codes_hint">支持批量输入；按 Ctrl/Cmd + Enter 可快速提交。格式：A股 6 位数字（600519）；港股 hk+5 位（hk00700）；美股 1-5 字母，可选 .x（aapl / brk.b）。</div>
          </div>
        </div>

	        <div class="card">
	          <div class="card-title">
	            <h3 class="section-title">
	              <span class="section-icon" aria-hidden="true">
	                <svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
	                  <path d="M12 20h9"></path>
	                  <path d="M12 4h9"></path>
	                  <path d="M4 20h.01"></path>
	                  <path d="M4 12h.01"></path>
	                  <path d="M4 4h.01"></path>
	                </svg>
	              </span>
	              常用配置
	            </h3>
	            <div class="card-hint">更完整的配置请到 <a href="/env">.env 配置</a></div>
	          </div>

	          <form method="post" action="/common/update">
	            <div class="settings-grid">
	              <div class="settings-section">
	                <div class="settings-section-title">
	                  <span>定时任务</span>
	                  <span class="card-hint">保存后可能需要重启生效</span>
	                </div>
	                <div class="settings-row">
	                  <div>
	                    <div class="settings-label">SCHEDULE_ENABLED</div>
	                    <div class="settings-desc">是否启用定时任务</div>
	                  </div>
	                  <div class="settings-control">
	                    <label class="switch">
	                      <input type="checkbox" name="SCHEDULE_ENABLED" {schedule_enabled_checked} />
	                      <span class="switch-track"><span class="switch-thumb"></span></span>
	                    </label>
	                  </div>
	                </div>
	                <div class="settings-row">
	                  <div>
	                    <div class="settings-label">SCHEDULE_TIME</div>
	                    <div class="settings-desc">每日执行时间（HH:MM）</div>
	                  </div>
	                  <div class="settings-control">
	                    <input class="input-sm" type="time" name="SCHEDULE_TIME" value="{schedule_time}" step="60" />
	                  </div>
	                </div>
	                <div class="settings-row">
	                  <div>
	                    <div class="settings-label">MARKET_REVIEW_ENABLED</div>
	                    <div class="settings-desc">是否启用大盘复盘</div>
	                  </div>
	                  <div class="settings-control">
	                    <label class="switch">
	                      <input type="checkbox" name="MARKET_REVIEW_ENABLED" {market_review_checked} />
	                      <span class="switch-track"><span class="switch-thumb"></span></span>
	                    </label>
	                  </div>
	                </div>
	              </div>
	            </div>

	            <div class="header-actions" style="margin-top: 12px;">
	              <button type="submit">保存常用配置</button>
	              <a class="nav-link" href="/env">打开 .env 配置中心</a>
	            </div>
	          </form>
	        </div>
      </div>

      <!-- 右侧：结果展示 -->
      <div class="panel">
	        <div class="card results-card">
	          <div class="card-title">
	            <h3 class="section-title">
	              <span class="section-icon" aria-hidden="true">
	                <svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
	                  <path d="M4 18V6"></path>
	                  <path d="M4 18H20"></path>
	                  <path d="M7 15l3-3 3 2 4-6"></path>
	                </svg>
	              </span>
	              分析结果
	            </h3>
	            <div class="card-hint">点击任务查看详情</div>
	          </div>

          <div class="results-split">
            <div id="task_list" class="task-list"></div>
            <div class="splitter" id="task_splitter" title="拖拽调整任务列表宽度" aria-hidden="true"></div>
            <div class="detail-pane" id="task_detail_view"></div>
          </div>
        </div>
      </div>
    </div>

    {toast_html}
    {analysis_js}
  </div>
"""
    
    page = render_base(
        title="A/H股自选配置 | WebUI",
        content=content
    )
    return page.encode("utf-8")


def render_env_editor_page(
    env_text: str,
    env_filename: str,
    message: Optional[str] = None
) -> bytes:
    """
    渲染 .env 配置编辑页面（全量编辑）。

    注意：该页面应仅在本机访问场景使用（handler 层已做回环地址限制）。
    """
    toast_html = render_toast(message) if message else ""
    safe_env_text = html.escape(env_text or "")

    content = f"""
	  <div class="app-shell">
	    <div class="app-header">
	      <div class="brand-line">
	        <span class="brand-mark" aria-hidden="true">
	          <svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
	            <path d="M4 18V6"></path>
	            <path d="M4 18H20"></path>
	            <path d="M7 14l3-3 3 2 4-5"></path>
	            <path d="M17 8h3v3"></path>
	          </svg>
	        </span>
	        <div class="brand">
	          <div class="brand-title">配置中心（.env）</div>
	          <div class="brand-subtitle">在页面维护所有环境变量（强烈建议仅本机使用）</div>
	        </div>
	      </div>
	      <div class="header-right">
	        <div class="header-actions">
	          <a class="nav-link" href="/">分析</a>
	          <a class="nav-link active" href="/env">.env 配置</a>
	        </div>
	        <div class="card-hint">{html.escape(env_filename)}</div>
	      </div>
	    </div>

	    <div class="app-grid" style="grid-template-columns: 1fr;">
	      <div class="panel">
	        <div class="card">
	          <div class="card-title">
	            <h3 class="section-title">
	              <span class="section-icon" aria-hidden="true">
	                <svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
	                  <path d="M12 20h9"></path>
	                  <path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z"></path>
	                </svg>
	              </span>
	              编辑 .env（全量）
	            </h3>
	            <div class="card-hint">保存会自动创建备份：{html.escape(env_filename)}.bak.YYYYMMDD_HHMMSS</div>
	          </div>

	          <div class="text-muted mt-2">
	            这里包含密钥/Token 等敏感信息。不要把 WebUI 暴露到公网；如需远程访问，请先加鉴权/反向代理。
	          </div>

	          <form method="post" action="/env/update" style="margin-top: 12px;">
	            <div class="form-group" style="margin-bottom: 12px;">
	              <textarea
	                  id="env_text"
	                  name="env_text"
	                  rows="28"
	                  spellcheck="false"
	                  autocapitalize="off"
	                  autocomplete="off"
	                  style="font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace; font-size: 12px; line-height: 1.5; min-height: 70vh;"
	                  placeholder="# 在这里粘贴/编辑 .env 内容"
	              >{safe_env_text}</textarea>
	            </div>
	            <div class="header-actions">
	              <button type="submit">保存 .env</button>
	              <a class="nav-link" href="/">返回分析</a>
	            </div>
	          </form>
	        </div>
	      </div>
	    </div>

	    {toast_html}
	  </div>
"""

    page = render_base(
        title=".env 配置中心 | WebUI",
        content=content
    )
    return page.encode("utf-8")


def render_error_page(
    status_code: int,
    message: str,
    details: Optional[str] = None
) -> bytes:
    """
    渲染错误页面
    
    Args:
        status_code: HTTP 状态码
        message: 错误消息
        details: 详细信息
    """
    details_html = f"<p class='text-muted'>{html.escape(details)}</p>" if details else ""
    
    content = f"""
  <div class="container" style="text-align: center;">
    <h2>😵 {status_code}</h2>
    <p>{html.escape(message)}</p>
    {details_html}
    <a href="/" style="color: var(--primary); text-decoration: none;">← 返回首页</a>
  </div>
"""
    
    page = render_base(
        title=f"错误 {status_code}",
        content=content
    )
    return page.encode("utf-8")
