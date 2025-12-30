"""
فرم‌های اپ reviews
"""
from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    """فرم نظر"""
    
    class Meta:
        model = Review
        fields = ['rating', 'title', 'content', 'pros', 'cons']
        widgets = {
            'rating': forms.RadioSelect(attrs={
                'class': 'rating-input',
            }),
            'title': forms.TextInput(attrs={
                'class': 'block w-full p-3 text-sm/6 md:text-base outline-1 -outline-offset-1 placeholder:text-gray-400 transition-all text-gray-800 bg-slate-200 border-b-4 border-gray-300 focus:border-b-primary-800 appearance-none rounded-lg outline-none',
                'placeholder': 'عنوان نظر (اختیاری)',
            }),
            'content': forms.Textarea(attrs={
                'class': 'block w-full p-3 text-sm/6 md:text-base outline-1 -outline-offset-1 placeholder:text-gray-400 transition-all text-gray-800 bg-slate-200 border-b-4 border-gray-300 focus:border-b-primary-800 appearance-none rounded-lg outline-none',
                'placeholder': 'متن نظر شما',
                'rows': 4,
            }),
            'pros': forms.Textarea(attrs={
                'class': 'block w-full p-3 text-sm/6 md:text-base outline-1 -outline-offset-1 placeholder:text-gray-400 transition-all text-gray-800 bg-slate-200 border-b-4 border-gray-300 focus:border-b-primary-800 appearance-none rounded-lg outline-none',
                'placeholder': 'نقاط قوت (اختیاری)',
                'rows': 2,
            }),
            'cons': forms.Textarea(attrs={
                'class': 'block w-full p-3 text-sm/6 md:text-base outline-1 -outline-offset-1 placeholder:text-gray-400 transition-all text-gray-800 bg-slate-200 border-b-4 border-gray-300 focus:border-b-primary-800 appearance-none rounded-lg outline-none',
                'placeholder': 'نقاط ضعف (اختیاری)',
                'rows': 2,
            }),
        }
