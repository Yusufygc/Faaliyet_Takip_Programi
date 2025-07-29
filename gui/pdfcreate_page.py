import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime
import os
from database import get_connection
# pdfcreate_page.py
def create_statistics_pdf(pdf_params):
    """
    İstatistik verilerine göre PDF raporu oluşturur
    
    Args:
        pdf_params (dict): PDF oluşturma parametreleri
            - file_path: PDF dosya yolu
            - date: Seçilen tarih
            - year_mode: Yıl modunda mı (bool)
            - include_monthly_chart: Aylık grafik dahil edilsin mi
            - include_yearly_chart: Yıllık grafik dahil edilsin mi
            - current_data: Mevcut istatistik verileri
    """
    # Set the font to support Turkish characters
    plt.rcParams['font.family'] = 'DejaVu Sans'
    
    file_path = pdf_params['file_path']
    date = pdf_params['date']
    year_mode = pdf_params['year_mode']
    include_monthly = pdf_params['include_monthly_chart']
    include_yearly = pdf_params['include_yearly_chart']
    current_data = pdf_params['current_data']
    
    # PDF oluşturma
    with PdfPages(file_path) as pdf:
        # Başlık sayfası
        create_title_page(pdf, date, year_mode)
        
        # Veri tablosu sayfası
        if current_data:
            create_data_table_page(pdf, current_data, date, year_mode)
        
        # Aylık grafik sayfası
        if include_monthly and not year_mode:
            create_monthly_chart_page(pdf, date)
        
        # Yıllık grafik sayfası  
        if include_yearly:
            create_yearly_chart_page(pdf, date[:4] if year_mode else date[:4])
        
        # Özet sayfa
        create_summary_page(pdf, current_data, date, year_mode)

def create_title_page(pdf, date, year_mode):
    """PDF başlık sayfasını oluşturur"""
    fig, ax = plt.subplots(figsize=(8.27, 11.69))  # A4 boyutu
    ax.axis('off')
    
    # Başlık
    ax.text(0.5, 0.8, 'FAALİYET İSTATİSTİKLERİ', 
            fontsize=24, fontweight='bold', ha='center', va='center')
    
    ax.text(0.5, 0.7, 'RAPORU', 
            fontsize=20, fontweight='bold', ha='center', va='center')
    
    # Tarih bilgisi
    if year_mode:
        period_text = f"Yıl: {date[:4]}"
    else:
        year = date[:4]
        month = date[5:7]
        month_names = {
            '01': 'Ocak', '02': 'Şubat', '03': 'Mart', '04': 'Nisan',
            '05': 'Mayıs', '06': 'Haziran', '07': 'Temmuz', '08': 'Ağustos',
            '09': 'Eylül', '10': 'Ekim', '11': 'Kasım', '12': 'Aralık'
        }
        period_text = f"Dönem: {month_names.get(month, month)} {year}"
    
    ax.text(0.5, 0.5, period_text, 
            fontsize=16, ha='center', va='center')
    
    # Oluşturulma tarihi
    creation_date = datetime.now().strftime("%d.%m.%Y %H:%M")
    ax.text(0.5, 0.3, f"Oluşturulma Tarihi: {creation_date}", 
            fontsize=12, ha='center', va='center')
    
    # Alt bilgi
    ax.text(0.5, 0.1, 'Faaliyet Takip Sistemi', 
            fontsize=10, ha='center', va='center', style='italic')
    
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)

def create_data_table_page(pdf, data, date, year_mode):
    """Veri tablosu sayfasını profesyonel A4 formatında oluşturur"""
    fig, ax = plt.subplots(figsize=(8.27, 11.69))  # A4 boyutu
    ax.axis('off')
    
    # Sayfa başlığı
    title = f"{date[:4]} YILI FAALİYET İSTATİSTİKLERİ" if year_mode else \
            f"{format_date_turkish(date).upper()} FAALİYET İSTATİSTİKLERİ"
    
    ax.text(0.5, 0.94, title, 
            fontsize=16, fontweight='bold', ha='center', color='#2E7D32')
    
    # Başlık altı çizgisi
    ax.plot([0.1, 0.9], [0.92, 0.92], color='#2E7D32', linewidth=0.8)
    
    # Tablo verisi hazırlama
    if data:
        table_data = [['FAALİYET TÜRÜ', 'TOPLAM SAYI']]
        total_count = 0
        
        for row in data:
            table_data.append([row[0].upper(), str(row[1])])
            total_count += row[1]
        
        # Toplam satırı ekle
        table_data.append(['TOPLAM', str(total_count)])
        
        # Tablo oluşturma
        table = ax.table(cellText=table_data[1:], 
                        colLabels=table_data[0],
                        cellLoc='center',
                        loc='center',
                        colWidths=[0.7, 0.2],
                        bbox=[0.1, 0.1, 0.8, 0.75])  # x, y, width, height
        
        # Tablo stil ayarları
        table.auto_set_font_size(False)
        table.set_fontsize(11)
        
        # Başlık satırı formatı
        for i in range(len(table_data[0])):
            table[(0, i)].set_facecolor('#2E7D32')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # Toplam satırı formatı
        last_row = len(table_data) - 1
        for i in range(len(table_data[0])):
            table[(last_row, i)].set_facecolor('#E8F5E9')
            table[(last_row, i)].set_text_props(weight='bold')
        
        # Hücre kenarlıkları
        for key, cell in table.get_celld().items():
            cell.set_edgecolor('#DDDDDD')
        
    else:
        ax.text(0.5, 0.5, 'BU DÖNEMDE VERİ BULUNAMADI', 
                fontsize=14, ha='center', va='center', color='#777777')
    
    # Sayfa numarası
    ax.text(0.85, 0.05, "Sayfa 2", 
            fontsize=9, ha='right', color='#777777')
    
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)

def create_monthly_chart_page(pdf, date):
    """Aylık grafik sayfasını oluşturur"""
    # Aylık veri çek
    monthly_data = get_monthly_data(date)
    
    if not monthly_data:
        return
    
    fig = plt.figure(figsize=(8.27, 11.69))  # A4 boyutu
    
    # Histogram
    ax1 = fig.add_subplot(2, 1, 1)
    types = [row[0] for row in monthly_data]
    counts = [row[1] for row in monthly_data]
    ax1.bar(types, counts, color='#2196F3')
    ax1.set_title(f'Aylık Faaliyet Dağılımı - Histogram ({date[:7]})', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Faaliyet Türü')
    ax1.set_ylabel('Sayı')
    ax1.tick_params(axis='x', rotation=45)
    
    # Pasta grafik
    ax2 = fig.add_subplot(2, 1, 2)
    ax2.pie(counts, labels=types, autopct='%1.1f%%', startangle=90)
    ax2.set_title(f'Aylık Faaliyet Dağılımı - Pasta Grafik ({date[:7]})', fontsize=14, fontweight='bold')
    
    plt.tight_layout(pad=3.0)
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)

def create_yearly_chart_page(pdf, year):
    """Yıllık grafik sayfasını oluşturur"""
    # Yıllık veri çek
    yearly_data = get_yearly_data(year)
    
    if not yearly_data:
        return
    
    fig = plt.figure(figsize=(8.27, 11.69))  # A4 boyutu
    
    # Histogram
    ax1 = fig.add_subplot(2, 1, 1)
    types = [row[0] for row in yearly_data]
    counts = [row[1] for row in yearly_data]
    ax1.bar(types, counts, color='#4CAF50')
    ax1.set_title(f'Yıllık Faaliyet Dağılımı - Histogram ({year})', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Faaliyet Türü')
    ax1.set_ylabel('Sayı')
    ax1.tick_params(axis='x', rotation=45)
    
    # Pasta grafik
    ax2 = fig.add_subplot(2, 1, 2)
    ax2.pie(counts, labels=types, autopct='%1.1f%%', startangle=90)
    ax2.set_title(f'Yıllık Faaliyet Dağılımı - Pasta Grafik ({year})', fontsize=14, fontweight='bold')
    
    plt.tight_layout(pad=3.0)
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)

def create_summary_page(pdf, data, date, year_mode):
    """Özet sayfasını oluşturur"""
    fig, ax = plt.subplots(figsize=(8.27, 11.69))  # A4 boyutu
    ax.axis('off')
    
    # Sayfa başlığı
    ax.text(0.1, 0.9, 'RAPOR ÖZETİ', fontsize=18, fontweight='bold')
    
    if data:
        total_activities = sum(row[1] for row in data)
        most_common = max(data, key=lambda x: x[1])
        
        summary_text = f"""
GENEL BİLGİLER:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• Toplam Faaliyet Sayısı: {total_activities}
• Faaliyet Türü Çeşidi: {len(data)}
• En Çok Yapılan Faaliyet: {most_common[0]} ({most_common[1]} adet)

DETAYLI FAALİYET DAĞILIMI:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        
        # Her faaliyet türü için detay sayısını ekle
        for activity_type, count in sorted(data, key=lambda x: x[1], reverse=True):
            percentage = (count / total_activities) * 100
            details = get_activity_details(activity_type, date, year_mode)
            unique_dates = len(set(detail[1] for detail in details)) if details else 0
            
            summary_text += f"• {activity_type}: {count} adet (%{percentage:.1f})\n"
            summary_text += f"  └─ {unique_dates} farklı günde gerçekleştirildi\n"
        
        summary_text += f"""

RAPOR BİLGİLERİ:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• Rapor Türü: {"Yıllık" if year_mode else "Aylık"} İstatistik
• Dönem: {date[:4] if year_mode else date[:7]}
• Oluşturulma: {datetime.now().strftime("%d.%m.%Y %H:%M")}
• Sayfa Sayısı: {pdf.get_pagecount()}
        """
        
    else:
        summary_text = """
Bu dönemde herhangi bir faaliyet kaydı bulunmamaktadır.

• Toplam Faaliyet: 0
• Faaliyet Türü: 0
        """
    
    ax.text(0.1, 0.8, summary_text, fontsize=11, va='top', ha='left', 
            fontfamily='monospace')
    
    # Sayfa numarası
    ax.text(0.85, 0.05, f"Sayfa {pdf.get_pagecount()}", 
            fontsize=9, ha='right', color='#777777')
    
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)

def get_monthly_data(date):
    """Belirtilen aya ait verileri getirir"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT type, COUNT(*) FROM activities WHERE date LIKE ? GROUP BY type",
        (date[:7] + "%",)
    )
    
    data = cursor.fetchall()
    conn.close()
    return data

def get_yearly_data(year):
    """Belirtilen yıla ait verileri getirir"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT type, COUNT(*) FROM activities WHERE date LIKE ? GROUP BY type",
        (year + "%",)
    )
    
    data = cursor.fetchall()
    conn.close()
    return data

def get_activity_details(activity_type, date, year_mode):
    """Belirli bir faaliyet türünün detaylarını getirir"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if year_mode:
        cursor.execute(
            "SELECT name, date FROM activities WHERE type = ? AND date LIKE ? ORDER BY date",
            (activity_type, date[:4] + "%")
        )
    else:
        cursor.execute(
            "SELECT name, date FROM activities WHERE type = ? AND date LIKE ? ORDER BY date",
            (activity_type, date[:7] + "%")
        )
    
    data = cursor.fetchall()
    conn.close()
    return data

def format_date_turkish(date_str):
    """Tarihi Türkçe ay formatında döndürür (2024-01 -> OCAK 2024)"""
    month_names = {
        '01': 'OCAK', '02': 'ŞUBAT', '03': 'MART', '04': 'NİSAN',
        '05': 'MAYIS', '06': 'HAZİRAN', '07': 'TEMMUZ', '08': 'AĞUSTOS',
        '09': 'EYLÜL', '10': 'EKİM', '11': 'KASIM', '12': 'ARALIK'
    }
    if len(date_str) == 7:  # YYYY-MM formatı
        return f"{month_names.get(date_str[5:7])} {date_str[:4]}"
    return date_str

def format_full_date(date_str):
    """Tam tarih string'ini Türkçe formatta döndürür (YYYY-MM-DD -> DD Ay YYYY)"""
    try:
        if len(date_str) >= 10:  # YYYY-MM-DD formatı
            year = date_str[:4]
            month = date_str[5:7]
            day = date_str[8:10]
            month_names = {
                '01': 'Ocak', '02': 'Şubat', '03': 'Mart', '04': 'Nisan',
                '05': 'Mayıs', '06': 'Haziran', '07': 'Temmuz', '08': 'Ağustos',
                '09': 'Eylül', '10': 'Ekim', '11': 'Kasım', '12': 'Aralık'
            }
            return f"{int(day)} {month_names.get(month, month)} {year}"
        else:
            return date_str
    except:
        return date_str

# Ana test fonksiyonu
if __name__ == "__main__":
    # Test parametreleri
    test_params = {
        'file_path': 'test_report.pdf',
        'date': '2024-01',
        'year_mode': False,
        'include_monthly_chart': True,
        'include_yearly_chart': True,
        'current_data': [('Spor', 15), ('Okuma', 10), ('Müzik', 8)]
    }
    
    try:
        create_statistics_pdf(test_params)
        print("Test PDF başarıyla oluşturuldu!")
    except Exception as e:
        print(f"Test hatası: {e}")