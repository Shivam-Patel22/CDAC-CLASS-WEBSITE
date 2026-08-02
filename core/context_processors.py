from .models import ContactContent

def site_content(request):
    try:
        contact_obj = ContactContent.get_solo()
        return {'site_contact': contact_obj}
    except Exception:
        return {'site_contact': None}
