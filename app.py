import streamlit as st
import database as db
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Finance Manager",
    page_icon="💰",
    layout="wide"
)

# Initialize database
db.init_db()

# Initialize session state for navigation
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Dashboard"
if 'selected_type' not in st.session_state:
    st.session_state.selected_type = "Income"
if 'selected_type' not in st.session_state:
    st.session_state.selected_type = "outcome"

# Custom CSS for professional look
st.markdown("""
    <style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.title("☰ Menu")
pages = ["Dashboard", "Input Data", "Table Report"]
current_index = pages.index(st.session_state.current_page)

def on_page_change():
    st.session_state.current_page = st.session_state.nav_page

st.sidebar.radio(
    "Pilih halaman:",
    pages,
    index=current_index,
    on_change=on_page_change,
    key="nav_page"
)

# --- DASHBOARD PAGE ---
if st.session_state.current_page == "Dashboard":
    st.markdown('<p class="main-header">💰 Dashboard Keuangan</p>', unsafe_allow_html=True)
    
    # Get summary data
    summary = db.get_summary()
    
    # Display Metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📈 Total Income", f"Rp {summary['total_income']:,.2f}", delta_color="normal")
    
    with col2:
        st.metric("📉 Total Outcome", f"Rp {summary['total_outcome']:,.2f}", delta_color="inverse")
        
    with col3:
        st.metric("💵 Sisa Saldo", f"Rp {summary['balance']:,.2f}")

    st.divider()
    
    # Quick Actions (as per flowchart "Tambah Income?" logic)
    st.subheader("🚀 Aksi Cepat")
    col_a, col_b = st.columns(2)
    with col_a:
        def go_to_income():
            st.session_state.selected_type = "Income"
            st.session_state.current_page = "Input Data"
            st.session_state.nav_page = "Input Data"
        
        if st.button("➕ Tambah Income", use_container_width=True, key="btn_income", help="Klik untuk menambah pendapatan", on_click=go_to_income):
            pass
            
    with col_b:
        def go_to_outcome():
            st.session_state.selected_type = "Outcome"
            st.session_state.current_page = "Input Data"
            st.session_state.nav_page = "Input Data"
        
        if st.button("➖ Tambah Outcome", use_container_width=True, key="btn_outcome", help="Klik untuk menambah pengeluaran", on_click=go_to_outcome):
            pass

# --- INPUT PAGE ---
elif st.session_state.current_page == "Input Data":
    st.markdown('<p class="main-header">📝 Input Transaksi</p>', unsafe_allow_html=True)
    
    # Determine default type from session state
    default_idx = 0 if st.session_state.selected_type == "Income" else 1

    with st.form("transaction_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            trans_type = st.radio("Tipe Transaksi", ["Income", "Outcome"], index=default_idx, horizontal=True)
            date_input = st.date_input("📅 Tanggal", datetime.now())
            amount = st.number_input("💵 Nominal (Rp)", min_value=0.0, step=1000.0, format="%.2f")
            
        with col2:
            if trans_type == "Income":
                category = st.selectbox("🏷️ Kategori Income", ["Gaji", "Bonus", "Investasi", "Lainnya"])
            else:
                category = st.selectbox("🏷️ Kategori Outcome", ["Makan", "Transport", "Belanja", "Tagihan", "Lainnya"])
            
            description = st.text_area("📝 Keterangan", height=107)
            
        submitted = st.form_submit_button("💾 Simpan Transaksi", use_container_width=True)
        
        if submitted:
            if amount > 0:
                db.add_transaction(trans_type, category, amount, description, date_input.strftime("%Y-%m-%d"))
                st.success(f"✅ Berhasil menyimpan {trans_type} sebesar Rp {amount:,.2f}")
                st.session_state.selected_type = trans_type
            else:
                st.error("❌ Nominal harus lebih besar dari 0")

# --- TABLE REPORT PAGE ---
elif st.session_state.current_page == "Table Report":
    st.markdown('<p class="main-header">📊 Laporan Transaksi</p>', unsafe_allow_html=True)
    
    data = db.get_transactions()
    
    if not data:
        st.info("📊 Belum ada data transaksi.")
    else:
        # Display data as a table
        st.dataframe(data, use_container_width=True, hide_index=True)
        
        st.divider()
        st.subheader("🔧 Kelola Data")
        
        # Select transaction to edit/delete
        options = {f"{d['date']} - {d['type']} - {d['description'][:30]} (Rp {d['amount']:,.0f})": d['id'] for d in data}
        selected_label = st.selectbox("Pilih data untuk Edit/Hapus:", list(options.keys()))
        selected_id = options[selected_label]
        
        if selected_id:
            col_edit, col_delete = st.columns(2)
            
            # --- DELETE LOGIC ---
            with col_delete:
                if st.button("🗑️ Hapus Data", type="primary", use_container_width=True, key=f"del_{selected_id}"):
                    st.session_state[f'confirm_delete_{selected_id}'] = True
                
                if st.session_state.get(f'confirm_delete_{selected_id}'):
                    st.warning("⚠️ Apakah anda yakin ingin menghapus data ini?")
                    col_yes, col_no = st.columns(2)
                    if col_yes.button("✅ Ya, Hapus", key=f"yes_{selected_id}"):
                        db.delete_transaction(selected_id)
                        st.session_state[f'confirm_delete_{selected_id}'] = False
                        st.success("✅ Data berhasil dihapus!")
                        st.rerun()
                    if col_no.button("❌ Batal", key=f"no_{selected_id}"):
                        st.session_state[f'confirm_delete_{selected_id}'] = False
                        st.rerun()

            # --- EDIT LOGIC ---
            with col_edit:
                with st.expander("✏️ Edit Data", expanded=True):
                    record = db.get_transaction_by_id(selected_id)
                    if record:
                        with st.form(f"edit_form_{selected_id}"):
                            e_type = st.selectbox("Tipe", ["Income", "Outcome"], index=0 if record['type'] == "Income" else 1, key=f"type_{selected_id}")
                            e_date = st.date_input("Tanggal", datetime.strptime(record['date'], "%Y-%m-%d"), key=f"date_{selected_id}")
                            e_amount = st.number_input("Nominal", value=record['amount'], min_value=0.0, key=f"amount_{selected_id}")
                            
                            cat_opts = ["Gaji", "Bonus", "Investasi", "Lainnya"] if e_type == "Income" else ["Makan", "Transport", "Belanja", "Tagihan", "Lainnya"]
                            try:
                                cat_index = cat_opts.index(record['category'])
                            except ValueError:
                                cat_index = 0
                            e_category = st.selectbox("Kategori", cat_opts, index=cat_index, key=f"cat_{selected_id}")
                            
                            e_desc = st.text_area("Keterangan", value=record['description'], key=f"desc_{selected_id}")
                            
                            if st.form_submit_button("💾 Simpan Perubahan", use_container_width=True):
                                db.update_transaction(selected_id, e_type, e_category, e_amount, e_desc, e_date.strftime("%Y-%m-%d"))
                                st.success("✅ Perubahan tersimpan!")
                                st.rerun()