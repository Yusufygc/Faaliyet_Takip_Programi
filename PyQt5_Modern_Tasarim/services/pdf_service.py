# services/pdf_service.py
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

class PDFService:
    def __init__(self):
        self.font_registered = False
        self._register_fonts()

    def _register_fonts(self):
        """Türkçe karakter desteği için fontları yükler."""
        try:
            # Font dosyalarının projenin 'fonts' klasöründe olduğunu varsayıyoruz
            # Eğer fonts klasörünüz yoksa, sistem fontlarını veya varsayılanları kullanırız.
            if os.path.exists("fonts/DejaVuSans.ttf"):
                pdfmetrics.registerFont(TTFont('DejaVuSans', 'fonts/DejaVuSans.ttf'))
                pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'fonts/DejaVuSans-Bold.ttf'))
                self.font_registered = True
        except Exception as e:
            print(f"Font yükleme hatası: {e}")

    def create_report(self, file_path, title, data_summary, data_details):
        """PDF raporunu oluşturur ve kaydeder."""
        try:
            doc = SimpleDocTemplate(file_path, pagesize=A4,
                                    rightMargin=inch/2, leftMargin=inch/2,
                                    topMargin=inch/2, bottomMargin=inch/2)
            
            styles = getSampleStyleSheet()
            font_name = 'DejaVuSans' if self.font_registered else 'Helvetica'
            font_name_bold = 'DejaVuSans-Bold' if self.font_registered else 'Helvetica-Bold'

            # Özel Stiller
            title_style = ParagraphStyle('Title', parent=styles['Title'], fontName=font_name_bold, fontSize=24)
            normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontName=font_name)
            
            story = []

            # Başlık
            story.append(Paragraph("FAALİYET TAKİP SİSTEMİ", title_style))
            story.append(Spacer(1, 0.2 * inch))
            story.append(Paragraph(f"<b>{title}</b>", ParagraphStyle('Sub', parent=normal_style, fontSize=16, alignment=1)))
            story.append(Spacer(1, 0.5 * inch))

            # Özet Bilgiler
            story.append(Paragraph("<b>Özet Bilgiler:</b>", normal_style))
            for key, value in data_summary.items():
                story.append(Paragraph(f"• {key}: {value}", normal_style))
            story.append(Spacer(1, 0.3 * inch))

            # Tablo
            story.append(Paragraph("<b>Detaylı Faaliyet Listesi</b>", normal_style))
            story.append(Spacer(1, 0.1 * inch))

            # Tablo Verisi Hazırlama (Başlıklar + Veri)
            table_data = [['Tür', 'Ad', 'Tarih', 'Puan']]
            for item in data_details:
                # item: (type, name, date, comment, rating, id)
                table_data.append([item[0], item[1], item[2], str(item[4])])

            t = Table(table_data, colWidths=[1.5*inch, 3*inch, 1.5*inch, 0.8*inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E7D32')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), font_name_bold),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), font_name)
            ]))
            
            story.append(t)

            doc.build(story)
            return True, "PDF başarıyla oluşturuldu."
        except Exception as e:
            return False, f"PDF oluşturulurken hata: {e}"