from django import forms
from django.contrib.auth import get_user_model
from .models import Message

User = get_user_model()

class MessageForm(forms.ModelForm):
    recipient = forms.ModelChoiceField(queryset=User.objects.all(), required=False, widget=forms.HiddenInput())
    recipient_autocomplete = forms.CharField(
        label="Recipient",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control autocomplete-recipient', 'placeholder': 'Search for a user'})
    )

    class Meta:
        model = Message
        fields = ['recipient', 'recipient_autocomplete', 'subject', 'body']
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
            self.fields['recipient_autocomplete'].widget = forms.HiddenInput()
        else:
            self.fields['recipient'].required = True
            self.fields['recipient'].widget = forms.HiddenInput()
            self.fields['recipient'].queryset = User.objects.exclude(id=self.initial.get('sender_id'))