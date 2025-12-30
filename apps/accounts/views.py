"""
ویوهای اپ accounts
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import UpdateView, DeleteView
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.conf import settings

from .models import User, OTPCode, Address
from .forms import PhoneForm, OTPVerifyForm, RegistrationForm, AddressForm


class LoginView(View):
    """ورود با شماره موبایل"""
    
    template_name = 'accounts/login.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard:home')
        
        # ذخیره next URL برای ریدایرکت بعد از لاگین
        next_url = request.GET.get('next', '')
        if next_url:
            request.session['login_next_url'] = next_url
        
        # ذخیره session_key برای انتقال سبد خرید مهمان
        if request.session.session_key:
            request.session['guest_session_key'] = request.session.session_key
        
        form = PhoneForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = PhoneForm(request.POST)
        
        if form.is_valid():
            phone = form.cleaned_data['phone']
            
            # بررسی وجود کاربر
            user_exists = User.objects.filter(phone=phone).exists()
            
            # ایجاد کد OTP
            code = OTPCode.generate_code()
            OTPCode.objects.create(phone=phone, code=code)
            
            # ذخیره شماره در session
            request.session['auth_phone'] = phone
            request.session['user_exists'] = user_exists
            
            # ارسال پیامک
            if settings.DEBUG:
                # در محیط توسعه، کد را به صورت alert نمایش می‌دهیم
                messages.info(request, f'کد تایید: {code}')
            else:
                # ارسال پیامک واقعی با کاوه‌نگار
                from apps.core.sms import send_otp_sms
                result = send_otp_sms(phone, code)
                if not result['success']:
                    messages.warning(request, 'خطا در ارسال پیامک. لطفاً دوباره تلاش کنید.')
            
            return redirect('accounts:verify_otp')
        
        return render(request, self.template_name, {'form': form})


class VerifyOTPView(View):
    """تایید کد یکبار مصرف"""
    
    template_name = 'accounts/verify_otp.html'
    template_name_register = 'accounts/register.html'
    
    def _merge_guest_cart(self, guest_session_key, user):
        """انتقال سبد خرید مهمان به کاربر"""
        from apps.cart.models import Cart
        
        try:
            guest_cart = Cart.objects.get(
                session_key=guest_session_key,
                user__isnull=True
            )
            
            # دریافت یا ایجاد سبد کاربر
            user_cart, created = Cart.objects.get_or_create(user=user)
            
            # انتقال آیتم‌ها
            for item in guest_cart.items.all():
                user_cart.add_item(item.product, item.quantity)
            
            # حذف سبد مهمان
            guest_cart.delete()
            
        except Cart.DoesNotExist:
            pass
    
    def get(self, request):
        phone = request.session.get('auth_phone')
        if not phone:
            return redirect('accounts:login')
        
        user_exists = request.session.get('user_exists', False)
        
        if user_exists:
            form = OTPVerifyForm()
            return render(request, self.template_name, {
                'form': form,
                'phone': phone
            })
        else:
            form = RegistrationForm()
            return render(request, self.template_name_register, {
                'form': form,
                'phone': phone
            })
    
    def post(self, request):
        phone = request.session.get('auth_phone')
        if not phone:
            return redirect('accounts:login')
        
        user_exists = request.session.get('user_exists', False)
        
        if user_exists:
            # کاربر موجود - فقط تایید کد
            form = OTPVerifyForm(request.POST)
            if form.is_valid():
                code = form.cleaned_data['code']
                
                # بررسی کد OTP
                otp = OTPCode.objects.filter(
                    phone=phone,
                    code=code,
                    is_used=False
                ).order_by('-created_at').first()
                
                if otp and otp.is_valid():
                    otp.is_used = True
                    otp.save()
                    
                    # ذخیره session_key مهمان قبل از لاگین
                    guest_session_key = request.session.get('guest_session_key')
                    next_url = request.session.get('login_next_url', '')
                    
                    user = User.objects.get(phone=phone)
                    login(request, user, backend='apps.accounts.backends.PhoneAuthBackend')
                    
                    # انتقال سبد خرید مهمان به کاربر
                    if guest_session_key:
                        self._merge_guest_cart(guest_session_key, user)
                    
                    # پاک کردن session
                    if 'auth_phone' in request.session:
                        del request.session['auth_phone']
                    if 'user_exists' in request.session:
                        del request.session['user_exists']
                    if 'guest_session_key' in request.session:
                        del request.session['guest_session_key']
                    if 'login_next_url' in request.session:
                        del request.session['login_next_url']
                    
                    messages.success(request, f'خوش آمدید {user.get_full_name()}')
                    
                    # ریدایرکت به صفحه قبلی یا داشبورد
                    if next_url:
                        return redirect(next_url)
                    return redirect('dashboard:home')
                else:
                    if otp:
                        otp.attempts += 1
                        otp.save()
                    messages.error(request, 'کد وارد شده نامعتبر یا منقضی شده است')
            
            return render(request, self.template_name, {
                'form': form,
                'phone': phone
            })
        
        else:
            # کاربر جدید - ثبت‌نام
            form = RegistrationForm(request.POST)
            if form.is_valid():
                code = form.cleaned_data['code']
                
                # بررسی کد OTP
                otp = OTPCode.objects.filter(
                    phone=phone,
                    code=code,
                    is_used=False
                ).order_by('-created_at').first()
                
                if otp and otp.is_valid():
                    otp.is_used = True
                    otp.save()
                    
                    # ذخیره session_key مهمان قبل از ثبت‌نام
                    guest_session_key = request.session.get('guest_session_key')
                    next_url = request.session.get('login_next_url', '')
                    
                    # ایجاد کاربر جدید
                    user = User.objects.create_user(
                        phone=phone,
                        first_name=form.cleaned_data['first_name'],
                        last_name=form.cleaned_data['last_name'],
                        national_code=form.cleaned_data['national_code'],
                        gender=form.cleaned_data['gender'],
                        is_verified=True
                    )
                    
                    login(request, user, backend='apps.accounts.backends.PhoneAuthBackend')
                    
                    # انتقال سبد خرید مهمان به کاربر جدید
                    if guest_session_key:
                        self._merge_guest_cart(guest_session_key, user)
                    
                    # پاک کردن session
                    if 'auth_phone' in request.session:
                        del request.session['auth_phone']
                    if 'user_exists' in request.session:
                        del request.session['user_exists']
                    if 'guest_session_key' in request.session:
                        del request.session['guest_session_key']
                    if 'login_next_url' in request.session:
                        del request.session['login_next_url']
                    
                    messages.success(request, 'ثبت‌نام با موفقیت انجام شد')
                    
                    # ریدایرکت به صفحه قبلی یا داشبورد
                    if next_url:
                        return redirect(next_url)
                    return redirect('dashboard:home')
                else:
                    if otp:
                        otp.attempts += 1
                        otp.save()
                    messages.error(request, 'کد وارد شده نامعتبر یا منقضی شده است')
            
            return render(request, self.template_name_register, {
                'form': form,
                'phone': phone
            })


class ResendOTPView(View):
    """ارسال مجدد کد OTP"""
    
    def post(self, request):
        phone = request.session.get('auth_phone')
        
        if not phone:
            return JsonResponse({'success': False, 'message': 'شماره موبایل یافت نشد'})
        
        # ایجاد کد جدید
        code = OTPCode.generate_code()
        OTPCode.objects.create(phone=phone, code=code)
        
        # TODO: ارسال پیامک واقعی
        
        return JsonResponse({
            'success': True,
            'message': 'کد جدید ارسال شد',
            'code': code  # فقط در محیط توسعه
        })


class LogoutView(View):
    """خروج"""
    
    def get(self, request):
        logout(request)
        messages.success(request, 'با موفقیت خارج شدید')
        return redirect('core:home')


class AddressListView(LoginRequiredMixin, View):
    """لیست آدرس‌ها"""
    
    template_name = 'accounts/addresses.html'
    
    def get(self, request):
        addresses = request.user.addresses.all()
        form = AddressForm()
        return render(request, self.template_name, {
            'addresses': addresses,
            'form': form
        })


class AddressCreateView(LoginRequiredMixin, View):
    """ایجاد آدرس جدید"""
    
    def post(self, request):
        form = AddressForm(request.POST)
        
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'آدرس با موفقیت اضافه شد')
        else:
            messages.error(request, 'خطا در ذخیره آدرس')
        
        return redirect('accounts:addresses')


class AddressUpdateView(LoginRequiredMixin, UpdateView):
    """ویرایش آدرس"""
    
    model = Address
    form_class = AddressForm
    template_name = 'accounts/address_form.html'
    success_url = reverse_lazy('accounts:addresses')
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'آدرس با موفقیت بروزرسانی شد')
        return super().form_valid(form)


class AddressDeleteView(LoginRequiredMixin, DeleteView):
    """حذف آدرس"""
    
    model = Address
    success_url = reverse_lazy('accounts:addresses')
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'آدرس با موفقیت حذف شد')
        return super().delete(request, *args, **kwargs)


class SetDefaultAddressView(LoginRequiredMixin, View):
    """تنظیم آدرس پیش‌فرض"""
    
    def post(self, request, pk):
        address = get_object_or_404(Address, pk=pk, user=request.user)
        address.is_default = True
        address.save()
        messages.success(request, 'آدرس پیش‌فرض تغییر کرد')
        return redirect('accounts:addresses')
