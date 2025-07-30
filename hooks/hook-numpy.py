from PyInstaller.utils.hooks import collect_data_files

# numpy'nin MKL kütüphanelerini bulmasını sağlar
datas = collect_data_files('numpy.core.mkl')