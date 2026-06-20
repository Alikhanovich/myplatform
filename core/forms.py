"""
Contact form (02-System-Design: ContactView) + oddiy spam himoyasi.

Spam himoyasi: honeypot field (`website`) — botlar to'ldiradi, odam ko'rmaydi
(CSS bilan yashirilgan). To'ldirilgan bo'lsa, forma jim rad etiladi.
(01-Arxitektura 4-bo'lim: contact form'da oddiy spam himoyasi.)
"""
from django import forms


class ContactForm(forms.Form):
    name = forms.CharField(
        label="Ism",
        max_length=120,
        widget=forms.TextInput(attrs={"placeholder": "Ismingiz", "autocomplete": "name"}),
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={"placeholder": "siz@example.com", "autocomplete": "email"}
        ),
    )
    message = forms.CharField(
        label="Xabar",
        max_length=4000,
        widget=forms.Textarea(attrs={"placeholder": "Qanday tizim kerak?", "rows": 5}),
    )

    # --- Honeypot: odam bo'sh qoldiradi, bot to'ldiradi ---
    website = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "tabindex": "-1",
                "autocomplete": "off",
                "aria-hidden": "true",
            }
        ),
    )

    def clean_website(self):
        if self.cleaned_data.get("website"):
            # Bot aniqlandi — umumiy xato (sababini oshkor qilmaymiz).
            raise forms.ValidationError("Xato so'rov.")
        return ""
