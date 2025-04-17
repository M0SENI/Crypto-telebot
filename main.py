import telebot
import requests
import logging
from typing import Dict, Union, Tuple, Optional
from telebot.apihelper import ApiTelegramException
from config import TOKEN

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(TOKEN)

class CryptoPriceBot:
    def __init__(self, token: str = "7532465174:AAHsO56qNXednrsrBdijzhrVK8zrkQMtx5w", usdt_toman_price: float = 55000):
        self.bot = telebot.TeleBot(token)
        self.KUCOIN_API_URL = "https://api.kucoin.com/api/v1/market/orderbook/level1"
        self.BINANCE_API_URL = "https://api.binance.com/api/v3/ticker/price"
        self.USDT_TOMAN_PRICE = usdt_toman_price
        self._setup_handlers()
    
    def _setup_handlers(self):
        @self.bot.message_handler(commands=['start', 'help'])
        def send_welcome(message):
            welcome_text = """
            سلام! 👋
            من می‌توانم قیمت بیت‌کوین را به شما نشان دهم.
            
            دستورات موجود:
            /price - نمایش قیمت بیت‌کوین
            /help - نمایش این راهنما
            """
            try:
                self.bot.reply_to(message, welcome_text)
            except ApiTelegramException as e:
                logger.error(f"خطا در ارسال پیام خوش‌آمدگویی: {e}")

        @self.bot.message_handler(commands=['price'])
        def send_price(message):
            try:
                success, result = self.get_crypto_price()
                
                if success:
                    btc_usdt = result["btc_usdt"]
                    btc_toman = btc_usdt * self.USDT_TOMAN_PRICE
                    source = result.get("source", "نامشخص")
                    
                    response_text = f"""
💰 قیمت‌های لحظه‌ای:

BTC/USDT: {btc_usdt:,.2f} USDT
BTC/TOMAN: {btc_toman:,.0f} تومان

🏢 منبع: {source}
🕒 بروزرسانی: هم اکنون
                    """
                else:
                    response_text = f"❌ خطا: {result}"
                
                self.bot.reply_to(message, response_text)
            except ApiTelegramException as e:
                logger.error(f"خطا در ارسال قیمت‌ها: {e}")
            except Exception as e:
                logger.error(f"خطای غیرمنتظره: {e}")
    
    def get_crypto_price(self) -> Tuple[bool, Union[Dict, str]]:
        try:
            response = requests.get(f"{self.KUCOIN_API_URL}?symbol=BTC-USDT", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data["code"] == "200000" and "data" in data:
                    return True, {
                        "btc_usdt": float(data["data"]["price"]),
                        "status": "success",
                        "source": "KuCoin"
                    }
        except Exception as e:
            logger.warning(f"خطا در دریافت قیمت از KuCoin: {e}")

        try:
            response = requests.get(f"{self.BINANCE_API_URL}?symbol=BTCUSDT", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return True, {
                    "btc_usdt": float(data["price"]),
                    "status": "success",
                    "source": "Binance"
                }
        except Exception as e:
            logger.warning(f"خطا در دریافت قیمت از Binance: {e}")

        return False, "خطا در دریافت اطلاعات از تمامی API‌ها"
    
    def run(self, debug: bool = False):
        try:
            if debug:
                logger.info("در حال راه‌اندازی ربات...")
            
            me = self.bot.get_me()
            logger.info(f"ربات با نام @{me.username} با موفقیت راه‌اندازی شد")
            logger.info('code by Mohsen Qorbani')
            
            self.bot.infinity_polling(timeout=60, long_polling_timeout=30)
        except ApiTelegramException as e:
            logger.error(f"خطا در اتصال به API تلگرام: {e}")
            raise
        except Exception as e:
            logger.error(f"خطای غیرمنتظره در اجرای ربات: {e}")
            raise

if __name__ == "__main__":
    try:
        bot = CryptoPriceBot()
        bot.run(debug=True)
    except Exception as e:
        logger.error(f"خطا در راه‌اندازی ربات: {e}") 