import streamlit as st
from docxtpl import DocxTemplate
import pandas as pd
import os
import io
import zipfile
import smtplib
from email.message import EmailMessage

# Define the templates folder location
TEMPLATES_DIR = "templates"
if not os.path.exists(TEMPLATES_DIR):
    os.makedirs(TEMPLATES_DIR)

st.set_page_config(page_title="Trust Admin Automator", layout="wide")

st.title("Trust Admin Document Generator")
st.markdown("""
Fill out the details below to automatically populate the Trust Administration documents. 
When submitted, the system will generate a ZIP file of all documents and email them directly to **anu@barthattorneys.com**.
""")

# Setup Form Tabs for better organization
tab1, tab2, tab3, tab4 = st.tabs([
    "1. Decedent & Trust", 
    "2. Trustee Info", 
    "3. Beneficiaries",
    "4. Email Delivery Settings"
])

with st.form("ta_automation_form"):
    
    # --- TAB 1: DECEDENT & TRUST ---
    with tab1:
        st.subheader("Decedent Details")
        col1, col2, col3 = st.columns(3)
        with col1:
            decedent_name = st.text_input("Decedent Full Name")
        with col2:
            date_of_death = st.text_input("Date of Death", placeholder="e.g., January 15, 2026")
        with col3:
            ssn = st.text_input("Social Security Number", placeholder="XXX-XX-1234")
            
        st.subheader("Trust & Will Details")
        col4, col5, col6 = st.columns(3)
        with col4:
            trust_name = st.text_input("Full Trust Name", placeholder="e.g., The Doe Family Trust")
            settlor_name = st.text_input("Settlor Name", placeholder="e.g., John H. Doe")
        with col5:
            trust_date = st.text_input("Date of Trust", placeholder="e.g., October 5, 2015")
            will_date = st.text_input("Date of Will", placeholder="e.g., October 5, 2015")
        with col6:
            attorney_name = st.text_input("Attorney Name", value="Harry Barth, Esq.")
            law_firm_name = st.text_input("Law Firm Name", value="BarthCalderon LLP")

    # --- TAB 2: TRUSTEE INFO ---
    with tab2:
        st.subheader("Currently Acting Trustee")
        trustee_name = st.text_input("Trustee Full Name")
        trustee_address = st.text_input("Trustee Address (One Line)", placeholder="123 Main Street, Los Angeles, CA 90001")
        trustee_phone = st.text_input("Trustee Phone", placeholder="(555) 123-4567")

    # --- TAB 3: BENEFICIARIES ---
    with tab3:
        st.subheader("Beneficiaries (For 16061.7 Notices)")
        st.markdown("Enter the beneficiaries below. The template can loop through these to create a notice for each.")
        
        # Interactive table for dynamic beneficiary entry
        default_ben_df = pd.DataFrame([
            {"Beneficiary Name": "", "Beneficiary Address": ""}
        ])
        edited_bens = st.data_editor(default_ben_df, num_rows="dynamic", use_container_width=True)

    # --- TAB 4: EMAIL SETTINGS ---
    with tab4:
        st.subheader("Email Delivery Authentication")
        st.info("Results will be sent from **shekerlianlaw@gmail.com** to **anu@barthattorneys.com**.")
        gmail_password = st.text_input("Gmail App Password", type="password", help="Enter the 16-character Google App Password for shekerlianlaw@gmail.com")

    # --- SUBMIT BUTTON ---
    st.markdown("---")
    submit_btn = st.form_submit_button("Generate Documents & Email Results", type="primary")

# --- PROCESSING LOGIC ---
if submit_btn:
    if not decedent_name or not gmail_password:
        st.error("⚠️ Decedent Name and Gmail App Password are required.")
    else:
        with st.spinner("Generating documents and preparing email..."):
            
            # Convert beneficiaries dataframe to a list of dictionaries for docxtpl
            beneficiaries_list = edited_bens.to_dict('records')
            
            # Master Dictionary holding all variables for the Word Templates
            context = {
                "decedent_name": decedent_name,
                "date_of_death": date_of_death,
                "ssn": ssn,
                "trust_name": trust_name,
                "trust_date": trust_date,
                "settlor_name": settlor_name,
                "will_date": will_date,
                "trustee_name": trustee_name,
                "trustee_address": trustee_address,
                "trustee_phone": trustee_phone,
                "attorney_name": attorney_name,
                "law_firm_name": law_firm_name,
                "beneficiaries": beneficiaries_list  # Use `{% for ben in beneficiaries %}` in Word
            }

            # 1. Generate Documents into a ZIP file in memory
            zip_buffer = io.BytesIO()
            docs_generated = False
            
            try:
                with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                    for filename in os.listdir(TEMPLATES_DIR):
                        if filename.endswith(".docx") and not filename.startswith("~$"):
                            docs_generated = True
                            doc = DocxTemplate(os.path.join(TEMPLATES_DIR, filename))
                            
                            # Render the template with our context data
                            doc.render(context)
                            
                            # Save to in-memory buffer
                            doc_buffer = io.BytesIO()
                            doc.save(doc_buffer)
                            
                            # Write to the zip file
                            clean_name = decedent_name.replace(' ', '_')
                            zip_file.writestr(f"{clean_name}_{filename}", doc_buffer.getvalue())
                
                if not docs_generated:
                    st.error(f"❌ No .docx templates found in the '{TEMPLATES_DIR}' folder.")
                    st.stop()

            except Exception as e:
                st.error(f"❌ Error generating documents: {e}")
                st.stop()

            # 2. Email the ZIP file
            try:
                msg = EmailMessage()
                msg['Subject'] = f"Trust Administration Documents: Estate of {decedent_name}"
                msg['From'] = "shekerlianlaw@gmail.com"
                msg['To'] = "anu@barthattorneys.com"
                
                # Email body
                body_text = f"""Anu,

The Trust Administration documents for the Estate of {decedent_name} have been automatically generated.

Please find the finalized documents attached in the ZIP file.

Best,
TA Automator Bot
"""
                msg.set_content(body_text)
                
                # Attach the zip file
                zip_name = f"{decedent_name.replace(' ', '_')}_TA_Documents.zip"
                msg.add_attachment(zip_buffer.getvalue(), maintype='application', subtype='zip', filename=zip_name)
                
                # Connect to Gmail SMTP server
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    smtp.login("shekerlianlaw@gmail.com", gmail_password)
                    smtp.send_message(msg)
                
                st.success("✅ Documents generated and successfully emailed to anu@barthattorneys.com!")
                
            except smtplib.SMTPAuthenticationError:
                st.error("❌ Email Failed: Authentication Error. Please ensure you are using a valid 16-character Google App Password, not your standard login password.")
            except Exception as e:
                st.error(f"❌ Email Failed: An unexpected error occurred: {e}")
