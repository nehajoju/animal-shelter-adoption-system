from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth.hashers import check_password
from functools import wraps
from ..models import *
from ..forms import *


from django.http import HttpResponse
from django.shortcuts import redirect
from functools import wraps
from django.contrib.auth import authenticate, login, logout

from ..decorators import admin_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from ..models import ChatRoom, Message,UserProfile


from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

def panel_login(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:

            # 🔐 ADMIN (is_staff = True)
            if user.is_staff:
                login(request, user)
                return redirect("admin_dashboard")

            # 🩺 VET (Group: Vet)
            elif user.groups.filter(name="Vet").exists():
                login(request, user)
                return redirect("vet_dashboard")

            # 🏢 STAFF (Group: Staff)
            elif user.groups.filter(name="Staff").exists():
                login(request, user)
                return redirect("staff_dashboard")

            # ❌ Normal user not allowed
            else:
                return render(request, "adoption_system/panel_login.html", {
                    "error": "You are not authorized to access this panel."
                })

        # ❌ Invalid credentials
        return render(request, "adoption_system/panel_login.html", {
            "error": "Invalid username or password."
        })

    return render(request, "adoption_system/panel_login.html")

from django.contrib.auth.models import User, Group
from django.contrib import messages


@admin_required
def employee_management(request):

    staff = User.objects.filter(groups__name="Staff")
    vets = User.objects.filter(groups__name="Vet")

    return render(
        request,
        "adoption_system/shelteradmin/employee_management.html",
        {
            "staff": staff,
            "vets": vets
        }
    )
                                                                                                    
@admin_required
def add_employee(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        role = request.POST.get("role")   # Staff or Vet

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("add_employee")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        group = Group.objects.get(name=role)
        user.groups.add(group)

        messages.success(request, f"{role} account created successfully!")

        return redirect("employee_management")

    return render(request, "adoption_system/shelteradmin/add_employee.html")

@admin_required
def employee_list(request):

    staff = User.objects.filter(groups__name="Staff")
    vets = User.objects.filter(groups__name="Vet")

    return render(
        request,
        "adoption_system/shelteradmin/employee_list.html",
        {
            "staff": staff,
            "vets": vets
        }
    )

@admin_required
def edit_employee(request, user_id):

    employee = get_object_or_404(User, id=user_id)

    if request.method == "POST":

        employee.username = request.POST.get("username")
        employee.email = request.POST.get("email")
        employee.save()

        messages.success(request, "Employee updated successfully.")

        return redirect("employee_management")

    return render(
        request,
        "adoption_system/shelteradmin/edit_employee.html",
        {"employee": employee}
    )
@admin_required
def toggle_employee_status(request, user_id):

    employee = get_object_or_404(User, id=user_id)

    if employee.is_active:
        employee.is_active = False
        messages.warning(request, "Employee blocked.")
    else:
        employee.is_active = True
        messages.success(request, "Employee unblocked.")

    employee.save()

    return redirect("employee_management")

@admin_required
def delete_employee(request, user_id):

    employee = get_object_or_404(User, id=user_id)

    employee.delete()

    messages.success(request, "Employee deleted.")

    return redirect("employee_management")



from django.contrib.auth import logout
from django.shortcuts import redirect

def panel_logout(request):
    logout(request)
    return redirect('panel_login')


# ================= ADMIN AUTH =================

# def admin_login(request):
#     if request.method == "POST":
#         username = request.POST.get("username")
#         password = request.POST.get("password")

#         user = authenticate(request, username=username, password=password)

#         if user and user.is_staff:
#             login(request, user)
#             return redirect("admin_dashboard")

#         return render(request, "adoption_system/shelteradmin/admin_login.html", {
#             "error": "Invalid or unauthorized credentials."
#         })

#     return render(request, "adoption_system/shelteradmin/admin_login.html")


# @admin_required
# def admin_logout(request):
#     logout(request)
#     return redirect('admin_login')


# ================= ADMIN DASHBOARD =================
from adoption_system.utils.notifications import create_user_notification
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncDate

from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta

@admin_required
def admin_dashboard(request):

    # BASIC COUNTS
    lost_pet_count = LostPet.objects.filter(status="Missing").count()
    found_pet_count = FoundPet.objects.filter(status="Found").count()

    total_unread = Message.objects.filter(
        sender="user",
        is_read=False
    ).count()

    # STATS GRID COUNTS
    animals_count = Animal.objects.count()

    pending_adoptions = AdoptionApplication.objects.filter(
        status="Pending"
    ).count()

    upcoming_visits = VisitRequest.objects.filter(
        status="Approved"
    ).count()

    donation_total = Donation.objects.aggregate(
        total=Sum("amount")
    )["total"] or 0

    # WEEKLY ADOPTIONS (Last 7 Days)
    today = timezone.now().date()
    week_ago = today - timedelta(days=6)

    weekly_queryset = (
        AdoptionApplication.objects
        .filter(status="Completed")
        .filter(submitted_at__date__gte=week_ago)
        .annotate(day=TruncDate("submitted_at"))
        .values("day")
        .annotate(total=Count("id"))
        .order_by("day")
    )

    weekly_dict = {
        item["day"]: item["total"]
        for item in weekly_queryset
    }

    weekly_labels = []
    weekly_adoptions = []

    for i in range(7):
        day = week_ago + timedelta(days=i)
        weekly_labels.append(day.strftime("%d %b"))
        weekly_adoptions.append(weekly_dict.get(day, 0))

    context = {
        "lost_pet_count": lost_pet_count,
        "found_pet_count": found_pet_count,
        "total_unread": total_unread,

        # STATS GRID DATA
        "animals_count": animals_count,
        "pending_adoptions": pending_adoptions,
        "upcoming_visits": upcoming_visits,
        "donation_total": donation_total,

        # CHART DATA
        "weekly_labels": weekly_labels,
        "weekly_adoptions": weekly_adoptions,
    }

    return render(
        request,
        "adoption_system/shelteradmin/admin_dashboard.html",
        context
    )
from django.db.models import Q
from ..models import LostPet, FoundPet

@admin_required
def lost_pets(request):

    # ================= GET FILTERS =================
    status_filter = request.GET.get('status')
    search_query = request.GET.get('search')

    lost_pets = LostPet.objects.all()

    # ================= STATUS FILTER =================
    if status_filter:
        lost_pets = lost_pets.filter(status=status_filter)

    # ================= SEARCH FILTER =================
    if search_query:
        lost_pets = lost_pets.filter(
            Q(pet_name__icontains=search_query) |
            Q(last_seen_location__icontains=search_query) |
            Q(breed__icontains=search_query) |
            Q(user__username__icontains=search_query)
        )

    lost_pets = lost_pets.order_by('-reported_date')

    # ================= MATCHING LOGIC =================
    found_pets = FoundPet.objects.filter(status="Found")

    matches = {}

    for lost in lost_pets:

        matched_found = []

        for found in found_pets:

            # 1️⃣ Pet type must match
            if found.pet_type != lost.pet_type:
                continue

            # 2️⃣ Location similarity (safe check)
            if lost.last_seen_location and found.found_location:

                lost_location = lost.last_seen_location.lower()
                found_location = found.found_location.lower()

                if lost_location in found_location or found_location in lost_location:
                    matched_found.append(found)

        # 3️⃣ Save matches
        if matched_found:
            matches[lost.id] = matched_found

    # ================= RENDER =================
    return render(
        request,
        "adoption_system/shelteradmin/lost_pets.html",
        {
            "lost_pets": lost_pets,
            "status_filter": status_filter,
            "search_query": search_query,
            "matches": matches
        }
    )
@admin_required
def admin_confirm_reunited(request, pet_id):

    pet = get_object_or_404(FoundPet, id=pet_id)

    if request.method == "POST":
        pet.status = "Returned"
        pet.save()

    return redirect('found_pets')


@admin_required
def admin_confirm_shelter(request, pet_id):

    pet = get_object_or_404(FoundPet, id=pet_id)

    if request.method == "POST":
        pet.status = "Shelter Intake"
        pet.save()

    return redirect('found_pets')

@admin_required
def found_pets(request):

    # ✅ status filter from URL
    status_filter = request.GET.get('status')

    found_pets = FoundPet.objects.all()

    # ✅ apply filter
    if status_filter:
        found_pets = found_pets.filter(status=status_filter)

    found_pets = found_pets.order_by('-reported_date')

    # only missing lost pets for matching
    lost_pets = LostPet.objects.filter(status="Missing")

    matches = {}
    strong_matches = {}

    for found in found_pets:

        matched_list = []
        strong_list = []

        for lost in lost_pets:

            # ✅ LEVEL 1 — Same pet type
            if found.pet_type_id != lost.pet_type_id:
                continue

            # ✅ LEVEL 2 — Location similarity
            if found.found_location and lost.last_seen_location:

                # normalize text
                found_loc = found.found_location.lower().strip()
                lost_loc = lost.last_seen_location.lower().strip()

                found_words = found_loc.split()
                lost_words = lost_loc.split()

                # ✅ STRONG MATCH (full text match)
                if found_loc in lost_loc or lost_loc in found_loc:
                    strong_list.append(lost)
                    matched_list.append(lost)

                # ✅ MEDIUM MATCH (same first area word)
                elif (
                    found_words and lost_words and
                    found_words[0] == lost_words[0]
                ):
                    matched_list.append(lost)

                # ✅ WEAK MATCH (any common word)
                elif any(word in lost_words for word in found_words):
                    matched_list.append(lost)

        matches[found.id] = matched_list
        strong_matches[found.id] = strong_list

    return render(
        request,
        "adoption_system/shelteradmin/found_pets.html",
        {
            'found_pets': found_pets,
            'matches': matches,
            'strong_matches': strong_matches,
            'status_filter': status_filter
        }
    )



from django.contrib import messages
@admin_required
def delete_pet_type(request, pk):
    pet_type = get_object_or_404(PetType, pk=pk)

    pet_type.delete()

    messages.success(request, "Pet Type deleted successfully.")
    return redirect('pet_type_list')

       

@admin_required
def admin_mark_pet_returned(request, pet_id):

    pet = get_object_or_404(FoundPet, id=pet_id)

    if request.method == "POST":
        pet.status = "Returned"
        pet.save()

    return redirect('found_pets')


# ================= ADMIN ANIMAL MANAGEMENT =================

@admin_required
def animal_management(request):
    animals = Animal.objects.all()
    pet_types = PetType.objects.filter(is_active=True)
    breeds = Breed.objects.filter(is_active=True)

    return render(
        request,
        'adoption_system/shelteradmin/animal_management.html',
        {
            'animals': animals,
            'pet_types': pet_types,
            'breeds': breeds,
        }
    )


@admin_required
def add_animal(request):
    if request.method == 'POST':
        form = AnimalForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('animal_management')
    else:
        form = AnimalForm()

    return render(
        request,
        'adoption_system/shelteradmin/add_animal.html',
        {'form': form}
    )

@admin_required
def edit_animal(request, animal_id):

    animal = get_object_or_404(Animal, id=animal_id)

    if request.method == 'POST':
        form = AnimalForm(request.POST, request.FILES, instance=animal)
        if form.is_valid():
            form.save()
            return redirect('animal_management')
    else:
        form = AnimalForm(instance=animal)

    return render(
        request,
        'adoption_system/shelteradmin/add_animal.html',
        {
            'form': form,
            'edit_mode': True,
            'animal': animal
        }
    )
@admin_required
def delete_animal(request, animal_id):

    animal = get_object_or_404(Animal, id=animal_id)

    if request.method == "POST":
        animal.delete()
        return redirect('animal_management')

    return redirect('animal_management')


# ================= ADMIN MASTER DATA =================

@admin_required
def pet_type_list(request):
    pet_types = PetType.objects.all()
    return render(
        request,
        'adoption_system/shelteradmin/pet_type_list.html',
        {'pet_types': pet_types}
    )


@admin_required
def add_pet_type(request):
    if request.method == 'POST':
        form = PetTypeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pet_type_list')
    else:
        form = PetTypeForm()

    return render(
        request,
        'adoption_system/shelteradmin/add_pet_type.html',
        {'form': form}
    )


@admin_required
def add_breed(request):
    if request.method == 'POST':
        form = BreedForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pet_type_list')
    else:
        form = BreedForm()

    return render(
        request,
        'adoption_system/shelteradmin/add_breed.html',
        {'form': form}
    )


# ================= ADMIN MODULE PAGES =================
from django.utils import timezone
from datetime import timedelta
from ..models import UserProfile

@admin_required
def user_management(request):

    # ================= USERS =================
    users = UserProfile.objects.all().order_by('-created_at')

    # ================= STATISTICS =================
    total_users = UserProfile.objects.count()

    blocked_users = UserProfile.objects.filter(
        is_blocked=True
    ).count()

    completed_profiles = UserProfile.objects.filter(
        is_profile_completed=True
    ).count()

    # users registered in last 7 days
    new_users = UserProfile.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=7)
    ).count()

    # ================= CONTEXT =================
    context = {
        "users": users,
        "total_users": total_users,
        "blocked_users": blocked_users,
        "completed_profiles": completed_profiles,
        "new_users": new_users,
    }

    return render(
        request,
        "adoption_system/shelteradmin/user_management.html",
        context
    )

@admin_required
def block_user(request, user_id):

    user = get_object_or_404(UserProfile, id=user_id)

    if user.is_blocked:
        user.is_blocked = False
        messages.success(request,"User unblocked successfully.")
    else:
        user.is_blocked = True
        messages.warning(request,"User has been blocked.")

    user.save()

    return redirect("user_management")


@admin_required
def delete_user(request, user_id):

    user = get_object_or_404(UserProfile, id=user_id)

    user.delete()

    messages.success(request,"User deleted successfully.")

    return redirect("user_management")

@admin_required
def animals_in_care(request):

    animals = Animal.objects.filter(is_active=True).select_related(
        "pet_type",
        "breed"
    )

    return render(
        request,
        "adoption_system/shelteradmin/animals_in_care.html",
        {"animals": animals}
    )

@admin_required
def pending_adoptions(request):
    return render(request, "adoption_system/shelteradmin/pending_adoptions.html")


@admin_required
def upcoming_visits(request):
    visits = VisitRequest.objects.all().order_by('-created_at')

    return render(
        request,
        'adoption_system/shelteradmin/upcoming_visits.html',
        {'visits': visits}
    )

@admin_required
def update_visit_status(request, id):

    visit = VisitRequest.objects.get(id=id)

    if request.method == "POST":

        action = request.POST.get("action")

        if action == "approve":
            visit.status = "Approved"
            visit.save()

            create_user_notification(
    visit.user,
    "Visit Approved 🐾",
    f"Your visit is scheduled on {visit.visit_date} at {visit.visit_time}."
)
        elif action == "reject":
            visit.status = "Rejected"
            visit.save()

            create_user_notification(
                visit.user,
                "Visit Request Rejected",
                "Unfortunately, your shelter visit request was rejected."
            )

    return redirect('upcoming_visits')


@admin_required
def adoption_schedule(request):

    pending_requests = AdoptionApplication.objects.filter(
        status="Date Requested"
    )

    scheduled_adoptions = AdoptionApplication.objects.filter(
        status="Scheduled"
    )

    completed_adoptions = AdoptionApplication.objects.filter(
        status="Completed"
    )

    return render(request,
        'adoption_system/shelteradmin/adoption_schedule.html',
        {
            'pending_requests': pending_requests,
            'scheduled_adoptions': scheduled_adoptions,
            'completed_adoptions': completed_adoptions,
        }
    )

@admin_required
def approve_adoption_schedule(request, id):

    adoption = get_object_or_404(AdoptionApplication, id=id)

    adoption.scheduled_date = adoption.requested_date
    adoption.scheduled_time = adoption.requested_time
    adoption.status = "Scheduled"
    adoption.save()
    create_user_notification(
    adoption.user_profile,
    "Adoption Visit Scheduled",
    f"Your adoption visit for {adoption.animal.name} has been scheduled."
)

    return redirect('adoption_schedule')


@admin_required
def complete_adoption(request, id):

    adoption = get_object_or_404(AdoptionApplication, id=id)

    adoption.status = "Completed"
    adoption.save()

    # mark animal adopted
    if adoption.animal:
        adoption.animal.status = "Adopted"
        adoption.animal.save()

    # 🔔 Notify user
    create_user_notification(
        adoption.user_profile,
        "Adoption Completed ❤️",
        f"You have successfully adopted {adoption.animal.name}. Congratulations!"
    )

    return redirect('adoption_schedule')


@admin_required
def reject_adoption_schedule(request, id):

    adoption = get_object_or_404(AdoptionApplication, id=id)

    if request.method == "POST":

        adoption.status = "Approved"
        adoption.requested_date = None
        adoption.requested_time = None
        adoption.save()

        # 🔔 Notify user
        create_user_notification(
            adoption.user_profile,
            "Adoption Schedule Update",
            f"Your requested adoption date for {adoption.animal.name} was not available. Please request another date."
        )

    return redirect('adoption_schedule')

@admin_required
def donations_list(request):
    return render(request, "adoption_system/shelteradmin/donations_list.html")




@admin_required
def adoption_review(request):

    status_filter = request.GET.get('status')
    search_query = request.GET.get('search')

    applications = AdoptionApplication.objects.all()

    # ---------- STATUS FILTER ----------
    if status_filter == "Approved":
        applications = applications.filter(is_approved=True)

    elif status_filter == "Rejected":
        applications = applications.filter(is_rejected=True)

    elif status_filter == "Pending":
        applications = applications.filter(
            is_approved=False,
            is_rejected=False
        )

    # ---------- SEARCH FILTER ----------
    if search_query:
        applications = applications.filter(
            Q(user__username__icontains=search_query) |
            Q(animal__name__icontains=search_query)
        )

    # ---------- ORDER ----------
    applications = applications.order_by('-submitted_at')

    return render(
        request,
        "adoption_system/shelteradmin/adoption_review.html",
        {
            "applications": applications,
            "status_filter": status_filter,
            "search_query": search_query
        }
    )



@admin_required
def approve_application(request, app_id):

    application = get_object_or_404(AdoptionApplication, id=app_id)

    if request.method == "POST":
        application.status = "Approved"
        application.save()

        create_user_notification(
            application.user_profile,
            "Adoption Approved 🎉",
            f"Your adoption request for {application.animal.name} has been approved."
        )
    return redirect('adoption_review')


@admin_required
def reject_application(request, app_id):

    application = get_object_or_404(AdoptionApplication, id=app_id)

    if request.method == "POST":
        application.status = "Rejected"
        application.save()
        create_user_notification(
        application.user_profile,
        "Adoption Request Rejected",
        f"Your adoption request for {application.animal.name} was not approved."
    )
    return redirect('adoption_review')

from django.shortcuts import render, get_object_or_404, redirect
from ..models import RehomePet

@admin_required
def rehome_list(request):
    requests = RehomePet.objects.all().order_by('-created_at')
    return render(request, 'adoption_system/shelteradmin/rehome_list.html', {
        'requests': requests
    })

# @admin_required
# def rehome_review(request, id):

#     pet = RehomePet.objects.get(id=id)

#     if request.method == "POST":

#         action = request.POST.get("action")

#         if action == "approve":
#             pet.status = "Approved"

#         elif action == "reject":
#             pet.status = "Rejected"

#         elif action == "rehomed":
#             pet.status = "Rehomed"

#         pet.admin_notes = request.POST.get("admin_notes")
#         pet.save()

#         return redirect('rehome_list')   # ✅ correct

#     return render(
#         request,
#         'adoption_system/shelteradmin/rehome_review.html',
#         {'pet': pet}
#     )

@admin_required
def rehome_review(request, id):

    pet = RehomePet.objects.get(id=id)

    if request.method == "POST":

        action = request.POST.get("action")

        if action == "approve":

            pet.status = "Approved"
            pet.admin_notes = request.POST.get("admin_notes")
            pet.save()

            # 🔹 Create Animal entry so it appears in adoption list
            pet_type_obj = PetType.objects.filter(name=pet.pet_type).first()
            breed_obj = Breed.objects.filter(name=pet.breed).first()

            Animal.objects.create(
                name=pet.pet_name,
                pet_type=pet_type_obj,
                breed=breed_obj,
                age=pet.age,
                gender=pet.gender,
                color=pet.color,
                status="Available",
                is_active=True
            )
            create_user_notification(
                pet.user_profile,
                "Rehome Request Approved",
                f"Your rehome request for {pet.pet_name} has been approved."
            )

        elif action == "reject":
            pet.status = "Rejected"
            pet.admin_notes = request.POST.get("admin_notes")
            pet.save()

        elif action == "rehomed":
            pet.status = "Rehomed"
            pet.admin_notes = request.POST.get("admin_notes")
            pet.save()

        return redirect('rehome_list')

    return render(
        request,
        'adoption_system/shelteradmin/rehome_review.html',
        {'pet': pet}
    )

@admin_required
def medical_management(request):
    return render(request, "adoption_system/shelteradmin/medical_management.html")



@admin_required
def appointment_management(request):
    return render(request, "adoption_system/shelteradmin/appointment_management.html")

from django.db.models import Sum, Avg
from ..models import Donation, AdoptionApplication


@admin_required
def donation_finance(request):

    donations = Donation.objects.filter(payment_status="Paid").order_by("-donated_at")

    adoption_payments = AdoptionApplication.objects.filter(payment_status="Paid")

    total_general = donations.aggregate(total=Sum("amount"))["total"] or 0
    total_adoption = adoption_payments.aggregate(total=Sum("donation_amount"))["total"] or 0

    total_income = total_general + total_adoption

    highest_donation = donations.aggregate(max=Sum("amount"))["max"] or 0
    average_donation = donations.aggregate(avg=Avg("amount"))["avg"] or 0

    top_donors = (
        Donation.objects
        .values("user__username")
        .annotate(total=Sum("amount"))
        .order_by("-total")[:5]
    )

    context = {
        "donations": donations,
        "adoption_payments": adoption_payments,
        "total_general": total_general,
        "total_adoption": total_adoption,
        "total_income": total_income,
        "highest_donation": highest_donation,
        "average_donation": average_donation,
        "top_donors": top_donors,
    }

    return render(
        request,
        "adoption_system/shelteradmin/donation_finance.html",
        context
    )
@admin_required
def export_reports(request):
    return render(request, "adoption_system/shelteradmin/export_reports.html")


@admin_required
def admin_messages(request):
    return render(request, "adoption_system/shelteradmin/admin_messages.html")

@admin_required
def medical_attention_list(request):

    animals = Animal.objects.exclude(status='Adopted')

    return render(
        request,
        "adoption_system/shelteradmin/medical_attention_list.html",
        {"animals": animals}
    )


@admin_required
def mark_medical_attention(request, animal_id):

    animal = get_object_or_404(Animal, id=animal_id)

    animal.medical_attention_required = True
    animal.save()
    # 🔔 Notify Vet
    for vet in User.objects.filter(groups__name="Vet"):
        Notification.objects.create(
            user=vet,
            title="Animal Assigned for Medical Check",
            message=f"{animal.name} needs medical attention (assigned by Admin)."
        )
    return redirect("medical_attention_list")


@admin_required
def add_symptoms(request, animal_id):

    animal = get_object_or_404(Animal, id=animal_id)

    if request.method == "POST":
        symptoms = request.POST.get("reported_symptoms")

        TreatmentRecord.objects.create(
            animal=animal,
            reported_symptoms=symptoms
        )

        # treatment started / handled
        animal.medical_attention_required = False
        animal.save()

        return redirect('medical_attention_list')

    return render(
        request,
        "adoption_system/shelteradmin/add_symptoms.html",
        {"animal": animal}
    )




@admin_required
def admin_chat_list(request):

    rooms = ChatRoom.objects.all()

    room_data = []

    for room in rooms:
        unread_count = room.messages.filter(
            sender="user",
            is_read=False
        ).count()

        room_data.append({
            "room": room,
            "unread": unread_count
        })

    return render(request, "adoption_system/chat/admin_chat_list.html", {
        "rooms": room_data
    })


@admin_required
def admin_chat_room(request, room_id):

    room = get_object_or_404(ChatRoom, id=room_id)

    # ✅ Mark user messages as read
    room.messages.filter(
        sender="user",
        is_read=False
    ).update(is_read=True)

    # ✅ Send new message
    if request.method == "POST":
        msg = request.POST.get("message")
        if msg:
            Message.objects.create(
                room=room,
                sender="admin",
                message=msg
            )
            return redirect('admin_chat_room', room_id=room.id)

    # ✅ IMPORTANT: Hide messages deleted only for admin
    messages = room.messages.filter(
        deleted_for_admin=False
    ).order_by("timestamp")

    return render(
        request,
        "adoption_system/chat/admin_chat_room.html",
        {
            "room": room,
            "messages": messages
        }
    )

@admin_required
def fetch_admin_messages(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)

    messages = room.messages.all().order_by("timestamp")

    data = []
    for msg in messages:
       data.append({
    "sender": msg.sender,
    "message": msg.message,
    "timestamp": msg.timestamp.strftime("%H:%M"),
    "deleted_for_everyone": msg.deleted_for_everyone,
})

    return JsonResponse({"messages": data})


@admin_required
def delete_message_admin(request, message_id):
    message = get_object_or_404(Message, id=message_id)

    # Hide only for admin
    message.deleted_for_admin = True
    message.save()

    return redirect('admin_chat_room', room_id=message.room.id)

@admin_required
def delete_message_everyone_admin(request, message_id):
    message = get_object_or_404(Message, id=message_id)

    # Mark as deleted for everyone
    message.deleted_for_everyone = True
    message.message = ""
    message.save()

    return redirect('admin_chat_room', room_id=message.room.id)

@admin_required
def clear_chat_admin(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    room.messages.update(deleted_for_admin=True)
    return redirect('admin_chat_list')




@admin_required
def admin_donations(request):

    donations = AdoptionApplication.objects.filter(
        payment_status="Paid",
        donation_amount__gt=0
    ).order_by("-submitted_at")

    total_donations = donations.aggregate(
        total=Sum("donation_amount")
    )["total"] or 0

    return render(
        request,
        "adoption_system/admin/donations.html",
        {
            "donations": donations,
            "total_donations": total_donations
        }
    )

@admin_required
def admin_mark_paid(request, id):

    adoption = get_object_or_404(AdoptionApplication, id=id)

    adoption.payment_status = "Paid"
    adoption.transaction_id = "OFFLINE-" + str(adoption.id)
    adoption.save()

    return redirect("adoption_schedule")



@admin_required
def edit_pet_type(request, pet_id):

    pet = get_object_or_404(PetType, id=pet_id)

    if request.method == "POST":
        pet.name = request.POST.get("name")
        pet.save()

        messages.success(request, "Pet type updated successfully.")
        return redirect("pet_type_list")

    return render(request,
        "adoption_system/shelteradmin/edit_pet_type.html",
        {"pet": pet}
    )

@admin_required
def delete_pet_type(request, pet_id):

    pet = get_object_or_404(PetType, id=pet_id)

    if request.method == "POST":
        pet.delete()
        messages.success(request, "Pet type deleted successfully.")

    return redirect("pet_type_list")
@admin_required
def delete_breed(request, breed_id):

    breed = get_object_or_404(Breed, id=breed_id)

    if request.method == "POST":
        breed.delete()
        messages.success(request, "Breed deleted successfully.")

    return redirect("pet_type_list")


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

@admin_required
def confirm_offline_donation(request, donation_id):

    donation = get_object_or_404(Donation, id=donation_id)

    donation.payment_status = "completed"
    donation.save()
    create_user_notification(
    donation.user_profile,
    "Donation Received ❤️",
    "Thank you for supporting our shelter!"
)

    messages.success(request, "Offline donation confirmed successfully!")

    return redirect("donation_finance")


@admin_required
def medical_management(request):

    animals = Animal.objects.exclude(status='Adopted')

    return render(
        request,
        "adoption_system/shelteradmin/medical_management.html",
        {"animals": animals}
    )

@admin_required
def admin_notifications(request):

    notifications = Notification.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(
        request,
        "adoption_system/shelteradmin/notifications.html",
        {"notifications": notifications}
    )

@admin_required
def delete_admin_notification(request, id):

    Notification.objects.filter(
        id=id,
        user=request.user
    ).delete()

    return JsonResponse({"status": "deleted"})


@admin_required
def admin_mark_all_read(request):

    Notification.objects.filter(
        user=request.user,
        is_read=False
    ).update(is_read=True)

    return JsonResponse({"status": "updated"})


@admin_required
def admin_clear_all_notifications(request):

    Notification.objects.filter(
        user=request.user
    ).delete()

    return JsonResponse({"status": "deleted"})