cat << 'EOF' > ~/Desktop/growth_app/app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from datetime import datetime

# Injecting Custom CSS for Purple Theme Branding
st.set_page_config(page_title="Nimo Core Operations Workspace", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background-color: #fcfaff;
    }
    h1 {
        color: #5D3FD3 !important;
        font-family: 'Helvetica Neue', Arial, sans-serif;
        font-weight: 800;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f3ebff;
        border-radius: 8px 8px 0px 0px;
        padding: 10px 20px;
        color: #5D3FD3;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #5D3FD3 !important;
        color: white !important;
    }
    div[data-testid="stExpander"] {
        border: 1px solid #e1d4f7 !important;
        background-color: #ffffff !important;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🔮 Nimo Core Operations Workspace")
st.caption("✨ Designed Architecture for Deliberate Personal Growth & Life Strategy")

DB_FILE = "growth_tracker.db"
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

cursor.execute('CREATE TABLE IF NOT EXISTS goals (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, category TEXT, image_url TEXT, target_date TEXT)')
cursor.execute('CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, goal_id INTEGER, task_name TEXT, status TEXT DEFAULT "To Do", est_hours REAL, act_hours REAL, date_logged TEXT)')
cursor.execute('CREATE TABLE IF NOT EXISTS accounting_ledger (id INTEGER PRIMARY KEY AUTOINCREMENT, description TEXT, type TEXT, amount REAL, date_logged TEXT)')
conn.commit()

st.sidebar.header("📚 Add Strategic Vision Goal")
new_goal = st.sidebar.text_input("Goal Target Label")
goal_cat = st.sidebar.selectbox("Life Dimension", ["Project Sprint", "Financial Asset Growth", "Core Skills", "Personal Mastery"])
goal_img = st.sidebar.text_input("Vision Image Link", "https://unsplash.com")
goal_date = st.sidebar.date_input("Target Delivery Deadline")

if st.sidebar.button("Commit Goal to Vision Board"):
    if new_goal:
        cursor.execute("INSERT INTO goals (title, category, image_url, target_date) VALUES (?, ?, ?, ?)", (new_goal, goal_cat, goal_img, str(goal_date)))
        conn.commit()
        st.rerun()

goals_df = pd.read_sql_query("SELECT * FROM goals", conn)

st.sidebar.header("📝 Task Logistics Logger")
if not goals_df.empty:
    selected_goal = st.sidebar.selectbox("Link Action to Strategic Goal", goals_df['title'].tolist())
    goal_id_mapped = int(goals_df[goals_df['title'] == selected_goal]['id'].values)
    new_task = st.sidebar.text_input("Task Action Description")
    est_h = st.sidebar.number_input("Budgeted Allocation (Est Hours)", min_value=0.1, value=1.0)
    task_status = st.sidebar.selectbox("Initial Sprint Status", ["To Do", "In Progress", "Completed"])
    
    if st.sidebar.button("Log Action Item"):
        if new_task:
            cursor.execute("INSERT INTO tasks (goal_id, task_name, status, est_hours, act_hours, date_logged) VALUES (?, ?, ?, ?, 0.0, ?)", (goal_id_mapped, new_task, task_status, est_h, datetime.today().strftime('%Y-%m-%d')))
            conn.commit()
            st.rerun()
else:
    st.sidebar.info("Initialize at least one vision goal target to activate task infrastructure.")

tab1, tab2, tab3, tab4 = st.tabs(["📖 Dashboard & Vision Board", "🗂️ Task & Project Sprints", "📈 Growth Analytics & Metrics", "🔮 Personal Accounting Ledger"])

with tab1:
    st.subheader("Executive Vision Board & OKR Mapping")
    if goals_df.empty: 
        st.info("System is currently blank. Use the left dashboard controls to populate your vision architecture.")
    else:
        cols = st.columns(3)
        for index, row in goals_df.iterrows():
            with cols[index % 3]:
                st.image(row['image_url'], use_container_width=True)
                st.markdown(f"### **{row['title']}**")
                st.markdown(f"🧬 **Dimension:** {row['category']} | 📅 **Target:** {row['target_date']}")
                
                t_df = pd.read_sql_query(f"SELECT status FROM tasks WHERE goal_id = {row['id']}", conn)
                if not t_df.empty:
                    done = len(t_df[t_df['status'] == 'Completed'])
                    total = len(t_df)
                    progress = done / total
                    st.progress(progress, text=f"Execution Progress: {int(progress*100)}%")
                else:
                    st.progress(0.0, text="Execution Progress: 0% (No baseline tasks linked)")

with tab2:
    st.subheader("Project Execution Workspace (Agile Kanban System)")
    tasks_df = pd.read_sql_query("SELECT t.id, t.task_name, t.status, t.est_hours, t.act_hours, g.title as goal_title FROM tasks t LEFT JOIN goals g ON t.goal_id = g.id", conn)
    
    if tasks_df.empty: 
        st.info("No active operations planned inside your project sprints.")
    else:
        k_todo, k_progress, k_done = st.columns(3)
        with k_todo:
            st.markdown("### 🟣 To Do Pipeline")
            for _, t in tasks_df[tasks_df['status'] == 'To Do'].iterrows():
                with st.expander(f"📌 {t['task_name']}"):
                    st.caption(f"Parent Goal: {t['goal_title']} | Budgeted: {t['est_hours']}h")
                    if st.button("Deploy into Action ➔", key=f"s_{t['id']}"):
                        cursor.execute("UPDATE tasks SET status = 'In Progress' WHERE id = ?", (t['id'],))
                        conn.commit()
                        st.rerun()
        with k_progress:
            st.markdown("### 🔵 Active In Progress")
            for _, t in tasks_df[tasks_df['status'] == 'In Progress'].iterrows():
                with st.expander(f"⚡ {t['task_name']}"):
                    st.caption(f"Parent Goal: {t['goal_title']}")
                    actual_input = st.number_input("Log execution hours spent:", min_value=0.0, value=t['act_hours'], key=f"h_{t['id']}")
                    if st.button("Verify Completion ✔️", key=f"c_{t['id']}"):
                        cursor.execute("UPDATE tasks SET status = 'Completed', act_hours = ? WHERE id = ?", (actual_input, t['id']))
                        conn.commit()
                        st.rerun()
        with k_done:
            st.markdown("### 🍇 Finalized Logs")
            for _, t in tasks_df[tasks_df['status'] == 'Completed'].iterrows():
                st.success(f"🎉 **{t['task_name']}** \n\n Used: {t['act_hours']}h (Plan: {t['est_hours']}h)")

with tab3:
    st.subheader("Growth Overview & SQL Performance Metrics")
    tasks_analytics_df = pd.read_sql_query("SELECT * FROM tasks", conn)
    
    if tasks_analytics_df.empty: 
        st.info("Performance charts will dynamically render as soon as sprint logs capture data inputs.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            comp = tasks_analytics_df[tasks_analytics_df['status'] == 'Completed']
            if not comp.empty:
                fig_bar = px.bar(comp, x='task_name', y=['est_hours', 'act_hours'], barmode='group', 
                                 title="Task Allocation Precision (Budgeted vs. Actual)",
                                 labels={'value': 'Total Hours Spent', 'variable': 'Time Metric'},
                                 color_discrete_sequence=['#A388EE', '#5D3FD3'])
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.warning("Complete active items on your Kanban board to view time allocation charts.")
        with c2:
            fig_pie = px.pie(tasks_analytics_df, names='status', hole=0.4, 
                             title="Overall Task Lifecycle Distribution",
                             color_discrete_sequence=['#5D3FD3', '#A388EE', '#E8DFFF'])
            st.plotly_chart(fig_pie, use_container_width=True)

with tab4:
    st.subheader("Financial Assets Ledger & Resource Management")
    c_led1, c_led2 = st.columns(2)
    
    with c_led1:
        st.markdown("#### Log Asset Flow")
        tx_desc = st.text_input("Asset Entry Description")
        tx_type = st.selectbox("Flow Category", ["Capital Inflow (Revenue)", "Capital Outflow (Investment/Expense)"])
        tx_amt = st.number_input("Amount ($)", min_value=0.01, value=10.0)
        
        if st.button("Commit Ledger Entry"):
            if tx_desc:
                cursor.execute("INSERT INTO accounting_ledger (description, type, amount, date_logged) VALUES (?, ?, ?, ?)",
                               (tx_desc, tx_type, tx_amt, datetime.today().strftime('%Y-%m-%d')))
                conn.commit()
                st.rerun()
                
    with c_led2:
        st.markdown("#### Live Financial Balances")
        ledger_df = pd.read_sql_query("SELECT * FROM accounting_ledger", conn)
        if ledger_df.empty:
            st.info("No ledger entries captured yet.")
        else:
            inflow = ledger_df[ledger_df['type'] == "Capital Inflow (Revenue)"]['amount'].sum()
            outflow = ledger_df[ledger_df['type'] == "Capital Outflow (Investment/Expense)"]['amount'].sum()
            net_position = inflow - outflow
            
            st.metric(label="Net Strategic Capital Position", value=f"${net_position:,.2f}", delta=f"${inflow:,.2f} Gross Inflow")
            st.dataframe(ledger_df[['date_logged', 'description', 'type', 'amount']], use_container_width=True)

conn.close()
EOF
