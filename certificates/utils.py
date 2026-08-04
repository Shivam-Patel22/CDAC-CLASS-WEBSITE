import uuid
from datetime import datetime

def generate_certificate_id():
    """
    Auto-generates a unique server-side certificate ID in format cert-yyyy-xxxxxx
    using lowercase UUID hex with collision retry logic.
    """
    from .models import Certificate
    year = datetime.now().year
    while True:
        random_code = uuid.uuid4().hex[:6].lower()
        cert_id = f"cert-{year}-{random_code}"
        if not Certificate.objects.filter(certificate_id=cert_id).exists():
            return cert_id
