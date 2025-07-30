# pdfcreate_page.py
import customtkinter as ctk
from tkinter import messagebox, filedialog
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont # TTF fontlarını kaydetmek için
import matplotlib.pyplot as plt
import os
import datetime
import io # io modülü eklendi

# Projenizin diğer dosyalarından importlar
from database import get_connection
from utils import is_valid_yyyymm, is_valid_yyyy

# Türkçe karakter desteği için font kaydı
# 'DejaVuSans' font ailesi genellikle Türkçe karakterleri destekler.
# Font yüklemesinin başarılı olup olmadığını takip etmek için bir bayrak kullanacağız.
font_registered = False
try:
    # Font dosyalarını kaydet
    pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'DejaVuSans-Bold.ttf'))
    font_registered = True
except Exception as e:
    # Font dosyaları bulunamazsa veya yüklenemezse hata mesajı yazdır
    print(f"Font yükleme hatası: {e}. Lütfen 'DejaVuSans.ttf' ve 'DejaVuSans-Bold.ttf' dosyalarının '{os.getcwd()}' dizininde mevcut olduğundan emin olun veya başka bir font kullanın.")
    # Fallback olarak ReportLab'ın varsayılan fontlarını kullanmaya devam edecek.

# Matplotlib için Türkçe karakter desteği
# Matplotlib font ayarı, ReportLab'dan bağımsızdır ve burada doğrudan yapılabilir.
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False # Negatif işaretlerin düzgün görünmesi için

class PDFCreatePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=0) # Sabit yükseklikler
        self.grid_rowconfigure(6, weight=1) # Alt kısım genişlesin

        # Başlık
        self.title_label = ctk.CTkLabel(self, text="PDF Raporu Oluştur", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.grid(row=0, column=0, pady=(20, 10))

        # PDF oluşturma seçenekleri (Aya Göre / Yıla Göre)
        self.pdf_option_frame = ctk.CTkFrame(self)
        self.pdf_option_frame.grid(row=1, column=0, pady=10, padx=20, sticky="ew")
        self.pdf_option_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(self.pdf_option_frame, text="Rapor Oluşturma Seçeneği:").grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.pdf_option_var = ctk.StringVar(value="month") # Varsayılan olarak aya göre
        self.month_radio = ctk.CTkRadioButton(self.pdf_option_frame, text="Aya Göre Rapor", variable=self.pdf_option_var, value="month", command=self.on_option_change)
        self.month_radio.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        self.year_radio = ctk.CTkRadioButton(self.pdf_option_frame, text="Yıla Göre Rapor", variable=self.pdf_option_var, value="year", command=self.on_option_change)
        self.year_radio.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        # Tarih Seçimi
        self.date_selection_frame = ctk.CTkFrame(self)
        self.date_selection_frame.grid(row=2, column=0, pady=10, padx=20, sticky="ew")
        self.date_selection_frame.grid_columnconfigure((0, 1), weight=1)

        self.month_label = ctk.CTkLabel(self.date_selection_frame, text="Ay:")
        self.month_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.month_combobox = ctk.CTkComboBox(self.date_selection_frame, values=[""] + [f"{i:02d}" for i in range(1, 13)])
        self.month_combobox.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.month_combobox.set("") # Başlangıçta boş

        self.year_label = ctk.CTkLabel(self.date_selection_frame, text="Yıl:")
        self.year_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        current_year = datetime.datetime.now().year
        self.year_combobox = ctk.CTkComboBox(self.date_selection_frame, values=[""] + [str(i) for i in range(current_year - 10, current_year + 2)])
        self.year_combobox.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self.year_combobox.set("") # Başlangıçta boş

        # Grafik seçeneği
        self.graph_option_frame = ctk.CTkFrame(self)
        self.graph_option_frame.grid(row=3, column=0, pady=10, padx=20, sticky="ew")
        self.graph_option_frame.grid_columnconfigure((0, 1), weight=1)

        self.graph_checkbox = ctk.CTkCheckBox(self.graph_option_frame, text="Grafik Ekle", onvalue=True, offvalue=False)
        self.graph_checkbox.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # PDF Oluştur butonu
        self.create_pdf_button = ctk.CTkButton(self, text="PDF Oluştur", command=self.create_pdf_report)
        self.create_pdf_button.grid(row=4, column=0, pady=20, padx=20, sticky="ew")

        # Mesaj etiketi
        self.message_label = ctk.CTkLabel(self, text="", text_color="red")
        self.message_label.grid(row=5, column=0, pady=(0, 10))

        # Başlangıçta ay seçeneği aktif, yıl seçeneği de gösterilebilir.
        self.on_option_change()

    def on_option_change(self):
        """PDF oluşturma seçeneği değiştiğinde UI güncellemeleri."""
        selected_option = self.pdf_option_var.get()
        if selected_option == "month":
            self.month_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
            self.month_combobox.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
            self.year_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
            self.year_combobox.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        elif selected_option == "year":
            self.month_label.grid_forget()
            self.month_combobox.grid_forget()
            self.year_label.grid(row=0, column=0, padx=10, pady=5, sticky="w") # Yıl etiketi yukarı kaydırıldı
            self.year_combobox.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

    def create_pdf_report(self):
        self.message_label.configure(text="") # Önceki mesajı temizle

        selected_option = self.pdf_option_var.get()
        selected_month = self.month_combobox.get()
        selected_year = self.year_combobox.get()
        include_graph = self.graph_checkbox.get()

        # Tarih kontrolü
        if selected_option == "month":
            if not selected_month or not selected_year:
                self.message_label.configure(text="Lütfen rapor oluşturmak için ay ve yıl seçiniz.")
                return
            date_prefix = f"{selected_year}-{selected_month}"
            if not is_valid_yyyymm(date_prefix):
                self.message_label.configure(text="Geçersiz tarih formatı. Lütfen YYYY-MM formatında seçiniz.")
                return
            report_period_display = f"{self.get_turkish_month_name(selected_month)} {selected_year}"
            report_title_suffix = f"{report_period_display} Faaliyet Raporu"
            graph_title_suffix = f"{report_period_display} Faaliyet Grafiği"

        elif selected_option == "year":
            if not selected_year:
                self.message_label.configure(text="Lütfen rapor oluşturmak için yıl seçiniz.")
                return
            date_prefix = selected_year
            if not is_valid_yyyy(date_prefix):
                self.message_label.configure(text="Geçersiz yıl formatı. Lütfen YYYY formatında seçiniz.")
                return
            report_period_display = f"{selected_year}"
            report_title_suffix = f"{report_period_display} Yılı Faaliyet Raporu"
            graph_title_suffix = f"{report_period_display} Yılı Faaliyet Grafiği"

        # Verileri çek
        data = self.get_activity_data(date_prefix)
        if not data:
            self.message_label.configure(text="Seçilen dönem için faaliyet verisi bulunamadı.")
            return

        # PDF dosya yolu seçimi
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF dosyaları", "*.pdf")],
            title="PDF Raporunu Kaydet"
        )

        if not file_path:
            return # Kullanıcı iptal etti

        try:
            doc = SimpleDocTemplate(file_path, pagesize=A4,
                                    rightMargin=inch/2, leftMargin=inch/2,
                                    topMargin=inch/2, bottomMargin=inch/2)
            
            # Stiller için örnek stil sayfası alın
            styles = getSampleStyleSheet()

            # Font ismini belirle
            # Eğer DejaVuSans fontları yüklendiyse onları kullan, aksi takdirde varsayılan Helvetica'yı kullan.
            if font_registered:
                font_name_regular = 'DejaVuSans'
                font_name_bold = 'DejaVuSans-Bold'
            else:
                font_name_regular = 'Helvetica'
                font_name_bold = 'Helvetica-Bold'


            styles.add(ParagraphStyle(name='TitleStyle',
                                      fontSize=24,
                                      leading=28,
                                      alignment=TA_CENTER,
                                      fontName=font_name_bold))
            styles.add(ParagraphStyle(name='SubtitleStyle',
                                      fontSize=18,
                                      leading=22,
                                      alignment=TA_CENTER,
                                      fontName=font_name_bold))
            styles.add(ParagraphStyle(name='Heading3Style',
                                      fontSize=14,
                                      leading=18,
                                      fontName=font_name_bold,
                                      spaceAfter=6))
            styles.add(ParagraphStyle(name='NormalStyle',
                                      fontSize=10,
                                      leading=12,
                                      fontName=font_name_regular))
            styles.add(ParagraphStyle(name='FooterStyle',
                                      fontSize=8,
                                      leading=10,
                                      alignment=TA_RIGHT,
                                      fontName=font_name_regular))

            story = []

            # Başlık Sayfası
            story.append(Paragraph("<b>FAALİYET TAKİP SİSTEMİ</b>", styles['TitleStyle']))
            story.append(Spacer(1, 0.2 * inch))
            story.append(Paragraph(f"<b>{report_title_suffix}</b>", styles['SubtitleStyle']))
            story.append(Spacer(1, 0.5 * inch))
            story.append(Paragraph(f"Hazırlayan: Kullanıcı Adı", styles['NormalStyle'])) # Buraya kullanıcı adı eklenebilir
            story.append(Paragraph(f"Tarih: {datetime.date.today().strftime('%d.%m.%Y')}", styles['NormalStyle']))
            story.append(Spacer(1, 2 * inch))
            story.append(Paragraph("Bu rapor, seçilen dönemdeki faaliyetlerinizi özetlemektedir.", styles['NormalStyle']))
            story.append(PageBreak()) # Yeni sayfa

            # Veri Tablosu Sayfası
            story.append(Paragraph("<b>1. Faaliyet Detayları Tablosu</b>", styles['Heading3Style']))
            story.append(Spacer(1, 0.1 * inch))

            table_data = [['Faaliyet Türü', 'Faaliyet Adı', 'Tarih', 'Yorum', 'Puan']]
            for activity_type, name, date, comment, rating, _id in self.get_detailed_activity_data(date_prefix):
                table_data.append([activity_type, name, date, comment, str(rating)])

            table = Table(table_data, colWidths=[1.2*inch, 2*inch, 1*inch, 2*inch, 0.7*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E7D32')), # Yeşil başlık
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), font_name_bold),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#E8F5E9')), # Açık yeşil satırlar
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), font_name_regular),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('LEFTPADDING', (0,0), (-1,-1), 6),
                ('RIGHTPADDING', (0,0), (-1,-1), 6),
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ]))
            story.append(table)
            story.append(PageBreak()) # Yeni sayfa

            # Grafik Sayfası (Eğer istenirse)
            if include_graph:
                graph_data = self.get_activity_counts_for_graph(date_prefix)
                if graph_data["types"] and graph_data["counts"]:
                    try:
                        # Matplotlib için Türkçe font ayarı
                        # Bu ayar zaten dosyanın başında yapıldığı için burada tekrar etmeye gerek yok.
                        # Ancak emin olmak için tekrar edilebilir, bir zararı olmaz.
                        # plt.rcParams['font.family'] = 'DejaVu Sans'
                        # plt.rcParams['axes.unicode_minus'] = False 

                        fig, ax = plt.subplots(figsize=(8, 6))
                        ax.bar(graph_data["types"], graph_data["counts"], color='#1f77b4') # Mavi ton
                        ax.set_xlabel("Faaliyet Türü")
                        ax.set_ylabel("Sayı")
                        ax.set_title(graph_title_suffix)
                        plt.xticks(rotation=45, ha='right')
                        plt.tight_layout()

                        # Grafiği bir BytesIO nesnesine kaydet
                        img_buffer = io.BytesIO()
                        plt.savefig(img_buffer, format='png')
                        plt.close(fig) # Grafiği kaydettikten sonra belleği temizle
                        img_buffer.seek(0) # Başlangıca dön

                        story.append(Paragraph("<b>2. Faaliyet Dağılım Grafiği</b>", styles['Heading3Style']))
                        story.append(Spacer(1, 0.1 * inch))
                        # Image objesine BytesIO nesnesini ver
                        img = Image(img_buffer, width=500, height=375) # A4'e sığacak şekilde ayarlandı
                        story.append(img)
                        story.append(Spacer(1, 0.5 * inch))

                        story.append(PageBreak()) # Yeni sayfa

                    except Exception as e:
                        self.message_label.configure(text=f"Grafik oluşturulurken bir hata oluştu: {e}")
                        print(f"Grafik oluşturma hatası: {e}")
                else:
                    story.append(Paragraph("Grafik oluşturmak için yeterli veri bulunamadı.", styles['NormalStyle']))
                    story.append(Spacer(1, 0.5 * inch))
                    story.append(PageBreak())

            # Özet Sayfası
            story.append(Paragraph("<b>3. Rapor Özeti</b>", styles['Heading3Style']))
            story.append(Spacer(1, 0.1 * inch))

            total_activities = sum(item[1] for item in data) if data else 0
            activity_types_count = len(data) if data else 0
            most_common_activity = ""
            if data:
                # data formatı: [(type, count), ...]
                most_common = max(data, key=lambda x: x[1])
                most_common_activity = f"{most_common[0]} ({most_common[1]} adet)"

            summary_text = f"""
            • Toplam Faaliyet Sayısı: {total_activities}
            • Faaliyet Türü Çeşidi: {activity_types_count}
            • En Çok Yapılan Faaliyet: {most_common_activity}
            """
            story.append(Paragraph(summary_text, styles['NormalStyle']))
            story.append(Spacer(1, 0.5 * inch))
            story.append(Paragraph(f"Bu rapor, {report_period_display} dönemindeki faaliyetlerinizin kapsamlı bir özetini sunmaktadır. Detaylı analizler ve eğilimler, gelecekteki faaliyet planlamalarınız için değerli bilgiler sağlayabilir.", styles['NormalStyle']))


            doc.build(story, onFirstPage=self.add_page_number, onLaterPages=self.add_page_number)
            messagebox.showinfo("Başarılı", f"PDF raporu başarıyla oluşturuldu: {file_path}")
            os.startfile(file_path) # PDF'i otomatik aç

        except Exception as e:
            messagebox.showerror("Hata", f"PDF oluşturulurken genel bir hata oluştu: {e}")
            print(f"PDF oluşturulurken genel hata: {e}")

    def add_page_number(self, canvas, doc):
        """Her sayfaya sayfa numarası ekler."""
        canvas.saveState()
        # Sayfa numarası için de Türkçe font kullan
        if font_registered:
            canvas.setFont('DejaVuSans', 8)
        else:
            canvas.setFont('Helvetica', 8)
        canvas.drawString(A4[0] - inch, 0.75 * inch, f"Sayfa {doc.page}")
        canvas.restoreState()

    def get_turkish_month_name(self, month_number_str):
        """Ay numarasını Türkçe ay adına çevirir."""
        month_names = {
            '01': 'Ocak', '02': 'Şubat', '03': 'Mart', '04': 'Nisan',
            '05': 'Mayıs', '06': 'Haziran', '07': 'Temmuz', '08': 'Ağustos',
            '09': 'Eylül', '10': 'Ekim', '11': 'Kasım', '12': 'Aralık'
        }
        return month_names.get(month_number_str, month_number_str)

    def get_activity_data(self, date_prefix):
        """
        Veritabanından faaliyet türüne göre sayım verisi çeker.
        date_prefix: YYYY veya YYYY-MM
        """
        conn = get_connection()
        cursor = conn.cursor()
        query = "SELECT type, COUNT(*) FROM activities WHERE date LIKE ? GROUP BY type"
        cursor.execute(query, (f"{date_prefix}%",))
        data = cursor.fetchall()
        conn.close()
        return data

    def get_detailed_activity_data(self, date_prefix):
        """
        Veritabanından tüm faaliyet detaylarını çeker.
        date_prefix: YYYY veya YYYY-MM
        """
        conn = get_connection()
        cursor = conn.cursor()
        query = "SELECT type, name, date, comment, rating, id FROM activities WHERE date LIKE ? ORDER BY date, type, name"
        cursor.execute(query, (f"{date_prefix}%",))
        data = cursor.fetchall()
        conn.close()
        return data

    def get_activity_counts_for_graph(self, date_prefix):
        """
        Grafik için faaliyet türü ve sayılarını çeker.
        """
        data = self.get_activity_data(date_prefix) # get_activity_data zaten sayım yapıyor
        types = [row[0] for row in data]
        counts = [row[1] for row in data]
        return {"types": types, "counts": counts}

