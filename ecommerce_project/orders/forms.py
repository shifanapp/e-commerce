from django import forms

class CouponApplyForm(forms.Form):
    coupon_code = forms.CharField(label='Coupon Code', max_length=50)
