import streamlit as st
import pandas as pd
from utils import ThaiGoldScraper, GoldConverter
import time
import os

# Page Config
st.set_page_config(page_title="Thailand Gold - 泰国黄金", layout="wide")

# Localization
LANGS = {
    "TH": {
        "title": "ราคาทองคำประเทศไทย",
        "bullion": "ทองคำแท่ง",
        "ornament": "ทองรูปพรรณ",
        "buy": "รับซื้อ",
        "sell": "ขายออก",
        "converter": "เครื่องคิดเลข",
        "weight_baht": "น้ำหนัก (บาท)",
        "gamnuy": "ค่ากำเหน็จ (บาท)",
        "total": "ราคาสุทธิ",
        "last_update": "อัพเดทล่าสุด",
        "exchange_rates": "อัตราแลกเปลี่ยน",
        "rmb_thb": "หยวน/บาท (RMB/THB)",
        "gold_spot": "ทองสปอต (Spot)",
        "thb_usd": "ดอลลาร์/บาท (THB/USD)",
        "unit_converter": "เครื่องมือแปลงหน่วย",
        "baht": "บาท (Baht)",
        "gram": "กรัม (Gram)",
        "ounce": "ออนซ์ (Ounce)",
        "main_title": "ราคาทองคำประเทศไทย (Thai Gold Live)",
        "investment_calc": "คำนวณผลกำไร/ขาดทุน",
        "buy_date": "วันที่ซื้อ",
        "buy_price": "ราคาที่ซื้อ (ต่อบาท)",
        "buy_amount": "จำนวนที่ซื้อ (บาท)",
        "current_value": "มูลค่าปัจจุบัน",
        "profit_loss": "กำไร/ขาดทุน",
        "return_rate": "อัตราผลตอบแทน",
        "annual_return": "อัตราผลตอบแทนต่อปี",
        "calc_settings": "ตั้งค่าการคำนวณ",
        "gold_type": "ประเภททอง",
        "alerts": "แจ้งเตือนราคา",
        "alert_target": "เป้าหมายราคาทองคำแท่ง",
        "alert_cond": "เงื่อนไข",
        "alert_above": "สูงกว่า",
        "alert_below": "ต่ำกว่า",
        "alert_reached": "🎯 บรรลุเป้าหมายราคาแล้ว!",
        "alert_monitoring": "⏳ กำลังติดตาม",
        "alert_set": "ตั้งค่า",
        "set_confirm": "ตั้งค่าแจ้งเตือนแล้ว!",
        "sponsor_title": "☕ สนับสนุน",
        "sponsor_desc": "หากคุณชอบแนวคิดนี้ คุณสามารถสนับสนุนได้!",
        "sponsor_alipay": "Alipay (จีน)",
        "sponsor_promptpay": "PromptPay (ไทย)",
        "sponsor_msg": "ขอให้โชคดีทุกความฝันครับ"
    },
    "CN": {
        "title": "泰国黄金实时报价",
        "bullion": "金条",
        "ornament": "金饰/首饰",
        "buy": "买入价",
        "sell": "卖出价",
        "converter": "计算器",
        "weight_baht": "重量 (Baht)",
        "gamnuy": "加工费 (Gamnuy)",
        "total": "总价 (泰铢)",
        "last_update": "最后更新",
        "exchange_rates": "汇率监控",
        "rmb_thb": "人民币/泰铢 (RMB/THB)",
        "gold_spot": "国际金价 (Spot)",
        "thb_usd": "泰铢/美元 (THB/USD)",
        "unit_converter": "单位换算",
        "baht": "泰铢 (Baht)",
        "gram": "克 (Gram)",
        "ounce": "盎司 (Ounce)",
        "main_title": "泰国黄金 (Thai Gold Live)",
        "investment_calc": "投资盈亏计算器",
        "buy_date": "买入日期",
        "buy_price": "买入单价 (每铢)",
        "buy_amount": "买入数量 (铢)",
        "current_value": "当前市值",
        "profit_loss": "盈亏金额",
        "return_rate": "累计收益率",
        "annual_return": "年化收益率",
        "calc_settings": "计算设置",
        "gold_type": "黄金类型",
        "alerts": "价格预警",
        "alert_target": "目标金条价格",
        "alert_cond": "触发条件",
        "alert_above": "高于",
        "alert_below": "低于",
        "alert_reached": "🎯 已达到目标价格!",
        "alert_monitoring": "⏳ 正在监控",
        "alert_set": "设定",
        "set_confirm": "预警设定成功!",
        "sponsor_title": "☕ 赞助作者",
        "sponsor_desc": "如果您的思路多了一点提示，请给我一点赞助，我会更有动力去更新和分享。",
        "sponsor_alipay": "中国支付宝",
        "sponsor_promptpay": "泰国收款码",
        "sponsor_msg": "祝终有一日你我梦想成真"
    },
    "EN": {
        "title": "Thai Gold Real-time",
        "bullion": "Bullion",
        "ornament": "Ornaments",
        "buy": "Buy",
        "sell": "Sell",
        "converter": "Calculator",
        "weight_baht": "Weight (Baht)",
        "gamnuy": "Gamnuy Fee",
        "total": "Total (THB)",
        "last_update": "Updated",
        "exchange_rates": "Rates",
        "rmb_thb": "RMB/THB",
        "gold_spot": "Spot",
        "thb_usd": "THB/USD",
        "unit_converter": "Converter",
        "baht": "Baht",
        "gram": "Gram",
        "ounce": "Ounce",
        "main_title": "Thai Gold Live",
        "investment_calc": "Investment P&L Calc",
        "buy_date": "Purchase Date",
        "buy_price": "Purchase Price (per Baht)",
        "buy_amount": "Amount (Baht)",
        "current_value": "Current Value",
        "profit_loss": "Profit/Loss",
        "return_rate": "Return Rate",
        "annual_return": "Annual ROI",
        "calc_settings": "Calculator Settings",
        "gold_type": "Gold Type",
        "alerts": "Price Alerts",
        "alert_target": "Target Bullion Price",
        "alert_cond": "Condition",
        "alert_above": "Above",
        "alert_below": "Below",
        "alert_reached": "🎯 Price Alert Reached!",
        "alert_monitoring": "⏳ Monitoring",
        "alert_set": "Set",
        "set_confirm": "Alert set successfully!",
        "sponsor_title": "☕ Support",
        "sponsor_desc": "If you find this useful and want to support continued development.",
        "sponsor_alipay": "Alipay (CN)",
        "sponsor_promptpay": "PromptPay (TH)",
        "sponsor_msg": "May your dreams come true."
    }
}

# --- Language Selection (At Top for Mobile) ---
if "lang_choice" not in st.session_state:
    st.session_state.lang_choice = "CN"

c_l, lc1, lc2, lc3 = st.columns([2, 1, 1, 1])
with lc1:
    if st.button("🇨🇳 中文", use_container_width=True, type="primary" if st.session_state.lang_choice == "CN" else "secondary"):
        st.session_state.lang_choice = "CN"
        st.rerun()
with lc2:
    if st.button("🇹🇭 ไทย", use_container_width=True, type="primary" if st.session_state.lang_choice == "TH" else "secondary"):
        st.session_state.lang_choice = "TH"
        st.rerun()
with lc3:
    if st.button("🇺🇸 EN", use_container_width=True, type="primary" if st.session_state.lang_choice == "EN" else "secondary"):
        st.session_state.lang_choice = "EN"
        st.rerun()

lang_code = st.session_state.lang_choice
t = LANGS[lang_code]

# --- 0. MAIN HEADER ---
st.markdown(f"""
<div style="text-align: center; padding: 10px; border-bottom: 2px solid #ffd700; margin-bottom: 20px;">
    <h1 style="color: #d4af37; margin: 0;">🏆 {t['main_title']}</h1>
    <p style="color: #888; margin: 0; font-size: 0.9em;">Real-time Gold & Currency Monitor</p>
</div>
""", unsafe_allow_html=True)

# st.title(f"💰 {t['title']}") # Removed old title

# --- 1. EXCHANGE RATES - TOP BAR ---
@st.cache_data(ttl=600)
def fetch_ex_rates():
    return ThaiGoldScraper.get_superrich_rates()

ex_rates = fetch_ex_rates()

@st.cache_data(ttl=300)
def fetch_gold_data():
    data = ThaiGoldScraper.get_latest_prices()
    if data:
        from utils import DataManager
        DataManager.save_snapshot(data)
    return data

prices = fetch_gold_data()

st.subheader(f"🌍 {t['exchange_rates']}")
rate_col1, rate_col2, rate_col3 = st.columns(3)

with rate_col1:
    # RMB/THB first, no SuperRich labels
    st.metric(t['rmb_thb'], f"{ex_rates['buy']:.2f}")
with rate_col2:
    # Display Thai Bullion Sell instead of Gold Spot
    val = prices['bullion_sell'] if prices else 0
    st.metric(f"{t['bullion']}({t['sell']})", f"{val:,.0f}")
with rate_col3:
    # THB/USD cleaned up
    st.metric(t['thb_usd'], "34.50")

st.divider()

# --- 2. REAL-TIME PRICES & INTEGRATED CALCULATOR ---
st.subheader(f"📊 {t['bullion']} & {t['ornament']}")

if prices:
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"🏆 {t['bullion']}")
        st.metric(label=t['sell'], value=f"{prices['bullion_sell']:,.0f} THB")
        st.metric(label=t['buy'], value=f"{prices['bullion_buy']:,.0f} THB")
        
        # Integrated Calculator for Bullion
        st.markdown(f"**🧮 {t['converter']}**")
        b_weight = st.number_input(f"{t['weight_baht']}", min_value=0.0, value=1.0, step=0.01, key="b_weight")
        b_gamnuy = st.number_input(f"{t['gamnuy']}", min_value=0, value=100, key="b_gamnuy")
        b_total = (b_weight * prices['bullion_sell']) + b_gamnuy
        st.write(f"👉 **{b_total:,.2f} THB**")
        
    with col2:
        st.warning(f"💍 {t['ornament']}")
        st.metric(label=t['sell'], value=f"{prices['ornament_sell']:,.0f} THB")
        st.metric(label=t['buy'], value=f"{prices['tax_base']:,.0f} THB")
        
        # Integrated Calculator for Ornaments
        st.markdown(f"**🧮 {t['converter']}**")
        o_weight = st.number_input(f"{t['weight_baht']}", min_value=0.0, value=1.0, step=0.01, key="o_weight")
        o_gamnuy = st.number_input(f"{t['gamnuy']}", min_value=0, value=500, key="o_gamnuy")
        o_total = (o_weight * prices['ornament_sell']) + o_gamnuy
        st.write(f"👉 **{o_total:,.2f} THB**")
    
    st.caption(f"🕒 {t['last_update']}: {prices['update_time']}")
else:
    st.error("Failed to fetch prices.")

# --- 3. GOLD INVESTMENT CALCULATOR (P&L) ---
st.divider()
st.subheader(f"📈 {t['investment_calc']}")

st.markdown(f"**💼 {t['calc_settings']}**")
inv_col1, inv_col2, inv_col3, inv_col4 = st.columns(4)
with inv_col1:
    inv_type = st.radio(t['gold_type'], [t['bullion'], t['ornament']], horizontal=True, key="inv_type")
with inv_col2:
    buy_date = st.date_input(t['buy_date'], value=pd.to_datetime("today") - pd.Timedelta(days=30))
with inv_col3:
    buy_price = st.number_input(t['buy_price'], min_value=0.0, value=64000.0, step=100.0)
with inv_col4:
    buy_amount = st.number_input(t['buy_amount'], min_value=0.0, value=1.0, step=1.0)

if prices:
    current_price = prices['bullion_sell'] if inv_type == t['bullion'] else prices['ornament_sell']
    total_cost = buy_price * buy_amount
    current_val = current_price * buy_amount
    pnl = current_val - total_cost
    roi = (pnl / total_cost * 100) if total_cost > 0 else 0
    
    # Calculate Annualized ROI
    today = pd.to_datetime("today").normalize()
    b_date = pd.to_datetime(buy_date).normalize()
    days_diff = (today - b_date).days
    if days_diff <= 0: days_diff = 1
    annual_roi = ((1 + roi/100)**(365/days_diff) - 1) * 100
    
    res_col1, res_col2, res_col3, res_col4 = st.columns(4)
    res_col1.metric(t['current_value'], f"{current_val:,.0f} THB")
    res_col2.metric(t['profit_loss'], f"{pnl:,.0f} THB", delta=f"{pnl:,.0f}")
    res_col3.metric(t['return_rate'], f"{roi:.2f}%", delta=f"{roi:.2f}%")
    res_col4.metric(t['annual_return'], f"{annual_roi:.2f}%")

# --- 3.5 [NEW] PRICE ALERTS ---
st.divider()
st.subheader(f"🔔 {t['alerts']}")

@st.cache_resource
def get_alert_manager():
    from utils import AlertManager
    return AlertManager()

alerts_col1, alerts_col2, alerts_col3 = st.columns([2, 1, 1])
with alerts_col1:
    target_price = st.number_input(t['alert_target'], min_value=0, value=65000, step=100)
with alerts_col2:
    condition = st.selectbox(t['alert_cond'], [t['alert_above'], t['alert_below']])
with alerts_col3:
    if st.button(t['alert_set'], use_container_width=True):
        st.session_state.active_alert = {"target": target_price, "cond": condition}
        st.success(t['set_confirm'])

if "active_alert" in st.session_state:
    alert = st.session_state.active_alert
    current = prices['bullion_sell'] if prices else 0
    triggered = False
    if alert['cond'] == t['alert_above'] and current >= alert['target']: triggered = True
    if alert['cond'] == t['alert_below'] and current <= alert['target']: triggered = True
    
    if triggered:
        st.toast(f"{t['alert_reached']} {current:,.0f} {alert['cond']} {alert['target']:,.0f}", icon="🔥")
        st.error(f"{t['alert_reached']}: {current:,.0f} {alert['cond']} {alert['target']:,.0f}")
    else:
        st.info(f"{t['alert_monitoring']}: {t['bullion']} {current:,.0f} vs {t['alert_target']} {alert['target']:,.0f}")

# --- 4. UNIT CONVERTER (Weight Only) ---
st.divider()
st.subheader(f"⚖️ {t['unit_converter']}")

u_col1, u_col2, u_col3 = st.columns(3)

# Session state to handle mutual updates
if 'u_baht' not in st.session_state: st.session_state.u_baht = 1.0

def update_from_baht():
    b = st.session_state.u_baht
    st.session_state.u_gram = b * 15.244
    st.session_state.u_oz = st.session_state.u_gram / 31.1035

def update_from_gram():
    g = st.session_state.u_gram
    st.session_state.u_baht = g / 15.244
    st.session_state.u_oz = g / 31.1035

def update_from_oz():
    oz = st.session_state.u_oz
    st.session_state.u_gram = oz * 31.1035
    st.session_state.u_baht = st.session_state.u_gram / 15.244

# Initialize others
if 'u_gram' not in st.session_state: update_from_baht()

with u_col1:
    st.number_input(t['baht'], key="u_baht", on_change=update_from_baht, step=0.1)
with u_col2:
    st.number_input(t['gram'], key="u_gram", on_change=update_from_gram, step=1.0)
with u_col3:
    st.number_input(t['ounce'], key="u_oz", on_change=update_from_oz, step=0.1)

# --- 5. SPONSOR MODULE ---
st.divider()
st.markdown(f"""
<div style="text-align: center; color: #888; border-top: 1px solid #eee; padding-top: 20px;">
    <h4>{t['sponsor_title']}</h4>
    <p style="font-size: 0.9em;">{t['sponsor_desc']}</p>
</div>
""", unsafe_allow_html=True)

s_col1, s_col2 = st.columns(2)
with s_col1:
    st.write(f"💳 **{t['sponsor_alipay']}**")
    if os.path.exists("qr_alipay.jpg"):
        st.image("qr_alipay.jpg", caption=t['sponsor_msg'])
    else:
        st.image("https://via.placeholder.com/200?text=Alipay+QR", caption=t['sponsor_msg'])
with s_col2:
    st.write(f"📲 **{t['sponsor_promptpay']}**")
    if os.path.exists("qr_promptpay.jpg"):
        st.image("qr_promptpay.jpg", caption=t['sponsor_msg'])
    else:
        st.image("https://via.placeholder.com/200?text=PromptPay+QR", caption=t['sponsor_msg'])

st.markdown(f"<div style='text-align: center; color: #bbb; font-size: 0.8em;'>{t['sponsor_msg']}</div>", unsafe_allow_html=True)

# --- 6. FOOTER ---
st.divider()
st.markdown(f"""
<div style="text-align: center; color: #888; padding: 20px;">
    <p>📧 Contact: <a href="mailto:kelvinbo@gmail.com" style="color: #d4af37;">kelvinbo@gmail.com</a></p>
    <p>© 2025 Thai Gold Live - Your Premium Gold Companion</p>
</div>
""", unsafe_allow_html=True)
