import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

st.set_page_config(page_title="🏆 比赛记录查询", page_icon="🏆", layout="centered")

# ========== 数据文件 ==========
DATA_FILE = "contest_data.json"
CONFIG_FILE = "config.json"

def load_data():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return pd.DataFrame(data)
    except:
        pass
    return pd.DataFrame(columns=["ID", "Password", "Name", "Mode", "Result", "Detail", "XP", "Date"])

def save_data(df):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(df.to_dict(orient="records"), f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

def load_config():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return {"admin_password": "admin123"}

def save_config(config):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

# ========== 初始化 ==========
if "data" not in st.session_state:
    st.session_state.data = load_data()

config = load_config()
if "admin_password" not in st.session_state:
    st.session_state.admin_password = config.get("admin_password", "admin123")

if "logged_in_player" not in st.session_state:
    st.session_state.logged_in_player = None


def admin_mode():
    st.subheader("🔐 管理员控制台")
    
    with st.expander("🔑 修改管理员密码"):
        with st.form("change_admin_pwd"):
            col1, col2, col3 = st.columns(3)
            with col1:
                old_pwd = st.text_input("当前密码", type="password")
            with col2:
                new_pwd = st.text_input("新密码", type="password")
            with col3:
                confirm_pwd = st.text_input("确认新密码", type="password")
            if st.form_submit_button("修改管理员密码"):
                if old_pwd != st.session_state.admin_password:
                    st.error("❌ 当前密码错误")
                elif len(new_pwd) < 4:
                    st.error("❌ 新密码至少4位")
                elif new_pwd != confirm_pwd:
                    st.error("❌ 两次输入不一致")
                else:
                    st.session_state.admin_password = new_pwd
                    save_config({"admin_password": new_pwd})
                    st.success("✅ 管理员密码修改成功！")
                    st.rerun()
    
    st.divider()
    
    st.subheader("➕ 添加新参赛者")
    with st.form("add_player"):
        col1, col2, col3 = st.columns(3)
        with col1:
            new_id = st.text_input("编号 (ID)", placeholder="例如 A001")
        with col2:
            new_password = st.text_input("密码 (Password)", placeholder="例如 8888")
        with col3:
            new_name = st.text_input("姓名 (Name)", placeholder="例如 陈冠宇")
        if st.form_submit_button("添加参赛者"):
            if not new_id or not new_password or not new_name:
                st.error("请填写完整信息")
            elif new_id in st.session_state.data["ID"].values:
                st.error("该编号已存在，请使用不同的编号")
            else:
                new_row = pd.DataFrame([{
                    "ID": new_id.strip(),
                    "Password": new_password.strip(),
                    "Name": new_name.strip(),
                    "Mode": "",
                    "Result": "",
                    "Detail": "",
                    "XP": "",
                    "Date": ""
                }])
                st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)
                save_data(st.session_state.data)
                st.success(f"✅ 参赛者 {new_name}（编号 {new_id}）已添加！")
                st.rerun()
    
    st.divider()
    
    if st.session_state.data.empty:
        st.info("📌 还没有参赛者，请在上方添加")
        return
    
    players = st.session_state.data.drop_duplicates(subset=["ID", "Name"])
    player_options = {f"{row['ID']} - {row['Name']}": row['ID'] for _, row in players.iterrows()}
    selected_label = st.selectbox("选择参赛者", list(player_options.keys()))
    selected_id = player_options[selected_label]
    
    player_data = st.session_state.data[st.session_state.data["ID"] == selected_id]
    player_name = player_data.iloc[0]["Name"] if not player_data.empty else ""
    
    st.subheader(f"📊 {player_name} 的比赛记录")
    
    if not player_data.empty:
        valid_records = player_data[player_data["Mode"] != ""]
        if not valid_records.empty:
            sorted_records = valid_records.sort_values("Date", ascending=False)
            display_records = sorted_records.head(6)
            
            for _, row in display_records.iterrows():
                # 游戏风格卡片
                result_text = row['Result']
                if "VICTORY" in result_text.upper() or "WIN" in result_text.upper():
                    result_display = f"🟢 {result_text}"
                elif "DEFEAT" in result_text.upper() or "LOSE" in result_text.upper():
                    result_display = f"🔴 {result_text}"
                elif "CLEAR" in result_text.upper():
                    result_display = f"🟡 {result_text}"
                else:
                    result_display = f"⚪ {result_text}"
                
                xp_display = f"⬆ {row['XP']}" if row['XP'] and '↑' in str(row['XP']) else f"⬇ {row['XP']}" if row['XP'] and '↓' in str(row['XP']) else row['XP']
                
                st.markdown(f"""
                <div style="
                    background: #1e2a36;
                    border-radius: 12px;
                    padding: 14px 18px;
                    margin-bottom: 10px;
                    border-left: 4px solid #fbbf24;
                ">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                        <div>
                            <span style="color: #e8edf2; font-size: 1.0rem; font-weight: 500;">{row['Mode']}</span>
                            {f'<div style="color: #6b7f8f; font-size: 0.8rem; margin-top: 2px;">{row["Detail"]}</div>' if row['Detail'] else ''}
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 1.0rem; font-weight: 500;">{result_display}</div>
                            {f'<div style="color: #c8d0d8; font-size: 0.9rem;">{xp_display}</div>' if row['XP'] else ''}
                            {f'<div style="color: #4a5a6a; font-size: 0.7rem;">📅 {row["Date"]}</div>' if row['Date'] else ''}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            if len(valid_records) > 6:
                st.warning(f"⚠️ 该参赛者有 {len(valid_records)} 条记录，仅显示最新6条")
        else:
            st.info("暂无比赛记录")
    
    st.divider()
    st.subheader(f"➕ 为 {player_name} 添加比赛记录")
    with st.form("add_record"):
        col1, col2 = st.columns(2)
        with col1:
            new_mode = st.text_input("模式 (Mode)", placeholder="例如 对战模式")
            new_result = st.text_input("结果 (Result)", placeholder="例如 VICTORY")
            new_detail = st.text_input("详情 (Detail)", placeholder="例如 AS(99.87%)")
        with col2:
            new_xp = st.text_input("积分变化 (XP)", placeholder="例如 18733 (↑66)")
            new_date = st.date_input("日期 (Date)", value=datetime.today())
        
        if st.form_submit_button("添加记录"):
            if not new_mode:
                st.error("请输入模式")
            else:
                existing = st.session_state.data[st.session_state.data["ID"] == selected_id]
                name = existing.iloc[0]["Name"] if not existing.empty else player_name
                password = existing.iloc[0]["Password"] if not existing.empty else ""
                
                new_row = pd.DataFrame([{
                    "ID": selected_id,
                    "Password": password,
                    "Name": name,
                    "Mode": new_mode.strip(),
                    "Result": new_result.strip(),
                    "Detail": new_detail.strip(),
                    "XP": new_xp.strip(),
                    "Date": new_date.strftime("%Y/%m/%d")
                }])
                st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)
                save_data(st.session_state.data)
                st.success("✅ 记录添加成功！")
                st.rerun()
    
    st.divider()
    with st.expander("🗑️ 删除选项"):
        if st.button(f"删除参赛者 {selected_label}"):
            st.session_state.data = st.session_state.data[st.session_state.data["ID"] != selected_id]
            save_data(st.session_state.data)
            st.success(f"已删除 {selected_label}")
            st.rerun()


def player_mode():
    st.subheader("🔍 参赛者登录")
    
    if st.session_state.logged_in_player:
        player_id = st.session_state.logged_in_player
        player_data = st.session_state.data[st.session_state.data["ID"] == player_id]
        
        if player_data.empty:
            st.session_state.logged_in_player = None
            st.rerun()
        
        name = player_data.iloc[0]["Name"] if not player_data.empty else "参赛者"
        
        if st.button("🚪 退出登录"):
            st.session_state.logged_in_player = None
            st.rerun()
        
        with st.expander("🔑 修改密码"):
            with st.form("change_player_pwd"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    old_pwd = st.text_input("当前密码", type="password")
                with col2:
                    new_pwd = st.text_input("新密码", type="password")
                with col3:
                    confirm_pwd = st.text_input("确认新密码", type="password")
                if st.form_submit_button("修改密码"):
                    current_pwd = player_data.iloc[0]["Password"]
                    if old_pwd != current_pwd:
                        st.error("❌ 当前密码错误")
                    elif len(new_pwd) < 4:
                        st.error("❌ 新密码至少4位")
                    elif new_pwd != confirm_pwd:
                        st.error("❌ 两次输入不一致")
                    else:
                        idx = player_data.index[0]
                        st.session_state.data.at[idx, "Password"] = new_pwd
                        save_data(st.session_state.data)
                        st.success("✅ 密码修改成功！")
                        st.rerun()
        
        st.subheader(f"📊 {name} 的比赛记录")
        valid_records = player_data[player_data["Mode"] != ""]
        
        if valid_records.empty:
            st.info("暂无比赛记录")
        else:
            sorted_records = valid_records.sort_values("Date", ascending=False)
            for _, row in sorted_records.iterrows():
                result_text = row['Result']
                if "VICTORY" in result_text.upper() or "WIN" in result_text.upper():
                    result_display = f"🟢 {result_text}"
                elif "DEFEAT" in result_text.upper() or "LOSE" in result_text.upper():
                    result_display = f"🔴 {result_text}"
                elif "CLEAR" in result_text.upper():
                    result_display = f"🟡 {result_text}"
                else:
                    result_display = f"⚪ {result_text}"
                
                xp_display = f"⬆ {row['XP']}" if row['XP'] and '↑' in str(row['XP']) else f"⬇ {row['XP']}" if row['XP'] and '↓' in str(row['XP']) else row['XP']
                
                st.markdown(f"""
                <div style="
                    background: #1e2a36;
                    border-radius: 12px;
                    padding: 14px 18px;
                    margin-bottom: 10px;
                    border-left: 4px solid #3b82f6;
                ">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                        <div>
                            <span style="color: #e8edf2; font-size: 1.0rem; font-weight: 500;">{row['Mode']}</span>
                            {f'<div style="color: #6b7f8f; font-size: 0.8rem; margin-top: 2px;">{row["Detail"]}</div>' if row['Detail'] else ''}
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 1.0rem; font-weight: 500;">{result_display}</div>
                            {f'<div style="color: #c8d0d8; font-size: 0.9rem;">{xp_display}</div>' if row['XP'] else ''}
                            {f'<div style="color: #4a5a6a; font-size: 0.7rem;">📅 {row["Date"]}</div>' if row['Date'] else ''}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        return
    
    with st.form("login_form"):
        col1, col2 = st.columns(2)
        with col1:
            query_id = st.text_input("编号 (ID)")
        with col2:
            query_password = st.text_input("密码 (Password)", type="password")
        submitted = st.form_submit_button("🔓 登录")
    
    if submitted:
        if not query_id or not query_password:
            st.warning("请输入编号和密码")
        elif st.session_state.data.empty:
            st.warning("暂无数据")
        else:
            result = st.session_state.data[
                (st.session_state.data["ID"] == query_id.strip()) &
                (st.session_state.data["Password"] == query_password.strip())
            ]
            if result.empty:
                st.error("❌ 编号或密码错误")
            else:
                st.session_state.logged_in_player = query_id.strip()
                st.success("✅ 登录成功！")
                st.rerun()


st.title("🏆 比赛记录系统")

mode = st.radio("选择模式", ["参赛者查询", "管理员录入"], horizontal=True)

if mode == "管理员录入":
    admin_password = st.text_input("请输入管理员密码", type="password")
    if admin_password == st.session_state.admin_password:
        admin_mode()
    elif admin_password:
        st.error("密码错误")
else:
    player_mode()

st.divider()
st.caption("💾 数据已自动保存，刷新页面不会丢失")
