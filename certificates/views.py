from django.shortcuts import render
from .forms import CertificateVerificationForm
from .models import Certificate

def verify(request):
    cert_id = None
    certificate = None
    error_message = None

    if request.method == 'POST':
        form = CertificateVerificationForm(request.POST)
        if form.is_valid():
            cert_id = form.cleaned_data['certificate_id']
            # Rule 9: Exact match lookup ONLY (no icontains/wildcard)
            try:
                certificate = Certificate.objects.select_related('course', 'student').get(certificate_id=cert_id)
            except Certificate.DoesNotExist:
                error_message = f"No valid certificate found matching Certificate ID '{cert_id}'."
    else:
        # Check GET parameter if passed from dashboard link
        initial_id = request.GET.get('certificate_id', '').strip().upper()
        if initial_id:
            form = CertificateVerificationForm(initial={'certificate_id': initial_id})
            try:
                certificate = Certificate.objects.select_related('course', 'student').get(certificate_id=initial_id)
            except Certificate.DoesNotExist:
                error_message = f"No valid certificate found matching Certificate ID '{initial_id}'."
        else:
            form = CertificateVerificationForm()

    if certificate:
        return render(request, 'certificates/result.html', {
            'certificate': certificate,
            'form': form
        })

    return render(request, 'certificates/verify.html', {
        'form': form,
        'error_message': error_message
    })
