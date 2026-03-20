import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone
import json
import os

# --- 1. 基本設定與時區 (UTC+8) ---
tz = timezone(timedelta(hours=8)) 
STAFF_FILE = "staff_list.json"
ORDER_FILE = "orders_data.json"
CONFIG_FILE = "system_config.json"

st.set_page_config(page_title="台大環職部 德克士訂餐系統", layout="wide")

# --- 2. 資料處理函數 (確保 UTF-8 防止亂碼) ---
def load_data(file_path, default_data):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            return default_data
    return default_data

def save_data(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 初始化名單與訂單
initial_staff = ["文鴻", "舒荻", "卓憲", "序立", "述辰", "秉高", "其家", "茵婕", "品妤", "宛霖", "廷恩", "虹彣", "立涵", "喬菲", "智葳", "芸華", "立潔", "薇諠", "馥戎"]
if 'staff' not in st.session_state:
    st.session_state.staff = load_data(STAFF_FILE, initial_staff)
if 'orders' not in st.session_state:
    st.session_state.orders = load_data(ORDER_FILE, [])

# --- 3. 自動換日重置邏輯 ---
now_tpe = datetime.now(tz)
today_str = now_tpe.strftime("%Y-%m-%d")
config = load_data(CONFIG_FILE, {"last_reset_date": today_str})

if config["last_reset_date"] != today_str:
    st.session_state.orders = []
    save_data(ORDER_FILE, [])
    config["last_reset_date"] = today_str
    save_data(CONFIG_FILE, config)

# --- 4. 價格查詢表 (請確保與圖片檔名一致) ---
price_map = {
    "咔滋脆皮炸雞": 75, "超級酪乳雞腿堡": 149, "雙層香酥脆雞堡": 119,
    "起司蔬菜牛肉堡": 79, "檸香雞腿堡": 119, "椒香雞腿堡": 119, "黃金Q蝦堡": 139,
    "咔滋薯霸(大)": 63, "黃金薯餅": 38, "紫金QQ球": 45, "咔滋洋蔥圈": 49, "咔滋啃骨雞(辣味)": 59,
    "冰紅茶(M)": 40, "無糖綠茶(M)": 40, "經典冰奶茶": 45, "百事可樂(M)": 38, "七喜(M)": 38, 
    "鮮萃檸檬綠茶": 59, "現磨美式咖啡(M)": 48
}

special_items = {
    8: ("咔滋脆皮炸雞", 75, "咔滋脆皮炸雞.png"),
    18: ("超級酪乳雞腿堡", 149, "超級酪乳雞腿堡.png"),
    28: ("雙層香酥脆雞堡", 119, "雙層香酥脆雞堡.png")
}

regular_menu = [
    ("起司蔬菜牛肉堡", 79, "起司蔬菜牛肉堡.png"), ("檸香雞腿堡", 119, "檸香雞腿堡.png"),
    ("椒香雞腿堡", 119, "椒香雞腿堡.png"), ("黃金Q蝦堡", 139, "黃金Q蝦堡.png"),
    ("咔滋薯霸(大)", 63, "咔滋薯霸(大).png"), ("黃金薯餅", 38, "黃金薯餅.png"),
    ("紫金QQ球", 45, "紫金QQ球.png"), ("咔滋洋蔥圈", 49, "咔滋洋蔥圈.png"),
    ("咔滋啃骨雞(辣味)", 59, "咔滋啃骨雞(辣味).png"), ("冰紅茶(M)", 40, "冰紅茶(M).png"),
    ("無糖綠茶(M)", 40, "無糖綠茶(M).png"), ("經典冰奶茶", 45, "經典冰奶茶.png"),
    ("百事可樂(M)", 38, "百事可樂(M).png"), ("七喜(M)", 38, "七喜(M).png"),
    ("鮮萃檸檬綠茶", 59, "鮮萃檸檬綠茶.png"), ("現磨美式咖啡(M)", 48, "現磨美式咖啡(M).png")
]

# --- 5. 管理員後台 ---
st.sidebar.title("🔐 管理後台")
pwd = st.sidebar.text_input("輸入管理密碼", type="password")
if pwd == "@ntuh121005":
    with st.sidebar.expander("👥 人員管理"):
        new_name_adm = st.text_input("新增姓名")
        if st.button("確認新增"):
            if new_name_adm and new_name_adm not in st.session_state.staff:
                st.session_state.staff.append(new_name_adm)
                save_data(STAFF_FILE, st.session_state.staff)
                st.rerun()
    if st.sidebar.button("🚨 立即清空所有訂單"):
        st.session_state.orders = []
        save_data(ORDER_FILE, [])
        st.rerun()

# --- 6. 前台主畫面 ---
st.title("🍔 台大環職部 德克士訂餐系統")
is_member_day = now_tpe.day in [8, 18, 28]

# 湊對看板
st.subheader("📢 湊對即時看板")
if st.session_state.orders:
    all_o = [o['餐點'] for o in st.session_state.orders]
    counts = pd.Series(all_o).value_counts()
    odd_items = counts[counts % 2 != 0]
    if not odd_items.empty:
        cols = st.columns(min(len(odd_items), 5))
        for i, (name, count) in enumerate(odd_items.items()):
            cols[i % 5].warning(f"**{name}**\n目前 {count} 份\n⚠️ 差 1 人湊對")
    else:
        st.success("✅ 目前所有品項皆已成雙！享+10元優惠中")
else:
    st.info("目前還沒有人點餐")

st.divider()

# --- 7. 點餐與精確取消功能 ---
col_u, col_c = st.columns([2, 1])
with col_u:
    st.subheader("👤 第一步：誰要點餐？")
    user_opts = ["--請選擇--", "➕ 新增姓名"] + sorted(st.session_state.staff)
    sel_user = st.selectbox("選擇或新增您的姓名", user_opts)
    final_user = st.text_input("請輸入您的姓名：") if sel_user == "➕ 新增姓名" else sel_user

with col_c:
    st.subheader("⚠️ 點錯了要取消？")
    if final_user and final_user not in ["--請選擇--", "➕ 新增姓名", ""]:
        # 找出該員的所有訂單
        user_orders = [o for o in st.session_state.orders if o['姓名'] == final_user]
        if user_orders:
            # 建立可取消的選項（品項 + 時間）
            cancel_opts = [f"{o['餐點']} ({o['時間']})" for o in user_orders]
            to_cancel = st.selectbox("選擇要取消的品項", cancel_opts)
            if st.button(f"確認取消該筆"):
                # 找出索引並刪除
                idx_to_del = next(i for i, o in enumerate(st.session_state.orders) 
                                if o['姓名'] == final_user and f"{o['餐點']} ({o['時間']})" == to_cancel)
                st.session_state.orders.pop(idx_to_del)
                save_data(ORDER_FILE, st.session_state.orders)
                st.warning("訂單已取消")
                st.rerun()
        else:
            st.caption("您目前沒有點餐記錄")

# --- 8. 菜單顯示與點餐按鈕 ---
st.subheader("🍕 第二步：選擇餐點")
today_spec = special_items.get(now_tpe.day)
f_menu = [("⭐今日限定", today_spec[0], today_spec[1], today_spec[2])] if today_spec else []
f_menu += [("常規品項", m[0], m[1], m[2]) for m in regular_menu]

cols = st.columns(4)
for idx, (tag, name, price, img_file) in enumerate(f_menu):
    with cols[idx % 4]:
        st.error(tag) if "⭐" in tag else st.caption(tag)
        img_p = os.path.join("img", img_file)
        if os.path.exists(img_p):
            st.image(img_p, use_container_width=True)
        st.write(f"**{name}** | ${price}")
        if st.button(f"點選這項", key=f"btn_{idx}"):
            if final_user in ["--請選擇--", ""]:
                st.error("請提供姓名")
            else:
                if final_user not in st.session_state.staff:
                    st.session_state.staff.append(final_user)
                    save_data(STAFF_FILE, st.session_state.staff)
                st.session_state.orders.append({
                    "姓名": final_user, 
                    "餐點": name, 
                    "時間": datetime.now(tz).strftime("%H:%M:%S")
                })
                save_data(ORDER_FILE, st.session_state.orders)
                st.rerun()

# --- 9. 統計與金額計算系統 ---
st.divider()
st.subheader("📋 目前點餐名單 (每人彙整)")

if st.session_state.orders:
    df = pd.DataFrame(st.session_state.orders)
    item_counts = df['餐點'].value_counts()
    
    # 計算分攤單價
    avg_price_map = {}
    item_summary_list = []
    
    for item_name, count in item_counts.items():
        base_p = price_map.get(item_name, 0)
        if is_member_day:
            # 總價 = (成對數 * (原價+10)) + (落單數 * 原價)
            total_cost = ((count // 2) * (base_p + 10)) + ((count % 2) * base_p)
        else:
            total_cost = count * base_p
        
        avg_p = total_cost / count
        avg_price_map[item_name] = avg_p
        item_summary_list.append({
            "餐點名稱": item_name,
            "總數量": int(count),
            "原價單價": int(base_p),
            "該品項總金額": int(total_cost)
        })

    # A. 個人總名單 (一人一列)
    person_list = []
    unique_names = df['姓名'].unique()
    for p_name in sorted(unique_names):
        p_items = df[df['姓名'] == p_name]['餐點'].tolist()
        # 格式化顯示點了什麼: "炸雞 x2, 紅茶 x1"
        detail_str = ", ".join([f"{it} x{p_items.count(it)}" for it in set(p_items)])
        # 計算該員總金額 (四捨五入到整數)
        p_total = sum(avg_price_map[it] for it in p_items)
        person_list.append({
            "姓名": p_name,
            "點餐詳細": detail_str,
            "應付總金額": int(round(p_total, 0))
        })
    
    st.table(pd.DataFrame(person_list))

    # B. 品項總計
    st.subheader("📊 品項總計 (主揪核對用)")
    st.table(pd.DataFrame(item_summary_list))
    
    grand_total = sum(d['該品項總金額'] for d in item_summary_list)
    st.markdown(f"### 💰 今日訂單總金額： **${grand_total}**")

else:
    st.write("目前尚無人點餐")

st.info("💡 金額計算說明：會員日優惠 (+10元多一件) 已自動由點購相同品項的同仁平均分攤。所有金額已取整數顯示。")