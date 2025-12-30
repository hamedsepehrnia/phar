"""
فرم‌های اپ core
"""
from django import forms
from .models import ContactMessage


class ContactForm(forms.ModelForm):
    """فرم تماس با ما"""
    
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'block w-full p-3 text-sm/6 md:text-base outline-1 -outline-offset-1 placeholder:text-gray-400 transition-all text-gray-800 bg-slate-200 border-b-4 border-gray-300 focus:border-b-primary-800 appearance-none rounded-lg outline-none',
                'placeholder': 'نام و نام خانوادگی',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'block w-full p-3 text-sm/6 md:text-base outline-1 -outline-offset-1 placeholder:text-gray-400 transition-all text-gray-800 bg-slate-200 border-b-4 border-gray-300 focus:border-b-primary-800 appearance-none rounded-lg outline-none',
                'placeholder': 'ایمیل',
                'dir': 'ltr',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'block w-full p-3 text-sm/6 md:text-base outline-1 -outline-offset-1 placeholder:text-gray-400 transition-all text-gray-800 bg-slate-200 border-b-4 border-gray-300 focus:border-b-primary-800 appearance-none rounded-lg outline-none',
                'placeholder': 'شماره تماس',
                'dir': 'ltr',
            }),
            'subject': forms.TextInput(attrs={
                'class': 'block w-full p-3 text-sm/6 md:text-base outline-1 -outline-offset-1 placeholder:text-gray-400 transition-all text-gray-800 bg-slate-200 border-b-4 border-gray-300 focus:border-b-primary-800 appearance-none rounded-lg outline-none',
                'placeholder': 'موضوع',
            }),
            'message': forms.Textarea(attrs={
                'class': 'block w-full p-3 text-sm/6 md:text-base outline-1 -outline-offset-1 placeholder:text-gray-400 transition-all text-gray-800 bg-slate-200 border-b-4 border-gray-300 focus:border-b-primary-800 appearance-none rounded-lg outline-none',
                'placeholder': 'پیام شما',
                'rows': 5,
            }),
        }
