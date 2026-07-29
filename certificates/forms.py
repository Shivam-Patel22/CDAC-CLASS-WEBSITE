from django import forms

class CertificateVerificationForm(forms.Form):
    certificate_id = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Certificate ID (e.g. CERT-2026-A1B2C3)',
            'required': 'required',
            'style': 'text-transform: uppercase;'
        })
    )

    def clean_certificate_id(self):
        return self.cleaned_data.get('certificate_id', '').strip().upper()
