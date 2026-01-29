# services/pdf_service.py
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from datetime import datetime

class PDFService:
    def __init__(self):
        self.font_registered = False
        self._register_fonts()

    def _register_fonts(self):
        """Türkçe karakter desteği için DejaVu fontlarını yükler."""
        try:
            # Font yolları (Proje ana dizininde 'fonts' klasörü olmalı)
            font_dir = "fonts"
            regular_font = os.path.join(font_dir, "DejaVuSans.ttf")
            bold_font = os.path.join(font_dir, "DejaVuSans-Bold.ttf")

            if os.path.exists(regular_font) and os.path.exists(bold_font):
                pdfmetrics.registerFont(TTFont('DejaVuSans', regular_font))
                pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', bold_font))
                self.font_registered = True
            else:
                print("UYARI: Font dosyaları bulunamadı. Türkçe karakterler bozuk çıkabilir.")
        except Exception as e:
            print(f"Font yükleme hatası: {e}")

    def create_report(self, file_path, title, data_summary, data_details):
        """PDF raporunu oluşturur ve kaydeder."""
        try:
            doc = SimpleDocTemplate(file_path, pagesize=A4,
                                    rightMargin=inch/2, leftMargin=inch/2,
                                    topMargin=inch/2, bottomMargin=inch/2)
            
            # Stilleri Ayarla
            styles = getSampleStyleSheet()
            # Font yüklendiyse onu kullan, yoksa varsayılanı
            font_name = 'DejaVuSans' if self.font_registered else 'Helvetica'
            font_name_bold = 'DejaVuSans-Bold' if self.font_registered else 'Helvetica-Bold'

            # Başlık ve Metin Stilleri
            title_style = ParagraphStyle('CustomTitle', parent=styles['Title'], fontName=font_name_bold, fontSize=24, spaceAfter=20)
            heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontName=font_name_bold, fontSize=14, spaceAfter=10, textColor=colors.HexColor("#2C3E50"))
            normal_style = ParagraphStyle('CustomNormal', parent=styles['Normal'], fontName=font_name, fontSize=10, leading=14)
            
            story = []

            # 1. Başlık Alanı
            story.append(Paragraph("FAALİYET TAKİP SİSTEMİ", title_style))
            story.append(Paragraph(f"Rapor: {title}", heading_style))
            story.append(Paragraph(f"Oluşturulma Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M')}", normal_style))
            story.append(Spacer(1, 0.3 * inch))

            # 2. Özet Bilgiler
            story.append(Paragraph("Özet Bilgiler", heading_style))
            for key, value in data_summary.items():
                story.append(Paragraph(f"• <b>{key}:</b> {value}", normal_style))
            story.append(Spacer(1, 0.3 * inch))

            # 3. Tablo
            story.append(Paragraph("Detaylı Faaliyet Listesi", heading_style))
            story.append(Spacer(1, 0.1 * inch))

            if not data_details:
                story.append(Paragraph("Bu dönem için kayıtlı faaliyet bulunmamaktadır.", normal_style))
            else:
                # Tablo Başlıkları
                table_data = [['Kategori', 'Faaliyet Adı', 'Tarih', 'Puan']]
                
                # Tablo Verileri
                for item in data_details:
                    # item formatı: (type, name, date, comment, rating, id)
                    # None kontrolü ve String çevrimi yapıyoruz
                    cat = item[0] if item[0] else ""
                    name = item[1] if item[1] else ""
                    start_date = item[2] if item[2] else ""
                    # item formatı güncellendi: (type, name, date, comment, rating, id, end_date)
                    end_date = item[6] if len(item) > 6 and item[6] else None
                    
                    if end_date:
                        # Tarih aralığı varsa alt alta göster
                        date_display = f"{start_date}\n- {end_date}"
                    else:
                        date_display = start_date
                        
                    rating = str(item[4]) if item[4] else "-"
                    
                    # Satırı ekle
                    table_data.append([cat.title(), name, date_display, rating])

                # Tabloyu Oluştur
                # Sütun genişlikleri (Toplam ~7.2 inch)
                col_widths = [1.2*inch, 3.5*inch, 1.5*inch, 0.8*inch]
                t = Table(table_data, colWidths=col_widths, repeatRows=1)
                
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')), # Başlık Arka Planı
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),           # Başlık Yazı Rengi
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),                         # Sola Yasla
                    ('ALIGN', (3, 0), (3, -1), 'CENTER'),                        # Puanı Ortala
                    ('FONTNAME', (0, 0), (-1, -1), font_name),                   # Türkçe Font
                    ('FONTNAME', (0, 0), (-1, 0), font_name_bold),               # Başlık Kalın
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),                # Çizgiler
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9F9')]) # Zebra Efekti
                ]))
                
                story.append(t)

            # PDF'i Oluştur
            doc.build(story)
            return True, "PDF başarıyla oluşturuldu."

        except Exception as e:
            import traceback
            traceback.print_exc() # Hatanın detayını konsola bas
            return False, f"PDF oluşturulurken hata: {e}"