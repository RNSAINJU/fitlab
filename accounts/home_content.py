from .models import (
    HomePageSettings,
    HomePowerlifter,
    HomeScheduleSlot,
    HomeTrainer,
)


def get_home_page_context():
    settings = HomePageSettings.load()
    return {
        "hp": settings,
        "powerlifters": HomePowerlifter.objects.filter(is_active=True),
        "trainers": HomeTrainer.objects.filter(is_active=True),
        "schedule_slots": HomeScheduleSlot.objects.filter(is_active=True),
    }
