import random
import re
from datetime import datetime

def get_next_certificate_sequence():
    """
    Returns the next 2-digit sequence number formatted with leading zeros (01, 02... 99).
    Increments based on the highest existing suffix sequence number or total count.
    """
    from .models import Certificate
    max_seq = 0
    for cert in Certificate.objects.all():
        match = re.search(r'-(\d{2})$', cert.certificate_id)
        if match:
            try:
                seq_num = int(match.group(1))
                if seq_num > max_seq:
                    max_seq = seq_num
            except ValueError:
                pass

    if max_seq > 0:
        next_seq = max_seq + 1
    else:
        next_seq = Certificate.objects.count() + 1

    if next_seq > 99:
        next_seq = ((next_seq - 1) % 99) + 1

    return f"{next_seq:02d}"

def generate_certificate_id(first_name="", last_name=""):
    """
    Auto-generates a unique server-side certificate ID in format CERT-YYYY-FL-RANDOM-SEQ
    Where:
    - YYYY = current year
    - FL = first letter of First Name + first letter of Last Name (uppercase)
    - RANDOM = random 4-digit number
    - SEQ = running certificate number with leading zeros (2 digits: 01, 02... 99)
    """
    from .models import Certificate
    year = datetime.now().year

    fn_clean = first_name.strip() if first_name else ""
    ln_clean = last_name.strip() if last_name else ""

    f_char = fn_clean[0].upper() if fn_clean else "X"
    l_char = ln_clean[0].upper() if ln_clean else "X"
    fl = f"{f_char}{l_char}"

    seq_str = get_next_certificate_sequence()

    while True:
        random_num = random.randint(1000, 9999)
        cert_id = f"CERT-{year}-{fl}-{random_num}-{seq_str}"
        if not Certificate.objects.filter(certificate_id__iexact=cert_id).exists():
            return cert_id

