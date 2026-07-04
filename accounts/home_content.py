from .models import (
    HomeClientSpotlight,
    HomeGalleryImage,
    HomePageSettings,
    HomePowerlifter,
    HomePricingPlan,
    HomeScheduleSlot,
    HomeTestimonial,
    HomeTrainer,
    HomeTrainingService,
)


def get_home_page_context():
    settings = HomePageSettings.load()
    return {
        "hp": settings,
        "powerlifters": HomePowerlifter.objects.filter(is_active=True),
        "trainers": HomeTrainer.objects.filter(is_active=True),
        "training_services": HomeTrainingService.objects.filter(is_active=True),
        "schedule_slots": HomeScheduleSlot.objects.filter(is_active=True),
        "pricing_plans": HomePricingPlan.objects.filter(is_active=True).prefetch_related("tiers"),
        "gallery_images": HomeGalleryImage.objects.filter(is_active=True),
        "testimonials": HomeTestimonial.objects.filter(is_active=True),
        "clients_row_1": HomeClientSpotlight.objects.filter(
            is_active=True, row=HomeClientSpotlight.Row.ROW_1
        ),
        "clients_row_2": HomeClientSpotlight.objects.filter(
            is_active=True, row=HomeClientSpotlight.Row.ROW_2
        ),
    }
