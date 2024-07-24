import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
import pytz
import os

# تعيين المنطقة الزمنية لمصر
egypt_tz = pytz.timezone('Africa/Cairo')

# تحميل بيانات المستخدمين من ملف JSON
def load_users():
    try:
        with open('users5.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "knhp322": {"password": "knhp322", "first_login": True, "name": "Shehab Ayman", "last_password_update": str(datetime.now(egypt_tz))},
            "krxs742": {"password": "krxs742", "first_login": True, "name": "Mohamed Ashry", "last_password_update": str(datetime.now(egypt_tz))},
            "kxsv748": {"password": "kxsv748", "first_login": True, "name": "Mohamed El masry", "last_password_update": str(datetime.now(egypt_tz))},
            "kvwp553": {"password": "kvwp553", "first_login": True, "name": "sameh", "last_password_update": str(datetime.now(egypt_tz))},
            "knfb489": {"password": "knfb489", "first_login": True, "name": "Yasser Hassan", "last_password_update": str(datetime.now(egypt_tz))},
            "kjjd308": {"password": "kjjd308", "first_login": True, "name": "Kaleed", "last_password_update": str(datetime.now(egypt_tz))},
            "kibx268": {"password": "kibx268", "first_login": True, "name": "Zeinab Mobarak", "last_password_update": str(datetime.now(egypt_tz))},
            "engy": {"password": "1234", "first_login": True, "name": "D.Engy", "last_password_update": str(datetime.now(egypt_tz))}
        }

# حفظ بيانات المستخدمين إلى ملف JSON
def save_users(users):
    with open('users5.json', 'w') as f:
        json.dump(users, f)

users = load_users()

# تحميل التنبيهات من ملف JSON
def load_alerts():
    try:
        with open('alerts.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# حفظ التنبيهات إلى ملف JSON
def save_alerts(alerts):
    with open('alerts.json', 'w') as f:
        json.dump(alerts, f)

st.session_state.alerts = load_alerts()

# تحميل سجلات التحديث من ملف JSON
def load_update_logs():
    try:
        with open('update_logs.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# حفظ سجلات التحديث إلى ملف JSON
def save_update_logs(update_logs):
    with open('update_logs.json', 'w') as f:
        json.dump(update_logs, f)

st.session_state.update_logs = load_update_logs()

# دالة لتسجيل الدخول
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
        st.error("Incorrect username or password")

# دالة لتحديث كلمة المرور
def update_password(username, new_password, confirm_new_password):
    if new_password == confirm_new_password:
        users[username]["password"] = new_password
        users[username]["first_login"] = False
        users[username]["last_password_update"] = str(datetime.now(egypt_tz))
        save_users(users)
        st.session_state.first_login = False
        st.session_state.password_expired = False
        st.success("Password updated successfully!")
    else:
        st.error("Passwords do not match!")

# دالة لتحديث الكمية
def update_quantity(row_index, quantity, operation, username):
    old_quantity = st.session_state.df.loc[row_index, 'Actual Quantity']
    if operation == 'add':
        st.session_state.df.loc[row_index, 'Actual Quantity'] += quantity
    elif operation == 'subtract':
        st.session_state.df.loc[row_index, 'Actual Quantity'] -= quantity
    new_quantity = st.session_state.df.loc[row_index, 'Actual Quantity']
    st.session_state.df.to_csv('matril.csv', index=False)
    st.success(f"Quantity updated successfully by {username}! New Quantity: {int(st.session_state.df.loc[row_index, 'Actual Quantity'])}")
    log_entry = {
        'user': username,
        'time': datetime.now(egypt_tz).strftime('%Y-%m-%d %H:%M:%S'),
        'item': st.session_state.df.loc[row_index, 'Item Name'],
        'old_quantity': old_quantity,
        'new_quantity': new_quantity,
        'operation': operation
    }
    st.session_state.logs.append(log_entry)
    
    # حفظ السجلات إلى ملف CSV
    logs_df = pd.DataFrame(st.session_state.logs)
    logs_df.to_csv('logs.csv', index=False)
    
    # تحقق من الكميات وتحديث التنبيهات
    check_quantities()

# دالة للتحقق من الكميات الحالية وعرض التنبيهات
def check_quantities():
    new_alerts = []
    for index, row in st.session_state.df.iterrows():
        if row['Actual Quantity'] < 100:  # تغيير القيمة حسب الحاجة
            new_alerts.append(row['Item Name'])
    
    st.session_state.alerts = new_alerts
    save_alerts(st.session_state.alerts)

# دالة للتحقق من الكميات لكل تبويب وعرض التنبيهات
def check_tab_quantities(tab_name, min_quantity):
    tab_alerts = []
    df_tab = st.session_state.df[st.session_state.df['Item Name'] == tab_name]
    return tab_alerts, df_tab

# دالة لتأكيد أو رفض الكمية
def confirm_or_reject_batch(row_index, status):
    st.session_state.df.loc[row_index, 'Status'] = status
    st.session_state.update_logs.append({
        'user': st.session_state.username,
        'time': datetime.now(egypt_tz).strftime('%Y-%m-%d %H:%M:%S'),
        'item': st.session_state.df.loc[row_index, 'Item Name'],
        'status': status
    })
    save_update_logs(st.session_state.update_logs)

# عرض التبويبات
def display_tab(tab_name, min_quantity):
    st.header(f'{tab_name}')
    row_number = st.number_input(f'Select row number for {tab_name}:', min_value=0, max_value=len(st.session_state.df)-1, step=1, key=f'{tab_name}_row_number')
    
    st.markdown(f"""
    <div style='font-size: 20px; color: blue;'>Selected Item: {st.session_state.df.loc[row_number, 'Item Name']}</div>
    <div style='font-size: 20px; color: blue;'>Current Quantity: {int(st.session_state.df.loc[row_number, 'Actual Quantity'])}</div>
    """, unsafe_allow_html=True)
    
    quantity = st.number_input(f'Enter quantity for {tab_name}:', min_value=1, step=1, key=f'{tab_name}_quantity')
    operation = st.radio(f'Choose operation for {tab_name}:', ('add', 'subtract'), key=f'{tab_name}_operation')

    if st.button('Update Quantity', key=f'{tab_name}_update_button'):
        update_quantity(row_number, quantity, operation, st.session_state.username)
    
    tab_alerts, df_tab = check_tab_quantities(tab_name, min_quantity)
    if tab_alerts:
        st.error(f"Low stock for items in {tab_name}: {', '.join(tab_alerts)}")
        st.write(f"Items in {tab_name} with low stock:")
        st.dataframe(df_tab.style.applymap(lambda x: 'background-color: red' if x < min_quantity else '', subset=['Actual Quantity']))

    # زرين لتأكيد أو رفض الكمية
    if st.session_state.username == "shehabayman":  # تأكيد فقط لمستخدم محدد
        if st.button('Confirm Quantity', key=f'{tab_name}_confirm_button'):
            confirm_or_reject_batch(row_number, 'confirmed')
        if st.button('Reject Quantity', key=f'{tab_name}_reject_button'):
            confirm_or_reject_batch(row_number, 'rejected')

# تحميل البيانات من ملف CSV
if 'df' not in st.session_state:
    st.session_state.df = pd.read_csv('matril.csv')
    st.session_state.logs = []

# واجهة المستخدم لتسجيل الدخول
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    if st.button("Login"):
        login(username, password)

# تغيير كلمة المرور عند تسجيل الدخول لأول مرة أو انتهاء صلاحية كلمة المرور
elif st.session_state.first_login or st.session_state.password_expired:
    st.title("Update Password")
    new_password = st.text_input("New Password", type='password')
    confirm_new_password = st.text_input("Confirm New Password", type='password')
    if st.button("Update Password"):
        update_password(st.session_state.username, new_password, confirm_new_password)

# واجهة المستخدم الرئيسية بعد تسجيل الدخول
else:
    st.title(f"Welcome, {users[st.session_state.username]['name']}")

    st.sidebar.title("Navigation")
    option = st.sidebar.selectbox("Select an option", ["View Items", "Receiving Logs", "Location Logs"])

    if option == "View Items":
        st.header("Find your Mechanical parts")
        search_keyword = st.text_input("Enter keyword to search:")

        if search_keyword:
            filtered_df = st.session_state.df[st.session_state.df['Item Name'].str.contains(search_keyword, case=False)]
            st.dataframe(filtered_df)
        else:
            st.write("Please enter a keyword to search.")

    elif option == "Receiving Logs":
        st.subheader("Receiving Logs")
        if 'logs_receving' in st.session_state:
            logs_df = pd.DataFrame(st.session_state.logs_receving)
            st.dataframe(logs_df)
            csv = logs_df.to_csv(index=False)
            st.download_button(label="Download Logs as CSV", data=csv, file_name='user_logs_receving.csv', mime='text/csv')
            if st.button("Clear Receiving Logs"):
                st.session_state.logs_receving = []
                if os.path.exists('user_logs_receving.csv'):
                    os.remove('user_logs_receving.csv')
                st.success("Receiving logs cleared successfully!")
        else:
            st.write("No receiving logs available.")

    elif option == "Location Logs":
        st.subheader("Location Logs")
        if 'logs_location' in st.session_state:
            logs_df = pd.DataFrame(st.session_state.logs_location)
            st.dataframe(logs_df)
            csv = logs_df.to_csv(index=False)
            st.download_button(label="Download Logs as CSV", data=csv, file_name='location_logs.csv', mime='text/csv')
            if st.button("Clear Location Logs"):
                st.session_state.logs_location = []
                if os.path.exists('location_logs.csv'):
                    os.remove('location_logs.csv')
                st.success("Location logs cleared successfully!")
        else:
            st.write("No location logs available.")
        
        # عرض التبويبات وتخصيص الزرين لمستخدم محدد
        display_tab('Reel for Item Label (Small)', 100)
        display_tab('Reel for Item Label (Large)', 100)
        display_tab('Ink Reels for Item Label', 50)
        display_tab('Red Tape', 200)
        display_tab('Adhesive Tape', 150)
        display_tab('Cartridges', 300)
        display_tab('MultiPharma Cartridge', 50)
