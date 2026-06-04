# ================= IMPORTS =================
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth.hashers import check_password
from functools import wraps
from decimal import Decimal
from ..models import (
    UserProfile,
    Animal,
    PetType,
    LostPet,
    FoundPet,
    RehomePet,
    AdoptionApplication,
    VisitRequest,
    Donation,
    Notification
)

from ..forms import (
    UserRegistrationForm,
    UserProfileUpdateForm,
    AdoptionApplicationForm,
)

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from ..models import ChatRoom, Message, UserProfile
# ================= COMMON HELPERS =================

def sentence_case(text):
    if text:
        return text.strip().capitalize()
    return text


# ================= HOME =================

def home(request):
    return render(request, 'adoption_system/user/home.html')


# ================= USER AUTH =================


def user_login_required(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        user_id = request.session.get('user_id')

        if not user_id:
            return redirect('login')

        try:
            request.profile = UserProfile.objects.get(id=user_id)
        except UserProfile.DoesNotExist:
            return redirect('login')

        return view_func(request, *args, **kwargs)

    return wrapper








def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_profile_completed = False
            user.save()
            return redirect('login')
    else:
        form = UserRegistrationForm()

    return render(
        request,
        'adoption_system/user/register.html',
        {'form': form}
    )


# from django.shortcuts import render, redirect
# from django.db.models import Q
# from django.contrib.auth.hashers import check_password
# from ..models import UserProfile

def login_view(request):

    if request.method == 'POST':
        identifier = request.POST.get('identifier')
        password = request.POST.get('password')

        try:
            user_profile = UserProfile.objects.get(
                Q(email=identifier) | Q(phone_number=identifier)
            )
        except UserProfile.DoesNotExist:
            return render(request,
                'adoption_system/user/login.html',
                {'error': 'Account not registered.'}
            )

        if not check_password(password, user_profile.password):
            return render(request,
                'adoption_system/user/login.html',
                {'error': 'Incorrect password.'}
            )
        if user_profile.is_blocked:
            return render(request,
                'adoption_system/user/login.html',
                {'error': 'Your account has been blocked by the admin.'}
            )
        request.session.flush()
        request.session['user_id'] = user_profile.id

        # Instead of redirect immediately
        return render(request,
            'adoption_system/user/login.html',
            {'login_success': True}
        )

    return render(request, 'adoption_system/user/login.html')

def logout_view(request):
    request.session.flush()
    return redirect('login')


# ================= USER MODULE =================
from django.contrib.auth.models import User
from django.db.models import Sum
from ..models import AdoptionApplication, VisitRequest, Donation, Message

from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta

@user_login_required
def userhome(request):

    profile = request.profile

    # ================= COUNTS =================
    adoption_count = AdoptionApplication.objects.filter(
        user=profile
    ).count()

    approved_count = AdoptionApplication.objects.filter(
        user=profile,
        status="Approved"
    ).count()

    donation_total = Donation.objects.filter(
        user=profile,
        payment_status="Paid"
    ).aggregate(total=Sum("amount"))["total"] or 0

    visit_count = VisitRequest.objects.filter(
        user=profile
    ).count()

    unread_count = Message.objects.filter(
        room__user=profile,
        sender="admin",
        is_read=False
    ).count()

    context = {
        "adoption_count": adoption_count,
        "approved_count": approved_count,
        "donation_total": donation_total,
        "visit_count": visit_count,
        "unread_count": unread_count,
        "user_profile": profile
    }

    return render(
        request,
        "adoption_system/user/userhome.html",
        context
    )
@user_login_required
def recent_activity(request):

    profile = request.profile

    # Dropdown filter (default 7 days for activity page)
    days = request.GET.get("days", "7")

    try:
        days = int(days)
    except ValueError:
        days = 7

    if days not in [5, 7, 30]:
        days = 7

    filter_date = timezone.now() - timedelta(days=days)

    # Fetch data
    recent_adoptions = AdoptionApplication.objects.filter(
        user=profile,
        submitted_at__gte=filter_date
    )

    recent_donations = Donation.objects.filter(
        user=profile,
        donated_at__gte=filter_date
    )

    recent_visits = VisitRequest.objects.filter(
        user=profile,
        created_at__gte=filter_date
    )

    # Merge into single timeline
    activities = []

    for adoption in recent_adoptions:
        pet_name = (
            adoption.animal.name
            if adoption.animal
            else adoption.rehome_pet.pet_name
        )

        activities.append({
            "type": "adoption",
            "id": adoption.id,
            "title": f"Adoption Request for {pet_name}",
            "status": adoption.status,
            "date": adoption.submitted_at
        })

    for donation in recent_donations:
        activities.append({
            "type": "donation",
            "id": donation.id,
            "title": f"Donation of ₹{donation.amount}",
            "status": "Paid",
            "date": donation.donated_at
        })

    for visit in recent_visits:
        activities.append({
            "type": "visit",
            "id": visit.id,
            "title": "Shelter Visit Request",
            "status": visit.status,
            "date": visit.created_at
        })

    activities = sorted(
        activities,
        key=lambda x: x["date"],
        reverse=True
    )
    context = {
        "activities": activities,
        "selected_days": days
    }

    return render(
        request,
        "adoption_system/user/recent_activity.html",
        context
    )


@user_login_required
def delete_activity(request, activity_type, activity_id):

    profile = request.profile

    if activity_type == "adoption":
        AdoptionApplication.objects.filter(id=activity_id, user=profile).update(is_deleted=True)

    elif activity_type == "donation":
        Donation.objects.filter(id=activity_id, user=profile).update(is_deleted=True)

    elif activity_type == "visit":
        VisitRequest.objects.filter(id=activity_id, user=profile).update(is_deleted=True)

    return redirect("recent_activity")


@user_login_required
def clear_all_activity(request):

    profile = request.profile

    AdoptionApplication.objects.filter(user=profile).update(is_deleted=True)
    Donation.objects.filter(user=profile).update(is_deleted=True)
    VisitRequest.objects.filter(user=profile).update(is_deleted=True)

    return redirect("recent_activity")


from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from django.http import HttpResponse

@user_login_required
def export_activity_pdf(request):

    profile = request.profile

    activities = AdoptionApplication.objects.filter(
        user=profile,
        is_deleted=False
    )

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="activity_report.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("Activity Report", styles["Heading1"]))
    elements.append(Spacer(1, 20))

    for act in activities:
        elements.append(Paragraph(f"{act.pet_name} - {act.status}", styles["Normal"]))
        elements.append(Spacer(1, 10))

    doc.build(elements)
    return response

    
@user_login_required
def animals(request):

    animals = Animal.objects.filter(
    is_active=True,
    status="Available"
)
    pet_types = PetType.objects.filter(is_active=True)

    # ✅ ADD THIS LINE
    rehome_pets = RehomePet.objects.filter(status="Approved")

    selected_type = request.GET.get('type')
    selected_age = request.GET.get('age')

    if selected_type:
        try:
            animals = animals.filter(pet_type_id=int(selected_type))
        except ValueError:
            pass

    if selected_age == 'young':
        animals = animals.filter(age__lte=1)
    elif selected_age == 'adult':
        animals = animals.filter(age__gte=2, age__lte=7)
    elif selected_age == 'senior':
        animals = animals.filter(age__gte=8)

    return render(
        request,
        'adoption_system/user/animals.html',
        {
            'animals': animals,
            'rehome_pets': rehome_pets,   # ✅ ADD THIS
            'pet_types': pet_types,
            'selected_type': selected_type or '',
            'selected_age': selected_age or ''
        }
    )
from django.contrib import messages


@user_login_required
def adoption_request(request, animal_id):

    user = request.profile
    pet_id = animal_id

    # Try finding in Animal
    animal = Animal.objects.filter(id=pet_id, status="Available").first()

    # Try finding in RehomePet
    rehome_pet = RehomePet.objects.filter(id=pet_id, status="Approved").first()

    # If neither found
    if not animal and not rehome_pet:
        return redirect("animals")

    # Extra safety check
    if animal and animal.status != "Available":
        return redirect("animals")

    # Decide which pet
    pet_name = animal.name if animal else rehome_pet.pet_name
    pet_type = animal.pet_type.name if animal else rehome_pet.pet_type
    pet_gender = animal.gender if animal else rehome_pet.gender
    pet_age_value = animal.age if animal else rehome_pet.age

    # Age category
    if pet_age_value <= 1:
        pet_age = "Puppy / Kitten"
    elif pet_age_value <= 7:
        pet_age = "Adult"
    else:
        pet_age = "Senior"

    initial_data = {
        "full_name": user.username,
        "email": user.email,
        "phone": user.phone_number,
        "address": user.address,
        "pet_name": pet_name,
        "pet_type": pet_type,
        "pet_gender": pet_gender,
        "pet_age": pet_age,
    }

    if request.method == "POST":

        form = AdoptionApplicationForm(request.POST)

        if form.is_valid():

            # Prevent duplicate applications
            duplicate = AdoptionApplication.objects.filter(
                user=user,
                animal=animal if animal else None,
                rehome_pet=rehome_pet if rehome_pet else None
            ).exclude(status="Rejected").exists()

            if duplicate:
                messages.warning(
                    request,
                    "⚠ You have already applied to adopt this pet."
                )
                return redirect("animals")

            application = form.save(commit=False)
            application.user = user
            application.animal = animal if animal else None
            application.rehome_pet = rehome_pet if rehome_pet else None
            application.terms_accepted = True
            application.save()

            # 🔒 Lock the pet while adoption is under review
            if animal:
                animal.status = "Under Review"
                animal.save()

            if rehome_pet:
                rehome_pet.status = "Under Review"
                rehome_pet.save()

            # Notify admins
            for admin in User.objects.filter(is_staff=True):
                Notification.objects.create(
                    user=admin,
                    title="New Adoption Request",
                    message=f"{user.username} applied to adopt {pet_name}"
                )

            return redirect("userhome")

    else:
        form = AdoptionApplicationForm(initial=initial_data)

    return render(
        request,
        "adoption_system/user/adoption.html",
        {"form": form}
    )

from django.shortcuts import render, redirect
from ..models import RehomePet, UserProfile



@user_login_required
def my_adoptions(request):

    profile = request.profile

    adoptions = AdoptionApplication.objects.filter(
        user=profile
    ).order_by('-submitted_at')

    return render(
        request,
        'adoption_system/user/my_adoptions.html',
        {
            'adoptions': adoptions
        }
    )

@user_login_required
def request_adoption_date(request, id):

    adoption = get_object_or_404(
        AdoptionApplication,
        id=id,
        user=request.profile
    )

    if request.method == "POST":

        requested_date = request.POST.get("requested_date")
        requested_time = request.POST.get("requested_time")

        # SAVE ONLY IF USER PROVIDED VALUES
        if requested_date and requested_time:
            adoption.requested_date = requested_date
            adoption.requested_time = requested_time
            adoption.status = "Date Requested"
            adoption.save()

            return redirect("my_adoptions")

    return render(
        request,
        "adoption_system/user/request_adoption_date.html",
        {"adoption": adoption}
    )



@user_login_required
def foster(request):
    return render(request, 'adoption_system/user/foster.html')

@user_login_required
def visit_request(request, id):

    profile = request.profile

    animal = Animal.objects.filter(id=id).first()
    rehome_pet = RehomePet.objects.filter(id=id).first()

    if request.method == "POST":

        VisitRequest.objects.create(
            user=profile,
            animal=animal if animal else None,
            rehome_pet=rehome_pet if rehome_pet else None,
            visit_date=request.POST.get('visit_date'),
            visit_time=request.POST.get('visit_time'),
            message=request.POST.get('message')
        )

        return redirect('animals')

    return render(
        request,
        'adoption_system/user/visits.html',
        {
            'pet_name': animal.name if animal else rehome_pet.pet_name,
            'pet_type': animal.pet_type.name if animal else rehome_pet.pet_type
        }
    )

@user_login_required
def my_visits(request):
    profile = request.profile

    visits = VisitRequest.objects.filter(
        user=profile
    ).order_by('-created_at')

    return render(
        request,
        'adoption_system/user/my_visits.html',
        {'visits': visits}
    )


@user_login_required
def donations(request):
    return render(request, 'adoption_system/user/donations.html')


@user_login_required
def profile(request):
    user = UserProfile.objects.get(id=request.session['user_id'])

    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.is_profile_completed = True
            profile.save()
            return redirect('profile')
    else:
        form = UserProfileUpdateForm(instance=user)

    return render(
        request,
        'adoption_system/user/profile.html',
        {'form': form, 'user': user}
    )

from ..models import PetType, Breed, RehomePet, UserProfile
@user_login_required
def rehome_pet(request):

    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('login')

    profile = UserProfile.objects.filter(id=user_id).first()

    if not profile:
        return redirect('login')

    # GET dropdown data
    pet_types = PetType.objects.all()
    breeds = Breed.objects.all()

    if request.method == "POST":

        RehomePet.objects.create(
            user=profile,

            pet_type_id=request.POST.get('pet_type'),
            pet_name=request.POST.get('pet_name'),
            age=request.POST.get('age'),
            breed_id=request.POST.get('breed'),
            color=request.POST.get('color'),
            gender=request.POST.get('gender'),

            vaccination_status=request.POST.get('vaccination_status'),
            medical_conditions=request.POST.get('medical_conditions'),
            neutered=request.POST.get('neutered'),
            last_vaccination_date=request.POST.get('last_vaccination_date'),
            special_diet=request.POST.get('special_diet'),

            rehoming_reason=request.POST.get('rehoming_reason'),
            hide_reason=True if request.POST.get('hide_reason') else False,

            living_environment=request.POST.get('living_environment'),
            child_friendly=request.POST.get('child_friendly'),
            good_with_pets=request.POST.get('good_with_pets'),

            house_trained=request.POST.get('house_trained'),
            leash_trained=request.POST.get('leash_trained'),
            aggressive_behavior=request.POST.get('aggressive_behavior'),

            pet_description=request.POST.get('pet_description'),
            meet_greet_availability=request.POST.get('meet_greet_availability'),
            urgency=request.POST.get('urgency'),

            city=profile.city,
            state=profile.state,
            owner_name=profile.username,
            contact_info=profile.phone_number,
        )

        return redirect('userhome')

    return render(
        request,
        'adoption_system/user/rehome_pet.html',
        {
            'profile': profile,
            'pet_types': pet_types,
            'breeds': breeds
        }
    )



@user_login_required
def my_rehome_requests(request):

    profile = request.profile

    pets = RehomePet.objects.filter(user=profile).order_by('-created_at')

    return render(request,
        'adoption_system/user/my_rehome_requests.html',
        {'pets': pets}
    )



@user_login_required
def chat_admin(request):
    return render(request, 'adoption_system/user/chat_admin.html')

from ..matching_engine import find_best_match, image_similarity
from datetime import datetime
# ================= LOST PET - USER =================
@user_login_required
def lost_pet(request):

    pet_types = PetType.objects.filter(is_active=True)

    if request.method == "POST":

        user = UserProfile.objects.get(
            id=request.session['user_id']
        )

        # 1️⃣ Save Lost Pet
        lost_pet_obj = LostPet.objects.create(
            user=user,
            pet_name=sentence_case(request.POST.get('pet_name')),
            pet_type_id=request.POST.get('pet_type'),
            breed=sentence_case(request.POST.get('breed')),
            last_seen_location=sentence_case(
                request.POST.get('last_seen_location')
            ),
            date_lost=datetime.strptime(
            request.POST.get('date_lost'),
            "%Y-%m-%d"
            ).date(),
            identification_details=sentence_case(
                request.POST.get('identification_details')
            ),
            pet_photo=request.FILES.get('pet_photo')
        )
        # Notify Staff
        for staff in User.objects.filter(groups__name="Staff"):
            Notification.objects.create(
                user=staff,
                title="New Lost Pet Report",
                message=f"A lost pet '{lost_pet_obj.pet_name}' was reported."
            )

        # Notify Admin
        for admin in User.objects.filter(is_staff=True):
            Notification.objects.create(
                user=admin,
                title="New Lost Pet Report",
                message=f"A lost pet '{lost_pet_obj.pet_name}' was reported."
            )

        # 2️⃣ Run Matching
        best_match, ml_score = find_best_match(lost_pet_obj)

        if best_match:
            image_score = 0

            if lost_pet_obj.pet_photo and best_match.pet_photo:
                image_score = image_similarity(
                    lost_pet_obj.pet_photo,
                    best_match.pet_photo
                )

            final_score = (ml_score * 0.5) + (image_score * 0.5)

            if final_score > 0.6:
                lost_pet_obj.matched_found_pet = best_match
                lost_pet_obj.match_score = final_score
                lost_pet_obj.save()

        return redirect('userhome')

    return render(
        request,
        'adoption_system/user/lost_pet.html',
        {'pet_types': pet_types}
    )

@user_login_required
def my_lost_pets(request):

    user = UserProfile.objects.get(
        id=request.session['user_id']
    )

    lost_pets = LostPet.objects.filter(
        user=user
    ).order_by('-reported_date')

    return render(
        request,
        'adoption_system/user/my_lost_pets.html',
        {'lost_pets': lost_pets}
    )

@user_login_required
def browse_found_pets(request):

    found_pets = FoundPet.objects.filter(
        status="Found"
    ).order_by('-reported_date')

    return render(
        request,
        'adoption_system/user/browse_found_pets.html',
        {'found_pets': found_pets}
    )
@user_login_required
def contact_finder(request, pet_id):

    pet = get_object_or_404(FoundPet, id=pet_id)

    finder = pet.user

    return render(
        request,
        'adoption_system/user/contact_finder.html',
        {'pet': pet, 'finder': finder}
    )

@user_login_required
def report_match(request, pet_id):

    pet = get_object_or_404(FoundPet, id=pet_id)

    user = UserProfile.objects.get(
        id=request.session['user_id']
    )

    # simple notification example
    Message.objects.create(
        sender=user,
        receiver=pet.user,
        content=f"A user thinks the pet you reported might be theirs."
    )

    return redirect('browse_found_pets')   
@user_login_required
def mark_pet_found(request, pet_id):

    pet = get_object_or_404(LostPet, id=pet_id)

    if request.method == "POST":
        pet.status = "Found"
        pet.save()

    return redirect('my_lost_pets')


# ================= FOUND PET - USER =================
@user_login_required
def found_pet(request):

    pet_types = PetType.objects.filter(is_active=True)

    if request.method == "POST":

        user = UserProfile.objects.get(
            id=request.session['user_id']
        )

        FoundPet.objects.create(
            user=user,
            pet_type_id=request.POST.get('pet_type'),
            found_location=request.POST.get('found_location'),
            date_found=request.POST.get('date_found'),
            condition=request.POST.get('condition'),
            description=request.POST.get('description'),
            pet_photo=request.FILES.get('pet_photo')
        )

        return redirect('userhome')

    return render(
        request,
        'adoption_system/user/found_pet.html',
        {'pet_types': pet_types}
    )

@user_login_required
def my_found_pets(request):

    user = UserProfile.objects.get(
        id=request.session['user_id']
    )

    found_pets = FoundPet.objects.filter(
        user=user
    ).order_by('-reported_date')

    return render(
        request,
        'adoption_system/user/my_found_pets.html',
        {
            'found_pets': found_pets
        }
    )
@user_login_required
def handover_shelter(request, pet_id):

    pet = get_object_or_404(FoundPet, id=pet_id)

    user = UserProfile.objects.get(
        id=request.session['user_id']
    )

    if pet.user != user:
        return redirect('my_found_pets')

    if request.method == "POST":
        pet.status = "Handed to Shelter"
        pet.save()

    return redirect('my_found_pets')

@user_login_required

def mark_pet_returned(request, pet_id):

    pet = get_object_or_404(FoundPet, id=pet_id)

    if request.method == "POST":
        pet.status = "Returned"
        pet.save()

    return redirect('my_found_pets')



@user_login_required
def animal_detail(request, id):

    # Try finding the pet in Animal table
    animal = Animal.objects.filter(id=id).first()

    # Try finding the pet in RehomePet table
    rehome_pet = RehomePet.objects.filter(id=id, status="Approved").first()

    # If pet not found in both tables
    if not animal and not rehome_pet:
        return redirect("animals")

    context = {
        "animal": animal,
        "rehome_pet": rehome_pet
    }

    return render(
        request,
        "adoption_system/user/animal_detail.html",
        context
    )

@user_login_required
def start_chat(request):
    user_id = request.session.get('user_id')

    user = get_object_or_404(UserProfile, id=user_id)

    room, created = ChatRoom.objects.get_or_create(user=user)

    return redirect('user_chat_room', room.id)


@user_login_required
def user_chat_room(request, room_id):
    user_id = request.session.get('user_id')

    room = get_object_or_404(ChatRoom, id=room_id)

    # 🔐 Security check
    if room.user.id != user_id:
        return redirect('login')

    # ✅ Mark admin messages as read
    room.messages.filter(
        sender="admin",
        is_read=False
    ).update(is_read=True)

    # ✅ Send new message
    if request.method == "POST":
        msg = request.POST.get("message")
        if msg:
            Message.objects.create(
                room=room,
                sender="user",
                message=msg
            )
            return redirect('user_chat_room', room_id=room.id)

    # ✅ IMPORTANT: Hide messages deleted only for user
    messages = room.messages.filter(
        deleted_for_user=False
    ).order_by("timestamp")

    return render(
        request,
        "adoption_system/chat/user_chat_room.html",
        {
            "room": room,
            "messages": messages
        }
    )

@user_login_required
def fetch_user_messages(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)

    # IMPORTANT: hide messages cleared for user
    messages = room.messages.filter(
        deleted_for_user=False
    ).order_by("timestamp")

    data = []

    for msg in messages:
        data.append({
            "sender": msg.sender,
            "message": msg.message,
            "timestamp": msg.timestamp.strftime("%H:%M"),
            "deleted_for_everyone": msg.deleted_for_everyone,
        })

    return JsonResponse({"messages": data})


@user_login_required
def delete_message_user(request, message_id):
    message = get_object_or_404(Message, id=message_id)

    # Hide only for user
    message.deleted_for_user = True
    message.save()

    return redirect('user_chat_room', room_id=message.room.id)

@user_login_required
def delete_message_user(request, message_id):
    message = get_object_or_404(Message, id=message_id)

    # Hide only for user
    message.deleted_for_user = True
    message.save()

    return redirect('user_chat_room', room_id=message.room.id)
@user_login_required
def delete_message_everyone_user(request, message_id):
    message = get_object_or_404(Message, id=message_id)

    if message.sender == "user":
        message.deleted_for_everyone = True
        message.message = ""
        message.save()

    return redirect('user_chat_room', room_id=message.room.id)

@user_login_required
def clear_chat_user(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    room.messages.update(deleted_for_user=True)
    return redirect('user_chat_room', room_id=room.id)

import requests
import json
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def ai_chatbot(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "")

            if not user_message:
                return JsonResponse({"response": "Please type something."})

            url = "https://api.groq.com/openai/v1/chat/completions"

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.GROQ_API_KEY}"
            }

            payload = {
    "model": "llama-3.1-8b-instant",
    "messages": [
        {
            "role": "system",
            "content": """
You are an AI assistant for THIS Animal Shelter & Adoption Management System.

IMPORTANT RULES:
- Only answer based on the features available in this system.
- Do NOT invent adoption fees, policies, or processes.
- If information is not available in the system, say:
  "Please contact the shelter admin for accurate details."
- Keep answers short and clear.
"""
        },
        {
            "role": "user",
            "content": user_message
        }
    ],
    "max_tokens": 300
}

            response = requests.post(url, headers=headers, json=payload)

            # print("STATUS:", response.status_code)
            # print("RAW:", response.text)

            result = response.json()

            if "choices" in result:
                reply = result["choices"][0]["message"]["content"]
            else:
                reply = result.get("error", {}).get("message", "AI unavailable.")

            return JsonResponse({"response": reply})

        except Exception as e:
            print("SERVER ERROR:", e)
            return JsonResponse({"response": "Server error. Try again."})

    return JsonResponse({"response": "Invalid request."})




from decimal import Decimal

@user_login_required
def adoption_payment(request, id):

    adoption = get_object_or_404(
        AdoptionApplication,
        id=id,
        user=request.profile
    )

    if adoption.animal:
        adoption_fee = adoption.animal.adoption_fee or Decimal("0")
    elif adoption.rehome_pet:
        adoption_fee = adoption.rehome_pet.adoption_fee or Decimal("0")
    else:
        adoption_fee = Decimal("0")

    if request.method == "POST":

        payment_method = request.POST.get("payment_method")
        donation = Decimal(request.POST.get("donation_amount") or "0")

        total_amount = adoption_fee + donation

        request.session['payment_data'] = {
    'type': 'adoption',   # 🔥 ADD THIS LINE
    'adoption_id': adoption.id,
    'payment_method': payment_method,
    'donation': str(donation),
    'total': str(total_amount)
}

        return redirect("review_payment")

    return render(
        request,
        "adoption_system/user/adoption_payment.html",
        {
            "adoption_fee": adoption_fee,
            "adoption": adoption
        }
    )

@user_login_required
def review_payment(request):

    payment_data = request.session.get('payment_data')

    if not payment_data:
        return redirect("my_adoptions")

    return render(request,
        "adoption_system/user/review_payment.html",
        payment_data
    )


@user_login_required
def enter_pin(request):

    if request.method == "POST":
        pin = request.POST.get("pin", "").strip()

        if pin == "1234":

            payment_data = request.session.get("payment_data")

            if not payment_data:
                return redirect("my_adoptions")

            if payment_data.get("type") == "donation":
                return redirect("donation_processing")
            else:
                return redirect("adoption_processing")

        return render(
            request,
            "adoption_system/user/enter_pin.html",
            {"error": "Invalid PIN"}
        )

    return render(request, "adoption_system/user/enter_pin.html")


@user_login_required
def processing_payment(request):

    payment_data = request.session.get("payment_data")

    if not payment_data:
        return redirect("my_adoptions")

    if payment_data.get("type") == "donation":
        success_url = "donation_payment_success"
    else:
        success_url = "adoption_payment_success"

    return render(
        request,
        "adoption_system/user/processing.html",
        {"success_url": success_url}
    )

import uuid
from django.utils import timezone
import uuid
from decimal import Decimal

@user_login_required
def adoption_payment_success(request):

    payment_data = request.session.get("payment_data")

    # If session expired
    if not payment_data:
        return redirect("my_adoptions")

    adoption = get_object_or_404(
        AdoptionApplication,
        id=payment_data["adoption_id"],
        user=request.profile
    )

    transaction_id = "TXN" + uuid.uuid4().hex[:10].upper()

    adoption.payment_method = payment_data["payment_method"]
    adoption.donation_amount = Decimal(payment_data["donation"])
    adoption.payment_status = "Paid"
    adoption.status = "Completed"
    adoption.transaction_id = transaction_id
    adoption.save()

    # 🔹 Update animal status
    if adoption.animal:
        adoption.animal.status = "Adopted"
        adoption.animal.save()

    if adoption.rehome_pet:
        adoption.rehome_pet.status = "Adopted"
        adoption.rehome_pet.save()

    # remove payment session
    request.session.pop("payment_data", None)

    # ALWAYS return something
    return render(
        request,
        "adoption_system/user/payment_success.html",
        {
            "total": payment_data["total"],
            "transaction_id": transaction_id,
            "adoption": adoption
        }
    )

@user_login_required
def adoption_processing(request):
    return render(
        request,
        "adoption_system/user/adoption_processing.html"
    )
@user_login_required
def donation_processing(request):
    return render(request, "adoption_system/user/donation_processing.html")

import uuid
from decimal import Decimal

@user_login_required
def donation_payment_success(request):

    payment_data = request.session.get('payment_data')

    if not payment_data:
        return redirect("donate")

    transaction_id = "DON" + uuid.uuid4().hex[:10].upper()

    Donation.objects.create(
        user=request.profile,
        amount=Decimal(payment_data['total']),
        payment_method=payment_data['payment_method'],
        payment_status="Paid",
        transaction_id=transaction_id
    )

    request.session.pop('payment_data', None)

    return render(
        request,
        "adoption_system/user/donation_success.html",
        {
            "total": payment_data['total'],
            "transaction_id": transaction_id
        }
    )
from decimal import Decimal
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch


@user_login_required
def download_receipt(request, id):

    adoption = get_object_or_404(
        AdoptionApplication,
        id=id,
        user=request.profile
    )

    # Get fees
    if adoption.animal:
        adoption_fee = adoption.animal.adoption_fee or Decimal("0")
    elif adoption.rehome_pet:
        adoption_fee = adoption.rehome_pet.adoption_fee or Decimal("0")
    else:
        adoption_fee = Decimal("0")

    donation = adoption.donation_amount or Decimal("0")
    total_paid = Decimal(adoption_fee) + Decimal(donation)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{adoption.id}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = styles["Heading1"]
    normal_style = styles["Normal"]

    elements.append(Paragraph("ANIMAL SHELTER & ADOPTION CENTER", title_style))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("<b>Payment Receipt</b>", styles["Heading2"]))
    elements.append(Spacer(1, 0.3 * inch))

    # Receipt info table
    info_data = [
        ["Receipt No:", f"RCPT-{adoption.id}"],
        ["Transaction ID:", adoption.transaction_id or "-"],
        ["Date:", timezone.now().strftime("%d %B %Y")],
        ["Adopter Name:", adoption.full_name],
        ["Pet Name:", adoption.pet_name],
        ["Payment Method:", adoption.payment_method],
    ]

    info_table = Table(info_data, colWidths=[150, 300])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))

    elements.append(info_table)
    elements.append(Spacer(1, 0.4 * inch))

    # Payment breakdown table
    payment_data = [
        ["Description", "Amount (₹)"],
        ["Adoption Fee", f"{adoption_fee:.2f}"],
        ["Donation", f"{donation:.2f}"],
        ["Total Paid", f"{total_paid:.2f}"],
    ]

    payment_table = Table(payment_data, colWidths=[300, 150])
    payment_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.7, colors.grey),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),

        # Highlight total row
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))

    elements.append(payment_table)
    elements.append(Spacer(1, 0.5 * inch))

    elements.append(Paragraph(
        "Thank you for supporting animal welfare and giving a loving home!",
        normal_style
    ))

    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph(
        "This is a system-generated receipt and does not require a signature.",
        styles["Italic"]
    ))

    doc.build(elements)

    return response
from django.shortcuts import render, redirect
from django.contrib import messages
from ..models import Donation

@user_login_required
def donate(request):

    if request.method == "POST":
        amount = float(request.POST.get("donation_amount") or 0)
        payment_method = request.POST.get("payment_method")

        if amount <= 0:
            return render(
                request,
                "adoption_system/user/donate.html",
                {"error": "Enter a valid amount"}
            )

        # 🔹 OFFLINE DONATION
        if payment_method == "offline":

            donation = Donation.objects.create(
                user=request.profile,
                amount=amount,
                payment_method="offline",
                status="pending"
            )

            return render(
                request,
                "adoption_system/user/offline_donation_success.html",
                {"donation": donation}
            )

        # 🔹 ONLINE DONATION
        request.session['payment_data'] = {
            'type': 'donation',
            'adoption_id': None,
            'payment_method': payment_method,
            'donation': amount,
            'total': amount
        }

        return redirect("review_payment")

    return render(request, "adoption_system/user/donate.html")


@user_login_required
def user_notifications(request):

    notifications = Notification.objects.filter(
        user_profile=request.profile
    ).order_by("-created_at")

    return render(
        request,
        "adoption_system/user/notifications.html",
        {"notifications": notifications}
    )
    
@user_login_required
def delete_notification(request, id):

    Notification.objects.filter(
        id=id,
        user_profile=request.profile
    ).delete()

    return JsonResponse({"status": "deleted"})

@user_login_required
def mark_all_notifications_read(request):
    Notification.objects.filter(
        user_profile=request.profile, 
        is_read=False
    ).update(is_read=True)
    return JsonResponse({"status": "updated"})

@user_login_required
def clear_all_notifications(request):
    Notification.objects.filter(
        user_profile=request.profile
    ).delete()
    return JsonResponse({"status": "deleted"})