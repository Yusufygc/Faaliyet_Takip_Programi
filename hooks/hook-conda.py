from PyInstaller.utils.hooks import collect_data_files, collect_all
import os
# Conda ortamına özgü DLL ve diğer dosyaları toplamak için
# Conda ortamının ana dizinini belirlememiz gerekiyor.
# Bu hook genellikle "bin", "Library/bin", "DLLs" gibi yerlerden toplama yapar.

# Bu hook, PyInstaller'ın Conda ortamındaki bin/Library/bin/DLLs klasörlerini aramasını sağlar.
# Bu, genellikle numpy ve matplotlib gibi kütüphanelerin dış bağımlılıklarını çözmek için önemlidir.

# collect_data_files genellikle veri dosyaları içindir (.json, .txt vb.)
# collect_all genellikle bir paketin tüm bağımlılıklarını (modüller, veri dosyaları, DLL'ler) toplamak içindir.

# numpy ve matplotlib için zaten --collect-all kullanıyoruz.
# Buradaki asıl amacımız, Conda'nın özel DLL dizinlerini PyInstaller'a daha açıkça bildirmek.

# Path to your conda environment's base DLL directories
# Lütfen buradaki yolu kendi Conda ortamınızın tam yolu ile değiştirin!
# Örnek: C:/Users/ysfygc/anaconda3/envs/Ftakip
CONDA_ENV_BASE = "C:/Users/ysfygc/anaconda3/envs/Ftakip"

# Add DLLs from conda's specific locations
datas = []
binaries = []

# Common Conda DLL paths relative to env base
conda_dll_paths = [
    os.path.join(CONDA_ENV_BASE, 'bin'),
    os.path.join(CONDA_ENV_BASE, 'Library', 'bin'),
    os.path.join(CONDA_ENV_BASE, 'DLLs'),
]

for dll_path in conda_dll_paths:
    if os.path.exists(dll_path):
        # Add all files in these directories
        for root, _, files in os.walk(dll_path):
            for f in files:
                full_path = os.path.join(root, f)
                # Sadece DLL'leri veya diğer önemli ikili dosyaları eklemek isterseniz filtreleyebilirsiniz.
                # Örneğin: if f.endswith(('.dll', '.pyd', '.so')):
                binaries.append((full_path, '.')) # Hedef dizin olarak '.' kök dizini kullanıyoruz