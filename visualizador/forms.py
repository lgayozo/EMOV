# forms.py
from django import forms

class UploadFileForm(forms.Form):
    zip_file = forms.FileField(required=False, label='Archivo ZIP (Shapefile)')
    csv_file = forms.FileField(required=False, label='Archivo CSV')

