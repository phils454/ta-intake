import streamlit as st
import os
import smtplib
from email.message import EmailMessage
from docxtpl import DocxTemplate
from datetime import datetime
import json

# --- Configuration & Helpers ---
SENDER_EMAIL = st.secrets["sender_email"]
SENDER_PASSWORD = st.secrets["sender_password"]
RECEIVER_EMAIL = "shekerlianlaw@gmail.com"

def send_email_with_docx(docx_path, filename):
    msg = EmailMessage()
    msg['Subject'] = f"New TA Intake: {filename}"
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg.set_content("A new Trust Administration questionnaire has been completed. The generated Word document is attached.")

    with open(docx_path, 'rb') as f:
        msg.add_attachment(f.read(), maintype='application', subtype='vnd.openxmlformats-officedocument.wordprocessingml.document', filename=filename)

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)

def cb(condition):
    return "☑" if condition else "☐"

# --- Main App Interface ---
st.set_page_config(page_title="BarthCalderon TA Questionnaire", layout="wide")

# --- Sidebar: Draft Restore System ---
with st.sidebar:
    st.header("💾 Resume Progress")
    st.write("If you saved a draft to your computer, upload the `.json` file here to restore your answers.")
    draft_file = st.file_uploader("Upload Draft File", type=["json"], key="draft_uploader")
    
    if draft_file is not None:
        try:
            saved_data = json.load(draft_file)
            for k, v in saved_data.items():
                if k != "draft_uploader":
                    st.session_state[k] = v
            st.success("Draft loaded! Your answers have been fully restored.")
        except Exception as e:
            st.error("Error loading draft. Please ensure it is a valid file.")

st.title("BarthCalderon Trust Administration Questionnaire")
st.markdown("---")

warning_msg = "⚠️ **CRITICAL WARNING:** Your privacy is our priority, so your answers are NOT stored on a cloud database. **If you close this browser window or lose internet connection, all information will be lost.** To avoid this, go to Tab 5 at any time and click **'Save Draft to Computer'**."

t_contact, t_relatives, t_taxes_benes, t_assets, t_debts = st.tabs([
    "1. Contact & Decedent", "2. Relatives & Marriages", "3. Taxes & Beneficiaries", 
    "4. Assets & Real Estate", "5. Vehicles, Debts & Misc"
])

with t_contact:
    st.warning(warning_msg)
    st.subheader("Contact Information")
    c1, c2, c3 = st.columns(3)
    t_fname = c1.text_input("First Name", key="t_fname")
    t_mname = c2.text_input("Middle Name", key="t_mname")
    t_lname = c3.text_input("Last Name", key="t_lname")
    
    t_addr = st.text_input("Street Address", key="t_addr")
    c4, c5, c6 = st.columns(3)
    t_city = c4.text_input("City", key="t_city")
    t_state = c5.text_input("State", key="t_state")
    t_zip = c6.text_input("Zip Code", key="t_zip")
    
    c7, c8, c9 = st.columns(3)
    t_hphone = c7.text_input("Home Phone", key="t_hphone")
    t_cphone = c8.text_input("Cell Phone", key="t_cphone")
    t_wphone = c9.text_input("Work Phone", key="t_wphone")
    
    c10, c11, c12 = st.columns(3)
    t_ssn = c10.text_input("Social Security Number", key="t_ssn")
    t_email = c11.text_input("Email", key="t_email")
    t_dob = c12.text_input("Date of Birth", key="t_dob")
    
    is_trustee = st.radio("Are you named as the Trustee of the estate?", ["Yes", "No"], key="is_trustee")
    t_other_name = st.text_input("If No, who is:", key="t_other_name")

    st.markdown("---")
    st.subheader("The Person who died (Decedent)")
    d1, d2, d3 = st.columns(3)
    d_fname = d1.text_input("Legal Name of decedent (First)", key="d_fname")
    d_mname = d2.text_input("Legal Name of decedent (Middle)", key="d_mname")
    d_lname = d3.text_input("Legal Name of decedent (Last)", key="d_lname")
    
    d_addr = st.text_input("Decedent’s Street Address", key="d_addr")
    d4, d5, d6 = st.columns(3)
    d_city = d4.text_input("Decedent’s City", key="d_city")
    d_state = d5.text_input("Decedent’s State", key="d_state")
    d_zip = d6.text_input("Decedent’s Zip Code", key="d_zip")
    
    d7, d8 = st.columns(2)
    d_dob = d7.text_input("Decedent’s Date of Birth", key="d_dob")
    d_dod = d8.text_input("Decedent’s Date of Death", key="d_dod")
    
    d9, d10 = st.columns(2)
    d_county = d9.text_input("Decedent’s County of Death", key="d_county")
    d_ssn = d10.text_input("Decedent’s Social Security Number", key="d_ssn")
    
    st.write("Current or Most Recent Spouse")
    s1, s2, s3 = st.columns(3)
    s_fname = s1.text_input("Name of current or most recent spouse (First)", key="s_fname")
    s_mname = s2.text_input("Name of current or most recent spouse (Middle)", key="s_mname")
    s_lname = s3.text_input("Name of current or most recent spouse (Last)", key="s_lname")
    s4, s5 = st.columns(2)
    s_dob = s4.text_input("Spouse’s Date of Birth", key="s_dob")
    s_dod = s5.text_input("Spouse’s Date of Death", key="s_dod")

    st.markdown("---")
    st.subheader("Trust and Will")
    has_tw = st.radio("Did Decedent leave a Trust & Will?", ["Yes", "No"], key="has_tw")
    st.write("If you do not have access to it, please state the information of the person in its possession.")
    tw1, tw2, tw3 = st.columns(3)
    tw_fname = tw1.text_input("Possessor First Name", key="tw_fname")
    tw_mname = tw2.text_input("Possessor Middle Name", key="tw_mname")
    tw_lname = tw3.text_input("Possessor Last Name", key="tw_lname")
    tw_addr = st.text_input("Possessor Street Address", key="tw_addr")
    tw4, tw5, tw6 = st.columns(3)
    tw_city = tw4.text_input("Possessor City", key="tw_city")
    tw_state = tw5.text_input("Possessor State", key="tw_state")
    tw_zip = tw6.text_input("Possessor Zip Code", key="tw_zip")

with t_relatives:
    st.warning(warning_msg)
    st.subheader("Decedent’s LIVING & Adopted LIVING Relatives")
    st.write("Parents")
    p1, p2 = st.columns(2)
    mom_name = p1.text_input("Mom’s Name", key="mom_name")
    mom_dob = p2.text_input("Mom’s Date of Birth", key="mom_dob")
    mom_addr = st.text_input("Mom’s Address", key="mom_addr")
    
    p3, p4 = st.columns(2)
    dad_name = p3.text_input("Dad’s Name", key="dad_name")
    dad_dob = p4.text_input("Dad’s Date of Birth", key="dad_dob")
    dad_addr = st.text_input("Dad’s Address", key="dad_addr")
    
    st.markdown("---")
    st.write("Siblings")
    sibs = []
    for i in range(1, 5):
        with st.expander(f"Sibling #{i}"):
            s_name = st.text_input(f"Sibling #{i}’s Name", key=f"sib{i}_name")
            s_dob = st.text_input(f"Sibling #{i}’s Date of Birth", key=f"sib{i}_dob")
            s_addr = st.text_input(f"Sibling #{i}’s Address", key=f"sib{i}_addr")
            sibs.append({'name': s_name, 'dob': s_dob, 'addr': s_addr})

    st.markdown("---")
    st.write("Children (If all children are deceased, also list Grandchildren)")
    children = []
    for i in range(1, 7):
        with st.expander(f"Child #{i}"):
            c_name = st.text_input(f"Child #{i}’s Name", key=f"ch{i}_name")
            c_dob = st.text_input(f"Child #{i}’s Date of Birth", key=f"ch{i}_dob")
            c_addr = st.text_input(f"Child #{i}’s Address", key=f"ch{i}_addr")
            children.append({'name': c_name, 'dob': c_dob, 'addr': c_addr})

    st.markdown("---")
    st.subheader("Previous Marriages (only list if Decedent was divorced)")
    exes = []
    for i in range(1, 3):
        with st.expander(f"Ex-Spouse #{i}"):
            ex_name = st.text_input(f"Ex-Spouse #{i}’s Name", key=f"ex{i}_name")
            ex_addr = st.text_input(f"Ex-Spouse #{i}’s Address", key=f"ex{i}_addr")
            ex1, ex2, ex3 = st.columns(3)
            ex_dob = ex1.text_input("Date of Birth", key=f"ex{i}_dob")
            ex_dom = ex2.text_input("Date of Marriage", key=f"ex{i}_dom")
            ex_div = ex3.text_input("Date of Divorce", key=f"ex{i}_div")
            exes.append({'name': ex_name, 'addr': ex_addr, 'dob': ex_dob, 'dom': ex_dom, 'div': ex_div})

with t_taxes_benes:
    st.warning(warning_msg)
    st.subheader("Taxes")
    tax_inc = st.radio("Did Decedent make any income in the year they died?", ["Yes", "No"], key="tax_inc")
    tax_srv = st.radio("Will you require our services to prepare personal and/or trust tax returns?", ["Yes", "No"], key="tax_srv")
    
    st.markdown("---")
    st.subheader("Beneficiaries (only list beneficiaries named in a Trust)")
    benes = []
    for i in range(1, 5):
        with st.expander(f"Beneficiary #{i}"):
            b_name = st.text_input(f"Bene #{i} Name", key=f"ben{i}_name")
            b_addr = st.text_input(f"Bene #{i} Address", key=f"ben{i}_addr")
            b1, b2, b3, b4 = st.columns(4)
            b_phone = b1.text_input("Phone Number", key=f"ben{i}_phone")
            b_rel = b2.text_input("Relationship to Decedent", key=f"ben{i}_rel")
            b_ssn = b3.text_input("Social Security Number", key=f"ben{i}_ssn")
            b_dob = b4.text_input("Date of Birth", key=f"ben{i}_dob")
            benes.append({'name': b_name, 'addr': b_addr, 'phone': b_phone, 'rel': b_rel, 'ssn': b_ssn, 'dob': b_dob})
            
    add_benes = st.radio("Additional Beneficiaries?", ["Yes", "No"], key="add_benes")

with t_assets:
    st.warning(warning_msg)
    st.subheader("Decedent’s Life Insurance")
    insurances = []
    for i in range(1, 5):
        i1, i2 = st.columns(2)
        ins = i1.text_input(f"Insurance #{i} Institution", key=f"ins{i}_inst")
        amt = i2.text_input(f"Insurance #{i} Death Benefit Amount", key=f"ins{i}_amt")
        insurances.append({'inst': ins, 'amt': amt})

    st.markdown("---")
    st.subheader("Decedent’s Investments-CD/Bond/Stock/Crypto/Mutual Fund/Retirement/etc")
    investments = []
    for i in range(1, 15):
        iv1, iv2 = st.columns(2)
        inst = iv1.text_input(f"Investment #{i} Institution", key=f"inv{i}_inst")
        val = iv2.text_input(f"Investment #{i} Value", key=f"inv{i}_val")
        investments.append({'inst': inst, 'val': val})

    st.markdown("---")
    st.subheader("Decedent’s Business Ownership/Investments")
    businesses = []
    for i in range(1, 5):
        with st.expander(f"Business #{i}"):
            bz1, bz2 = st.columns(2)
            name = bz1.text_input(f"Business #{i} Name & Type (LLC/INC)", key=f"biz{i}_name")
            pct = bz2.text_input("% Owned", key=f"biz{i}_pct")
            desc = st.text_input("What it is/does", key=f"biz{i}_desc")
            state = st.text_input("State of Incorporation", key=f"biz{i}_state")
            businesses.append({'name': name, 'pct': pct, 'desc': desc, 'state': state})

    st.markdown("---")
    st.subheader("Decedent’s Real Estate")
    real_estate = []
    for i in range(1, 6):
        with st.expander(f"Property #{i}"):
            r1, r2 = st.columns(2)
            addr = r1.text_input(f"Property #{i} Address", key=f"re{i}_addr")
            val = r2.text_input("Approx Value", key=f"re{i}_val")
            cnty = r1.text_input("County Located In", key=f"re{i}_cnty")
            mort = r2.text_input("Mortgage Institution & Amount", key=f"re{i}_mort")
            real_estate.append({'addr': addr, 'val': val, 'cnty': cnty, 'mort': mort})

with t_debts:
    st.warning(warning_msg)
    st.subheader("Decedent’s Autos, Boats, Motors, Motorcycles, and Other Recreational Vehicles")
    vehicles = []
    for i in range(1, 5):
        with st.expander(f"Vehicle #{i}"):
            v1, v2 = st.columns(2)
            ymm = v1.text_input(f"Vehicle #{i} Year/Make/Model", key=f"veh{i}_ymm")
            loc = v2.text_input(f"Vehicle #{i} City/State", key=f"veh{i}_loc")
            val = v1.text_input(f"Vehicle #{i} Blue Book Value", key=f"veh{i}_val")
            owed = v2.text_input(f"Vehicle #{i} Amount Owed", key=f"veh{i}_owed")
            vehicles.append({'ymm': ymm, 'loc': loc, 'val': val, 'owed': owed})

    st.markdown("---")
    st.subheader("Decedent’s Debts")
    debts = []
    for i in range(1, 9):
        db1, db2 = st.columns(2)
        inst = db1.text_input(f"Debt #{i} Institution", key=f"debt{i}_inst")
        val = db2.text_input(f"Debt #{i} Value", key=f"debt{i}_val")
        debts.append({'inst': inst, 'val': val})

    st.markdown("---")
    st.subheader("Decedent’s Furniture, Collectable, or Other Personal Items")
    st.write("Please list any additional items that have a substantial value. Additionally, please list any items of special sentimental value.")
    items = []
    for i in range(1, 11):
        it1, it2 = st.columns(2)
        desc = it1.text_input(f"Item #{i}", key=f"item{i}_desc")
        val = it2.text_input(f"Item #{i} Value", key=f"item{i}_val")
        items.append({'desc': desc, 'val': val})

    # --- SAVE / SUBMIT BUTTONS ---
    st.markdown("---")
    st.subheader("Finish or Save Progress")
    
    # Generate JSON payload for downloading, excluding Streamlit internal objects
    draft_dict = {
        k: v for k, v in st.session_state.items() 
        if isinstance(v, (str, int, float, bool, list)) 
        and k != "draft_uploader" 
        and not k.startswith("FormSubmitter")
    }
    draft_json = json.dumps(draft_dict, indent=2)
    
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="💾 Save Draft to Computer",
            data=draft_json,
            file_name=f"TA_Draft_{t_lname if t_lname else 'Client'}.json",
            mime="application/json"
        )
    with col2:
        submit = st.button("Submit Final Questionnaire ➔")

    if submit:
        ctx = {}
        
        # Contact
        ctx['t_fname'] = t_fname; ctx['t_mname'] = t_mname; ctx['t_lname'] = t_lname
        ctx['t_addr'] = t_addr; ctx['t_city'] = t_city; ctx['t_state'] = t_state; ctx['t_zip'] = t_zip
        ctx['t_hphone'] = t_hphone; ctx['t_cphone'] = t_cphone; ctx['t_wphone'] = t_wphone
        ctx['t_ssn'] = t_ssn; ctx['t_email'] = t_email; ctx['t_dob'] = t_dob
        ctx['cb_t_y'] = cb(is_trustee == "Yes"); ctx['cb_t_n'] = cb(is_trustee == "No"); ctx['t_other_name'] = t_other_name
        
        # Decedent & Spouse
        ctx['d_fname'] = d_fname; ctx['d_mname'] = d_mname; ctx['d_lname'] = d_lname
        ctx['d_addr'] = d_addr; ctx['d_city'] = d_city; ctx['d_state'] = d_state; ctx['d_zip'] = d_zip
        ctx['d_dob'] = d_dob; ctx['d_dod'] = d_dod; ctx['d_county'] = d_county; ctx['d_ssn'] = d_ssn
        ctx['s_fname'] = s_fname; ctx['s_mname'] = s_mname; ctx['s_lname'] = s_lname
        ctx['s_dob'] = s_dob; ctx['s_dod'] = s_dod
        
        # Trust/Will
        ctx['cb_tw_y'] = cb(has_tw == "Yes"); ctx['cb_tw_n'] = cb(has_tw == "No")
        ctx['tw_fname'] = tw_fname; ctx['tw_mname'] = tw_mname; ctx['tw_lname'] = tw_lname
        ctx['tw_addr'] = tw_addr; ctx['tw_city'] = tw_city; ctx['tw_state'] = tw_state; ctx['tw_zip'] = tw_zip

        # Relatives
        ctx['mom_name'] = mom_name; ctx['mom_dob'] = mom_dob; ctx['mom_addr'] = mom_addr
        ctx['dad_name'] = dad_name; ctx['dad_dob'] = dad_dob; ctx['dad_addr'] = dad_addr
        for i, s in enumerate(sibs, 1):
            ctx[f'sib{i}_name'] = s['name']; ctx[f'sib{i}_dob'] = s['dob']; ctx[f'sib{i}_addr'] = s['addr']
        for i, c in enumerate(children, 1):
            ctx[f'ch{i}_name'] = c['name']; ctx[f'ch{i}_dob'] = c['dob']; ctx[f'ch{i}_addr'] = c['addr']
        for i, ex in enumerate(exes, 1):
            ctx[f'ex{i}_name'] = ex['name']; ctx[f'ex{i}_addr'] = ex['addr']; ctx[f'ex{i}_dob'] = ex['dob']
            ctx[f'ex{i}_dom'] = ex['dom']; ctx[f'ex{i}_div'] = ex['div']

        # Taxes & Benes
        ctx['cb_tax_inc_y'] = cb(tax_inc == "Yes"); ctx['cb_tax_inc_n'] = cb(tax_inc == "No")
        ctx['cb_tax_srv_y'] = cb(tax_srv == "Yes"); ctx['cb_tax_srv_n'] = cb(tax_srv == "No")
        for i, b in enumerate(benes, 1):
            ctx[f'ben{i}_name'] = b['name']; ctx[f'ben{i}_addr'] = b['addr']; ctx[f'ben{i}_phone'] = b['phone']
            ctx[f'ben{i}_rel'] = b['rel']; ctx[f'ben{i}_ssn'] = b['ssn']; ctx[f'ben{i}_dob'] = b['dob']
        ctx['cb_add_ben_y'] = cb(add_benes == "Yes"); ctx['cb_add_ben_n'] = cb(add_benes == "No")

        # Assets
        for i, ins in enumerate(insurances, 1):
            ctx[f'ins{i}_inst'] = ins['inst']; ctx[f'ins{i}_amt'] = ins['amt']
        for i, inv in enumerate(investments, 1):
            ctx[f'inv{i}_inst'] = inv['inst']; ctx[f'inv{i}_val'] = inv['val']
        for i, bz in enumerate(businesses, 1):
            ctx[f'biz{i}_name'] = bz['name']; ctx[f'biz{i}_pct'] = bz['pct']; ctx[f'biz{i}_desc'] = bz['desc']; ctx[f'biz{i}_state'] = bz['state']
        for i, r in enumerate(real_estate, 1):
            ctx[f're{i}_addr'] = r['addr']; ctx[f're{i}_val'] = r['val']; ctx[f're{i}_cnty'] = r['cnty']; ctx[f're{i}_mort'] = r['mort']
            
        # Vehicles & Debts
        for i, v in enumerate(vehicles, 1):
            ctx[f'veh{i}_ymm'] = v['ymm']; ctx[f'veh{i}_loc'] = v['loc']; ctx[f'veh{i}_val'] = v['val']; ctx[f'veh{i}_owed'] = v['owed']
        for i, db in enumerate(debts, 1):
            ctx[f'debt{i}_inst'] = db['inst']; ctx[f'debt{i}_val'] = db['val']
        for i, it in enumerate(items, 1):
            ctx[f'item{i}_desc'] = it['desc']; ctx[f'item{i}_val'] = it['val']

        # Output Generation
        input_template = "TA Q (with Fields) - Rev. 4-14-26.docx"
        safe_name = t_lname.replace(" ", "_") if t_lname else "Client"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        output_filename = f"{safe_name}_TA_Intake_{timestamp}.docx"
        temp_path = f"/tmp/{output_filename}"

        try:
            doc = DocxTemplate(input_template)
            doc.render(context=ctx)
            doc.save(temp_path)
            
            send_email_with_docx(temp_path, output_filename)
            os.remove(temp_path)
            
            st.success("Success! The Trust Administration questionnaire has been securely submitted.")
            
        except Exception as e:
            st.error(f"Error compiling document: {e}. Ensure '{input_template}' is in the repository and formatted with the correct variable tags.")
