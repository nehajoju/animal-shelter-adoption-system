from django.urls import path

from .views import user_views, admin_views, vet_views, staff_views
urlpatterns = [

# ================= USER SIDE =================
path('panel/login/', admin_views.panel_login, name='panel_login'),
path('', user_views.home, name='home'),
path('register/', user_views.register, name='register'),
path('login/', user_views.login_view, name='login'),
path('logout/', user_views.logout_view, name='logout'),
path("employees/", admin_views.employee_management, name="employee_management"),
path("employees/add/", admin_views.add_employee, name="add_employee"),
path("employees/edit/<int:user_id>/", admin_views.edit_employee, name="edit_employee"),
path("employees/delete/<int:user_id>/", admin_views.delete_employee, name="delete_employee"),
path("employees/toggle/<int:user_id>/", admin_views.toggle_employee_status, name="toggle_employee_status"),
# ================= NOTIFICATIONS =================

path('userhome/', user_views.userhome, name='userhome'),
path('animals/', user_views.animals, name='animals'),
path('adoption/<int:animal_id>/', user_views.adoption_request, name='adoption'),

path('my_adoptions/', user_views.my_adoptions, name='my_adoptions'),
path('request_adoption_date/<int:id>/', user_views.request_adoption_date, name='request_adoption_date'),
path('adoption-payment/<int:id>/', 
     user_views.adoption_payment, 
     name='adoption_payment'),

path('foster/', user_views.foster, name='foster'),
path('visits/<int:id>/', user_views.visit_request, name='visits'),
path('my_visits/', user_views.my_visits, name='my_visits'),

path('donations/', user_views.donations, name='donations'),
path('profile/', user_views.profile, name='profile'),
path('chat_admin/', user_views.chat_admin, name='chat_admin'),

path('rehome_pet/', user_views.rehome_pet, name='rehome_pet'),
path('my_rehome_requests/', user_views.my_rehome_requests, name='my_rehome_requests'),
path('handover_shelter/<int:pet_id>/', user_views.handover_shelter, name='handover_shelter'),
path('lost_pet/', user_views.lost_pet, name='lost_pet'),
path('my_lost_pets/', user_views.my_lost_pets, name='my_lost_pets'),
path('mark-pet-found/<int:pet_id>/', user_views.mark_pet_found, name='mark_pet_found'),
path('browse_found_pets/', user_views.browse_found_pets, name='browse_found_pets'),
path('found_pet/', user_views.found_pet, name='found_pet'),
path('my_found_pets/', user_views.my_found_pets, name='my_found_pets'),
path('mark-pet-returned/<int:pet_id>/', user_views.mark_pet_returned, name='mark_pet_returned'),
path('report_match/<int:pet_id>/', user_views.report_match, name='report_match'),
path('contact_finder/<int:pet_id>/', user_views.contact_finder, name='contact_finder'),
# ================= PAYMENT FLOW =================
path('animal/<int:id>/',user_views.animal_detail, name='animal_detail'),
path('recent-activity/', user_views.recent_activity, name='recent_activity'),
path(
    'export-activity/',
    user_views.export_activity_pdf,
    name='export_activity_pdf'
),
path(
        'delete-activity/<str:activity_type>/<int:activity_id>/',
        user_views.delete_activity,
        name='delete_activity'
    ),

    path(
        'clear-all-activity/',
        user_views.clear_all_activity,
        name='clear_all_activity'
    ),
path(
    'adoption/payment/<int:id>/',
    user_views.adoption_payment,
    name='adoption_payment'
),

path(
    'adoption/review/',
    user_views.review_payment,
    name='review_payment'
),

path(
    'adoption/enter-pin/',
    user_views.enter_pin,
    name='enter_pin'
),

path(
    'adoption/processing/',
    user_views.adoption_processing,
    name='adoption_processing'
),

path(
    'donation/processing/',
    user_views.donation_processing,
    name='donation_processing'
),

path("adoption/success/", user_views.adoption_payment_success, name="adoption_payment_success"),
path("donation/success/", user_views.donation_payment_success, name="donation_payment_success"),
path(
    'adoption/receipt/<int:id>/',
    user_views.download_receipt,
    name='download_receipt'
),
path('donate/', user_views.donate, name='donate'),

path("ai-chat/", user_views.ai_chatbot, name="ai_chatbot"),
path('panel/logout/', admin_views.panel_logout, name='panel_logout'),
# ================= ADMIN LOST & FOUND =================

path('shelteradmin/found_pets/', admin_views.found_pets, name='found_pets'),
path('admin-mark-returned/<int:pet_id>/', admin_views.admin_mark_pet_returned, name='admin_mark_pet_returned'),
# ================= ADMIN =================

# path('admin_login/', admin_views.admin_login, name='admin_login'),
# path('admin_logout/', admin_views.admin_logout, name='admin_logout'),
path('shelteradmin/admin_dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),

# Dashboard Cards
path('shelteradmin/animals_in_care/', admin_views.animals_in_care, name='animals_in_care'),
path('shelteradmin/pending_adoptions/', admin_views.pending_adoptions, name='pending_adoptions'),
path('shelteradmin/upcoming_visits/', admin_views.upcoming_visits, name='upcoming_visits'),
path('shelteradmin/donations/', admin_views.donations_list, name='donations_list'),

# Lost & Found
path('shelteradmin/lost_pets/', admin_views.lost_pets, name='lost_pets'),
path('shelteradmin/found_pets/', admin_views.found_pets, name='found_pets'),
path('admin_mark_returned/<int:pet_id>/', admin_views.admin_mark_pet_returned, name='admin_mark_pet_returned'),

# Management
path('shelteradmin/users/', admin_views.user_management, name='user_management'),
path('shelteradmin/animal_management/', admin_views.animal_management, name='animal_management'),
path('shelteradmin/add_animal/', admin_views.add_animal, name='add_animal'),
path('shelteradmin/animal/edit/<int:animal_id>/', admin_views.edit_animal, name='edit_animal'),
path('shelteradmin/animal/delete/<int:animal_id>/', admin_views.delete_animal, name='delete_animal'),

path('shelteradmin/adoption_review/', admin_views.adoption_review, name='adoption_review'),
path('shelteradmin/approve_application/<int:app_id>/', admin_views.approve_application, name='approve_application'),
path('shelteradmin/reject_application/<int:app_id>/', admin_views.reject_application, name='reject_application'),

path('shelteradmin/rehome_requests/', admin_views.rehome_list, name='rehome_list'),
path('shelteradmin/rehome_review/<int:id>/', admin_views.rehome_review, name='rehome_review'),

path('shelteradmin/update_visit_status/<int:id>/', admin_views.update_visit_status, name='update_visit_status'),
path('shelteradmin/adoption_schedule/', admin_views.adoption_schedule, name='adoption_schedule'),
path('shelteradmin/approve_adoption_schedule/<int:id>/', admin_views.approve_adoption_schedule, name='approve_adoption_schedule'),
path('shelteradmin/reject_adoption_schedule/<int:id>/', admin_views.reject_adoption_schedule, name='reject_adoption_schedule'),
path('shelteradmin/complete_adoption/<int:id>/', admin_views.complete_adoption, name='complete_adoption'),

path('shelteradmin/medical_management/', admin_views.medical_management, name='medical_management'),
path('shelteradmin/appointment_management/', admin_views.appointment_management, name='appointment_management'),
path('shelteradmin/donation_finance/', admin_views.donation_finance, name='donation_finance'),
path('shelteradmin/export_reports/', admin_views.export_reports, name='export_reports'),
path('shelteradmin/messages/', admin_views.admin_messages, name='admin_messages'),

path('shelteradmin/add_pet_type/', admin_views.add_pet_type, name='add_pet_type'),
path('shelteradmin/pet_type_list/', admin_views.pet_type_list, name='pet_type_list'),
path('shelteradmin/add_breed/', admin_views.add_breed, name='add_breed'),

path('shelteradmin/medical_attention/', admin_views.medical_attention_list, name='medical_attention_list'),
path('shelteradmin/medical_attention/<int:animal_id>/', admin_views.mark_medical_attention, name='mark_medical_attention'),
path('shelteradmin/add_symptoms/<int:animal_id>/', admin_views.add_symptoms, name='add_symptoms'),
path(
    'shelteradmin/animal/delete/<int:animal_id>/',
    admin_views.delete_animal,
    name='delete_animal'
),
path(
'admin_confirm_reunited/<int:pet_id>/',
admin_views.admin_confirm_reunited,
name='admin_confirm_reunited'
),

path(
'admin_confirm_shelter/<int:pet_id>/',
admin_views.admin_confirm_shelter,
name='admin_confirm_shelter'
),
path(
    "edit_pet_type/<int:pet_id>/",
    admin_views.edit_pet_type,
    name="edit_pet_type"
),
path("delete_breed/<int:breed_id>/", admin_views.delete_breed, name="delete_breed"),

path(
    "pet-type/delete/<int:pet_id>/",
    admin_views.delete_pet_type,
    name="delete_pet_type"
),# User
path('start_chat/', user_views.start_chat, name='start_chat'),
path('chat/user_chat/<int:room_id>/', user_views.user_chat_room, name='user_chat_room'),
path('fetch_user_messages/<int:room_id>/', user_views.fetch_user_messages, name='fetch_user_messages'),
# User Delete
    path('delete_message_user/<int:message_id>/',
         user_views.delete_message_user,
         name='delete_message_user'),

    path('delete_message_everyone_user/<int:message_id>/',
         user_views.delete_message_everyone_user,
         name='delete_message_everyone_user'),

# Admin
path('chat/admin_chat_list/', admin_views.admin_chat_list, name='admin_chat_list'),
path('chat/admin_chat_room/<int:room_id>/', admin_views.admin_chat_room, name='admin_chat_room'),
path('fetch_admin_messages/<int:room_id>/', admin_views.fetch_admin_messages, name='fetch_admin_messages'),
# Admin Delete
    path('delete_message_admin/<int:message_id>/',
         admin_views.delete_message_admin,
         name='delete_message_admin'),

    path('delete_message_everyone_admin/<int:message_id>/',
         admin_views.delete_message_everyone_admin,
         name='delete_message_everyone_admin'),

path('clear_chat_admin/<int:room_id>/', admin_views.clear_chat_admin, name='clear_chat_admin'),
path('clear_chat_user/<int:room_id>/', user_views.clear_chat_user, name='clear_chat_user'),
path(
    "admin/donations/",
    admin_views.admin_donations,
    name="admin_donations"
),
path(
    "admin/adoption/mark-paid/<int:id>/",
    admin_views.admin_mark_paid,
    name="admin_mark_paid"
),
path('admin_mark_returned/<int:pet_id>/', admin_views.admin_mark_pet_returned, name='admin_mark_pet_returned'),
path(
    "confirm-donation/<int:donation_id>/",
    admin_views.confirm_offline_donation,
    name="confirm_offline_donation"
),
path("block_user/<int:user_id>/", admin_views.block_user, name="admin_block_user"),
path("delete_user/<int:user_id>/", admin_views.delete_user, name="admin_delete_user"),
# ================= VET =================

# path('vet/login/', vet_views.vet_login, name='vet_login'),
path('vet/dashboard/', vet_views.vet_dashboard, name='vet_dashboard'),

path('vet/assigned_pets/', vet_views.assigned_pets, name='assigned_pets'),
path('vet/add_checkup/<int:animal_id>/', vet_views.add_checkup, name='add_checkup'),

path('vet/profile/', vet_views.vet_profile, name='vet_profile'),
path('vet/all_pets/', vet_views.all_shelter_pets, name='all_shelter_pets'),
path('vet/medical_history/', vet_views.medical_history, name='medical_history'),

path('vet/vaccination_due/', vet_views.vaccination_due, name='vaccination_due'),
path('vet/quarantine/', vet_views.quarantine_animals, name='quarantine_animals'),

path('vet/add_vaccine/', vet_views.add_vaccine_name, name='add_vaccine_name'),

path('vet/add_medical_record/<int:checkup_id>/', vet_views.add_medical_record, name='add_medical_record'),

path('vet/treatment_cases/', vet_views.treatment_cases, name='treatment_cases'),

path('vet/update-treatment/<int:animal_id>/', vet_views.update_treatment_record, name='update_treatment_record'),

path('vet/medical-history/<int:animal_id>/', vet_views.pet_medical_history, name='pet_medical_history'),

path('vet/mark-vaccinated/<int:vaccine_id>/', vet_views.mark_vaccinated, name='mark_vaccinated'),
path('vet/quarantine/', vet_views.quarantine_animals, name='quarantine_animals'),




# ================= STAFF MODULE =================

path('staff/dashboard/', staff_views.staff_dashboard, name='staff_dashboard'),

# Animal Management
path('staff/animals/', staff_views.staff_animals, name='staff_animals'),
path('staff/add_animal/', staff_views.staff_add_animal, name='staff_add_animal'),
path('staff/edit_animal/<int:animal_id>/', staff_views.staff_edit_animal, name='staff_edit_animal'),

# Medical Attention
path(
    'staff/medical_attention/',
    staff_views.staff_medical_attention_list,
    name='staff_medical_attention_list'
),
path(
    'staff/mark_medical_attention/<int:animal_id>/',
    staff_views.staff_mark_medical_attention,
    name='staff_mark_medical_attention'
),

path(
    "staff/adoption_review/",
    staff_views.staff_adoption_review,
    name="staff_adoption_review"
),

path('staff/add_symptoms/<int:animal_id>/', staff_views.staff_add_symptoms, name='staff_add_symptoms'),
path('staff/adoption_schedule/', staff_views.staff_adoption_schedule, name='staff_adoption_schedule'),
# Lost & Found
path('staff/lost_pets/', staff_views.staff_lost_pets, name='staff_lost_pets'),
path('staff/found_pets/', staff_views.staff_found_pets, name='staff_found_pets'),
path(
    'staff/rehome-arrivals/',
    staff_views.staff_rehome_arrivals,
    name='staff_rehome_arrivals'
),

# Receive rehome pet
path(
    'staff/receive-rehome/<int:id>/',
    staff_views.receive_rehome_pet,
    name='receive_rehome_pet'
),
path(
    'staff/rehome-intake/<int:id>/',
    staff_views.rehome_intake_form,
    name='rehome_intake_form'
),

path(
    "notifications/",
    user_views.user_notifications,
    name="user_notifications"
),
path(
    "delete-notification/<int:id>/", 
    user_views.delete_notification, 
    name="delete_notification"
),
# ADMIN
path(
    "shelteradmin/notifications/",
    admin_views.admin_notifications,
    name="admin_notifications"
),

# STAFF
path(
    "staff/notifications/",
    staff_views.staff_notifications,
    name="staff_notifications"
),

# VET
path(
    "vet/notifications/",
    vet_views.vet_notifications,
    name="vet_notifications"
),

path("notifications/mark-read/", user_views.mark_all_notifications_read, name="mark_all_read"),
path("notifications/clear-all/", user_views.clear_all_notifications, name="clear_all_notifications"),
path(
    "shelteradmin/delete-notification/<int:id>/",
    admin_views.delete_admin_notification
),

path(
    "shelteradmin/notifications/mark-read/",
    admin_views.admin_mark_all_read
),

path(
    "shelteradmin/notifications/clear-all/",
    admin_views.admin_clear_all_notifications
),




]





