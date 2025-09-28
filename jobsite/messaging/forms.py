from django import forms
from django.contrib.auth import get_user_model
from .models import Message

User = get_user_model()

class MessageForm(forms.ModelForm):
    recipient = forms.ModelChoiceField(queryset=User.objects.all(), required=False)

    class Meta:
        model = Message
        fields = ['recipient', 'subject', 'body']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        parent_message = kwargs.pop('parent_message', None)
        super().__init__(*args, **kwargs)
        
        if parent_message:
            self.fields['subject'].required = False
        
        if self.initial.get('recipient'):
            self.fields['recipient'].widget = forms.HiddenInput()
        else:
            self.fields['recipient'].queryset = User.objects.exclude(id=self.initial.get('sender_id'))