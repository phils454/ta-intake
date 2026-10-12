import streamlit as st
from docxtpl import DocxTemplate
import pandas as pd
import os
import io
import zipfile
import smtplib
from email.message import EmailMessage
import json

# --- HIDDEN FIRM CREDENTIALS ---
GMAIL_APP_PASSWORD = "vanw lgrb uojp nbrm"

# Define the templates folder location
TEMPLATES_DIR = "templates"
if not os.path.exists(TEMPLATES_DIR):
    os.makedirs(TEMPLATES_DIR)

# Find all templates
template_files = []
for directory in [TEMPLATES_DIR, "."]:
    if os.path.exists(directory):
        for filename in os.listdir(directory):
            if filename.endswith(".docx") and not filename.startswith("~$"):
                filepath = os.path.join(directory, filename)
                if filepath not in template_files:
                    template_files.append(filepath)

st.set_page_config(page_title="Trust Admin Automator", layout="wide")

# --- INITIALIZE SESSION STATE ---
# This ensures all fields have a default value so saving/loading works smoothly
default_keys = {
    "decedent_name": "", "date_of_death": "", "ssn": "",
    "trust_name": "", "settlor_name": "", "trust_date": "", "will_date": "",
    "attorney_name": "", "law_firm_name": "BarthCalderon LLP",
    "trustee_name": "", "trustee_address": "", "trustee_phone": "",
    "beneficiaries_data": [
        {"Name": "", "Address": "", "Phone": "", "Relationship": "", "SSN": "", "DOB": ""}
    ]
}
for k, v in default_keys.items():
    if k not in st.session_state:
        st.session_state[k] = v

# --- SIDEBAR: SAVE & LOAD PROGRESS ---
with st.sidebar:
    st.header("💾 Save & Load Progress")
    st.markdown("Use these tools to save a client's incomplete form to your computer, or load a previously saved file.")
    
    # 1. Load Data
    uploaded_file = st.file_uploader("📂 Load Saved Client Data", type=["json"])
    if uploaded_file is not None:
        try:
            saved_data = json.load(uploaded_file)
            for k, v in saved_data.items():
                st.session_state[k] = v
            st.success("✅ Client data loaded! (Click the 'X' on the uploaded file to dismiss this message)")
        except Exception as e:
            st.error(f"Error loading file: {e}")
            
    st.markdown("---")
    
    # 2. Save Data
    # Collect only the specific keys we care about
    current_data = {k: st.session_state[k] for k in default_keys.keys() if k in st.session_state}
    json_data = json.dumps(current_data, indent=4)
    
    # Dynamic filename based on client name if available
    client_fname = st.session_state["decedent_name"].replace(" ", "_") if st.session_state["decedent_name"] else "Client"
    
    st.download_button(
        label="⬇️ Save Progress to Computer",
        data=json_data,
        file_name=f"TA_Progress_{client_fname}.json",
        mime="application/json",
        type="primary"
    )

# --- MAIN CONTENT ---
st.title("Trust Admin Document Generator")
st.markdown("Fill out the details below. Progress is automatically tracked so you can save it via the left sidebar at any time.")

tab1, tab2, tab3, tab4 = st.tabs([
    "1. Decedent & Trust", 
    "2. Trustee Info", 
    "3. Beneficiaries",
    "4. Email Delivery Settings"
])

# --- TAB 1: DECEDENT & TRUST ---
with tab1:
    st.subheader("Decedent Details")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.text_input("Decedent Full Name", key="decedent_name")
    with col2:
        st.text_input("Date of Death", placeholder="e.g., January 15, 2026", key="date_of_death")
    with col3:
        st.text_input("Social Security Number", placeholder="XXX-XX-1234", key="ssn")
        
    st.subheader("Trust & Will Details")
    col4, col5, col6 = st.columns(3)
    with col4:
        st.text_input("Full Trust Name", placeholder="e.g., The Doe Family Trust", key="trust_name")
        st.text_input("Settlor/Trustor Name(s) (exactly as written on the trust)", key="settlor_name")
    with col5:
        st.text_input("Date of Trust", placeholder="e.g., October 5, 2015", key="trust_date")
        st.text_input("Date of Will", placeholder="e.g., October 5, 2015", key="will_date")
    with col6:
        st.text_input("Attorney Name", key="attorney_name")
        st.text_input("Law Firm Name", key="law_firm_name")

# --- TAB 2: TRUSTEE INFO ---
with tab2:
    st.subheader("Currently Acting Trustee")
    st.text_input("Trustee Full Name", key="trustee_name")
    st.text_input("Trustee Address (One Line)", placeholder="123 Main Street, Los Angeles, CA 90001", key="trustee_address")
    st.text_input("Trustee Phone", placeholder="(555) 123-4567", key="trustee_phone")

# --- TAB 3: BENEFICIARIES ---
with tab3:
    st.subheader("Beneficiaries")
    st.markdown("Enter the beneficiaries below. The template loops through these to create a notice for each and lists them all in the Questionnaire.")
    
    # Interactive table linked to session state
    edited_bens = st.data_editor(
        st.session_state["beneficiaries_data"], 
        num_rows="dynamic", 
        use_container_width=True
    )
    # Save edits back to session state so the download button catches them
    st.session_state["beneficiaries_data"] = edited_bens

# --- TAB 4: EMAIL SETTINGS & SUBMIT ---
with tab4:
    st.subheader("Finalize & Submit")
    st.markdown("Click below to finalize the documents and email them securely.")
    st.markdown("---")
    
    # Replaced form_submit_button with standard button
    submit_btn = st.button("Generate Documents & Email Results", type="primary")

# --- PROCESSING LOGIC ---
if submit_btn:
    decedent_val = st.session_state["decedent_name"]
    
    if not decedent_val:
        st.error("⚠️ Decedent Name is required.")
    elif GMAIL_APP_PASSWORD == "PUT_YOUR_16_CHAR_PASSWORD_HERE":
        st.error("⚠️ Please update the GMAIL_APP_PASSWORD in the python code (around line 12) with your real app password.")
    else:
        with st.spinner("Generating documents and preparing email..."):
            
            # Master Dictionary holding all variables for the Word Templates
            context = {
                "decedent_name": st.session_state["decedent_name"],
                "date_of_death": st.session_state["date_of_death"],
                "ssn": st.session_state["ssn"],
                "trust_name": st.session_state["trust_name"],
                "trust_date": st.session_state["trust_date"],
                "settlor_name": st.session_state["settlor_name"],
                "will_date": st.session_state["will_date"],
                "trustee_name": st.session_state["trustee_name"],
                "trustee_address": st.session_state["trustee_address"],
                "trustee_phone": st.session_state["trustee_phone"],
                "attorney_name": st.session_state["attorney_name"],
                "law_firm_name": st.session_state["law_firm_name"],
                "beneficiaries": st.session_state["beneficiaries_data"]
            }

            # 1. Generate Documents into a ZIP file in memory
            zip_buffer = io.BytesIO()
            docs_generated = False
            
            try:
                with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                    for filepath in template_files:
                        docs_generated = True
                        doc = DocxTemplate(filepath)
                        doc.render(context)
                        
                        doc_buffer = io.BytesIO()
                        doc.save(doc_buffer)
                        
                        clean_name = decedent_val.replace(' ', '_')
                        filename = os.path.basename(filepath)
                        zip_file.writestr(f"{clean_name}_{filename}", doc_buffer.getvalue())
                
                if not docs_generated:
                    st.error("❌ No .docx templates found. Please ensure your .docx files are uploaded.")
                    st.stop()

            except Exception as e:
                st.error(f"❌ Error generating documents: {e}")
                st.stop()

            # 2. Email the ZIP file
            try:
                msg = EmailMessage()
                msg['Subject'] = f"Trust Administration Documents: Estate of {decedent_val}"
                msg['From'] = "shekerlianlaw@gmail.com"
                msg['To'] = "anu@barthattorneys.com"
                
                body_text = f"""Anu,\n\nThe Trust Administration documents for the Estate of {decedent_val} have been automatically generated.\n\nPlease find the finalized documents attached in the ZIP file.\n\nBest,\nTA Automator Bot"""
                msg.set_content(body_text)
                
                zip_name = f"{decedent_val.replace(' ', '_')}_TA_Documents.zip"
                msg.add_attachment(zip_buffer.getvalue(), maintype='application', subtype='zip', filename=zip_name)
                
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    smtp.login("shekerlianlaw@gmail.com", GMAIL_APP_PASSWORD)
                    smtp.send_message(msg)
                
                st.success("✅ Documents generated and successfully emailed to our office")
                
                # Download Button for the final package
                st.download_button(
                    label="⬇️ Download Generated Documents (ZIP)",
                    data=zip_buffer.getvalue(),
                    file_name=f"{decedent_val.replace(' ', '_')}_TA_Documents.zip",
                    mime="application/zip"
                )
                
            except smtplib.SMTPAuthenticationError:
                st.error("❌ Email Failed: Authentication Error. Please ensure you are using a valid 16-character Google App Password.")
            except Exception as e:
                st.error(f"❌ Email Failed: An unexpected error occurred: {e}")
