
# ================= IMPORTS =================

from datetime import datetime, date, timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.utils import timezone

from ..models import (
    Animal,
    Vaccine,
    CheckupHistory,
    CheckupVaccine,
    TreatmentRecord
)

from ..decorators import vet_required
from adoption_system.ml_model.predictor import predict_disease

# def vet_login(request):

#     if request.method == "POST":
#         username = request.POST['username']
#         password = request.POST['password']

#         user = authenticate(
#             request,
#             username=username,
#             password=password
#         )

#         if user is not None:
#             login(request, user)
#             return redirect('vet_dashboard')   # vet dashboard
#         else:
#             return render(
#                 request,
#                 'adoption_system/vet/vet_login.html',
#                 {'error': 'Invalid username or password'}
#             )

#     return render(request, 'adoption_system/vet/vet_login.html')

@vet_required
def vet_dashboard(request):

    today = timezone.now().date()

    total_animals = Animal.objects.exclude(status='Adopted').count()

    treatment_count = Animal.objects.filter(
        health_status='Under Treatment'
    ).count()

    healthy_count = Animal.objects.filter(
        health_status='Healthy'
    ).count()

    quarantine_count = Animal.objects.filter(
        status='Quarantine'
    ).count()

    risk_count = Animal.objects.filter(
        general_condition='Critical'
    ).count()

    # ✅ Correct model used here
    vaccination_due_count = CheckupVaccine.objects.filter(
        next_due_date__lte=today
    ).count()

    context = {
        'total_animals': total_animals,
        'treatment_count': treatment_count,
        'healthy_count': healthy_count,
        'quarantine_count': quarantine_count,
        'risk_count': risk_count,
        'vaccination_due_count': vaccination_due_count,
    }

    return render(
        request,
        'adoption_system/vet/vet_dashboard.html',
        context
    )



@vet_required
def all_shelter_pets(request):

    animals = Animal.objects.exclude(status='Adopted')

    return render(request,
                  'adoption_system/vet/all_shelter_pets.html',
                  {'animals': animals})


from ..models import CheckupHistory

@vet_required
def medical_history(request):

    animals = Animal.objects.exclude(status='Adopted')

    return render(
        request,
        'adoption_system/vet/medical_history.html',
        {'animals': animals}
    )
@vet_required
def pet_medical_history(request, animal_id):

    animal = get_object_or_404(Animal, id=animal_id)

    history = CheckupHistory.objects.filter(
        animal=animal
    ).order_by('-checkup_date')

    return render(
        request,
        'adoption_system/vet/pet_medical_history.html',
        {
            'animal': animal,
            'history': history
        }
    )





from django.contrib import messages
@vet_required
def add_vaccine_name(request):
    if request.method == "POST":
        name = request.POST.get("vaccine_name")

        if name:
            Vaccine.objects.create(name=name)
            messages.success(request, "Vaccine added successfully!")

        return redirect("add_vaccine_name")

    return render(request, "vet/add_vaccine_name.html")


@vet_required
def vet_profile(request):

    if not hasattr(request.user, 'vetprofile'):
        return redirect('vet_dashboard')

    vet = request.user.vetprofile

    return render(request,
              'adoption_system/vet/vet_profile.html',
              {'vet': vet})

from datetime import date, timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from ..models import CheckupVaccine


@vet_required
def vaccination_due(request):

    today = date.today()
    next_week = today + timedelta(days=7)

    vaccinations = CheckupVaccine.objects.select_related(
        'checkup__animal',
        'vaccine'
    ).all()

    for v in vaccinations:
        v.is_overdue = v.next_due_date and v.next_due_date < today
        v.due_soon = (
            v.next_due_date and
            today <= v.next_due_date <= next_week
        )

    # show only overdue or due soon
    vaccinations = [
        v for v in vaccinations
        if v.is_overdue or v.due_soon
    ]

    return render(
        request,
        'adoption_system/vet/vaccination_due.html',
        {'vaccinations': vaccinations}
    )
from datetime import date, timedelta

@vet_required
def mark_vaccinated(request, vaccine_id):

    vaccine_record = get_object_or_404(
        CheckupVaccine,
        id=vaccine_id
    )

    today = date.today()

    # update dose date
    vaccine_record.dose_date = today

    # calculate next due date again
    vaccine_record.next_due_date = (
        today + timedelta(
            days=vaccine_record.next_dose_after_days
        )
    )

    vaccine_record.save()

    return redirect('vaccination_due')


@vet_required
def quarantine_animals(request):

    animals = Animal.objects.filter(status='Quarantine')

    return render(request,
                  'adoption_system/vet/quarantine_animals.html',
                  {'animals': animals})





@vet_required
def assigned_pets(request):

    pets = Animal.objects.filter(
        medical_attention_required=True
    ).exclude(status='Adopted')

    # attach latest treatment record
    for pet in pets:
        pet.current_treatment = TreatmentRecord.objects.filter(
            animal=pet
        ).order_by('-created_at').first()

    return render(
        request,
        'adoption_system/vet/assigned_pets.html',
        {'pets': pets}
    )




@vet_required
def add_checkup(request, animal_id):

    animal = get_object_or_404(Animal, id=animal_id)
    vaccines = Vaccine.objects.all()

    # latest treatment record created by staff
    treatment = TreatmentRecord.objects.filter(
        animal=animal
    ).order_by('-created_at').first()

    if request.method == "POST":

        animal.weight = request.POST.get('weight')
        animal.height = request.POST.get('height')
        animal.temperature = request.POST.get('temperature')
        animal.general_condition = request.POST.get('general_condition')
        animal.health_status = request.POST.get('health_status')
        animal.medical_notes = request.POST.get('medical_notes')
        animal.save()

        # create checkup
        checkup = CheckupHistory.objects.create(
            animal=animal,
            weight=animal.weight,
            temperature=animal.temperature,
            health_status=animal.health_status,
            medical_notes=animal.medical_notes
        )

        # 🔴 LINK staff treatment record to checkup
        if treatment and treatment.checkup is None:
            treatment.checkup = checkup
            treatment.save()

        # save vaccines
        vaccine_ids = request.POST.getlist('vaccine[]')
        dose_dates = request.POST.getlist('date_given[]')
        dose_days = request.POST.getlist('next_dose_after_days[]')

        for v_id, d_date, days in zip(vaccine_ids, dose_dates, dose_days):

            if v_id and d_date and days:

                dose_date_obj = datetime.strptime(
                    d_date, "%Y-%m-%d"
                ).date()

                next_due = dose_date_obj + timedelta(days=int(days))

                CheckupVaccine.objects.create(
                    checkup=checkup,
                    vaccine_id=int(v_id),
                    dose_date=dose_date_obj,
                    next_dose_after_days=int(days),
                    next_due_date=next_due
                )

        animal.medical_attention_required = False

        # update shelter status
        if animal.status == "Quarantine":

            if animal.health_status == "Healthy":
                animal.status = "Available"

            elif animal.health_status in [
                "Under Treatment",
                "Recovering",
                "Critical"
            ]:
                animal.status = "Quarantine"

        animal.save()

        if animal.health_status in [
            "Under Treatment",
            "Recovering",
            "Critical"
        ]:
            return redirect('add_medical_record', checkup.id)

        return redirect('assigned_pets')

    return render(
        request,
        'adoption_system/vet/add_checkup.html',
        {
            'animal': animal,
            'vaccines': vaccines,
            'treatment': treatment
        }
    )
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from ..models import Animal


from datetime import date

@vet_required
def treatment_cases(request):

    pets = Animal.objects.filter(
        health_status__in=[
            "Under Treatment",
            "Recovering",
            "Critical"
        ]
    ).exclude(status='Adopted')

    today = date.today()

    for pet in pets:
        treatment = TreatmentRecord.objects.filter(
            animal=pet,
            treatment_status='Ongoing'
        ).order_by('-created_at').first()

        pet.current_treatment = treatment

        if treatment and treatment.follow_up_date:
            pet.follow_up_overdue = treatment.follow_up_date < today
        else:
            pet.follow_up_overdue = False

    return render(
        request,
        'adoption_system/vet/treatment_cases.html',
        {'pets': pets}
    )



@vet_required
def update_treatment_record(request, animal_id):

    animal = get_object_or_404(Animal, id=animal_id)

    treatment = TreatmentRecord.objects.filter(
        animal=animal,
        treatment_status='Ongoing'
    ).order_by('-created_at').first()

    if not treatment:
        return redirect('treatment_cases')

    top_predictions = []

    if request.method == "POST":

        observed_symptoms = request.POST.get('observed_symptoms')
        reported_symptoms = treatment.reported_symptoms or ""

        # ---------------- PREDICT ----------------
        if request.POST.get("action") == "predict":

            if observed_symptoms:
                all_symptoms = reported_symptoms + " " + observed_symptoms
                top_predictions = predict_disease(all_symptoms)

            return render(
                request,
            'adoption_system/vet/update_treatment_record.html',
                {
                    'animal': animal,
                    'treatment': treatment,
                    'top_predictions': top_predictions
                }
            )

        # ---------------- SAVE UPDATE ----------------
        if request.POST.get("action") == "save":

            treatment.observed_symptoms = observed_symptoms
            treatment.final_diagnosis = request.POST.get('final_diagnosis')
            treatment.treatment_plan = request.POST.get('treatment_plan')
            treatment.medication = request.POST.get('medication')
            treatment.treatment_status = request.POST.get('treatment_status')

            follow_up = request.POST.get('follow_up_date')
            treatment.follow_up_date = follow_up if follow_up else None
            treatment.is_quarantined = bool(request.POST.get("is_quarantined"))
            treatment.quarantine_reason = request.POST.get("quarantine_reason", "")

    
            treatment.save()

            animal.health_status = request.POST.get('health_status')

            if treatment.treatment_status == "Completed":
                animal.medical_attention_required = False

            animal.save()

            return redirect('treatment_cases')

    return render(
        request,
        'adoption_system/vet/update_treatment_record.html',
        {
            'animal': animal,
            'treatment': treatment,
            'top_predictions': top_predictions
        }
    )

@vet_required
def quarantine_animals(request):

    animals = Animal.objects.filter(
        status="Quarantine"
    )

    return render(
        request,
        'adoption_system/vet/quarantine_animals.html',
        {'animals': animals}
    )
@vet_required
def add_medical_record(request, checkup_id):

    checkup = get_object_or_404(CheckupHistory, id=checkup_id)
    animal = checkup.animal

    treatment, created = TreatmentRecord.objects.get_or_create(
        animal=animal,
        checkup=checkup,
        defaults={"treatment_status": "Ongoing"}
    )

    top_predictions = []

    if request.method == "POST":

        observed_symptoms = request.POST.get("observed_symptoms")
        reported_symptoms = treatment.reported_symptoms or ""

        # ================= PREDICT DISEASE =================
        if request.POST.get("action") == "predict":

            if observed_symptoms:
                all_symptoms = reported_symptoms + " " + observed_symptoms
                top_predictions = predict_disease(all_symptoms)

                # 🔴 SAVE top predicted disease
                if top_predictions:
                    treatment.predicted_disease = top_predictions[0][0]
                    treatment.save()

            return render(
                request,
                "adoption_system/vet/add_medical_record.html",
                {
                    "animal": animal,
                    "checkup": checkup,
                    "treatment": treatment,
                    "top_predictions": top_predictions
                }
            )

        # ================= SAVE MEDICAL RECORD =================
        if request.POST.get("action") == "save":

            treatment.observed_symptoms = observed_symptoms
            treatment.final_diagnosis = request.POST.get("final_diagnosis")
            treatment.treatment_plan = request.POST.get("treatment_plan")
            treatment.medication = request.POST.get("medication")

            follow_up = request.POST.get("follow_up_date")
            treatment.follow_up_date = follow_up if follow_up else None

            treatment.save()

            animal.health_status = request.POST.get("health_status")
            animal.save()

            return redirect("vet_dashboard")

    return render(
        request,
        "adoption_system/vet/add_medical_record.html",
        {
            "animal": animal,
            "checkup": checkup,
            "treatment": treatment,
            "top_predictions": top_predictions
        }
    )
    
@vet_required
def pet_medical_history(request, animal_id):

    animal = get_object_or_404(Animal, id=animal_id)

    history = CheckupHistory.objects.filter(
        animal=animal
    ).order_by("-checkup_date")

    # attach treatment record
    for record in history:
        record.treatment = TreatmentRecord.objects.filter(
            checkup=record
        ).first()

    return render(
        request,
        "adoption_system/vet/pet_medical_history.html",
        {
            "animal": animal,
            "history": history
        }
    )

from django.http import JsonResponse
from ..models import Notification

@vet_required
def vet_notifications(request):

    notifications = Notification.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(
        request,
        "adoption_system/vet/notifications.html",
        {"notifications": notifications}
    )
@vet_required
def delete_vet_notification(request, id):

    Notification.objects.filter(
        id=id,
        user=request.user
    ).delete()

    return JsonResponse({"status": "deleted"})


@vet_required
def vet_mark_all_read(request):

    Notification.objects.filter(
        user=request.user,
        is_read=False
    ).update(is_read=True)

    return JsonResponse({"status": "updated"})


@vet_required
def vet_clear_all_notifications(request):

    Notification.objects.filter(
        user=request.user
    ).delete()

    return JsonResponse({"status": "deleted"})