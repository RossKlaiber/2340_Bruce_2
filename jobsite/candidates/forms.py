from django import forms

class CandidateSearchForm(forms.Form):
    search_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Senior Python Developer'}),
    )
    skills = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Python, React'}),
        help_text='Comma-separated skills'
    )
    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Atlanta, GA'})
    )
    projects = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Agile methodologies, MERN stack'})
    )

    def cleaned_skills_list(self):
        raw = self.cleaned_data.get('skills') or ''
        return [s.strip() for s in raw.split(',') if s.strip()]