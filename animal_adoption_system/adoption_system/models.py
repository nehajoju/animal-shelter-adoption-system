# adoption_system/models.py
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.contrib.auth.models import User
from django.contrib.auth.models import User
from django.db import models

from django.db import models
from django.contrib.auth.models import User


class VetProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='vetprofile'
    )

    # Basic Info
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)

    # Professional Details
    qualification = models.CharField(max_length=150)
    experience_years = models.PositiveIntegerField()

    # Account Status
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='Active'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name



class UserProfile(models.Model):
    # --- Registration fields ---
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)

    password = models.CharField(max_length=128)  # hashed later (not Django auth)

    # --- Profile completion fields ---
    occupation = models.CharField(max_length=100, blank=True)

    address = models.TextField(blank=True)
    city = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=50, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    profile_image = models.ImageField(
        upload_to='profile_pics/',
        null=True,
        blank=True
    )
    housing_type = models.CharField(
        max_length=50,
        choices=[
            ('Apartment', 'Apartment'),
            ('Independent House', 'Independent House'),
            ('Villa', 'Villa'),
        ],
        blank=True
    )

    ownership = models.CharField(
        max_length=20,
        choices=[
            ('Owned', 'Owned'),
            ('Rented', 'Rented'),
        ],
        blank=True
    )

    family_members = models.PositiveIntegerField(null=True, blank=True)

    children = models.CharField(
        max_length=10,
        choices=[('Yes', 'Yes'), ('No', 'No')],
        blank=True
    )

    other_pets = models.CharField(
        max_length=10,
        choices=[('Yes', 'Yes'), ('No', 'No')],
        blank=True
    )

    home_proof = models.FileField(upload_to='home_proofs/', blank=True, null=True)

    is_profile_completed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    is_blocked = models.BooleanField(default=False)

    def __str__(self):
        return self.username



class PetType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Breed(models.Model):
    pet_type = models.ForeignKey(
        PetType,
        on_delete=models.CASCADE,
        related_name='breeds'
    )
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('pet_type', 'name')

    def __str__(self):
        return f"{self.name} ({self.pet_type.name})"



from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.contrib.auth.models import User


class Animal(models.Model):

    # ================= BASIC IDENTIFIERS =================
    code = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        help_text="Auto-generated shelter code"
    )

    name = models.CharField(
        max_length=100,
        help_text="Animal name or shelter-given name"
    )

    pet_type = models.ForeignKey(
        'PetType',
        on_delete=models.PROTECT,
        related_name='animals'
    )

    breed = models.ForeignKey(
        'Breed',
        on_delete=models.PROTECT,
        related_name='animals'
    )

    # ================= DEMOGRAPHICS =================
    age = models.PositiveIntegerField(help_text="Age in years")

    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Unknown', 'Unknown'),
    ]

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        default='Unknown'
    )

    color = models.CharField(max_length=50, blank=True)

    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Weight in kg"
    )

    # ================= MEDICAL =================
    is_vaccinated = models.BooleanField(default=False)
    is_sterilized = models.BooleanField(default=False)
    is_dewormed = models.BooleanField(default=False)

    HEALTH_STATUS_CHOICES = [
    ('Healthy', 'Healthy'),
    ('Under Treatment', 'Under Treatment'),
    ('Recovering', 'Recovering'),
    ('Critical', 'Critical'),
]

    health_status = models.CharField(
        max_length=50,
        choices=HEALTH_STATUS_CHOICES,
        blank=True
    )       
    medical_notes = models.TextField(blank=True)
    medical_attention_required = models.BooleanField(default=False)
    # ---- Physical Monitoring (Vet Use) ----
    height = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Height in cm"
    )

    temperature = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Body temperature in °C"
    )

    CONDITION_CHOICES = [
        ('Normal', 'Normal'),
        ('Weak', 'Weak'),
        ('Underweight', 'Underweight'),
        ('Critical', 'Critical'),
    ]

    general_condition = models.CharField(
        max_length=20,
        choices=CONDITION_CHOICES,
        blank=True
    )

    # ================= BEHAVIOR =================
    temperament = models.CharField(max_length=100, blank=True)
    good_with_kids = models.BooleanField(default=False)
    good_with_pets = models.BooleanField(default=False)
    training_level = models.CharField(max_length=100, blank=True)

    # ================= SHELTER =================
    arrival_date = models.DateField(default=timezone.now)
    intake_type = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=100, blank=True)

    # ================= ADOPTION =================
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Under Review', 'Under Review'),
        ('Reserved', 'Reserved'),
        ('Adopted', 'Adopted'),
        ('Not Adoptable', 'Not Adoptable'),
        ('Quarantine', 'Quarantine'),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Available'
    )

    adoption_fee = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True
    )
    TREATMENT_STATUS = (
        ('none', 'No Treatment'),
        ('pending', 'Treatment Pending'),
        ('completed', 'Treatment Completed'),
    )

    treatment_status = models.CharField(
        max_length=20,
        choices=TREATMENT_STATUS,
        default='none'
    )
    # ================= MEDIA =================
    image = models.ImageField(
        upload_to='animal_images/',
        blank=True,
        null=True
    )
    rehome_application = models.ForeignKey(
    "RehomePet",
    on_delete=models.SET_NULL,
    null=True,
    blank=True
    )
   
    # ================= SYSTEM =================
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.code:
            prefix = "ANM"
            if self.pet_type and self.pet_type.name:
                prefix = self.pet_type.name[:3].upper()

            date_part = timezone.now().strftime("%Y%m%d")

            while True:
                rand_part = get_random_string(
                    4,
                    allowed_chars="0123456789"
                )
                candidate = f"{prefix}-{date_part}-{rand_part}"

                if not Animal.objects.filter(code=candidate).exists():
                    self.code = candidate
                    break

        super().save(*args, **kwargs)

class Vaccine(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name






class CheckupHistory(models.Model):

    animal = models.ForeignKey(
        Animal,
        on_delete=models.CASCADE,
        related_name='checkups'
    )

    checkup_date = models.DateTimeField(auto_now_add=True)

    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)

    health_status = models.CharField(max_length=50)
    medical_notes = models.TextField(blank=True)

    next_checkup_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.animal.name} - {self.checkup_date.date()}"

class CheckupVaccine(models.Model):

    checkup = models.ForeignKey(
        CheckupHistory,
        on_delete=models.CASCADE,
        related_name='vaccines'
    )

    vaccine = models.ForeignKey(
        Vaccine,
        on_delete=models.PROTECT
    )

    dose_date = models.DateField()
    next_dose_after_days = models.PositiveIntegerField()
    next_due_date = models.DateField()

    def __str__(self):
        return f"{self.vaccine.name} - {self.checkup.animal.name}"



class MedicalAttention(models.Model):

    animal = models.ForeignKey(
        Animal,
        on_delete=models.CASCADE,
        related_name='medical_attentions'
    )

    reported_symptoms = models.TextField(
        help_text="Symptoms observed by staff/admin"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.animal.name} - Medical Attention"



from django.db import models
from django.utils.timezone import now


class TreatmentRecord(models.Model):

    # ================= CHECKUP LINK =================
    checkup = models.ForeignKey(
        'CheckupHistory',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    # ================= ANIMAL =================
    animal = models.ForeignKey(
        'Animal',
        on_delete=models.CASCADE,
        related_name='treatments'
    )

    # ================= SYMPTOMS =================

    # Staff entered symptoms
    reported_symptoms = models.TextField(blank=True)

    # Vet observed symptoms
    observed_symptoms = models.TextField(blank=True)

    # ================= ML OUTPUT =================

    # ML predicted disease
    predicted_disease = models.CharField(
        max_length=200,
        blank=True
    )

    # Final vet decision
    final_diagnosis = models.CharField(
        max_length=200,
        blank=True
    )

    # ================= TREATMENT DETAILS =================

    treatment_plan = models.TextField(blank=True)
    medication = models.TextField(blank=True)

    TREATMENT_STATUS = [
        ('Ongoing', 'Ongoing'),
        ('Completed', 'Completed')
    ]

    treatment_status = models.CharField(
        max_length=20,
        choices=TREATMENT_STATUS,
        default='Ongoing'
    )

    # Next visit date
    follow_up_date = models.DateField(
        null=True,
        blank=True
    )
    #  🔴 Quarantine Field
    is_quarantined = models.BooleanField(default=False)
    quarantine_reason = models.TextField(blank=True)
    # Record creation time
    created_at = models.DateTimeField(auto_now_add=True)

    # ================= AUTO FOLLOW-UP CHECK =================
    @property
    def is_followup_overdue(self):
        """
        Automatically checks if follow-up date has passed
        and treatment is still ongoing.
        """
        if (
            self.follow_up_date and
            self.treatment_status == "Ongoing" and
            self.follow_up_date < now().date()
        ):
            return True
        return False

    # ================= STRING REPRESENTATION =================
    def __str__(self):
        return f"{self.animal.name} Treatment"

# adoption_system/models.py
from django.db import models


class AdoptionApplication(models.Model):

    # ================= PERSONAL INFO =================
    full_name = models.CharField(max_length=100)
    age = models.PositiveIntegerField(help_text="Applicant age in years")
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField()

    # ================= PET PREFERENCE =================
    pet_name = models.CharField(max_length=100, blank=True)

    pet_type = models.CharField(
        max_length=30,
        choices=[
            ('Dog', 'Dog'),
            ('Cat', 'Cat'),
            ('Rabbit', 'Rabbit'),
        ]
    )

    pet_age = models.CharField(
        max_length=30,
        blank=True,
        choices=[
            ('Puppy / Kitten', 'Puppy / Kitten'),
            ('Adult', 'Adult'),
            ('Senior', 'Senior'),
        ]
    )

    pet_gender = models.CharField(
        max_length=20,
        blank=True,
        choices=[
            ('Male', 'Male'),
            ('Female', 'Female'),
            ('No Preference', 'No Preference'),
        ]
    )

    # ================= HOUSING =================
    housing_type = models.CharField(
        max_length=50,
        choices=[
            ('Apartment', 'Apartment'),
            ('Independent House', 'Independent House'),
            ('Farm House', 'Farm House'),
        ]
    )

    ownership = models.CharField(
        max_length=20,
        blank=True,
        choices=[
            ('Owned', 'Owned'),
            ('Rented', 'Rented'),
        ]
    )

    permission = models.CharField(
        max_length=30,
        blank=True,
        choices=[
            ('Yes', 'Yes'),
            ('No', 'No'),
            ('Not Applicable', 'Not Applicable'),
        ]
    )

    # ================= EXPERIENCE =================
    existing_pets = models.CharField(
        max_length=10,
        blank=True,
        choices=[('Yes', 'Yes'), ('No', 'No')]
    )

    experience = models.CharField(
        max_length=30,
        blank=True,
        choices=[
            ('First Time Owner', 'First Time Owner'),
            ('Experienced', 'Experienced'),
        ]
    )

    daily_schedule = models.TextField()

    # ================= COMMITMENT =================
    reason = models.TextField()
    long_term_plan = models.TextField()

    # ================= SYSTEM RELATIONS =================
    user = models.ForeignKey(
        'UserProfile',
        on_delete=models.CASCADE,
        related_name='adoption_applications',
        null=True,
        blank=True
    )

    animal = models.ForeignKey(
        'Animal',
        on_delete=models.CASCADE,
        related_name='adoption_applications',
        null=True,
        blank=True
    )
    rehome_pet = models.ForeignKey(
    'RehomePet',
    on_delete=models.CASCADE,
    related_name='adoption_applications',
    null=True,
    blank=True
)
    terms_accepted = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    # ================= APPLICATION STATUS =================
    status = models.CharField(
        max_length=30,
        default="Pending",
        choices=[
            ("Pending", "Pending"),
            ("Approved", "Approved"),
            ("Date Requested", "Date Requested"),
            ("Scheduled", "Scheduled"),
            ("Completed", "Completed"),
            ("Rejected", "Rejected"),
        ]
    )
    PAYMENT_METHODS = [
        ('Online', 'Online'),
        ('Offline', 'Offline'),
    ]

    PAYMENT_STATUS = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
    ]

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        null=True,
        blank=True
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default='Pending'
    )

    donation_amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True
    )
    transaction_id = models.CharField(
    max_length=50,
    blank=True,
    null=True
)
        # ================= ADOPTION SCHEDULING =================
    requested_date = models.DateField(null=True, blank=True)
    requested_time = models.CharField(max_length=20, null=True, blank=True)


    scheduled_date = models.DateField(null=True, blank=True)
    scheduled_time = models.CharField(max_length=20, null=True, blank=True)


    admin_notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.full_name} - {self.pet_type} ({self.status})"









class LostPet(models.Model):

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    pet_name = models.CharField(max_length=100)

    pet_type = models.ForeignKey(
        PetType,
        on_delete=models.SET_NULL,
        null=True
    )

    breed = models.CharField(max_length=100, blank=True)

    last_seen_location = models.CharField(max_length=200)
    date_lost = models.DateField()

    identification_details = models.TextField()

    pet_photo = models.ImageField(
        upload_to='lost_pets/',
        null=True,
        blank=True
    )
    match_score = models.FloatField(null=True, blank=True)

    matched_found_pet = models.ForeignKey(
    'FoundPet',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='related_lost_pets'
    )
    reported_date = models.DateTimeField(auto_now_add=True)

    status = models.CharField(max_length=20, default="Missing")

    def __str__(self):
        return self.pet_name







class FoundPet(models.Model):

    STATUS_CHOICES = [
        ('Found', 'Found'),
        ('Returned', 'Returned'),
    ]

    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE
    )

    pet_type = models.ForeignKey(
        PetType,
        on_delete=models.SET_NULL,
        null=True
    )


    found_location = models.CharField(max_length=150)
    date_found = models.DateField()

    condition = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    pet_photo = models.ImageField(
        upload_to='found_pets/',
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Found'
    )

    reported_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pet_type} found at {self.found_location}"






from django.db import models
from django.contrib.auth.models import User

class RehomePet(models.Model):

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    # PET DETAILS
    pet_type = models.ForeignKey(PetType, on_delete=models.SET_NULL, null=True)
    breed = models.ForeignKey(Breed, on_delete=models.SET_NULL, null=True)
    pet_name = models.CharField(max_length=100)
    age = models.IntegerField()
   
    color = models.CharField(max_length=100, blank=True)

    gender = models.CharField(max_length=10)
    vaccination_status = models.CharField(max_length=30)

    # HEALTH
    medical_conditions = models.TextField(blank=True)
    neutered = models.CharField(max_length=20)
    last_vaccination_date = models.CharField(max_length=50, null=True,blank=True)
    special_diet = models.TextField(blank=True)

    # REASON
    rehoming_reason = models.TextField()
    hide_reason = models.BooleanField(default=False)

    # BEHAVIOR
    living_environment = models.CharField(max_length=20)
    child_friendly = models.CharField(max_length=20)
    good_with_pets = models.CharField(max_length=20)

    # TRAINING
    house_trained = models.CharField(max_length=20)
    leash_trained = models.CharField(max_length=20)
    aggressive_behavior = models.CharField(max_length=20)

    # DESCRIPTION
    pet_description = models.TextField(blank=True)
    pet_image = models.ImageField(upload_to='rehome_pets/', blank=True, null=True)

    # MEET & GREET
    meet_greet_availability = models.CharField(max_length=30)

    # URGENCY & LOCATION
    urgency = models.CharField(max_length=30)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)

    # OWNER DETAILS (AUTO FILLED)
    owner_name = models.CharField(max_length=100)
    contact_info = models.CharField(max_length=100)
    adoption_fee = models.DecimalField(
    max_digits=7,
    decimal_places=2,
    null=True,
    blank=True
)
    # WORKFLOW
    status = models.CharField(max_length=30, default="Pending Review")
    admin_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.pet_name










class VisitRequest(models.Model):

    # USER WHO BOOKED VISIT
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="visit_requests"
    )

    # SHELTER ANIMAL (optional)
    animal = models.ForeignKey(
        Animal,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    # REHOME PET (optional)
    rehome_pet = models.ForeignKey(
        RehomePet,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    # VISIT DETAILS
    visit_date = models.DateField()
    visit_time = models.CharField(max_length=50)

    message = models.TextField(blank=True)

    # ADMIN STATUS
    status = models.CharField(
        max_length=20,
        default="Pending",
        choices=[
            ("Pending", "Pending"),
            ("Approved", "Approved"),
            ("Rejected", "Rejected"),
        ]
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.animal:
            return f"{self.user.username} - Visit {self.animal.name}"
        elif self.rehome_pet:
            return f"{self.user.username} - Visit {self.rehome_pet.pet_name}"
        return "Visit Request"



class ChatRoom(models.Model):
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='chat_rooms'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat with {self.user.username}"


class Message(models.Model):
    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='messages'
    )

    sender = models.CharField(
        max_length=10
    )  # 'user' or 'admin'

    message = models.TextField()

    timestamp = models.DateTimeField(auto_now_add=True)

    is_read = models.BooleanField(default=False)
    deleted_for_user = models.BooleanField(default=False)
    deleted_for_admin = models.BooleanField(default=False)
    deleted_for_everyone = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.sender}: {self.message[:20]}"






from django.db import models
from django.utils import timezone

class Donation(models.Model):

    PAYMENT_METHODS = [
        ("Online", "Online"),
        ("Offline", "Offline"),
    ]

    PAYMENT_STATUS = [
        ("Pending", "Pending"),
        ("Paid", "Paid"),
    ]

    user = models.ForeignKey(
        "UserProfile",
        on_delete=models.CASCADE,
        related_name="donations"
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    purpose = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default="Pending"
    )

    transaction_id = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    donated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.user.username} - ₹{self.amount}"











        from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    user_profile = models.ForeignKey("UserProfile", on_delete=models.CASCADE, null=True, blank=True)

    title = models.CharField(max_length=200)
    message = models.TextField()

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    link = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.title