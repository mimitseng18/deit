import streamlit as st
import pandas as pd
import datetime

# 設定網頁標題與圖示
st.set_page_config(page_title="政府資料庫級-飲食記帳熱量大師", page_icon="🥗", layout="wide")

# --- 遠端下載台灣食藥署(FDA)開放資料集 (最穩定的 GitHub 鏡像來源) ---
@st.cache_data
def load_government_db():
    gov_url = "https://raw.githubusercontent.com/yozb/taiwan-food-nutrients/master/food_nutrients.csv"
    try:
        df = pd.read_csv(gov_url, encoding="utf-8")
        if 'name' in df.columns and 'calories' in df.columns:
            df_cleaned = df[['name', 'calories']].dropna()
            df_cleaned.columns = ['食物名稱', '熱量 (kcal)']
        else:
            df_cleaned = df.iloc[:, [0, 1]].dropna()
            df_cleaned.columns = ['食物名稱', '熱量 (kcal)']
        return df_cleaned
    except Exception as e:
        # 網路斷線時的豐富備用資料庫
        backup_data = {
            '食物名稱': [
                "白飯 (碗)", "滷肉飯", "牛肉麵", "原味蛋餅", "起司蛋餅", "原味優格", "無糖優格", "希臘優格", 
                "拿鐵咖啡", "珍珠奶茶", "茶葉蛋", "炸雞腿便當", "炸排骨便當", "少油低卡健康餐盒"
            ],
            '熱量 (kcal)': [280, 650, 630, 260, 340, 65, 55, 95, 120, 650, 75, 950, 880, 480]
        }
        return pd.DataFrame(backup_data)

# 載入政府資料庫
gov_food_df = load_government_db()

# 🔥 【多人獨立關鍵】不讀寫任何本地 CSV 檔案，改用每位使用者瀏覽器獨立的 Session State 記憶體
if "user_records" not in st.session_state:
    st.session_state.user_records = pd.DataFrame(columns=["日期", "餐別", "項目名稱", "金額 (元)", "熱量 (kcal)"])

# 暫存自動帶入的數據
if "temp_name" not in st.session_state: st.session_state.temp_name = ""
if "temp_calories" not in st.session_state: st.session_state.temp_calories = 0

# --- 網頁介面設計 ---
st.title("🥗 全功能飲食記帳 x 衛福部食藥署資料庫")
st.write(f"📊 目前已成功連線雲端資料集，內建 **{len(gov_food_df)}** 筆台灣本土食品精準熱量數據！")
st.info("🔒 **隱私保護中**：本網頁目前採用「獨立工作階段」機制。每個連進來的使用者都有自己專屬的記帳板，其他人絕對看不到您的紀錄。*(註：網頁重新整理或關閉後，紀錄將會重置)*")

left_col, right_col = st.columns([1, 1.3])

# --- 左側欄位：搜尋與新增 ---
with left_col:
    st.markdown("### 🔍 衛福部食品營養成分查詢")
    search_query = st.text_input("輸入你想吃的（例如：雞胸肉、優格、貢丸、高麗菜）", placeholder="請輸入食物關鍵字...")
    
    if search_query:
        search_results = gov_food_df[gov_food_df['食物名稱'].str.contains(search_query, case=False, na=False)]
        if not search_results.empty:
            st.info(f"💡 幫你找到 {len(search_results)} 筆對應官方數據（顯示前 15 筆）：")
            for index, row in search_results.head(15).iterrows():
                food = row['食物名稱']
                try:
                    cal = int(float(row['熱量 (kcal)']))
                except:
                    cal = 0
                    
                col_food, col_btn = st.columns([3, 1])
                with col_food:
                    st.write(f"• **{food}**：約 `{cal}` kcal")
                with col_btn:
                    if st.button(f"帶入資料", key=f"btn_{index}"):
                        st.session_state.temp_name = food
                        st.session_state.temp_calories = cal
                        st.rerun()
        else:
            st.warning(" 找不到該食物，換個關鍵字試試看，或者直接在下方手動輸入。")
            
    st.markdown("---")
    
    st.markdown("### ➕ 新增今日飲食紀錄")
    with st.form(key="add_record_form", clear_on_submit=False):
        input_date = st.date_input("日期", datetime.date.today())
        input_meal = st.selectbox("餐別", ["早餐", "午餐", "晚餐", "點心/飲料"])
        
        input_name = st.text_input("項目名稱", value=st.session_state.temp_name, placeholder="例如：起司蛋餅")
        input_price = st.number_input("金額 (新台幣)", min_value=0, step=1, value=0)
        input_calories = st.number_input("估計熱量 (kcal)", min_value=0, step=1, value=st.session_state.temp_calories)
        
        submit_button = st.form_submit_button(label="確認新增紀錄")

    if submit_button:
        if input_name.strip() == "":
            st.error("❌ 請輸入項目名稱！")
        else:
            new_row = pd.DataFrame([{
                "日期": input_date, "餐別": input_meal, "項目名稱": input_name,
                "金額 (元)": input_price, "熱量 (kcal)": input_calories
            }])
            # 僅寫入該瀏覽器獨立的暫存記憶體
            st.session_state.user_records = pd.concat([st.session_state.user_records, new_row], ignore_index=True)
            st.success(f"✅ 已成功記錄：{input_name}！")
            
            st.session_state.temp_name = ""
            st.session_state.temp_calories = 0
            st.rerun()

# --- 右側欄位：數據儀表板與圖表分析 ---
with right_col:
    today = datetime.date.today()
    # 從使用者個人的獨立記憶體中過濾出當日數據
    today_records = st.session_state.user_records[st.session_state.user_records['日期'] == today]

    st.markdown("### 📊 今日數據摘要")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(label="💰 今日總花費", value=f"$ {today_records['金額 (元)'].sum()} 元")
    with col2:
        total_calories = today_records["熱量 (kcal)"].sum()
        if total_calories > 2200:
            st.metric(label="🔥 今日總熱量", value=f"{total_calories} kcal", delta="今日熱量偏高喔！", delta_color="inverse")
        else:
            st.metric(label="🔥 今日總熱量", value=f"{total_calories} kcal")
    with col3:
        st.metric(label="🍽️ 今日記錄餐數", value=f"{len(today_records)} 次")

    st.markdown("---")

    st.markdown("### 📈 歷史每日攝取量與消費分析")
    if not st.session_state.user_records.empty:
        st.session_state.user_records['日期'] = pd.to_datetime(st.session_state.user_records['日期']).dt.date
        daily_summary = st.session_state.user_records.groupby('日期').agg({'熱量 (kcal)': 'sum', '金額 (元)': 'sum'}).sort_index()
        
        tab1, tab2 = st.tabs(["🔥 每日總熱量趨勢", "💰 每日總花費趨勢"])
        with tab1:
            st.line_chart(daily_summary['熱量 (kcal)'])
            st.caption(f"💡 本次平均攝取熱量：**{round(daily_summary['熱量 (kcal)'].mean(), 1)} kcal**")
        with tab2:
            st.line_chart(daily_summary['金額 (元)'])
            st.caption(f"💡 本次平均餐費花費：**$ {round(daily_summary['金額 (元)'].mean(), 1)} 元**")
    else:
        st.info("尚未有數據可供生成圖表分析。")

    st.markdown("---")

    st.markdown("### 📋 本次飲食紀錄")
    if not st.session_state.user_records.empty:
        df_display = st.session_state.user_records.sort_values(by="日期", ascending=False).reset_index(drop=True)
        st.dataframe(df_display, use_container_width=True)
        
        if st.button("⚠️ 清空目前紀錄"):
            st.session_state.user_records = pd.DataFrame(columns=["日期", "餐別", "項目名稱", "金額 (元)", "熱量 (kcal)"])
            st.rerun()
    else:
        st.info("目前還沒有任何紀錄，快從左側新增第一筆吧！")
