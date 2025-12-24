import streamlit as st
from utils import ThaiGoldScraper

st.set_page_config(page_title="Thai Gold", layout="wide")

@st.cache_data(ttl=120)
def fetch_ex_rates():
    return ThaiGoldScraper.get_superrich_rates()

@st.cache_data(ttl=60)
def fetch_gold_prices():
    return ThaiGoldScraper.get_latest_prices()

ex_rates = fetch_ex_rates() or {"buy": 4.48, "sell": 4.52}
prices = fetch_gold_prices()

st.title("🏆 Thai Gold Live")

# ---- 汇率 ----
st.subheader("🌍 汇率")
st.metric("RMB / THB（买入）", f"{ex_rates['buy']:.4f}")

st.divider()

# ---- 金价 ----
if prices:
    c1, c2 = st.columns(2)
    with c1:
        st.metric(
            "金条 卖出",
            f"{prices['bullion_sell']:,.0f} THB"
        )
        st.metric(
            "金条 买入",
            f"{prices['bullion_buy']:,.0f} THB"
        )
    with c2:
        st.metric(
            "首饰 卖出",
            f"{prices['ornament_sell']:,.0f} THB"
        )
        st.metric(
            "首饰 回购",
            f"{prices['tax_base']:,.0f} THB"
        )

    st.caption(f"更新时间：{prices['update_time']}")
else:
    st.error("无法获取金价数据")
