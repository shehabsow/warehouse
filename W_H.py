import streamlit as st
import pandas as pd
import pytz
from datetime import datetime, timedelta
import json

st.set_page_config(
    layout="wide",
    page_title='warehouse',
    page_icon='🪙')

egypt_tz = pytz.timezone('Africa/Cairo')

# Load users data
def load_users():
    try:
        with open('users.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "knhp322": {"password": "knhp322", "first_login": True, "name": "Shehab Ayman", "last_password_update": str(datetime.now(egypt_tz))},
            "karm": {"password": "karm", "first_login": True, "name": "karm", "last_password_update": str(datetime.now(egypt_tz))},
            "kxsv748": {"password": "kxsv748", "first_login": True, "name": "Mohamed El masry", "last_password_update": str(datetime.now(egypt_tz))},
            "kvwp553": {"password": "kvwp553", "first_login": True, "name": "sameh", "last_password_update": str(datetime.now(egypt_tz))},
            "knfb489": {"password": "knfb489", "first_login": True, "name": "Yasser Hassan", "last_password_update": str(datetime.now(egypt_tz))},
            "kjjd308": {"password": "kjjd308", "first_login": True, "name": "Kaleed", "last_password_update": str(datetime.now(egypt_tz))},
            "kibx268": {"password": "kibx268", "first_login": True, "name": "Zeinab Mobarak", "last_password_update": str(datetime.now(egypt_tz))},
            "engy": {"password": "1234", "first_login": True, "name": "D.Engy", "last_password_update": str(datetime.now(egypt_tz))}
        }

# Save users data to JSON file
def save_users(users):
    with open('users.json', 'w') as f:
        json.dump(users, f)

# Load logs from files
def load_logs():
    try:
        logs_location = pd.read_csv('logs_location.csv').to_dict('records')
    except FileNotFoundError:
        logs_location = []
    
    try:
        logs_receving = pd.read_csv('logs_receving.csv').to_dict('records')
    except FileNotFoundError:
        logs_receving = []

    try:
        logs_confirmation = pd.read_csv('logs_confirmation.csv').to_dict('records')
    except FileNotFoundError:
        logs_confirmation = []

    return logs_location, logs_receving, logs_confirmation

# Login function
def login(username, password):
    if username in users and users[username]["password"] == password:
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.first_login = users[username]["first_login"]
        last_password_update = datetime.strptime(users[username]["last_password_update"], '%Y-%m-%d %H:%M:%S.%f%z')
        if datetime.now(egypt_tz) - last_password_update > timedelta(days=30):
            st.session_state.password_expired = True
        else:
            st.session_state.password_expired = False
    else:
        st.error("اسم المستخدم أو كلمة المرور غير صحيحة")

# Update password function
def update_password(username, new_password, confirm_new_password):
    if new_password == confirm_new_password:
        users[username]["password"] = new_password
        users[username]["first_login"] = False
        users[username]["last_password_update"] = str(datetime.now(egypt_tz))
        save_users(users)
        st.session_state.first_login = False
        st.session_state.password_expired = False
        st.success("تم تحديث كلمة المرور بنجاح!")
    else:
        st.error("كلمتا المرور غير متطابقتين!")

# Function to add new batch
def add_new_Batch(username, Product_Name, Batch_No, Item_Code, QTY_pack, Date, Delivered_by, Received_by):
    global df_Receving1
    try:
        QTY_pack_int = int(QTY_pack)
    except ValueError:
        st.error("الكمية يجب أن تكون عدد صحيح.")
        return

    pallets, cartons, boxes = calculate_packaging(QTY_pack_int)
    new_row = {
        'Product Name': Product_Name, 'Batch No': Batch_No, 'Item Code': Item_Code, 'QTY pack': QTY_pack,
        'Date': Date, 'Delivered by': Delivered_by, 'Received by': Received_by,
        'Pallets': pallets, 'Cartons': cartons, 'Boxes': boxes, 'Confirmed': 'No'
    }
    df_Receving1 = df_Receving1.append(new_row, ignore_index=True)
    df_Receving1.to_csv('Receving1.csv', index=False)
    st.success(f"تمت إضافة المنتج الجديد '{Batch_No}' بنجاح بكمية {QTY_pack}!")
    log_entry = {
        'user': username,
        'time': datetime.now(egypt_tz).strftime('%Y-%m-%d %H:%M:%S'),
        'Batch No': Batch_No,
        'QTY pack': QTY_pack,
        'Pallets': pallets,
        'Cartons': cartons,
        'Boxes': boxes,
        'Delivered by': Delivered_by,
        'Received by': Received_by
    }
    st.session_state.logs_receving.append(log_entry)
    logs_df = pd.DataFrame(st.session_state.logs_receving)
    logs_df.to_csv('logs_receving.csv', index=False)

# Function to calculate packaging
def calculate_packaging(total_boxes):
    cartons_per_pallet = 12
    boxes_per_carton = 240

    cartons = total_boxes // boxes_per_carton
    boxes_left = total_boxes % boxes_per_carton

    pallets = cartons // cartons_per_pallet
    cartons_left = cartons % cartons_per_pallet

    return pallets, cartons_left, boxes_left

# Function to display batch details and confirmation
def display_batch_details_and_confirmation():
    st.header("تأكيد أو رفض الدفعة")
    
    try:
        df_Receving1 = pd.read_csv('Receving1.csv')
    except FileNotFoundError:
        st.error("ملف الدفعات غير موجود.")
        return

    batch_numbers = df_Receving1['Batch No'].unique().tolist()

    batch_number = st.selectbox("اختر رقم الدفعة:", batch_numbers)
    
    if st.button("عرض الدفعة"):
        batch_df = df_Receving1[df_Receving1['Batch No'] == batch_number]
        if not batch_df.empty:
            def highlight_confirmed(val):
                color = 'background-color: green' if val == 'Yes' else ''
                return color
            
            st.dataframe(
                batch_df.style.applymap(highlight_confirmed, subset=['Confirmed'])
            )
            
            if st.button("تأكيد الدفعة"):
                st.success(f"تم تأكيد الدفعة {batch_number} بنجاح!")
                df_Receving1.loc[df_Receving1['Batch No'] == batch_number, 'Confirmed'] = 'Yes'
                df_Receving1.to_csv('Receving1.csv', index=False)
                
                log_entry = {
                    'user': st.session_state.username,
                    'time': datetime.now(egypt_tz).strftime('%Y-%m-%d %H:%M:%S'),
                    'Batch No': batch_number,
                    'operation': 'confirm'
                }
                st.session_state.logs_confirmation.append(log_entry)
                logs_df = pd.DataFrame(st.session_state.logs_confirmation)
                logs_df.to_csv('logs_confirmation.csv', index=False)
                st.experimental_rerun()
        else:
            st.error(f"الدفعة {batch_number} غير موجودة!")

users = load_users()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.logs_location, st.session_state.logs_receving, st.session_state.logs_confirmation = load_logs()
    st.session_state.logs = []

if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        username = st.text_input("اسم المستخدم")
        password = st.text_input("كلمة المرور", type="password")
        if st.button("تسجيل الدخول"):
            login(username, password)
else:
    if st.session_state.first_login:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.subheader("تغيير كلمة المرور")
            new_password = st.text_input("كلمة المرور الجديدة", type="password")
            confirm_new_password = st.text_input("تأكيد كلمة المرور الجديدة", type="password")
            if st.button("تحديث كلمة المرور"):
                if not new_password or not confirm_new_password:
                    st.error("يرجى إدخال كلا كلمتي المرور.")
                else:
                    update_password(st.session_state.username, new_password, confirm_new_password)
    else:
        st.sidebar.title(f"مرحباً، {st.session_state.username}")

        # Display batch details and confirmation interface
        display_batch_details_and_confirmation()
        
        # Option to add a new batch
        st.header("إضافة دفعة جديدة")
        with st.form(key='add_batch_form'):
            product_name = st.text_input("اسم المنتج")
            batch_no = st.text_input("رقم الدفعة")
            item_code = st.text_input("رمز الصنف")
            qty_pack = st.text_input("الكمية بالعبوة")
            date = st.date_input("التاريخ", min_value=datetime.now().date())
            delivered_by = st.text_input("تم تسليمها بواسطة")
            received_by = st.text_input("تم استلامها بواسطة")

            submit_button = st.form_submit_button("إضافة دفعة")
            if submit_button:
                add_new_Batch(st.session_state.username, product_name, batch_no, item_code, qty_pack, date, delivered_by, received_by)

        # Display current batch records
        st.header("سجلات الدفعات")
        try:
            df_Receving1 = pd.read_csv('Receving1.csv')
            st.dataframe(df_Receving1.style.applymap(lambda x: 'background-color: green' if x == 'Yes' else '', subset=['Confirmed']))
        except FileNotFoundError:
            st.error("ملف سجلات الدفعات غير موجود.")

        # Display logs
        st.header("سجلات الأنشطة")
        logs_df = pd.DataFrame(st.session_state.logs_receving)
        st.dataframe(logs_df)

        # Display all logs in separate sections
        st.subheader("Receiving Logs")
        if st.session_state.get('logs_receving', []):
            logs_df = pd.DataFrame(st.session_state.logs_receving)
            st.dataframe(logs_df)
            csv = logs_df.to_csv(index=False)
            st.download_button(label="Download Receiving Logs as CSV", data=csv, file_name='user_logs_receving.csv', mime='text/csv')
            if st.button("Clear Receiving Logs"):
                clear_logs("receiving")
        else:
            st.write("No receiving logs available.")
        
        st.subheader("Location Logs")
        if st.session_state.get('logs_location', []):
            logs_df = pd.DataFrame(st.session_state.logs_location)
            st.dataframe(logs_df)
            csv = logs_df.to_csv(index=False)
            st.download_button(label="Download Location Logs as CSV", data=csv, file_name='location_logs.csv', mime='text/csv')
            if st.button("Clear Location Logs"):
                clear_logs("location")
        else:
            st.write("No location logs available.")
        
        st.subheader("Confirmation Logs")
        if st.session_state.get('logs_confirmation', []):
            logs_df = pd.DataFrame(st.session_state.logs_confirmation)
            st.dataframe(logs_df)
            csv = logs_df.to_csv(index=False)
            st.download_button(label="Download Confirmation Logs as CSV", data=csv, file_name='logs_confirmation.csv', mime='text/csv')
            if st.button("Clear Confirmation Logs"):
                clear_logs("confirmation")
        else:
            st.write("No confirmation logs available.")

        # Option to logout
        if st.button("تسجيل الخروج"):
            st.session_state.logged_in = False
            st.experimental_rerun()
