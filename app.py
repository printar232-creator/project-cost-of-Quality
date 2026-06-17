import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ตั้งค่าหน้าเว็บหน้าจอ
st.set_page_config(
    page_title="Quality Cost Analyzer (COQ)",
    page_icon="📊",
    layout="wide"
)

# หัวข้อหลักอ้างอิงจากงานวิจัยกรณีศึกษา
st.title("📊 ระบบกรอกข้อมูลและวิเคราะห์ต้นทุนคุณภาพ (Cost of Quality: COQ)")
st.subheader("กรณีศึกษา: อ้างอิงโครงสร้างการวิเคราะห์อุตสาหกรรมผู้ผลิต")

# สร้าง Session State สำหรับเก็บข้อมูลหากไม่มีการบันทึกมาก่อน (เริ่มต้นด้วยข้อมูลจำลอง 4 สัปดาห์แรก)
if 'coq_data' not in st.session_state:
    st.session_state.coq_data = pd.DataFrame([
        {"สัปดาห์": "Week 1", "Prevention (บาท)": 15000, "Appraisal (บาท)": 25000, "Internal Failure (บาท)": 85000, "External Failure (บาท)": 12000},
        {"สัปดาห์": "Week 2", "Prevention (บาท)": 15000, "Appraisal (บาท)": 26000, "Internal Failure (บาท)": 78000, "External Failure (บาท)": 9000},
        {"สัปดาห์": "Week 3", "Prevention (บาท)": 18000, "Appraisal (บาท)": 30000, "Internal Failure (บาท)": 62000, "External Failure (บาท)": 5000},
        {"สัปดาห์": "Week 4", "Prevention (บาท)": 20000, "Appraisal (บาท)": 32000, "Internal Failure (บาท)": 45000, "External Failure (บาท)": 2000},
    ])

# แบ่งส่วนหน้าจอด้วย Tabs
tab1, tab2, tab3 = st.tabs(["📥 กรอกและจัดการข้อมูล", "📈 กราฟวิเคราะห์และแนวโน้ม", "📋 ตารางสรุปภาพรวม"])

# --- TAB 1: การกรอกข้อมูล ---
with tab1:
    st.header("เพิ่มข้อมูลต้นทุนคุณภาพรายสัปดาห์")
    
    col1, col2 = st.columns(2)
    with col1:
        week_input = st.text_input("ระบุสัปดาห์ (เช่น Week 5 หรือประจำวันที่):", f"Week {len(st.session_state.coq_data)+1}")
        p_cost = st.number_input("1. ต้นทุนการป้องกัน (Prevention Cost): เช่น ค่าเทรนนิ่ง, ปรับปรุงเครื่องจักร", min_value=0, value=10000, step=1000)
        a_cost = st.number_input("2. ต้นทุนการตรวจสอบ (Appraisal Cost): เช่น ค่าแรง QC, ค่าทดสอบแล็บ", min_value=0, value=20000, step=1000)
    
    with col2:
        i_cost = st.number_input("3. ต้นทุนความบกพร่องภายใน (Internal Failure): เช่น งานเสียหลอมใหม่ (Scrap), งานแก้ (Rework)", min_value=0, value=50000, step=1000)
        e_cost = st.number_input("4. ต้นทุนความบกพร่องภายนอก (External Failure): เช่น ของตีกลับจากลูกค้า, ค่าชดเชย", min_value=0, value=0, step=1000)
        
        st.write("##")
        if st.button("➕ บันทึกข้อมูลลงฐานข้อมูล", use_container_width=True):
            new_row = {
                "สัปดาห์": week_input,
                "Prevention (บาท)": p_cost,
                "Appraisal (บาท)": a_cost,
                "Internal Failure (บาท)": i_cost,
                "External Failure (บาท)": e_cost
            }
            # เพิ่มแถวข้อมูลใหม่เข้าไปใน Session State
            st.session_state.coq_data = pd.concat([st.session_state.coq_data, pd.DataFrame([new_row])], ignore_index=True)
            st.success(f"บันทึกข้อมูลของ {week_input} เรียบร้อยแล้ว!")
            st.rerun()

    st.write("---")
    st.subheader("ลบหรือรีเซ็ตข้อมูล")
    if st.button("🗑️ ลบข้อมูลสัปดาห์ล่าสุด", type="secondary"):
        if len(st.session_state.coq_data) > 0:
            st.session_state.coq_data = st.session_state.coq_data.drop(st.session_state.coq_data.index[-1])
            st.warning("ลบแถวข้อมูลล่าสุดเรียบร้อยแล้ว")
            st.rerun()

# ทำการคำนวณผลรวมเพื่อส่งไปใช้ใน Tab วิเคราะห์ผล
df = st.session_state.coq_data.copy()
if not df.empty:
    df["ต้นทุนรวม (บาท)"] = df["Prevention (บาท)"] + df["Appraisal (บาท)"] + df["Internal Failure (บาท)"] + df["External Failure (บาท)"]
    
    # คำนวณยอดรวมสุทธิสะสมทั้งหมด
    total_p = df["Prevention (บาท)"].sum()
    total_a = df["Appraisal (บาท)"].sum()
    total_i = df["Internal Failure (บาท)"].sum()
    total_e = df["External Failure (บาท)"].sum()
    grand_total = df["ต้นทุนรวม (บาท)"].sum()

# --- TAB 2: กราฟวิเคราะห์และแนวโน้ม ---
with tab2:
    if df.empty:
        st.info("กรุณากรอกข้อมูลใน Tab แรกก่อนเพื่อแสดงผลกราฟวิเคราะห์")
    else:
        st.header("📈 ผลการวิเคราะห์ต้นทุนคุณภาพเชิงลึก")
        
        # แสดง KPI Cards ด้านบน
        kpi1, kpi2, kpi3 = st.columns(3)
        with kpi1:
            st.metric("ต้นทุนคุณภาพรวมทั้งหมด (สะสม)", f"{grand_total:,.2f} บาท")
        with kpi2:
            max_fail_week = df.loc[df["Internal Failure (บาท)"].idxmax()]["สัปดาห์"]
            st.metric("สัปดาห์ที่เกิด Internal Failure สูงสุด", max_fail_week)
        with kpi3:
            # คำนวณสัดส่วนต้นทุนความเสียหาย (Internal + External) ต่อต้นทุนทั้งหมด
            fail_rate = ((total_i + total_e) / grand_total) * 100 if grand_total > 0 else 0
            st.metric("สัดส่วนความเสียหาย (Failure Rate)", f"{fail_rate:.1f}%")

        st.write("---")
        
        # กราฟที่ 1: กราฟแท่งซ้อนเปรียบเทียบแนวโน้มสะสม (Stacked Bar Chart)
        st.subheader("1. แนวโน้มและโครงสร้างต้นทุนคุณภาพจำแนกรายสัปดาห์")
        fig_bar = px.bar(
            df, 
            x="สัปดาห์", 
            y=["Prevention (บาท)", "Appraisal (บาท)", "Internal Failure (บาท)", "External Failure (บาท)"],
            title="การกระจายตัวของต้นทุนแต่ละประเภทในแต่ละช่วงเวลา",
            labels={"value": "จำนวนเงิน (บาท)", "variable": "ประเภทต้นทุนคุณภาพ"},
            barmode="stack"
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        
        col_graph1, col_graph2 = st.columns(2)
        
        # กราฟที่ 2: กราฟวงกลมแสดงสัดส่วนภาพรวม (Pie Chart)
        with col_graph1:
            st.subheader("2. สัดส่วนต้นทุนคุณภาพรวมสะสม")
            labels = ["Prevention Cost", "Appraisal Cost", "Internal Failure Cost", "External Failure Cost"]
            values = [total_p, total_a, total_i, total_e]
            fig_pie = px.pie(
                names=labels, 
                values=values, 
                title="สัดส่วนเปอร์เซ็นต์สะสมของ COQ ทั้งหมด",
                color_discrete_sequence=px.colors.sequential.RdBu
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            
        # กราฟที่ 3: กราฟเส้นเปรียบเทียบความสัมพันธ์ (Line Chart)
        with col_graph2:
            st.subheader("3. การวิเคราะห์ Trade-off ตามหลักทฤษฎีคุณภาพ")
            # แสดงความสัมพันธ์เมื่อลงทุนกับ Prevention/Appraisal สูงขึ้น จะช่วยลด Internal/External Failure ลง
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(x=df["สัปดาห์"], y=df["Prevention (บาท)"]+df["Appraisal (บาท)"], name="ต้นทุนการควบคุม (Prevention + Appraisal)", mode='lines+markers', line=dict(color='green', width=3)))
            fig_line.add_trace(go.Scatter(x=df["สัปดาห์"], y=df["Internal Failure (บาท)"]+df["External Failure (บาท)"], name="ต้นทุนความเสียหาย (Internal + External)", mode='lines+markers', line=dict(color='red', width=3)))
            fig_line.update_layout(title="ความสัมพันธ์ระหว่างต้นทุนการควบคุมและการเกิดของเสียในกระบวนการ", xaxis_title="สัปดาห์", yaxis_title="บาท")
            st.plotly_chart(fig_line, use_container_width=True)

        # บทวิเคราะห์และข้อแนะนำอัตโนมัติตามข้อมูล
        st.subheader("💡 ข้อเสนอแนะเชิงบริหาร (Executive Insights)")
        if total_i > (grand_total * 0.5):
            st.info(
                "**วิเคราะห์ผลตามหลักการศึกษา:** ปัจจุบันต้นทุนหลักของคุณยังคงเป็น **ต้นทุนความบกพร่องภายใน (Internal Failure)** "
                "เช่นเดียวกับระยะแรกของงานวิจัยโรงงานกรณีศึกษา แนะนำให้เพิ่มงบประมาณในส่วนของการป้องกัน (Prevention) "
                "และการตรวจสอบหน้างาน (Appraisal) เพื่อสกัดกั้นไม่ให้เกิดงานเสียกลางกระบวนการผลิต ซึ่งจะส่งผลให้ต้นทุนรวมลดลงในระยะยาว"
            )
        else:
            st.success(
                "**วิเคราะห์ผลตามหลักการศึกษา:** โครงสร้างต้นทุนคุณภาพอยู่ในทิศทางที่ดีขึ้น ต้นทุนความเสียหายภายในมีสัดส่วนต่ำกว่า 50% "
                "แสดงถึงประสิทธิภาพของการวางระบบป้องกันและการตรวจสอบที่เริ่มเห็นผลลัพธ์ชัดเจน"
            )

# --- TAB 3: ตารางสรุปภาพรวม ---
with tab3:
    if df.empty:
        st.info("ไม่มีข้อมูลให้แสดงผล")
    else:
        st.header("📋 ตารางข้อมูลและสัดส่วนโครงสร้างต้นทุน")
        
        # คำนวณ % สัดส่วนแยกแถว
        df_display = df.copy()
        for col in ["Prevention (บาท)", "Appraisal (บาท)", "Internal Failure (บาท)", "External Failure (บาท)"]:
            df_display[col.replace(" (บาท)", " (%)")] = (df_display[col] / df_display["ต้นทุนรวม (บาท)"]) * 100
            
        # จัดรูปแบบตัวเลขให้อ่านง่าย
        st.dataframe(
            df_display.style.format({
                "Prevention (บาท)": "{:,.0f}",
                "Appraisal (บาท)": "{:,.0f}",
                "Internal Failure (บาท)": "{:,.0f}",
                "External Failure (บาท)": "{:,.0f}",
                "ต้นทุนรวม (บาท)": "{:,.0f}",
                "Prevention (%)": "{:.1f}%",
                "Appraisal (%)": "{:.1f}%",
                "Internal Failure (%)": "{:.1f}%",
                "External Failure (%)": "{:.1f}%",
            }),
            use_container_width=True
        )
        
        # ปุ่มสำหรับให้ User ดาวน์โหลดข้อมูลออกไปเป็น CSV เพื่อใช้ใน Excel ได้
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 ดาวน์โหลดข้อมูลสรุปเป็นไฟล์ CSV (สำหรับ Excel)",
            data=csv,
            file_name='coq_quality_cost_summary.csv',
            mime='text/csv',
        )
