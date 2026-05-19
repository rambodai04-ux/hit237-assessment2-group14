from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.views.generic import CreateView
from django.urls import reverse_lazy

from .forms import CustomUserCreationForm
from .services import create_account


class SignupView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        create_account(
            username=form.cleaned_data['username'],
            email=form.cleaned_data.get('email', ''),
            first_name=form.cleaned_data.get('first_name', ''),
            last_name=form.cleaned_data.get('last_name', ''),
            password=form.cleaned_data['password1'],
        )
        return redirect(self.success_url)
