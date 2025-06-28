import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Konfigurasi halaman
st.set_page_config(
    page_title="Dashboard Prodi X",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Judul dan header
st.title("📊 Dashboard Program Studi X")
st.markdown("---")

# Fungsi untuk memuat data
@st.cache_data
def load_data():
    """Memuat data dari file Excel dengan multiple sheets"""
    try:
        # Membaca semua sheet
        data_2017 = pd.read_excel('D:\Magister\JADWAL\Semester1\DI\DASHBOARD\data.xlsx', sheet_name='2017')
        data_2018 = pd.read_excel('D:\Magister\JADWAL\Semester1\DI\DASHBOARD\data.xlsx', sheet_name='2018')
        data_2019 = pd.read_excel('D:\Magister\JADWAL\Semester1\DI\DASHBOARD\data.xlsx', sheet_name='2019')
        
        # Membersihkan data IPK untuk setiap sheet
        data_2017 = clean_ipk_data(data_2017)
        data_2018 = clean_ipk_data(data_2018)
        data_2019 = clean_ipk_data(data_2019)
        
        # Menambahkan kolom angkatan
        data_2017['Angkatan'] = '2017'
        data_2018['Angkatan'] = '2018'
        data_2019['Angkatan'] = '2019'
        
        # Menggabungkan semua data
        all_data = pd.concat([data_2017, data_2018, data_2019], ignore_index=True)
        
        return all_data, data_2017, data_2018, data_2019
    except FileNotFoundError:
        st.error("File 'data.xlsx' tidak ditemukan. Pastikan file berada di direktori yang sama dengan script.")
        return None, None, None, None
    except Exception as e:
        st.error(f"Error saat membaca file: {str(e)}")
        return None, None, None, None

def clean_ipk_data(df):
    """Membersihkan dan memvalidasi data IPK"""
    if 'IPK' in df.columns:
        # Konversi ke numeric, replace non-numeric dengan NaN
        df['IPK'] = pd.to_numeric(df['IPK'], errors='coerce')
        
        # Batasi IPK antara 0.00 - 4.00
        df['IPK'] = df['IPK'].clip(lower=0.00, upper=4.00)
        
        # Bulatkan ke 2 desimal
        df['IPK'] = df['IPK'].round(2)
        
        # Hapus baris dengan IPK NaN atau invalid
        df = df.dropna(subset=['IPK'])
        
        # Warning jika ada data yang dikoreksi
        invalid_count = len(df[df['IPK'] > 4.00]) + len(df[df['IPK'] < 0.00])
        if invalid_count > 0:
            st.warning(f"⚠️ Ditemukan {invalid_count} data IPK tidak valid (>4.00 atau <0.00). Data telah dikoreksi.")
    
    return df

# Memuat data
all_data, data_2017, data_2018, data_2019 = load_data()

if all_data is not None:
    # Sidebar untuk filter
    st.sidebar.header("🔍 Filter Data")
    
    # Filter angkatan
    angkatan_options = ['Semua Angkatan', '2017', '2018', '2019']
    selected_angkatan = st.sidebar.selectbox("Pilih Angkatan:", angkatan_options)
    
    # Filter data berdasarkan angkatan
    if selected_angkatan == 'Semua Angkatan':
        filtered_data = all_data
        st.sidebar.info(f"Menampilkan data dari semua angkatan ({len(all_data)} mahasiswa)")
    else:
        filtered_data = all_data[all_data['Angkatan'] == selected_angkatan]
        st.sidebar.info(f"Menampilkan data angkatan {selected_angkatan} ({len(filtered_data)} mahasiswa)")
    
    # Dropdown presentase status
    st.sidebar.subheader("📈 Presentase Status Mahasiswa")
    status_counts = all_data['Status'].value_counts()
    total_mahasiswa = len(all_data)
    
    for status, count in status_counts.items():
        percentage = (count / total_mahasiswa) * 100
        st.sidebar.metric(
            label=f"{status}",
            value=f"{count} mahasiswa",
            delta=f"{percentage:.1f}%"
        )
    
    # Layout utama
    if len(filtered_data) > 0:
        # Metrics cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Mahasiswa", len(filtered_data))
        
        with col2:
            valid_ipk = filtered_data['IPK'][(filtered_data['IPK'] >= 0) & (filtered_data['IPK'] <= 4)]
            avg_ipk = valid_ipk.mean()
            st.metric("Rata-rata IPK", f"{avg_ipk:.2f}")
        
        with col3:
            max_ipk = valid_ipk.max()
            st.metric("IPK Tertinggi", f"{max_ipk:.2f}")
        
        with col4:
            min_ipk = valid_ipk.min()
            st.metric("IPK Terendah", f"{min_ipk:.2f}")
        
        st.markdown("---")
        
        # Visualisasi dalam 2 kolom
        col1, col2 = st.columns(2)
        
        with col1:
            # Histogram IPK
            st.subheader("📊 Sebaran IPK Mahasiswa")
            
            # Validasi IPK sebelum membuat histogram
            valid_ipk = filtered_data['IPK'][(filtered_data['IPK'] >= 0) & (filtered_data['IPK'] <= 4)]
            
            fig_hist = px.histogram(
                x=valid_ipk, 
                nbins=20,
                title=f"Distribusi IPK - {selected_angkatan}",
                labels={'x': 'Indeks Prestasi Kumulatif (IPK)', 'y': 'Jumlah Mahasiswa'},
                color_discrete_sequence=['#FF6B6B'],
                range_x=[0, 4.0]  # Batasi sumbu X dari 0 sampai 4
            )
            fig_hist.update_layout(
                xaxis_title="IPK (0.00 - 4.00)",
                yaxis_title="Jumlah Mahasiswa",
                showlegend=False,
                height=400
            )
            # Tambahkan garis vertikal untuk rata-rata IPK
            avg_ipk = valid_ipk.mean()
            fig_hist.add_vline(x=avg_ipk, line_dash="dash", line_color="red", 
                              annotation_text=f"Rata-rata: {avg_ipk:.2f}")
            
            st.plotly_chart(fig_hist, use_container_width=True)
            
            # Informasi tambahan tentang IPK
            col_ipk1, col_ipk2 = st.columns(2)
            with col_ipk1:
                st.info(f"📊 **Kategori IPK:**\n- Cum Laude: ≥ 3.50\n- Sangat Memuaskan: 3.00-3.49\n- Memuaskan: 2.75-2.99")
            with col_ipk2:
                # Hitung kategori IPK
                cum_laude = len(valid_ipk[valid_ipk >= 3.50])
                sangat_memuaskan = len(valid_ipk[(valid_ipk >= 3.00) & (valid_ipk < 3.50)])
                memuaskan = len(valid_ipk[(valid_ipk >= 2.75) & (valid_ipk < 3.00)])
                st.success(f"🏆 **Prestasi:**\n- Cum Laude: {cum_laude} mhs\n- Sangat Memuaskan: {sangat_memuaskan} mhs\n- Memuaskan: {memuaskan} mhs")
            
            # Statistik IPK
            st.subheader("📈 Statistik IPK")
            valid_ipk = filtered_data['IPK'][(filtered_data['IPK'] >= 0) & (filtered_data['IPK'] <= 4)]
            ipk_stats = valid_ipk.describe()
            
            stats_df = pd.DataFrame({
                'Statistik': ['Jumlah Data', 'Rata-rata', 'Std Deviasi', 'IPK Minimum', 
                            'Kuartil 1 (25%)', 'Median (50%)', 'Kuartil 3 (75%)', 'IPK Maksimum'],
                'Nilai': [f"{ipk_stats['count']:.0f}", f"{ipk_stats['mean']:.2f}", 
                         f"{ipk_stats['std']:.3f}", f"{ipk_stats['min']:.2f}",
                         f"{ipk_stats['25%']:.2f}", f"{ipk_stats['50%']:.2f}",
                         f"{ipk_stats['75%']:.2f}", f"{ipk_stats['max']:.2f}"]
            })
            st.dataframe(stats_df, use_container_width=True, hide_index=True)
        
        with col2:
            # Pie Chart Status
            st.subheader("🍰 Status Mahasiswa")
            status_counts = filtered_data['Status'].value_counts()
            
            fig_pie = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title=f"Distribusi Status - {selected_angkatan}",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie.update_layout(height=400)
            st.plotly_chart(fig_pie, use_container_width=True)
            
            # Bar Chart sebaran mahasiswa (hanya untuk semua angkatan)
            if selected_angkatan == 'Semua Angkatan':
                st.subheader("📊 Sebaran Mahasiswa per Angkatan")
                angkatan_counts = all_data['Angkatan'].value_counts().sort_index()
                
                fig_bar = px.bar(
                    x=angkatan_counts.index,
                    y=angkatan_counts.values,
                    title="Jumlah Mahasiswa per Angkatan",
                    labels={'x': 'Angkatan', 'y': 'Jumlah Mahasiswa'},
                    color=angkatan_counts.values,
                    color_continuous_scale='Blues',
                    text=angkatan_counts.values,
                    category_orders={'x': ['2017', '2018', '2019']}  # Urutkan tahun
                )
                fig_bar.update_layout(
                    xaxis_title="Angkatan",
                    yaxis_title="Jumlah Mahasiswa",
                    showlegend=False,
                    height=350,
                    yaxis=dict(
                        range=[0, 300],  # Maksimal sumbu Y = 300
                        dtick=50  # Interval tick setiap 50
                    ),
                    xaxis=dict(
                        type='category',  # Pastikan X axis sebagai kategori
                        categoryorder='array',
                        categoryarray=['2017', '2018', '2019']
                    )
                )
                fig_bar.update_traces(texttemplate='%{text}', textposition='outside')
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                # Info bahwa sebaran mahasiswa tidak ditampilkan untuk filter angkatan tertentu
                st.subheader("📊 Sebaran Mahasiswa")
                st.info(f"💡 **Sebaran mahasiswa hanya ditampilkan untuk 'Semua Angkatan'**\n\n"
                       f"Saat ini menampilkan data untuk angkatan **{selected_angkatan}** "
                       f"dengan total **{len(filtered_data)} mahasiswa**.\n\n"
                       f"Ubah filter ke 'Semua Angkatan' untuk melihat perbandingan jumlah mahasiswa antar angkatan.")
                
                # Tampilkan informasi ringkas angkatan yang dipilih
                col_info1, col_info2, col_info3 = st.columns(3)
                with col_info1:
                    aktif_count = len(filtered_data[filtered_data['Status'] == 'Aktif']) if 'Aktif' in filtered_data['Status'].values else 0
                    st.metric("Mahasiswa Aktif", aktif_count)
                with col_info2:
                    lulus_count = len(filtered_data[filtered_data['Status'] == 'Lulus']) if 'Lulus' in filtered_data['Status'].values else 0
                    st.metric("Mahasiswa Lulus", lulus_count)
                with col_info3:
                    avg_ipk_angkatan = filtered_data['IPK'][(filtered_data['IPK'] >= 0) & (filtered_data['IPK'] <= 4)].mean()
                    st.metric("Rata-rata IPK", f"{avg_ipk_angkatan:.2f}")
        
        # Tabel data (opsional)
        st.markdown("---")
        st.subheader("📋 Data Mahasiswa")
        
        # Checkbox untuk menampilkan data
        show_data = st.checkbox("Tampilkan tabel data")
        if show_data:
            st.dataframe(filtered_data, use_container_width=True)
            
            # Download data
            csv = filtered_data.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download data sebagai CSV",
                data=csv,
                file_name=f'data_prodi_x_{selected_angkatan.lower().replace(" ", "_")}.csv',
                mime='text/csv'
            )
    
    else:
        st.warning("Tidak ada data untuk ditampilkan dengan filter yang dipilih.")

else:
    # Contoh data jika file tidak ditemukan
    st.warning("File data.xlsx tidak ditemukan. Menampilkan contoh dashboard dengan data dummy.")
    
    # Membuat data dummy
    np.random.seed(42)
    dummy_data = []
    
    for angkatan in ['2017', '2018', '2019']:
        n_students = np.random.randint(50, 100)
        for i in range(n_students):
            # Pastikan IPK dummy juga dalam range 0-4
            ipk_dummy = np.random.normal(3.2, 0.4)
            ipk_dummy = max(0.00, min(4.00, ipk_dummy))  # Batasi 0-4
            
            dummy_data.append({
                'No': i + 1,
                'IPK': round(ipk_dummy, 2),  # Bulatkan ke 2 desimal
                'Status': np.random.choice(['Aktif', 'Cuti', 'Lulus', 'DO'], p=[0.6, 0.1, 0.25, 0.05]),
                'Angkatan': angkatan
            })
    
    dummy_df = pd.DataFrame(dummy_data)
    
    st.info("Menggunakan data dummy untuk demonstrasi")
    
    # Menampilkan dashboard dengan data dummy
    st.subheader("🎯 Dashboard Demo")
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Mahasiswa", len(dummy_df))
    with col2:
        st.metric("Rata-rata IPK", f"{dummy_df['IPK'].mean():.2f}")
    with col3:
        st.metric("Jumlah Angkatan", dummy_df['Angkatan'].nunique())
    
    # Visualisasi dummy
    col1, col2 = st.columns(2)
    
    with col1:
        fig_hist = px.histogram(
            dummy_df, 
            x='IPK', 
            title="Distribusi IPK (Demo)",
            range_x=[0, 4.0],  # Batasi sumbu X
            nbins=20
        )
        fig_hist.update_layout(xaxis_title="IPK (0.00 - 4.00)")
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        status_counts = dummy_df['Status'].value_counts()
        fig_pie = px.pie(values=status_counts.values, names=status_counts.index, 
                        title="Status Mahasiswa (Demo)")
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Sebaran mahasiswa dummy (hanya untuk demo semua angkatan)
    st.subheader("📊 Sebaran Mahasiswa per Angkatan (Demo)")
    angkatan_counts = dummy_df['Angkatan'].value_counts().sort_index()
    fig_bar = px.bar(
        x=angkatan_counts.index,
        y=angkatan_counts.values,
        title="Jumlah Mahasiswa per Angkatan",
        text=angkatan_counts.values,
        category_orders={'x': ['2017', '2018', '2019']}
    )
    fig_bar.update_layout(
        yaxis=dict(
            range=[0, 300],  # Maksimal sumbu Y = 300
            dtick=50  # Interval tick setiap 50
        ),
        xaxis=dict(
            type='category',
            categoryorder='array',
            categoryarray=['2017', '2018', '2019']
        )
    )
    fig_bar.update_traces(texttemplate='%{text}', textposition='outside')
    st.plotly_chart(fig_bar, use_container_width=True)
st.markdown("---")
st.markdown("*Dashboard Program Studi X - Powered by Streamlit*")