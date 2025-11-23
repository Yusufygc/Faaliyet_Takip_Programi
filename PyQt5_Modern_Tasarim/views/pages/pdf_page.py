# views/pages/pdf_page.py
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                             QFileDialog, QMessageBox, QCheckBox)
from PyQt5.QtCore import Qt
from views.widgets import MonthYearWidget
from services.pdf_service import PDFService
import os

class PdfPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.pdf_service = PDFService()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("PDF Raporu Oluştur")
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)

        # Tarih Seçimi
        layout.addWidget(QLabel("Rapor Dönemi Seçin:"))
        self.date_picker = MonthYearWidget()
        layout.addWidget(self.date_picker)

        self.chk_year_only = QCheckBox("Sadece Yıllık Rapor")
        self.chk_year_only.toggled.connect(self.toggle_year_mode)
        layout.addWidget(self.chk_year_only)

        # Oluştur Butonu
        btn_create = QPushButton("Raporu Kaydet")
        btn_create.setFixedSize(200, 50)
        btn_create.setStyleSheet("background-color: #009688; color: white; font-weight: bold; font-size: 14px;")
        btn_create.clicked.connect(self.generate_pdf)
        layout.addWidget(btn_create)

    def toggle_year_mode(self, checked):
        self.date_picker.set_year_only_mode(checked)

    def generate_pdf(self):
        date_prefix = self.date_picker.get_date_str()
        if not date_prefix:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir tarih seçiniz.")
            return

        # Dosya Kayıt Yeri Seçimi
        file_path, _ = QFileDialog.getSaveFileName(self, "PDF Kaydet", f"Rapor_{date_prefix}.pdf", "PDF Files (*.pdf)")
        if not file_path:
            return

        # Verileri Hazırla (Controller üzerinden repository'e erişim)
        # Not: Controller'a bu metodu eklememiz gerekecek veya mevcutları kullanacağız.
        # Repository'deki 'get_detailed_data_for_pdf' metoduna controller üzerinden erişim sağlayalım.
        
        # Eğer controller'da henüz yoksa, basitçe repository'e erişelim (geçici olarak)
        # VEYA Controller'a yeni bir metod ekleyelim (En doğrusu bu).
        # Şimdilik varsayım: controller.repository.get_detailed_data_for_pdf var.
        raw_data = self.controller.repository.get_detailed_data_for_pdf(date_prefix)
        
        if not raw_data:
            QMessageBox.warning(self, "Uyarı", "Seçilen dönem için veri bulunamadı.")
            return

        # Özet Bilgi Hazırla
        summary = {
            "Rapor Dönemi": date_prefix,
            "Toplam Faaliyet Sayısı": len(raw_data),
            "Oluşturulma Tarihi":  str(datetime.now().date())
        }

        # Servisi Çağır
        success, message = self.pdf_service.create_report(file_path, f"{date_prefix} Dönemi Raporu", summary, raw_data)
        
        if success:
            QMessageBox.information(self, "Başarılı", message)
            os.startfile(file_path) # Dosyayı aç
        else:
            QMessageBox.critical(self, "Hata", message)