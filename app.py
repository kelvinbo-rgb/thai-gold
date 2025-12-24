import streamlit as st
from utils import ThaiGoldScraper

st.set_page_config(page_title="Thai Gold Monitor", layout="wide")

# 缓存机制：如果出错，不报错，返回一个安全对象
@st.cache_data(ttl=120)
def fetch_data_safe():
    try:
        p = ThaiGoldScraper.get_latest_prices()
        r = ThaiGoldScraper.get_realtime_rates()
        return {"prices": p, "rates": r}
    except Exception as e:
        # 万一代码内部还有错，直接返回保底字典，不让 UI 崩溃
        return {
            "prices": {"sell": "0", "buy": "0", "time": "Error"},
            "rates": {"rate": 4.48, "source": "Fallback"}
        }

# 获取数据
full_data = fetch_data_safe()
p = full_data["prices"]
r = full_data["rates"]

st.title("🏆 泰国金价与汇率")

# 汇率大字显示
st.metric(label=f"人民币兑泰铢 ({r['source']})", value=f"{r['rate']}")

# 金价显示
c1, c2 = st.columns(2)
c1.metric("金条卖出价", f"{p['sell']} THB")
c2.info(f"更新时间: {p['time']}")

st.divider()

# 计算逻辑：先清理字符串中的逗号
try:
    clean_price = float(str(p['sell']).replace(',', ''))
    if clean_price > 0:
        st.subheader("🧮 购金成本计算")
        weight = st.number_input("重量 (铢)", value=1.0, step=0.1)
        total_thb = weight * clean_price
        total_cny = total_thb / r['rate']
        
        st.success(f"总支出: {total_thb:,.2f} THB")
        st.success(f"约合: {total_cny:,.2f} CNY")
except:
    st.warning("等待数据同步中...")

if st.sidebar.button("强制刷新数据"):
    st.cache_data.clear()
    st.rerun()
