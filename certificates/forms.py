from django import forms

class CertificateVerificationForm(forms.Form):
    certificate_id = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Certificate ID (e.g. cert-2026-a1b2c3)',
            'required': 'required'
        })
    )

    def clean_certificate_id(self):
        return self.cleaned_data.get('certificate_id', '').strip().lower()
