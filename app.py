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

# ---------------- DATABASE ----------------
conn = sqlite3.connect("nivasisahay.db", check_same_thread=False)
c = conn.cursor()

# Create table safely (NO DROP)
c.execute("""
CREATE TABLE IF NOT EXISTS complaints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_no TEXT,
    area TEXT,
    issue_type TEXT,
    description TEXT,
    phone TEXT,
    image BLOB,
    date_reported TEXT,
    status TEXT
)
""")
conn.commit()

# ---------------- UI ----------------
st.title("🏘️ NivasiSahay")
st.caption("Community Civic Issue Registration System")

menu = st.sidebar.radio(
    "Menu",
    ["Register Complaint", "View Complaints"]
)

# ---------------- REGISTER COMPLAINT ----------------
if menu == "Register Complaint":
    st.subheader("📌 Register Your Problem")

    area = st.text_input("Area / Locality")
    issue_type = st.selectbox(
        "Type of Problem",
        ["Water Supply", "Garbage", "Streetlight", "Drainage", "Road Damage"]
    )
    description = st.text_area("Describe the problem clearly")
    uploaded_image = st.file_uploader(
        "Upload Image (Proof of problem)",
        type=["jpg", "jpeg", "png"]
    )
    phone = st.text_input("Mobile Number")

    if st.button("Submit Complaint"):
        if not (area and description and phone and uploaded_image):
            st.warning("⚠️ Please fill all fields and upload an image.")
        else:
            complaint_no = f"NS-{uuid.uuid4().hex[:8].upper()}"
            image_bytes = uploaded_image.getvalue()

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
            st.info(f"🧾 Your Complaint Number: **{complaint_no}**")

# ---------------- VIEW COMPLAINTS ----------------
elif menu == "View Complaints":
    st.subheader("📂 Registered Complaints")

    df = pd.read_sql_query(
        "SELECT * FROM complaints ORDER BY id DESC",
        conn
    )

    if df.empty:
        st.info("No complaints registered yet.")
    else:
        for _, row in df.iterrows():
            st.markdown(f"### 🧾 Complaint No: {row['complaint_no']}")
            st.write(f"📍 **Area:** {row['area']}")
            st.write(f"🛠️ **Issue Type:** {row['issue_type']}")
            st.write(f"📝 **Description:** {row['description']}")
            st.write(f"📅 **Date:** {row['date_reported']}")
            st.write(f"📞 **Phone:** {row['phone']}")
            st.write(f"📌 **Status:** {row['status']}")

            if row["image"] is not None:
                st.image(
                    BytesIO(row["image"]),
                    caption="Uploaded Image",
                    width=350
                )

            st.divider()
