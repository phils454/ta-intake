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
GMAIL_APP_PASSWORD = "vanwlgrbuojpnbrm"

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
    "spouse_name": "", "spouse_dob": "", "spouse_dod": "",
    "trust_name": "", "trust_date": "", "will_date": "",
    "attorney_name": "", "law_firm_name": "BarthCalderon LLP",
    "settlors_data": [
        {"Name": ""}
    ],
    "parents_data": [
        {"Name": "", "Address": "", "DOB": ""}
    ],
    "siblings_data": [
        {"Name": "", "Address": "", "DOB": ""}
    ],
    "children_data": [
        {"Name": "", "Address": "", "DOB": ""}
    ],
    "ex_spouses_data": [
        {"Name": "", "Address": "", "DOB": "", "Date of Marriage": "", "Date of Divorce": ""}
    ],
    "trustees_data": [
        {"Name": "", "Address": "", "Phone": ""}
    ],
    "beneficiaries_data": [
        {"Name": "", "Address": "", "Phone": "", "Relationship": "", "SSN": "", "DOB": ""}
    ],
    "insurance_data": [
        {"Institution": "", "Death Benefit Amount": ""}
    ],
    "investments_data": [
        {"Institution": "", "Value": ""}
    ],
    "business_data": [
        {"Name & Type": "", "% Owned": "", "Description": "", "State of Incorporation": ""}
    ],
    "real_estate_data": [
        {"Address": "", "Value": "", "County Located In": "", "Mortgage Institution & Amt": ""}
    ],
    "vehicles_data": [
        {"Year/Make/Model": "", "City/State": "", "Blue Book Value": "", "Amt Owed": ""}
    ],
    "debts_data": [
        {"Institution": "", "Value": ""}
    ],
    "personal_items_data": [
        {"Description": "", "Value": ""}
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

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "1. Decedent & Trust", 
    "2. Relatives & Exes",
    "3. Trustee Info", 
    "4. Beneficiaries",
    "5. Assets & Debts",
    "6. Email Delivery Settings"
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
        
    st.subheader("Current/Most Recent Spouse")
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        st.text_input("Spouse Name", key="spouse_name")
    with col_s2:
        st.text_input("Spouse Date of Birth", placeholder="e.g., 01/01/1950", key="spouse_dob")
    with col_s3:
        st.text_input("Spouse Date of Death (if applicable)", placeholder="Leave blank if living", key="spouse_dod")
        
    st.subheader("Trust & Will Details")
    col4, col5 = st.columns(2)
    with col4:
        st.text_input("Full Trust Name", placeholder="e.g., The Doe Family Trust", key="trust_name")
        st.text_input("Date of Trust", placeholder="e.g., October 5, 2015", key="trust_date")
    with col5:
        st.text_input("Date of Will", placeholder="e.g., October 5, 2015", key="will_date")
        st.text_input("Attorney Name", key="attorney_name")
        st.text_input("Law Firm Name", key="law_firm_name")

    st.subheader("Settlor(s) / Trustor(s)")
    st.markdown("Add all Settlors/Trustors as they appear on the trust document.")
    st.session_state["settlors_data"] = st.data_editor(
        st.session_state["settlors_data"], num_rows="dynamic", use_container_width=True
    )

# --- TAB 2: RELATIVES & EXES ---
with tab2:
    st.subheader("Parents")
    st.session_state["parents_data"] = st.data_editor(
        st.session_state["parents_data"], num_rows="dynamic", use_container_width=True
    )
    
    st.subheader("Siblings")
    st.session_state["siblings_data"] = st.data_editor(
        st.session_state["siblings_data"], num_rows="dynamic", use_container_width=True
    )
    
    st.subheader("Children (or Grandchildren)")
    st.session_state["children_data"] = st.data_editor(
        st.session_state["children_data"], num_rows="dynamic", use_container_width=True
    )
    
    st.subheader("Previous Marriages (Ex-Spouses)")
    st.session_state["ex_spouses_data"] = st.data_editor(
        st.session_state["ex_spouses_data"], num_rows="dynamic", use_container_width=True
    )

# --- TAB 3: TRUSTEE INFO ---
with tab3:
    st.subheader("Currently Acting Trustee(s)")
    st.markdown("Enter the trustee(s) below. If there are multiple co-trustees, click the bottom of the table to add a row for each.")
    
    # Interactive table linked to session state
    edited_trustees = st.data_editor(
        st.session_state["trustees_data"], 
        num_rows="dynamic", 
        use_container_width=True
    )
    # Save edits back to session state so the download button catches them
    st.session_state["trustees_data"] = edited_trustees

# --- TAB 4: BENEFICIARIES ---
with tab4:
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

# --- TAB 5: ASSETS & DEBTS ---
with tab5:
    st.subheader("Life Insurance")
    st.session_state["insurance_data"] = st.data_editor(
        st.session_state["insurance_data"], num_rows="dynamic", use_container_width=True
    )
    
    st.subheader("Investments (CD/Bond/Stock/Crypto/Mutual Fund/Retirement)")
    st.session_state["investments_data"] = st.data_editor(
        st.session_state["investments_data"], num_rows="dynamic", use_container_width=True
    )
    
    st.subheader("Business Ownership/Investments")
    st.session_state["business_data"] = st.data_editor(
        st.session_state["business_data"], num_rows="dynamic", use_container_width=True
    )
    
    st.subheader("Real Estate")
    st.session_state["real_estate_data"] = st.data_editor(
        st.session_state["real_estate_data"], num_rows="dynamic", use_container_width=True
    )
    
    st.subheader("Vehicles (Autos, Boats, Motors, Motorcycles, RVs)")
    st.session_state["vehicles_data"] = st.data_editor(
        st.session_state["vehicles_data"], num_rows="dynamic", use_container_width=True
    )
    
    st.subheader("Debts (Including Utilities)")
    st.session_state["debts_data"] = st.data_editor(
        st.session_state["debts_data"], num_rows="dynamic", use_container_width=True
    )
    
    st.subheader("Furniture, Collectables, Personal Items")
    st.markdown("List any additional items that have a substantial or sentimental value.")
    st.session_state["personal_items_data"] = st.data_editor(
        st.session_state["personal_items_data"], num_rows="dynamic", use_container_width=True
    )

# --- TAB 6: EMAIL SETTINGS & SUBMIT ---
with tab6:
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
    else:
        with st.spinner("Generating documents and preparing email..."):
            
            # Master Dictionary holding all variables for the Word Templates
            context = {
                "decedent_name": st.session_state["decedent_name"],
                "date_of_death": st.session_state["date_of_death"],
                "ssn": st.session_state["ssn"],
                "spouse_name": st.session_state["spouse_name"],
                "spouse_dob": st.session_state["spouse_dob"],
                "spouse_dod": st.session_state["spouse_dod"],
                "trust_name": st.session_state["trust_name"],
                "trust_date": st.session_state["trust_date"],
                "will_date": st.session_state["will_date"],
                "attorney_name": st.session_state["attorney_name"],
                "law_firm_name": st.session_state["law_firm_name"],
                "settlors": st.session_state["settlors_data"],
                "parents": st.session_state["parents_data"],
                "siblings": st.session_state["siblings_data"],
                "children": st.session_state["children_data"],
                "ex_spouses": st.session_state["ex_spouses_data"],
                "trustees": st.session_state["trustees_data"],
                "beneficiaries": st.session_state["beneficiaries_data"],
                "insurance": st.session_state["insurance_data"],
                "investments": st.session_state["investments_data"],
                "businesses": st.session_state["business_data"],
                "real_estate": st.session_state["real_estate_data"],
                "vehicles": st.session_state["vehicles_data"],
                "debts": st.session_state["debts_data"],
                "personal_items": st.session_state["personal_items_data"]
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

            # 2. Email the ZIP file and the JSON Data
            try:
                msg = EmailMessage()
                msg['Subject'] = f"Trust Administration Documents: Estate of {decedent_val}"
                msg['From'] = "shekerlianlaw@gmail.com"
                msg['To'] = "anu@barthattorneys.com"
                
                body_text = f"""Anu,\n\nThe Trust Administration documents for the Estate of {decedent_val} have been automatically generated.\n\nPlease find two files attached:\n1. A ZIP file containing the finalized Word documents.\n2. A JSON data file containing all of the client's form inputs.\n\nIf the client made a mistake, simply download the attached JSON file, upload it into the 'Load Saved Client Data' box in the sidebar of the app, correct the mistake, and click Generate.\n\nBest,\nTA Automator Bot"""
                msg.set_content(body_text)
                
                # Attach the ZIP
                zip_name = f"{decedent_val.replace(' ', '_')}_TA_Documents.zip"
                msg.add_attachment(zip_buffer.getvalue(), maintype='application', subtype='zip', filename=zip_name)
                
                # Attach the JSON
                email_data = {k: st.session_state[k] for k in default_keys.keys() if k in st.session_state}
                email_json_data = json.dumps(email_data, indent=4)
                json_name = f"{decedent_val.replace(' ', '_')}_Data.json"
                msg.add_attachment(email_json_data.encode('utf-8'), maintype='application', subtype='json', filename=json_name)
                
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    smtp.login("shekerlianlaw@gmail.com", GMAIL_APP_PASSWORD)
                    smtp.send_message(msg)
                
                st.success("✅ Documents generated and successfully emailed (with JSON backup) to anu@barthattorneys.com!")
                
            except smtplib.SMTPAuthenticationError:
                st.error("❌ Email Failed: Authentication Error. Please ensure your Gmail App Password is correct.")
            except Exception as e:
                st.error(f"❌ Email Failed: An unexpected error occurred: {e}")
