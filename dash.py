import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Konfigurasi halaman Streamlit
st.set_page_config(
    page_title="Dashboard Data Mahasiswa",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS untuk styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1f77b4;
    }
    .info-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #1f77b4;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Fungsi untuk memuat data
@st.cache_data
def load_data():
    """Memuat data dari file Excel dengan multiple sheets"""
    try:
        excel_file = pd.ExcelFile('data.xlsx')
        data_dict = {}
        
        # Membaca data dari setiap sheet (2017, 2018, 2019)
        for sheet_name in ['2017', '2018', '2019']:
            if sheet_name in excel_file.sheet_names:
                df = pd.read_excel('data.xlsx', sheet_name=sheet_name)
                data_dict[sheet_name] = df
                st.sidebar.success(f"✅ Sheet '{sheet_name}' dimuat: {len(df)} records")
            else:
                st.sidebar.warning(f"⚠️ Sheet '{sheet_name}' tidak ditemukan")
        
        return data_dict
    except FileNotFoundError:
        st.error("❌ File 'data.xlsx' tidak ditemukan! Pastikan file berada di direktori yang sama dengan script ini.")
        st.info("📁 Letakkan file 'data.xlsx' di folder yang sama dengan file Python ini.")
        return None
    except Exception as e:
        st.error(f"❌ Error saat membaca file: {str(e)}")
        return None

# Fungsi untuk validasi kolom
def validate_columns(df, required_columns):
    """Validasi keberadaan kolom yang diperlukan"""
    missing_columns = [col for col in required_columns if col not in df.columns]
    return missing_columns

# Fungsi untuk membuat line chart
def create_line_chart(df, year):
    """Membuat line chart untuk sebaran IPK"""
    # Buat distribusi IPK
    ipk_counts = df['IPK'].value_counts().sort_index()
    
    fig = px.line(
        x=ipk_counts.index, 
        y=ipk_counts.values,
        title=f"📈 Sebaran IPK Mahasiswa - Angkatan {year}",
        labels={'x': 'IPK', 'y': 'Jumlah Mahasiswa'},
        markers=True,
        line_shape='spline'
    )
    
    fig.update_traces(
        marker=dict(size=8, color='#1f77b4'),
        line=dict(width=3, color='#1f77b4')
    )
    
    fig.update_layout(
        xaxis_title="IPK",
        yaxis_title="Jumlah Mahasiswa",
        showlegend=False,
        height=400,
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    # Tambahkan grid
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    
    return fig

# Fungsi untuk membuat bar chart
def create_bar_chart(df, year):
    """Membuat bar chart untuk sebaran jumlah mahasiswa per kategori IPK"""
    # Buat kategori IPK
    bins = [0, 2.0, 2.5, 3.0, 3.5, 4.0]
    labels = ['< 2.0', '2.0 - 2.5', '2.5 - 3.0', '3.0 - 3.5', '3.5 - 4.0']
    
    df['IPK_Kategori'] = pd.cut(df['IPK'], bins=bins, labels=labels, include_lowest=True)
    kategori_counts = df['IPK_Kategori'].value_counts().reindex(labels, fill_value=0)
    
    # Warna untuk setiap kategori
    colors = ['#ff6b6b', '#ffa500', '#ffed4e', '#51cf66', '#339af0']
    
    fig = px.bar(
        x=kategori_counts.index,
        y=kategori_counts.values,
        title=f"📊 Distribusi Mahasiswa per Kategori IPK - Angkatan {year}",
        labels={'x': 'Kategori IPK', 'y': 'Jumlah Mahasiswa'},
        color=kategori_counts.values,
        color_continuous_scale='viridis'
    )
    
    fig.update_traces(
        marker_color=colors[:len(kategori_counts)],
        text=kategori_counts.values,
        textposition='outside'
    )
    
    fig.update_layout(
        xaxis_title="Kategori IPK",
        yaxis_title="Jumlah Mahasiswa",
        showlegend=False,
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

# Fungsi untuk membuat pie chart
def create_pie_chart(df, year):
    """Membuat pie chart untuk status mahasiswa"""
    status_counts = df['Status'].value_counts()
    
    fig = px.pie(
        values=status_counts.values,
        names=status_counts.index,
        title=f"🥧 Distribusi Status Mahasiswa - Angkatan {year}",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        textfont_size=12,
        marker=dict(line=dict(color='#FFFFFF', width=2))
    )
    
    fig.update_layout(
        height=400,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.01
        )
    )
    
    return fig

# Fungsi untuk menghitung statistik
def calculate_statistics(df):
    """Menghitung statistik dasar dari data"""
    stats = {
        'total_mahasiswa': len(df),
        'ipk_rata_rata': df['IPK'].mean(),
        'ipk_tertinggi': df['IPK'].max(),
        'ipk_terendah': df['IPK'].min(),
        'ipk_median': df['IPK'].median(),
        'ipk_std': df['IPK'].std(),
        'status_terbanyak': df['Status'].mode()[0] if len(df['Status'].mode()) > 0 else 'N/A'
    }
    return stats

# Main function
def main():
    # Header
    st.markdown('<h1 class="main-header">📊 Dashboard Visualisasi Data Mahasiswa</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Load data
    with st.spinner("📂 Memuat data..."):
        data_dict = load_data()
    
    if not data_dict:
        st.error("Tidak dapat memuat data. Silakan periksa file dan coba lagi.")
        st.info("""
        **Struktur file yang diharapkan:**
        - Nama file: `data.xlsx`
        - Sheet: `2017`, `2018`, `2019`
        - Kolom yang diperlukan: `No`, `IPK`, `Status`
        """)
        return
    
    # Sidebar untuk filter dan info
    st.sidebar.header("🔍 Filter & Kontrol")
    
    # Dropdown untuk memilih tahun angkatan
    available_years = list(data_dict.keys())
    selected_year = st.sidebar.selectbox(
        "📅 Pilih Tahun Angkatan:",
        options=available_years,
        index=0,
        help="Pilih tahun angkatan untuk ditampilkan"
    )
    
    # Ambil data berdasarkan tahun yang dipilih
    df = data_dict[selected_year]
    
    # Validasi kolom
    required_columns = ['IPK', 'No', 'Status']
    missing_columns = validate_columns(df, required_columns)
    
    if missing_columns:
        st.error(f"❌ Kolom berikut tidak ditemukan: {', '.join(missing_columns)}")
        st.info(f"📋 Kolom yang tersedia: {', '.join(df.columns)}")
        return
    
    # Hitung statistik
    stats = calculate_statistics(df)
    
    # Sidebar info
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Informasi Data")
    st.sidebar.markdown(f"**Tahun Angkatan:** {selected_year}")
    st.sidebar.markdown(f"**Total Mahasiswa:** {stats['total_mahasiswa']}")
    st.sidebar.markdown(f"**IPK Rata-rata:** {stats['ipk_rata_rata']:.2f}")
    st.sidebar.markdown(f"**Status Terbanyak:** {stats['status_terbanyak']}")
    
    # Tombol refresh
    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
    # Main content area
    # Metrics cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="👥 Total Mahasiswa",
            value=stats['total_mahasiswa'],
            help="Jumlah total mahasiswa dalam angkatan"
        )
    
    with col2:
        st.metric(
            label="📈 IPK Rata-rata",
            value=f"{stats['ipk_rata_rata']:.2f}",
            delta=f"±{stats['ipk_std']:.2f}",
            help="IPK rata-rata dengan standar deviasi"
        )
    
    with col3:
        st.metric(
            label="🏆 IPK Tertinggi",
            value=f"{stats['ipk_tertinggi']:.2f}",
            help="IPK tertinggi dalam angkatan"
        )
    
    with col4:
        high_achievers = len(df[df['IPK'] >= 3.5])
        high_achievers_pct = (high_achievers / len(df)) * 100
        st.metric(
            label="⭐ IPK ≥ 3.5",
            value=high_achievers,
            delta=f"{high_achievers_pct:.1f}%",
            help="Jumlah mahasiswa dengan IPK 3.5 ke atas"
        )
    
    st.markdown("---")
    
    # Visualisasi dalam layout grid
    # Baris pertama: Line Chart dan Bar Chart
    col1, col2 = st.columns(2)
    
    with col1:
        try:
            line_fig = create_line_chart(df, selected_year)
            st.plotly_chart(line_fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error membuat line chart: {str(e)}")
    
    with col2:
        try:
            bar_fig = create_bar_chart(df, selected_year)
            st.plotly_chart(bar_fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error membuat bar chart: {str(e)}")
    
    # Baris kedua: Pie Chart dan Statistik Detail
    col3, col4 = st.columns([2, 1])
    
    with col3:
        try:
            pie_fig = create_pie_chart(df, selected_year)
            st.plotly_chart(pie_fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error membuat pie chart: {str(e)}")
    
    with col4:
        st.markdown("### 📋 Detail Statistik")
        
        # Status distribution
        st.markdown("**Distribusi Status:**")
        status_counts = df['Status'].value_counts()
        for status, count in status_counts.items():
            percentage = (count / len(df)) * 100
            st.write(f"• {status}: {count} ({percentage:.1f}%)")
        
        st.markdown("---")
        
        # IPK categories
        st.markdown("**Kategori Prestasi:**")
        excellent = len(df[df['IPK'] >= 3.5])
        good = len(df[(df['IPK'] >= 3.0) & (df['IPK'] < 3.5)])
        fair = len(df[(df['IPK'] >= 2.5) & (df['IPK'] < 3.0)])
        poor = len(df[df['IPK'] < 2.5])
        
        st.write(f"• Sangat Baik (≥3.5): {excellent}")
        st.write(f"• Baik (3.0-3.5): {good}")
        st.write(f"• Cukup (2.5-3.0): {fair}")
        st.write(f"• Kurang (<2.5): {poor}")
    
    # Tabel data detail
    st.markdown("---")
    st.subheader(f"📋 Data Detail - Angkatan {selected_year}")
    
    # Filter untuk tabel
    with st.expander("🔧 Filter Tabel", expanded=False):
        col_filter1, col_filter2 = st.columns(2)
        
        with col_filter1:
            status_filter = st.multiselect(
                "Filter Status:",
                options=df['Status'].unique(),
                default=df['Status'].unique(),
                help="Pilih status yang ingin ditampilkan"
            )
        
        with col_filter2:
            ipk_range = st.slider(
                "Range IPK:",
                min_value=float(df['IPK'].min()),
                max_value=float(df['IPK'].max()),
                value=(float(df['IPK'].min()), float(df['IPK'].max())),
                step=0.1,
                help="Pilih rentang IPK"
            )
    
    # Apply filters
    filtered_df = df[
        (df['Status'].isin(status_filter)) &
        (df['IPK'] >= ipk_range[0]) &
        (df['IPK'] <= ipk_range[1])
    ]
    
    st.info(f"📊 Menampilkan {len(filtered_df)} dari {len(df)} mahasiswa")
    
    # Tampilkan tabel dengan paginasi
    if len(filtered_df) > 0:
        # Opsi untuk download
        col_download1, col_download2 = st.columns(2)
        
        with col_download1:
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"data_mahasiswa_{selected_year}.csv",
                mime="text/csv"
            )
        
        with col_download2:
            if st.button("📊 Tampilkan Semua Data"):
                st.dataframe(filtered_df, use_container_width=True, height=400)
    else:
        st.warning("Tidak ada data yang sesuai dengan filter yang dipilih.")

# Fungsi untuk menjalankan aplikasi
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"❌ Terjadi error: {str(e)}")
        st.info("Silakan refresh halaman atau periksa file data Anda.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 1rem;'>
            📊 Dashboard Data Mahasiswa | Dibuat dengan Streamlit & Plotly<br>
            💡 Tip: Gunakan sidebar untuk memilih angkatan dan melihat informasi detail
        </div>
        """,
        unsafe_allow_html=True
    )