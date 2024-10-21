# forms.py
from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment', 'fabric_quality', 'comfort', 'style', 'helpful_count', 'not_helpful_count']
        widgets = {
            'rating': forms.Select(choices=[(i, i) for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
            'helpful_count': forms.HiddenInput(),  # Hidden field
            'not_helpful_count': forms.HiddenInput(),  # Hidden field
        
        }
