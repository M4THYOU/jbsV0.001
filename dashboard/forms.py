from django import forms
from firesdk.firebase_functions.firebaseconn import CompanyId, encode_email, get_user
from firebase_admin import auth


class LoginForm(forms.Form):
    company_id = forms.CharField(max_length=50, required=True)
    email = forms.EmailField(max_length=254, required=True)
    password = forms.CharField(widget=forms.PasswordInput(), required=True)
    token = forms.CharField(widget=forms.HiddenInput())
    remember_code = forms.BooleanField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        company_id = cleaned_data.get('company_id')
        email = cleaned_data.get('email')
        token = cleaned_data.get('token')

        # check if company code is real.
        try:
            company_name = CompanyId.objects.get(company_code=company_id).name
        except CompanyId.DoesNotExist:
            raise forms.ValidationError('Invalid Credentials')

        # check if user exists in company
        user = get_user(company_name, encode_email(email))
        if not user:
            raise forms.ValidationError('Invalid Credentials')

        # validate token
        try:
            _ = auth.verify_id_token(token)
        except ValueError:
            raise forms.ValidationError('Invalid Credentials')

        return self.cleaned_data
