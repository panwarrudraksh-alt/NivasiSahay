import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
from PIL import Image
import os
import uuid

# ---------- CONFIG ----------
st.set_page_config(page_title="NivasiSahay", layout="centered")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------- DATABASE ----------
conn = sqlite3.connect("nivasisahay.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS complaints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_no TEXT,
    area TEXT,
    issue_type TEXT,
    description TEXT,
    phone TEXT,
    image_path TEXT,
    date_reported TEXT,
    status TEXT
)
""")
conn.commit()

# ---------- UI ----------
st.title("🏘️ NivasiSahay")
st.caption("Register Civic Issues with Proof")

menu = st.sidebar.radio("Menu", ["Register Complaint", "View Complaints"])

# ---------- REGISTER COMPLAINT ----------
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
            st.warning("Please fill all fields and upload an image")
        else:
            # Generate complaint number
            complaint_no = f"NS-{uuid.uuid4().hex[:8].upper()}"

            # Save image
            image_path = os.path.join(UPLOAD_FOLDER, f"{complaint_no}.png")
            image = Image.open(uploaded_image)
            image.save(image_path)

            # Insert into DB
            c.execute("""
                INSERT INTO complaints
                (complaint_no, area, issue_type, description, phone, image_path, date_reported, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                complaint_no,
                area,
                issue_type,
                description,
                phone,
                image_path,
                str(date.today()),
                "Registered"
            ))
            conn.commit()

            st.success("✅ Problem registered successfully!")
            st.info(f"🧾 Your Complaint Number: **{complaint_no}**")
            st.caption("Please save this number for future reference.")

# ---------- VIEW COMPLAINTS ----------
elif menu == "View Complaints":
    st.subheader("📂 Registered Complaints")

    df = pd.read_sql_query("SELECT * FROM complaints", conn)

    if df.empty:
        st.info("No complaints registered yet")
    else:
        df_display = df[[
            "complaint_no", "area", "issue_type", "date_reported", "status"
        ]]
        st.dataframe(df_display)