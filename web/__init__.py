# -*- coding: utf-8 -*-
"""
===================================
Web 服务模块
===================================

分层架构：
- server.py    - HTTP 服务器核心
- router.py    - 路由分发
- handlers.py  - 请求处理器
- services.py  - 业务服务层
- templates.py - HTML 模板

使用方式：
    from web import run_server_in_thread, WebServer
    
    # 后台启动
    run_server_in_thread(host="127.0.0.1", port=8000)
    
    # 前台启动
    server = WebServer(host="127.0.0.1", port=8000)
    server.run()
"""

from web.server import WebServer, run_server_in_thread

__all__ = [
    'WebServer',
    'run_server_in_thread',
]
