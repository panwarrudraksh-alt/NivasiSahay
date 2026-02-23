import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
import uuid
from io import BytesIO

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="NivasiSahay",
    page_icon="🏘️",
    layout="centered"
)

# ---------------- DATABASE CONNECTION ----------------
conn = sqlite3.connect("nivasisahay.db", check_same_thread=False)
c = conn.cursor()

# ---------------- SAFE TABLE CREATION ----------------
c.execute("""
CREATE TABLE IF NOT EXISTS complaints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_no TEXT,
    area TEXT,
    issue_type TEXT,
    description TEXT,
    phone TEXT,
    date_reported TEXT,
    status TEXT
)
""")
conn.commit()

# ---------------- SAFE SCHEMA MIGRATION ----------------
c.execute("PRAGMA table_info(complaints)")
existing_columns = [col[1] for col in c.fetchall()]

if "image" not in existing_columns:
    try:
        c.execute("ALTER TABLE complaints ADD COLUMN image BLOB")
        conn.commit()
    except Exception:
        pass  # Absolute safety: app must never crash here

# ---------------- UI HEADER ----------------
st.title("🏘️ NivasiSahay")
st.caption("Community Civic Issue Registration System")

menu = st.sidebar.radio(
    "Menu",
    ["Register Complaint", "View Complaints"]
)

# ================= REGISTER COMPLAINT =================
if menu == "Register Complaint":
    st.subheader("📌 Register Your Problem")

    area = st.text_input("Area / Locality")
    issue_type = st.selectbox(
        "Type of Problem",
        ["Water Supply", "Garbage", "Streetlight", "Drainage", "Road Damage"]
    )
    description = st.text_area("Describe the problem clearly")
    uploaded_image = st.file_uploader(
        "Upload Image (Optional)",
        type=["jpg", "jpeg", "png"]
    )
    phone = st.text_input("Mobile Number")

    if st.button("Submit Complaint"):
        if not area or not description or not phone:
            st.warning("⚠️ Please fill all required fields.")
        else:
            complaint_no = f"NS-{uuid.uuid4().hex[:8].upper()}"

            image_bytes = None
            if uploaded_image is not None:
                try:
                    image_bytes = uploaded_image.getvalue()
                except Exception:
                    image_bytes = None

            try:
                c.execute("""
                    INSERT INTO complaints
                    (complaint_no, area, issue_type, description, phone, image, date_reported, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    complaint_no,
                    area,
                    issue_type,
                    description,
                    phone,
                    image_bytes,
                    str(date.today()),
                    "Registered"
                ))
                conn.commit()

                st.success("✅ Problem registered successfully!")
                st.info(f"🧾 Complaint Number: **{complaint_no}**")

            except Exception:
                st.error("Something went wrong while saving. Please try again.")

# ================= VIEW COMPLAINTS =================
elif menu == "View Complaints":
    st.subheader("📂 Registered Complaints")

    try:
        df = pd.read_sql_query(
            "SELECT * FROM complaints ORDER BY id DESC",
            conn
        )
    except Exception:
        df = pd.DataFrame()

    if df.empty:
        st.info("No complaints registered yet.")
    else:
        for _, row in df.iterrows():
            st.markdown(f"### 🧾 Complaint No: {row.get('complaint_no', 'N/A')}")
            st.write(f"📍 **Area:** {row.get('area', 'N/A')}")
            st.write(f"🛠️ **Issue Type:** {row.get('issue_type', 'N/A')}")
            st.write(f"📝 **Description:** {row.get('description', 'N/A')}")
            st.write(f"📅 **Date:** {row.get('date_reported', 'N/A')}")
            st.write(f"📞 **Phone:** {row.get('phone', 'N/A')}")
            st.write(f"📌 **Status:** {row.get('status', 'N/A')}")

            image_data = row.get("image", None)
            if image_data:
                try:
                    st.image(
                        BytesIO(image_data),
                        caption="Uploaded Image",
                        width=350
                    )
                except Exception:
                    st.warning("Image could not be displayed.")

            st.divider()
