import requests
from bs4 import BeautifulSoup
import re

class ThaiGoldScraper:
    # 所有的链接和配置
    BOC_URL = "https://www.boc.cn/th/bocinfo/bi3/201309/t20130910_2462434.html"
    SR_API = "https://www.superrichthailand.com/api/v1/rates"
    GTA_URL = "https://www.goldtraders.or.th/"
    HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    @staticmethod
    def get_latest_prices():
        try:
            resp = requests.get(ThaiGoldScraper.GTA_URL, headers=ThaiGoldScraper.HEADERS, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            # 增加安全检查，防止找不到元素
            s_elem = soup.select_one("#DetailPlace_uc_goldprices1_lblBLSell")
            b_elem = soup.select_one("#DetailPlace_uc_goldprices1_lblBLBuy")
            t_elem = soup.select_one("#DetailPlace_uc_goldprices1_lblAsTime")
            
            return {
                "sell": s_elem.text if s_elem else "0",
                "buy": b_elem.text if b_elem else "0",
                "time": t_elem.text if t_elem else "未知"
            }
        except:
            return {"sell": "0", "buy": "0", "time": "获取失败"}

    @staticmethod
    def get_realtime_rates():
        # --- 1. SuperRich API (第一优先级) ---
        try:
            r = requests.get(ThaiGoldScraper.SR_API, timeout=5)
            if r.status_code == 200:
                all_data = r.json().get('data', {}).get('all', [])
                for item in all_data:
                    if item.get('currency') == 'CNY':
                        # 深度安全检查：必须有 denominations 且不为空
                        denoms = item.get('denominations', [])
                        if denoms:
                            rate = float(denoms[0].get('buy', 0))
                            if rate > 0:
                                return {"rate": rate, "source": "SuperRich API"}
        except: pass

        # --- 2. 中国银行泰国 (第二优先级) ---
        try:
            r = requests.get(ThaiGoldScraper.BOC_URL, headers=ThaiGoldScraper.HEADERS, timeout=8)
            r.encoding = 'utf-8'
            soup = BeautifulSoup(r.text, 'html.parser')
            for row in soup.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) > 2:
                    txt = cells[0].get_text()
                    if "CNY" in txt or "人民币" in txt:
                        val_str = cells[1].get_text().strip()
                        val = float(val_str)
                        # 如果是按100计价
                        rate = val / 100 if val > 10 else val
                        return {"rate": round(rate, 4), "source": "BOC Thailand"}
        except: pass

        # --- 3. 终极保底 (万一全挂了) ---
        return {"rate": 4.48, "source": "系统默认(已断开)"}
