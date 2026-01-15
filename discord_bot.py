# -*- coding: utf-8 -*-
"""
===================================
A股自选股智能分析系统 - Discord 机器人
===================================

职责：
1. 提供 Discord 斜杠指令交互
2. 管理自选股（数据库持久化）
3. 触发即时股票分析和大盘复盘
4. 增强通知推送体验
"""

import discord
from discord import app_commands
import logging
import asyncio
import os
from datetime import datetime
from typing import Optional, List

from config import get_config
from storage import get_db
from main import StockAnalysisPipeline, run_market_review
from notification import NotificationService

# 配置日志
logger = logging.getLogger(__name__)

class StockBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.config = get_config()
        self.db = get_db()

    async def setup_hook(self):
        # 同步斜杠指令
        await self.tree.sync()
        logger.info("Discord 斜杠指令已同步")

    async def on_ready(self):
        logger.info(f'机器人已登录: {self.user} (ID: {self.user.id})')
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="A股行情"))

    async def on_message(self, message):
        # 忽略机器人自己的消息
        if message.author.bot:
            return
            
        # 手动同步指令
        if message.content == "!sync":
            await self.tree.sync()
            await message.channel.send("✅ Slash Commands 已手动同步完成！")
            logger.info(f"Slash Commands 由 {message.author} 手动同步")

bot = StockBot()

@bot.tree.command(name="ping", description="检查机器人是否在线")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! Latency: {round(bot.latency * 1000)}ms")

@bot.tree.command(name="watchlist_list", description="显示当前自选股列表")
async def watchlist_list(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        stocks = bot.db.get_watchlist()
        if not stocks:
            # 如果数据库为空，尝试从配置读取
            config_stocks = bot.config.stock_list
            if config_stocks:
                await interaction.followup.send(f"📅 数据库暂无自选股，当前配置文件加载: `{', '.join(config_stocks)}`")
            else:
                await interaction.followup.send("❌ 当前暂无自选股，请使用 `/watchlist_add` 添加")
            return

        embed = discord.Embed(title="📋 我的自选股清单", color=discord.Color.blue(), timestamp=datetime.now())
        content = ""
        for i, s in enumerate(stocks, 1):
            name_str = f" ({s['name']})" if s['name'] else ""
            comment_str = f" - *{s['comment']}*" if s['comment'] else ""
            content += f"{i}. `{s['code']}`{name_str}{comment_str}\n"
        
        embed.description = content
        await interaction.followup.send(embed=embed)
    except Exception as e:
        logger.error(f"查询自选股失败: {e}")
        await interaction.followup.send(f"❌ 查询失败: {str(e)}")

@bot.tree.command(name="watchlist_add", description="添加股票到自选列表")
@app_commands.describe(code="股票代码 (如 600519)", name="股票名称 (可选)", comment="备注 (可选)")
async def watchlist_add(interaction: discord.Interaction, code: str, name: Optional[str] = None, comment: Optional[str] = None):
    # 简单的代码格式校验
    if not (code.isdigit() and len(code) == 6):
        await interaction.response.send_message("❌ 股票代码格式错误，请输入 6 位数字代码", ephemeral=True)
        return

    success = bot.db.add_to_watchlist(code, name, comment)
    if success:
        await interaction.response.send_message(f"✅ 已添加自选股: `{code}`" + (f" ({name})" if name else ""))
    else:
        await interaction.response.send_message("❌ 添加失败，请检查日志", ephemeral=True)

@bot.tree.command(name="watchlist_remove", description="从自选列表移除股票")
@app_commands.describe(code="股票代码")
async def watchlist_remove(interaction: discord.Interaction, code: str):
    success = bot.db.remove_from_watchlist(code)
    if success:
        await interaction.response.send_message(f"🗑️ 已成功移除自选股: `{code}`")
    else:
        await interaction.response.send_message(f"❌ 移除失败或未找到代码: `{code}`", ephemeral=True)

@bot.tree.command(name="analysis", description="立即对特定股票执行 AI 深度分析")
@app_commands.describe(code="股票代码")
async def analysis(interaction: discord.Interaction, code: str):
    await interaction.response.send_message(f"🔍 正在启动针对 `{code}` 的分析任务，请稍候...")
    
    # 在后台线程运行分析，避免阻塞异步循环
    def run_analysis_task():
        pipeline = StockAnalysisPipeline()
        return pipeline.process_single_stock(code)

    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, run_analysis_task)
        
        if result:
            # 这里先发送文本，后续优化 notification.py 后可以发送精美 Embed
            notifier = NotificationService()
            # 尝试通过通知渠道发送（如果配置了 Discord Webhook）
            # 同时在交互回复中也显示摘要
            summary = f"📊 **{result.name} ({result.code}) 分析报告**\n" \
                      f"💡 建议: {result.operation_advice}\n" \
                      f"🌡️ 情绪: {result.sentiment_score}/100\n" \
                      f"📈 趋势: {result.trend_prediction}\n\n" \
                      f"📝 **摘要**: {result.analysis_summary}"
            
            await interaction.followup.send(summary)
            
            # 手动触发全渠道推送（包含 Discord Webhook）
            # 注意：generate_dashboard_report 需要 List[AnalysisResult]
            report = notifier.generate_dashboard_report([result])
            notifier.send(report)
        else:
            await interaction.followup.send(f"❌ 分析 `{code}` 失败，请检查代码是否正确或查阅日志。")
    except Exception as e:
        logger.error(f"即时分析异常: {e}")
        await interaction.followup.send(f"❌ 执行异常: {str(e)}")

@bot.tree.command(name="market", description="获取当前大盘实时分析报告")
async def market(interaction: discord.Interaction):
    await interaction.response.send_message("📊 正在搜集市场情报并生成复盘报告...")
    
    def run_market_task():
        pipeline = StockAnalysisPipeline()
        return run_market_review(pipeline.notifier, pipeline.analyzer, pipeline.search_service)

    try:
        loop = asyncio.get_event_loop()
        report = await loop.run_in_executor(None, run_market_task)
        
        if report:
            # 截断超长报告（Discord 限制 2000）
            if len(report) > 1900:
                report = report[:1900] + "\n\n...(余下内容已通过 Webhook 推送)"
            await interaction.followup.send(report)
        else:
            await interaction.followup.send("❌ 生成大盘报告失败。")
    except Exception as e:
        logger.error(f"大盘复盘异常: {e}")
        await interaction.followup.send(f"❌ 执行异常: {str(e)}")

def main():
    config = get_config()
    token = config.discord_bot_token
    if not token:
        logger.error("未找到 DISCORD_BOT_TOKEN，请在环境变量中配置")
        return

    # 设置日志
    from main import setup_logging
    setup_logging(debug=config.debug, log_dir=config.log_dir)
    
    bot.run(token)

if __name__ == "__main__":
    main()
