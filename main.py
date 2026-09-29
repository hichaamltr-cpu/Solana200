import asyncio
import json
import websockets
import aiohttp
import asyncio

# معلومات البوت ديالك
TELEGRAM_BOT_TOKEN = "8920135049:AAFNWlYajeaQkWZVRRAwQjR0UXZOx6F_2aI"
TELEGRAM_CHAT_ID = "7083597478"

async def send_telegram_alert(mint, stats):
    message = (
        f"🚨 **تنبيه صيد عاجل (PUMP.FUN 5M)** 🚀\n\n"
        f"📌 **Mint:** `{mint}`\n"
        f"⏱️ **العمر:** {stats['age']} ثانية\n"
        f"📊 **ضغط الشراء:** {stats['buy_pressure']:.1f}%\n"
        f"🔢 **عدد الصفقات:** {stats['trades']}\n"
        f"👥 **المحافظ الفريدة:** {stats['wallets']}\n"
        f"💰 **الماركت كاب:** {stats['high_mcap_sol']} SOL\n"
        f"📉 **عمق Dip:** {stats['dip_depth']:.1f}%\n\n"
        f"🔗 **رابط الشراء الفوري:**\n"
        f"https://pump.fun/{mint}"
    )
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    async with aiohttp.ClientSession() as session:
        await session.post(url, json=payload)

# 1. حط هنا مفتاح API ديال Bitquery ديالك
BITQUERY_API_KEY = "ory_at_HiIVFD_1xPR8Cl5j1G8JgK0-3YMZEXqCnFX8c-mSOtQ.1RQUmg9s5SKSloQfb1qbl1H2sCc93AKdoqE152ap51E"

# 2. الاستعلام (GraphQL Subscription) الخاص بـ Pump.fun على Solana
BITQUERY_SUBSCRIPTION = """
subscription {
  Solana {
    DEXTrades(
      where: {Trade: {Dex: {ProtocolName: {is: "pump"}}}}
    ) {
      Trade {
        Dex {
          ProtocolName
        }
        Buy {
          Currency {
            MintAddress
            Symbol
          }
          Amount
        }
        Sell {
          Amount
        }
        Market {
          MarketAddress
        }
      }
    }
  }
}
"""

# ذاكرة متابعة التوكنات
active_tokens = {}

async def run_bitquery_sniper():
    # الرابط المباشر للـ WebSocket ديال Bitquery V2
    url = f"wss://streaming.bitquery.io/graphql?token={BITQUERY_API_KEY}"
    
    headers = {
        "Sec-WebSocket-Protocol": "graphql-ws"
    }

    async with websockets.connect(url, subprotocols=["graphql-ws"]) as ws:
        # Step 1: Connection Init
        await ws.send(json.dumps({"type": "connection_init"}))
        
        # Step 2: Start Subscription
        sub_message = {
            "id": "1",
            "type": "start",
            "payload": {
                "query": BITQUERY_SUBSCRIPTION
            }
        }
        await ws.send(json.dumps(sub_message))
        print("🚀 تم الاتصال بـ Bitquery API! جاري مراقبة صفقات Pump.fun الحية...\n")

        while True:
            try:
                response = await ws.recv()
                data = json.loads(response)

                if data.get("type") == "data":
                    trade_info = data["payload"]["data"]["Solana"]["DEXTrades"][0]["Trade"]
                    mint = trade_info["Buy"]["Currency"]["MintAddress"]
                    
                    # هنا كيتسجل التوكن وكيتبدؤوا يتحسبوا الشروط الـ 12
                    print(f"📡 صفقة جديدة لالتقاط التوكن: {mint[:10]}...")

            except Exception as e:
                print(f"⚠️ خطأ فـ الاتصال: {e}")
                break

# تشغيل السكريبت
asyncio.run(run_bitquery_sniper())
