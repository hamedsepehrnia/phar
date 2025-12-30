"""
فرم‌های اپ accounts
"""
from django import forms
from django.core.validators import RegexValidator
from .models import User, Address


class PhoneForm(forms.Form):
    """فرم ورود شماره موبایل"""
    
    phone_validator = RegexValidator(
        regex=r'^09\d{9}$',
        message='شماره موبایل باید با 09 شروع شود و 11 رقم باشد'
    )
    
    phone = forms.CharField(
        max_length=11,
        validators=[phone_validator],
        widget=forms.TextInput(attrs={
            'class': 'block w-full p-3 text-sm/6 md:text-base outline-1 -outline-offset-1 placeholder:text-gray-400 transition-all text-gray-800 bg-slate-200 border-b-4 border-gray-300 focus:border-b-primary-800 appearance-none rounded-lg outline-none',
            'placeholder': '09xxxxxxxxx',
            'dir': 'ltr',
            'autocomplete': 'tel',
        }),
        label='شماره موبایل'
    )


class OTPVerifyForm(forms.Form):
    """فرم تایید کد یکبار مصرف"""
    
    code = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'block w-full p-3 text-sm/6 md:text-base outline-1 -outline-offset-1 placeholder:text-gray-400 transition-all text-gray-800 bg-slate-200 border-b-4 border-gray-300 focus:border-b-primary-800 appearance-none rounded-lg outline-none text-center tracking-widest',
            'placeholder': '------',
            'dir': 'ltr',
            'autocomplete': 'one-time-code',
            'maxlength': '6',
        }),
        label='کد تایید'
    )


class RegistrationForm(forms.Form):
    """فرم ثبت‌نام کاربر جدید"""
    
    GENDER_CHOICES = [
        ('', 'انتخاب کنید'),
        ('M', 'مرد'),
        ('F', 'زن'),
    ]
    
    code = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'block w-full p-3 text-sm/6 md:text-base outline-1 -outline-offset-1 placeholder:text-gray-400 transition-all text-gray-800 bg-slate-200 border-b-4 border-gray-300 focus:border-b-primary-800 appearance-none rounded-lg outline-none text-center tracking-widest',
            'placeholder': '------',
            'dir': 'ltr',
            'autocomplete': 'one-time-code',
            'maxlength': '6',
        }),
        label='کد تایید'
    )
    
    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'block w-full p-3 text-sm/6 md:text-base outline-1 -outline-offset-1 placeholder:text-gray-400 transition-all text-gray-800 bg-slate-200 border-b-4 border-gray-300 focus:border-b-primary-800 appearance-none rounded-lg outline-none',
            'placeholder': 'نام',
        }),
        label='نام'
    )
    
    last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'block w-full p-3 text-sm/6 md:text-base outline-1 -outline-offset-1 placeholder:text-gray-400 transition-all text-gray-800 bg-slate-200 border-b-4 border-gray-300 focus:border-b-primary-800 appearance-none rounded-lg outline-none',
            'placeholder': 'نام خانوادگی',
        }),
        label='نام خانوادگی'
    )
    
    national_code = forms.CharField(
        max_length=10,
        min_length=10,
        widget=forms.TextInput(attrs={
            'class': 'block w-full p-3 text-sm/6 md:text-base outline-1 -outline-offset-1 placeholder:text-gray-400 transition-all text-gray-800 bg-slate-200 border-b-4 border-gray-300 focus:border-b-primary-800 appearance-none rounded-lg outline-none',
            'placeholder': 'کد ملی',
            'dir': 'ltr',
            'maxlength': '10',
        }),
        label='کد ملی'
    )
    
    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        widget=forms.Select(attrs={
            'class': 'block w-full p-3 text-sm/6 md:text-base outline-1 -outline-offset-1 placeholder:text-gray-400 transition-all text-gray-800 bg-slate-200 border-b-4 border-gray-300 focus:border-b-primary-800 appearance-none rounded-lg outline-none',
        }),
        label='جنسیت'
    )
    
    def clean_national_code(self):
        """اعتبارسنجی کد ملی"""
        national_code = self.cleaned_data.get('national_code')
        
        if not national_code.isdigit():
            raise forms.ValidationError('کد ملی باید فقط شامل اعداد باشد')
        
        # الگوریتم اعتبارسنجی کد ملی
        if len(set(national_code)) == 1:
            raise forms.ValidationError('کد ملی نامعتبر است')
        
        check = sum(int(national_code[i]) * (10 - i) for i in range(9)) % 11
        if check < 2:
            valid = check == int(national_code[9])
        else:
            valid = 11 - check == int(national_code[9])
        
        if not valid:
            raise forms.ValidationError('کد ملی نامعتبر است')
        
        # بررسی تکراری نبودن
        if User.objects.filter(national_code=national_code).exists():
            raise forms.ValidationError('این کد ملی قبلاً ثبت شده است')
        
        return national_code


class ProfileUpdateForm(forms.ModelForm):
    """فرم بروزرسانی پروفایل"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'national_code', 'birth_date', 'avatar']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'block w-full p-3 text-sm/6 md:text-base outline-1 -outline-offset-1 placeholder:text-gray-400 transition-all text-gray-800 bg-slate-200 border-b-4 border-gray-300 focus:border-b-primary-800 appearance-none rounded-lg outline-none',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'block w-full p-3 text-sm/6 md:text-base outline-1 -outline-offset-1 placeholder:text-gray-400 transition-all text-gray-800 bg-slate-200 border-b-4 border-gray-300 focus:border-b-primary-800 appearance-none rounded-lg outline-none',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'block w-full p-3 text-sm/6 md:text-base outline-1 -outline-offset-1 placeholder:text-gray-400 transition-all text-gray-800 bg-slate-200 border-b-4 border-gray-300 focus:border-b-primary-800 appearance-none rounded-lg outline-none',
                'dir': 'ltr',
            }),
            'national_code': forms.TextInput(attrs={
                'class': 'block w-full p-3 text-sm/6 md:text-base outline-1 -outline-offset-1 placeholder:text-gray-400 transition-all text-gray-800 bg-slate-200 border-b-4 border-gray-300 focus:border-b-primary-800 appearance-none rounded-lg outline-none',
                'placeholder': 'کد ملی',
                'dir': 'ltr',
                'maxlength': '10',
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'block w-full p-3 text-sm/6 md:text-base outline-1 -outline-offset-1 placeholder:text-gray-400 transition-all text-gray-800 bg-slate-200 border-b-4 border-gray-300 focus:border-b-primary-800 appearance-none rounded-lg outline-none',
                'type': 'date',
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100',
            }),
        }

    def clean_national_code(self):
        """اعتبارسنجی کد ملی و جلوگیری از تکرار برای کاربران دیگر"""
        national_code = self.cleaned_data.get('national_code')

        if not national_code:
            # اجازه خالی بودن و ذخیره None برای حذف مقدار قبلی
            return None

        national_code = national_code.strip()

        if not national_code.isdigit() or len(national_code) != 10:
            raise forms.ValidationError('کد ملی باید 10 رقم و فقط شامل عدد باشد')

        # الگوریتم صحت کد ملی
        if len(set(national_code)) == 1:
            raise forms.ValidationError('کد ملی نامعتبر است')

        check = sum(int(national_code[i]) * (10 - i) for i in range(9)) % 11
        if check < 2:
            valid = check == int(national_code[9])
        else:
            valid = 11 - check == int(national_code[9])

        if not valid:
            raise forms.ValidationError('کد ملی نامعتبر است')

        # جلوگیری از تکرار برای کاربران دیگر
        exists = User.objects.exclude(pk=self.instance.pk).filter(national_code=national_code).exists()
        if exists:
            raise forms.ValidationError('این کد ملی قبلاً ثبت شده است')

        return national_code


class AddressForm(forms.ModelForm):
    """فرم آدرس"""
    
    class Meta:
        model = Address
        fields = ['title', 'province', 'city', 'address', 'postal_code', 
                  'receiver_name', 'receiver_phone', 'is_default']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'block w-full p-3 text-sm/6 md:text-base outline-1 -outline-offset-1 placeholder:text-gray-400 transition-all text-gray-800 bg-slate-200 border-b-4 border-gray-300 focus:border-b-primary-800 appearance-none rounded-lg outline-none',
                'placeholder': 'مثال: منزل، محل کار',
            }),
            'province': forms.TextInput(attrs={
                'class': 'block w-full p-3 text-sm/6 md:text-base outline-1 -outline-offset-1 placeholder:text-gray-400 transition-all text-gray-800 bg-slate-200 border-b-4 border-gray-300 focus:border-b-primary-800 appearance-none rounded-lg outline-none',
                'placeholder': 'استان',
            }),
            'city': forms.TextInput(attrs={
                'class': 'block w-full p-3 text-sm/6 md:text-base outline-1 -outline-offset-1 placeholder:text-gray-400 transition-all text-gray-800 bg-slate-200 border-b-4 border-gray-300 focus:border-b-primary-800 appearance-none rounded-lg outline-none',
                'placeholder': 'شهر',
            }),
            'address': forms.Textarea(attrs={
                'class': 'block w-full p-3 text-sm/6 md:text-base outline-1 -outline-offset-1 placeholder:text-gray-400 transition-all text-gray-800 bg-slate-200 border-b-4 border-gray-300 focus:border-b-primary-800 appearance-none rounded-lg outline-none',
                'placeholder': 'آدرس کامل',
                'rows': 3,
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'block w-full p-3 text-sm/6 md:text-base outline-1 -outline-offset-1 placeholder:text-gray-400 transition-all text-gray-800 bg-slate-200 border-b-4 border-gray-300 focus:border-b-primary-800 appearance-none rounded-lg outline-none',
                'placeholder': 'کد پستی',
                'dir': 'ltr',
                'maxlength': '10',
            }),
            'receiver_name': forms.TextInput(attrs={
                'class': 'block w-full p-3 text-sm/6 md:text-base outline-1 -outline-offset-1 placeholder:text-gray-400 transition-all text-gray-800 bg-slate-200 border-b-4 border-gray-300 focus:border-b-primary-800 appearance-none rounded-lg outline-none',
                'placeholder': 'نام گیرنده',
            }),
            'receiver_phone': forms.TextInput(attrs={
                'class': 'block w-full p-3 text-sm/6 md:text-base outline-1 -outline-offset-1 placeholder:text-gray-400 transition-all text-gray-800 bg-slate-200 border-b-4 border-gray-300 focus:border-b-primary-800 appearance-none rounded-lg outline-none',
                'placeholder': '09xxxxxxxxx',
                'dir': 'ltr',
                'maxlength': '11',
            }),
            'is_default': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-primary-600 bg-gray-100 border-gray-300 rounded focus:ring-primary-500',
            }),
        }
