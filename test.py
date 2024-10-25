import os

file_path = 'media/test_file.txt'
with open(file_path, 'w') as f:
    f.write('Este es un archivo de prueba.')
print(f'Archivo de prueba guardado en {file_path}')
