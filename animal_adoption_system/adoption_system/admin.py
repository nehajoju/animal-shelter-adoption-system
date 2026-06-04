from django.contrib import admin
from .models import UserProfile, PetType, Breed, Animal, AdoptionApplication,CheckupHistory


from .models import VetProfile


@admin.register(VetProfile)
class VetProfileAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'user',
        'phone',
        'qualification',
        'experience_years',
        'status'
    )

    list_filter = ('status',)

    search_fields = ('name', 'user__username', 'phone')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'phone_number',
        'is_profile_completed',
        'created_at',
    )

    search_fields = ('username', 'email', 'phone_number')
    list_filter = ('is_profile_completed', 'created_at')


@admin.register(PetType)
class PetTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(Breed)
class BreedAdmin(admin.ModelAdmin):
    list_display = ('name', 'pet_type', 'is_active')
    list_filter = ('pet_type', 'is_active')
    search_fields = ('name',)

@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = (
        'code',
        'name',
        'pet_type',
        'breed',
        'age',
        'gender',
        'status',
        'is_active',
        'created_at',
    )

    list_filter = (
        'pet_type',
        'breed',
        'status',
        'gender',
        'is_active',
    )

    search_fields = (
        'code',
        'name',
        'breed__name',
    )

    readonly_fields = ('created_at', 'updated_at')

    ordering = ('-created_at',)

    fieldsets = (
        ('Basic Info', {
            'fields': ('code', 'name', 'pet_type', 'breed', 'age', 'gender')
        }),
        ('Medical', {
            'fields': (
                'is_vaccinated',
                'is_sterilized',
                'is_dewormed',
                'health_status',
                'medical_notes',
            )
        }),
        ('Behavior', {
            'fields': (
                'temperament',
                'good_with_kids',
                'good_with_pets',
                'training_level',
            )
        }),
        ('Shelter Info', {
            'fields': (
                'arrival_date',
                'intake_type',
                'location',
            )
        }),
        ('Adoption', {
            'fields': ('status', 'adoption_fee')
        }),
        ('System', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )


@admin.register(CheckupHistory)
class CheckupHistoryAdmin(admin.ModelAdmin):
    list_display = ('animal', 'checkup_date', 'health_status')
    list_filter = ('health_status',)

from .models import MedicalAttention
admin.site.register(MedicalAttention)

from .models import TreatmentRecord
from django.contrib import admin
from .models import TreatmentRecord


@admin.register(TreatmentRecord)
class TreatmentRecordAdmin(admin.ModelAdmin):

    list_display = (
        'animal',
        'predicted_disease',
        'final_diagnosis',
        'treatment_status',
        'follow_up_date',
        'created_at'
    )

    list_filter = (
        'treatment_status',
        'created_at'
    )

    search_fields = (
        'animal__name',
        'predicted_disease',
        'final_diagnosis'
    )

    ordering = ('-created_at',)

    readonly_fields = ('created_at',)

# adoption_system/admin.py
from django.contrib import admin
from .models import AdoptionApplication


@admin.register(AdoptionApplication)
class AdoptionApplicationAdmin(admin.ModelAdmin):

    list_display = (
        'full_name',
        'age',
        'user',
        'animal',
        'pet_type',
        'housing_type',
        'status',
        'submitted_at',
    )

    list_filter = (
        'pet_type',
        'housing_type',
        'status',
    )

    search_fields = (
        'full_name',
        'email',
        'phone',
    )

    readonly_fields = ('submitted_at',)

    fieldsets = (
        ('Personal Info', {
            'fields': ('full_name', 'age', 'email', 'phone', 'address')
        }),

        ('Relations', {
            'fields': ('user', 'animal', 'terms_accepted')
        }),

        ('Pet Preference', {
            'fields': ('pet_name', 'pet_type', 'pet_age', 'pet_gender')
        }),

        ('Housing', {
            'fields': ('housing_type', 'ownership', 'permission')
        }),

        ('Experience', {
            'fields': ('existing_pets', 'experience', 'daily_schedule')
        }),

        ('Commitment', {
            'fields': ('reason', 'long_term_plan')
        }),

        ('Adoption Status', {
            'fields': (
                'status',
                'requested_date',
                'requested_time',
                'scheduled_date',
                'scheduled_time',
                'admin_notes',
            )
        }),
    )







from .models import LostPet


@admin.register(LostPet)
class LostPetAdmin(admin.ModelAdmin):

    list_display = (
        'pet_name',
        'pet_type',
        'user',
        'last_seen_location',
        'status',
        'reported_date'
    )

    list_filter = (
        'pet_type',
        'status'
    )

    search_fields = (
        'pet_name',
        'last_seen_location'
    )


from .models import FoundPet

from django.contrib import admin
from .models import FoundPet


@admin.register(FoundPet)
class FoundPetAdmin(admin.ModelAdmin):

    list_display = (
        'pet_type',
        'found_location',
        'condition',
        'status',
        'reported_date'
    )

    list_filter = ('status', 'pet_type', 'condition')

    search_fields = (
        'found_location',
        'description'
    )



from .models import RehomePet


from .models import RehomePet


@admin.register(RehomePet)
class RehomePetAdmin(admin.ModelAdmin):

    list_display = (
        'pet_name',
        'pet_type',
        'breed',
        'color',
        'owner_name',
        'city',
        'status',
        'created_at'
    )

    list_filter = (
        'status',
        'pet_type',
        'vaccination_status',
        'city'
    )

    search_fields = (
        'pet_name',
        'breed',
        'color',
        'owner_name',
        'city'
    )

    readonly_fields = ('created_at',)



    from django.contrib import admin
from .models import VisitRequest


@admin.register(VisitRequest)
class VisitRequestAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'user',
        'get_pet_name',
        'visit_date',
        'visit_time',
        'status',
        'created_at'
    )

    list_filter = ('status', 'visit_date')
    search_fields = ('user__username',)

    def get_pet_name(self, obj):
        if obj.animal:
            return obj.animal.name
        elif obj.rehome_pet:
            return obj.rehome_pet.pet_name
        return "-"
    
    get_pet_name.short_description = "Pet"
