import streamlit as st
from utils import ThaiGoldScraper

st.set_page_config(page_title="Thai Gold", layout="wide")

# 缓存设为 2 分钟
@st.cache_data(ttl=120)
def fetch_data():
    p = ThaiGoldScraper.get_latest_prices()
    r = ThaiGoldScraper.get_realtime_rates()
    return {"prices": p, "rates": r}

data = fetch_data()
p = data["prices"]
r = data["rates"]

st.title("🏆 泰国金价 & 汇率监控")

col1, col2 = st.columns(2)

with col1:
    st.metric("人民币兑泰铢 (汇买价)", f"{r['rate']}")
    st.caption(f"来源: {r['source']}")

with col2:
    st.metric("黄金卖出价 (铢)", f"{p['sell']}")
    st.caption(f"更新时间: {p['time']}")

st.divider()

# 简易计算器，防止因为数据不是数字而崩溃
try:
    gold_price = float(p['sell'].replace(',', ''))
    ex_rate = float(r['rate'])
    
    st.subheader("🧮 快速折算")
    weight = st.number_input("购入重量 (铢)", value=1.0)
    total_thb = weight * gold_price
    total_cny = total_thb / ex_rate if ex_rate > 0 else 0
    
    st.success(f"总价: {total_thb:,.2f} 泰铢")
    st.success(f"约合: {total_cny:,.2f} 人民币")
except:
    st.warning("计算器暂不可用，请等待数据加载")

if st.button("刷新数据"):
    st.cache_data.clear()
    st.rerun()
