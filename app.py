import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone
import json
import os

# --- 1. 基本設定與時區 ---
tz = timezone(timedelta(hours=8)) 
STAFF_FILE = "staff_list.json"
ORDER_FILE = "orders_data.json"
CONFIG_FILE = "system_config.json"

st.set_page_config(page_title="台大環職部 德克士訂餐系統", layout="wide")

# --- 2. 資料處理函數 ---
def load_data(file_path, default_data):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return default_data
    return default_data

def save_data(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 初始化資料
initial_staff = ["文鴻", "舒荻", "卓憲", "序立", "述辰", "秉高", "其家", "茵婕", "品妤", "宛霖", "廷恩", "虹彣", "立涵", "喬菲", "智葳", "芸華", "立潔", "薇諠", "馥戎"]
if 'staff' not in st.session_state:
    st.session_state.staff = load_data(STAFF_FILE, initial_staff)
if 'orders' not in st.session_state:
    st.session_state.orders = load_data(ORDER_FILE, [])

# --- 3. 自動換日重置 ---
now_tpe = datetime.now(tz)
today_str = now_tpe.strftime("%Y-%m-%d")
config = load_data(CONFIG_FILE, {"last_reset_date": today_str})

if config["last_reset_date"] != today_str:
    st.session_state.orders = []
    save_data(ORDER_FILE, [])
    config["last_reset_date"] = today_str
    save_data(CONFIG_FILE, config)

# --- 4. 菜單資料與價格表 ---
# 建立一個統一的價格查詢表
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

# --- 5. 側邊欄與管理 ---
st.sidebar.title("🔐 管理後台")
pwd = st.sidebar.text_input("輸入管理密碼", type="password")
if pwd == "@ntuh121005":
    with st.sidebar.expander("👥 人員管理"):
        new_name = st.text_input("新增姓名")
        if st.button("確認新增"):
            if new_name and new_name not in st.session_state.staff:
                st.session_state.staff.append(new_name); save_data(STAFF_FILE, st.session_state.staff); st.rerun()
    if st.sidebar.button("🚨 清空點餐數據"):
        st.session_state.orders = []; save_data(ORDER_FILE, []); st.rerun()

# --- 6. 前台介面 ---
st.title("🍔 台大環職部 德克士訂餐系統")
is_member_day = now_tpe.day in [8, 18, 28]

# --- 6.1 湊對看板 ---
st.subheader("📢 湊對即時看板")
if st.session_state.orders:
    all_ordered_names = [o['餐點'] for o in st.session_state.orders]
    counts = pd.Series(all_ordered_names).value_counts()
    odd_items = counts[counts % 2 != 0]
    if not odd_items.empty:
        cols = st.columns(min(len(odd_items), 5))
        for i, (name, count) in enumerate(odd_items.items()):
            cols[i % 5].warning(f"**{name}**\n目前 {count} 份\n⚠️ 差 1 人湊對")
    else:
        st.success("✅ 目前所有品項皆已成雙！")
else: st.info("目前尚無人點餐")

st.divider()

# --- 6.2 點餐與取消 ---
col_u, col_c = st.columns([2, 1])
with col_u:
    user_opts = ["--請選擇--", "➕ 新增姓名"] + sorted(st.session_state.staff)
    sel_user = st.selectbox("👤 誰要點餐？", user_opts)
    final_user = st.text_input("請輸入您的姓名：") if sel_user == "➕ 新增姓名" else sel_user
with col_c:
    st.subheader("⚠️ 撤回")
    if final_user not in ["--請選擇--", "➕ 新增姓名", ""]:
        my_orders = [idx for idx, o in enumerate(st.session_state.orders) if o['姓名'] == final_user]
        if my_orders and st.button(f"撤回 {final_user} 的訂單"):
            st.session_state.orders.pop(my_orders[-1]); save_data(ORDER_FILE, st.session_state.orders); st.rerun()

# --- 6.3 菜單選單 ---
st.subheader("🍕 選擇餐點")
today_spec = special_items.get(now_tpe.day)
f_menu = [("⭐今日限定", today_spec[0], today_spec[1], today_spec[2])] if today_spec else []
f_menu += [("常規品項", m[0], m[1], m[2]) for m in regular_menu]

cols = st.columns(4)
for idx, (tag, name, price, img_file) in enumerate(f_menu):
    with cols[idx % 4]:
        st.error(tag) if "⭐" in tag else st.caption(tag)
        img_p = os.path.join("img", img_file)
        if os.path.exists(img_p): st.image(img_p, use_container_width=True)
        st.write(f"**{name}** | ${price}")
        if st.button(f"點選", key=f"btn_{idx}"):
            if final_user in ["--請選擇--", ""]: st.error("請提供姓名")
            else:
                if final_user not in st.session_state.staff:
                    st.session_state.staff.append(final_user); save_data(STAFF_FILE, st.session_state.staff)
                st.session_state.orders.append({"姓名": final_user, "餐點": name, "時間": datetime.now(tz).strftime("%H:%M")})
                save_data(ORDER_FILE, st.session_state.orders); st.rerun()

# --- 7. 統計與金額計算系統 ---
st.divider()
st.subheader("📋 目前點餐名單 (個人總計)")

if st.session_state.orders:
    df = pd.DataFrame(st.session_state.orders)
    item_counts = df['餐點'].value_counts()
    
    # 計算每樣餐點的「平均單價」
    avg_price_map = {}
    item_summary_data = []
    
    for item_name, count in item_counts.items():
        base_p = price_map.get(item_name, 0)
        if is_member_day:
            # 會員日邏輯: 每兩份為 (原價+10)，剩下一份原價
            total_item_cost = ((count // 2) * (base_p + 10)) + ((count % 2) * base_p)
        else:
            total_item_cost = count * base_p
        
        avg_p = total_item_cost / count
        avg_price_map[item_name] = avg_p
        item_summary_data.append({"餐點": item_name, "數量": count, "單價(原價)": base_p, "該品項總計金額": int(total_item_cost)})

    # A. 個人總名單 (一人一列)
    person_group = df.groupby("姓名")["餐點"].apply(lambda x: list(x)).reset_index()
    
    def calc_person_total(items):
        return sum(avg_price_map[it] for it in items)

    person_group["點餐詳細"] = person_group["餐點"].apply(lambda x: ", ".join([f"{i} x{x.count(i)}" for i in set(x)]))
    person_group["應付總金額"] = person_group["餐點"].apply(calc_person_total).round(1)
    
    st.table(person_group[["姓名", "點餐詳細", "應付總金額"]])

    # B. 品項總計
    st.subheader("📊 品項總計 (後台統計用)")
    st.table(pd.DataFrame(item_summary_data))
    
    total_bill = sum(d['該品項總計金額'] for d in item_summary_data)
    st.metric("今日訂單總金額", f"${total_bill}")

else: st.write("尚無資料")

st.info("💡 會員日金額說明：系統已自動將 +10 元優惠分攤給點購相同餐點的同仁。若金額有小數點，請自行協調入帳（或四捨五入）。")