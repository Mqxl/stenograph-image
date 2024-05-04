from django import forms

class LanguageForm(forms.Form):
    language = forms.ChoiceField(choices=[('en', 'English'), ('ru', 'Russian'), ('kk', 'Kazakh')])