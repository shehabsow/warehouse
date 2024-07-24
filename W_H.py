import streamlit as st
import pandas as pd
import pytz
from datetime import datetime, timedelta
import json
import csv
import os

st.set_page_config(
    layout="wide",
    page_title='Warehouse',
    page_icon='🪙')

egypt_tz = pytz.timezone('Africa/Cairo')
df_Material = pd.read_csv('matril.csv')

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

# Load batch status data
def load_batch_status():
    try:
        with open('batch_status.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Save batch status data to JSON file
def save_batch_status(batch_status):
    with open('batch_status.json', 'w') as f:
        json.dump(batch_status, f)

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

    return logs_location, logs_receving

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
        st.error("Incorrect username or password")

# Update password function
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

# Function to calculate packaging
def calculate_packaging(total_boxes):
    cartons_per_pallet = 12
    boxes_per_carton = 240

    cartons = total_boxes // boxes_per_carton
    boxes_left = total_boxes % boxes_per_carton

    pallets = cartons // cartons_per_pallet
    cartons_left = cartons % cartons_per_pallet

    return pallets, cartons_left, boxes_left

# Function to add new batch
def add_new_Batch(username, Product_Name, Batch_No, Item_Code, QTY_pack, Date, Delivered_by, Received_by):
    global df_Receving1
    try:
        QTY_pack_int = int(QTY_pack)
    except ValueError:
        st.error("The quantity must be a valid integer.")
        return

    pallets, cartons, boxes = calculate_packaging(QTY_pack_int)
    new_row = {
        'Product Name': Product_Name, 'Batch No': Batch_No, 'Item Code': Item_Code, 'QTY pack': QTY_pack,
        'Date': Date, 'Delivered by': Delivered_by, 'Received by': Received_by,
        'Pallets': pallets, 'Cartons': cartons, 'Boxes': boxes
    }
    df_Receving1 = df_Receving1.append(new_row, ignore_index=True)
    df_Receving1.to_csv('Receving1.csv', index=False)
    st.success(f"New item '{Batch_No}' added successfully with quantity {QTY_pack}!")
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

# Handle quantity change
def on_quantity_change(qty_pack):
    try:
        qty_pack = int(qty_pack)
        return calculate_packaging(qty_pack)
    except ValueError:
        st.error("Please enter a valid number for QTY pack.")
        return None, None, None

users = load_users()
batch_status = load_batch_status()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.logs_location, st.session_state.logs_receving1 = load_logs()

if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            login(username, password)
else:
    if st.session_state.first_login:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.subheader("Change Password")
            new_password = st.text_input("New Password", type="password")
            confirm_new_password = st.text_input("Confirm Password", type="password")
            if st.button("Update Password"):
                if not new_password or not confirm_new_password:
                    st.error("Please fill in all the fields.")
                else:
                    update_password(st.session_state.username, new_password, confirm_new_password)
    else:
        st.markdown(f"<div style='text-align: right; font-size: 20px; color: green;'> Login by : {users[st.session_state.username]['name']}</div>", unsafe_allow_html=True)

        # Load data frames
    if 'df' not in st.session_state:
        st.session_state.df = df_Material = pd.read_csv('matril.csv')
    try:
        df_BIN = pd.read_csv('LOCATION.csv')
    except FileNotFoundError:
        df_BIN = pd.DataFrame(columns=['Product Name', 'Item Code', 'Batch Number', "Warehouse Operator",
                                    'Quantity', 'Date', 'BIN1', 'QTY1', 'BIN2', 'QTY2', 'BIN3', 'QTY3'])
    
    try:
        df_Receving1 = pd.read_csv('Receving1.csv')
    except FileNotFoundError:
        df_Receving1 = pd.DataFrame(columns=['Product Name', "Batch No", 'Item Code', "QTY pack", "Date", "Delivered by", "Received by"])
    
    try:
        logs_df = pd.read_csv('logs_location.csv')
        st.session_state.logs_location = logs_df.to_dict('records')
    except FileNotFoundError:
        st.session_state.logs_location = []
    
    try:
        logs_df = pd.read_csv('logs_receving1.csv')
        st.session_state.logs_receving = logs_df.to_dict('records')
    except FileNotFoundError:
        st.session_state.logs_receving = []
    
    st.title('Warehouse Inventory System')
    st.sidebar.title('Navigation')
    
    menu = st.sidebar.radio('Go to', ['Receive Batch', 'View Batches', 'Log Out'])
    
    if menu == 'Receive Batch':
        st.header('Receive New Batch')
        with st.form(key='receive_form'):
            Product_Name = st.selectbox('Product Name', df_Material['Material Description'].dropna().values)
            Batch_No = st.text_input('Batch No')
            Item_Code = st.text_input('Item Code')
            QTY_pack = st.text_input('QTY pack', key='QTY_pack')
            Date = st.date_input('Date')
            Delivered_by = st.text_input('Delivered by')
            Received_by = st.text_input('Received by')
            
            if 'pallets' in st.session_state and 'cartons_left' in st.session_state and 'boxes_left' in st.session_state:
                st.write(f"Pallets: {st.session_state['pallets']}, Cartons left: {st.session_state['cartons_left']}, Boxes left: {st.session_state['boxes_left']}")
            
            submit_button = st.form_submit_button(label='Add New Batch')
        
        if submit_button:
            pallets, cartons_left, boxes_left = on_quantity_change(QTY_pack)
            if pallets is not None and cartons_left is not None and boxes_left is not None:
                st.session_state['pallets'] = pallets
                st.session_state['cartons_left'] = cartons_left
                st.session_state['boxes_left'] = boxes_left
                add_new_Batch(st.session_state.username, Product_Name, Batch_No, Item_Code, QTY_pack, Date, Delivered_by, Received_by)
    
    elif menu == 'View Batches':
        st.header('View Batches')
        for index, row in df_Receving1.iterrows():
            batch_no = row['Batch No']
            status = batch_status.get(batch_no, 'pending')
            color = {'confirmed': 'green', 'rejected': 'red', 'pending': 'yellow'}[status]
            st.markdown(f"**Batch No:** {row['Batch No']} **Status:** <span style='color:{color}'>{status}</span>", unsafe_allow_html=True)
            
            if st.session_state.username == 'engy':
                if status == 'pending':
                    if st.button('Confirm', key1=f'confirm_{batch_no}'):
                        batch_status[batch_no] = 'confirmed'
                        save_batch_status(batch_status)
                        st.experimental_rerun()
                    if st.button('Reject', key2=f'reject_{batch_no}'):
                        batch_status[batch_no] = 'rejected'
                        save_batch_status(batch_status)
                        st.experimental_rerun()
    
    elif menu == 'Log Out':
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.first_login = None
        st.session_state.password_expired = None
        st.experimental_rerun()
