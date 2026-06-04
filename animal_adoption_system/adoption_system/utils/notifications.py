from adoption_system.models import Notification

def create_user_notification(user_profile, title, message, link=None):

    Notification.objects.create(
        user_profile=user_profile,
        title=title,
        message=message,
        link=link
    )