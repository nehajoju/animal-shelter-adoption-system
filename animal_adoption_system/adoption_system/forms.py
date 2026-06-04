# adoption_system/forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
import re
from .models import UserProfile


class UserRegistrationForm(forms.ModelForm):
    confirm_password = forms.CharField(
        widget=forms.PasswordInput,
        label="Confirm Password"
    )

    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'phone_number', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }

    # ✅ Email validation
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if UserProfile.objects.filter(email=email).exists():
            raise ValidationError("Email already registered.")
        return email

    # ✅ Phone validation (10 digits)
    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if not phone.isdigit():
            raise ValidationError("Phone number must contain only digits.")
        if len(phone) != 10:
            raise ValidationError("Phone number must be 10 digits.")
        return phone

    # ✅ Password strength validation
    def clean_password(self):
        password = self.cleaned_data.get('password')

        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters.")

        if not re.search(r'[A-Z]', password):
            raise ValidationError("Password must contain at least one uppercase letter.")

        if not re.search(r'[a-z]', password):
            raise ValidationError("Password must contain at least one lowercase letter.")

        if not re.search(r'[0-9]', password):
            raise ValidationError("Password must contain at least one number.")

        return password

    # ✅ Confirm password check
    def clean(self):
        cleaned_data = super().clean()
        pw = cleaned_data.get("password")
        cpw = cleaned_data.get("confirm_password")

        if pw and cpw and pw != cpw:
            self.add_error('confirm_password', "Passwords do not match.")

        return cleaned_data

    # ✅ Save with hashed password
    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'phone_number',
            
            'occupation',
            'address',
            'city',
            'state',
            'pincode',
            'housing_type',
            'ownership',
            'family_members',
            'children',
            'other_pets',
            'home_proof',
        ]





from .models import PetType, Breed

class PetTypeForm(forms.ModelForm):
    class Meta:
        model = PetType
        fields = ['name', 'is_active']

class BreedForm(forms.ModelForm):
    class Meta:
        model = Breed
        fields = ['pet_type', 'name', 'is_active']


from django import forms
from .models import Animal, PetType, Breed



class AnimalForm(forms.ModelForm):
    class Meta:
        model = Animal
        fields = [
            'code',
            'name',
            'pet_type',
            'breed',
            'age',
            'gender',
            'color',
            'weight',
            'is_vaccinated',
            'is_sterilized',
            'is_dewormed',
            'health_status',
            'medical_notes',
            'temperament',
            'good_with_kids',
            'good_with_pets',
            'training_level',
            'arrival_date',
            'intake_type',
            'location',
            'status',
            'adoption_fee',
            'image',
            'is_active',
        ]

        widgets = {
            'arrival_date': forms.DateInput(attrs={'type': 'date'}),
            'medical_notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['pet_type'].queryset = PetType.objects.filter(is_active=True)
        self.fields['breed'].queryset = Breed.objects.filter(is_active=True)

        self.fields['code'].required = False

        self.fields['code'].widget.attrs.update({'placeholder': 'Auto-generated'})
        self.fields['name'].widget.attrs.update({'placeholder': 'Animal name'})
        self.fields['health_status'].widget.attrs.update({'placeholder': 'Healthy / Injured'})
        self.fields['temperament'].widget.attrs.update({'placeholder': 'Friendly, calm'})
        self.fields['training_level'].widget.attrs.update({'placeholder': 'House-trained'})
        self.fields['intake_type'].widget.attrs.update({'placeholder': 'Rescue / Stray'})
        self.fields['location'].widget.attrs.update({'placeholder': 'Kennel / Section'})












# adoption_system/forms.py
from django import forms
from .models import AdoptionApplication


class AdoptionApplicationForm(forms.ModelForm):

    class Meta:
        model = AdoptionApplication
        fields = [
            'full_name',
            'age',
            'email',
            'phone',
            'address',

            'pet_name',
            'pet_type',
            'pet_age',
            'pet_gender',

            'housing_type',
            'ownership',
            'permission',

            'existing_pets',
            'experience',
            'daily_schedule',

            'reason',
            'long_term_plan',
            'terms_accepted',
        ]

        widgets = {
            'address': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Enter your complete residential address'
            }),

            'daily_schedule': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Example: I work from 9 AM to 5 PM. The pet will stay indoors and I will spend evenings and weekends for feeding, walks, and playtime.'
            }),

            'reason': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Example: I want to adopt a pet for companionship and can provide a safe and loving home.'
            }),

            'long_term_plan': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Example: I will ensure regular vet visits, proper food, exercise, and lifelong care for the pet.'
            }),
        }

    def clean_age(self):
        age = self.cleaned_data.get('age')

        if age < 18:
            raise forms.ValidationError(
                "You must be at least 18 years old to adopt a pet."
            )

        if age > 80:
            raise forms.ValidationError(
                "Please enter a valid age."
            )

        return age



from .models import RehomePet


class RehomePetForm(forms.ModelForm):

    class Meta:
        model = RehomePet
        fields = '__all__'
        exclude = ['user', 'status', 'admin_notes', 'created_at']

        widgets = {
            'rehoming_reason': forms.Textarea(attrs={'rows': 4}),
            'medical_conditions': forms.Textarea(attrs={'rows': 3}),
            'special_diet': forms.Textarea(attrs={'rows': 3}),
            'pet_description': forms.Textarea(attrs={'rows': 4}),
        }