import asyncio
import json
import websockets

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
