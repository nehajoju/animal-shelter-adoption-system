from django.shortcuts import render, redirect, get_object_or_404
from ..models import *
from ..forms import *
from ..decorators import staff_required


# ================= STAFF DASHBOARD =================
@staff_required
def staff_dashboard(request):

    total_animals = Animal.objects.exclude(status='Adopted').count()

    medical_count = Animal.objects.filter(
        medical_attention_required=True
    ).count()

    lost_count = LostPet.objects.filter(status="Missing").count()

    return render(
        request,
        'adoption_system/shelterstaff/staff_dashboard.html',
        {
            'total_animals': total_animals,
            'medical_count': medical_count,
            'lost_count': lost_count,
        }
    )
# ================= ANIMAL MANAGEMENT =================

from django.db.models import Q
@staff_required
def staff_adoption_review(request):

    status_filter = request.GET.get('status')
    search_query = request.GET.get('search')

    applications = AdoptionApplication.objects.all()

    # STATUS FILTER
    if status_filter == "Approved":
        applications = applications.filter(is_approved=True)

    elif status_filter == "Rejected":
        applications = applications.filter(is_rejected=True)

    elif status_filter == "Pending":
        applications = applications.filter(
            is_approved=False,
            is_rejected=False
        )

    # SEARCH
    if search_query:
        applications = applications.filter(
            Q(user__username__icontains=search_query) |
            Q(animal__name__icontains=search_query)
        )

    applications = applications.order_by('-submitted_at')

    return render(
        request,
        "adoption_system/shelterstaff/staff_adoption_review.html",
        {
            "applications": applications,
            "status_filter": status_filter,
            "search_query": search_query
        }
    )

@staff_required
def staff_animals(request):

    animals = Animal.objects.filter(is_active=True)

    return render(
        request,
        'adoption_system/shelterstaff/staff_animals.html',
        {'animals': animals}
    )


@staff_required
def staff_add_animal(request):

    if request.method == 'POST':
        form = AnimalForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('staff_animals')
    else:
        form = AnimalForm()

    return render(
        request,
        'adoption_system/shelteradmin/add_animal.html',  # Reuse admin template
        {'form': form}
    )


@staff_required
def staff_edit_animal(request, animal_id):

    animal = get_object_or_404(Animal, id=animal_id)

    if request.method == 'POST':
        form = AnimalForm(request.POST, request.FILES, instance=animal)
        if form.is_valid():
            form.save()
            return redirect('staff_animals')
    else:
        form = AnimalForm(instance=animal)

    return render(
        request,
        'adoption_system/shelteradmin/add_animal.html',
        {
            'form': form,
            'edit_mode': True
        }
    )


# ================= MEDICAL ATTENTION =================

@staff_required
def staff_medical_attention_list(request):

    animals = Animal.objects.exclude(status='Adopted')

    return render(
        request,
        "adoption_system/shelterstaff/staff_medical_attention_list.html",
        {"animals": animals}
    )


from django.shortcuts import redirect, get_object_or_404
from ..models import Animal
from ..decorators import staff_required

@staff_required
def staff_medical_attention_list(request):

    animals = Animal.objects.filter(
        medical_attention_required=True
    )

    for animal in animals:

        latest_record = (
            TreatmentRecord.objects
            .filter(animal=animal)
            .order_by("-id")
            .first()
        )

        if latest_record:
            animal.symptoms = latest_record.reported_symptoms
            animal.priority = getattr(latest_record, "priority", "Mild")
        else:
            animal.symptoms = "No symptoms reported"
            animal.priority = "Mild"

    context = {
        "animals": animals
    }

    return render(
        request,
        "adoption_system/shelterstaff/staff_medical_attention_list.html",
        context
    )

@staff_required
def staff_mark_medical_attention(request, animal_id):

    animal = get_object_or_404(Animal, id=animal_id)

    animal.medical_attention_required = True
    animal.health_status = "Needs Medical Attention"
    animal.save()
    for vet in User.objects.filter(groups__name="Vet"):
        Notification.objects.create(
            user=vet,
            title="Animal Assigned for Medical Check",
            message=f"{animal.name} needs medical attention (assigned by Staff)."
        )


    return redirect("staff_medical_attention_list")


@staff_required
def staff_add_symptoms(request, animal_id):

    animal = get_object_or_404(Animal, id=animal_id)

    if request.method == "POST":

        # symptoms from checkboxes
        symptoms_list = request.POST.getlist("symptoms")
        symptoms_text = ", ".join(symptoms_list)

        # additional notes from textarea
        notes = request.POST.get("reported_symptoms", "").strip()

        # combine symptoms and notes
        combined_symptoms = symptoms_text

        if notes:
            if combined_symptoms:
                combined_symptoms += f" | Notes: {notes}"
            else:
                combined_symptoms = f"Notes: {notes}"

        # avoid saving empty record
        if not combined_symptoms:
            combined_symptoms = "Symptoms reported but not specified"

        # save treatment record
        TreatmentRecord.objects.create(
            animal=animal,
            reported_symptoms=combined_symptoms,
            treatment_status="Ongoing"
        )

        # keep the animal in vet queue
        animal.medical_attention_required = True
        animal.save()

        return redirect("staff_medical_attention_list")

    return render(
        request,
        "adoption_system/shelterstaff/staff_add_symptoms.html",
        {"animal": animal}
    )

@staff_required
def staff_lost_pets(request):

    lost_pets = LostPet.objects.all().order_by('-reported_date')

    return render(
        request,
        "adoption_system/shelterstaff/staff_lost_pets.html",
        {'lost_pets': lost_pets}
    )


# ================= FOUND PETS =================

@staff_required
def staff_found_pets(request):

    status_filter = request.GET.get('status')

    found_pets = FoundPet.objects.all()

    if status_filter:
        found_pets = found_pets.filter(status=status_filter)

    found_pets = found_pets.order_by('-reported_date')

    # Only missing lost pets for matching
    lost_pets = LostPet.objects.filter(status="Missing")

    matches = {}
    strong_matches = {}

    for found in found_pets:

        matched_list = []
        strong_list = []

        for lost in lost_pets:

            # LEVEL 1 – Same pet type
            if found.pet_type_id != lost.pet_type_id:
                continue

            if found.found_location and lost.last_seen_location:

                found_loc = found.found_location.lower().strip()
                lost_loc = lost.last_seen_location.lower().strip()

                found_words = found_loc.split()
                lost_words = lost_loc.split()

                # Strong Match
                if found_loc in lost_loc or lost_loc in found_loc:
                    strong_list.append(lost)
                    matched_list.append(lost)

                # Medium Match
                elif (
                    found_words and lost_words and
                    found_words[0] == lost_words[0]
                ):
                    matched_list.append(lost)

                # Weak Match
                elif any(word in lost_words for word in found_words):
                    matched_list.append(lost)

        matches[found.id] = matched_list
        strong_matches[found.id] = strong_list

    return render(
        request,
        "adoption_system/shelteradmin/found_pets.html",  # Reuse admin template
        {
            'found_pets': found_pets,
            'matches': matches,
            'strong_matches': strong_matches,
            'status_filter': status_filter,
            'is_staff_view': True
        }
    )


@staff_required
def staff_adoption_schedule(request):
    return render(request,'adoption_system/shelterstaff/staff_adoption_schedule.html')

@staff_required
def staff_rehome_arrivals(request):

    pets = RehomePet.objects.filter(
        status="Approved"
    ).order_by("-created_at")

    return render(
        request,
        "adoption_system/shelterstaff/rehome_arrivals.html",
        {"pets": pets}
    )
@staff_required
def receive_rehome_pet(request, id):

    pet = get_object_or_404(RehomePet, id=id)

    return redirect("rehome_intake_form", id=pet.id)

@staff_required
def rehome_intake_form(request, id):

    pet = get_object_or_404(RehomePet, id=id)

    pet_types = PetType.objects.all()
    breeds = Breed.objects.all()

    # prevent duplicate intake
    if pet.status == "Transferred to Shelter":
        return redirect("staff_rehome_arrivals")

    if request.method == "POST":

        pet_type_id = request.POST.get("pet_type")
        breed_id = request.POST.get("breed")

        pet_type = get_object_or_404(PetType, id=pet_type_id)
        breed = get_object_or_404(Breed, id=breed_id)

        # ⭐ NEW: image handling
        uploaded_image = request.FILES.get("image")

        if uploaded_image:
            image = uploaded_image
        else:
            image = pet.pet_image

        animal = Animal.objects.create(
            name=request.POST.get("name"),
            pet_type=pet_type,
            breed=breed,
            age=request.POST.get("age"),
            gender=request.POST.get("gender"),
            color=request.POST.get("color"),
            temperament=request.POST.get("temperament"),
            good_with_pets=request.POST.get("good_with_pets") == "True",
            good_with_kids=request.POST.get("good_with_kids") == "True",
            image=image,
            status="Quarantine",
            intake_type="Rehome",
            medical_attention_required=True,
            is_active=False
        )

        # create initial treatment record
        TreatmentRecord.objects.create(
            animal=animal,
            reported_symptoms="Initial health check required after intake.",
            treatment_status="pending"
        )

        # notify all vets
        for vet in User.objects.filter(groups__name="Vet"):
            Notification.objects.create(
                user=vet,
                title="New Animal Needs Checkup",
                message=f"{animal.name} has arrived at the shelter and requires an initial medical check."
            )

        # mark rehome request transferred
        pet.status = "Transferred to Shelter"
        pet.save()

        return redirect("staff_rehome_arrivals")

    return render(
        request,
        "adoption_system/shelterstaff/rehome_intake.html",
        {
            "pet": pet,
            "pet_types": pet_types,
            "breeds": breeds
        }
    )
    
from django.http import JsonResponse

@staff_required
def staff_notifications(request):

    notifications = Notification.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(
        request,
        "adoption_system/shelterstaff/notifications.html",
        {"notifications": notifications}
    )   

@staff_required
def delete_staff_notification(request, id):

    Notification.objects.filter(
        id=id,
        user=request.user
    ).delete()

    return JsonResponse({"status": "deleted"})


@staff_required
def staff_mark_all_read(request):

    Notification.objects.filter(
        user=request.user,
        is_read=False
    ).update(is_read=True)

    return JsonResponse({"status": "updated"})


@staff_required
def staff_clear_all_notifications(request):

    Notification.objects.filter(
        user=request.user
    ).delete()

    return JsonResponse({"status": "deleted"})