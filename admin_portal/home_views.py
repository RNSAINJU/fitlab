from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import (
    HomeClientSpotlight,
    HomeGalleryImage,
    HomePageSettings,
    HomePowerlifter,
    HomePricingPlan,
    HomePricingTier,
    HomeScheduleSlot,
    HomeTestimonial,
    HomeTrainer,
    HomeTrainingService,
)

from .decorators import staff_required
from .home_forms import (
    HomeClientSpotlightForm,
    HomeFooterForm,
    HomeGalleryImageForm,
    HomeHeroForm,
    HomePowerlifterForm,
    HomePowerliftersSectionForm,
    HomePricingImageForm,
    HomePricingPlanForm,
    HomePricingTierForm,
    HomeScheduleSectionForm,
    HomeScheduleSlotForm,
    HomeSectionsForm,
    HomeTestimonialForm,
    HomeTrainerForm,
    HomeTrainingForm,
    HomeTrainingServiceForm,
    HomeWelcomeForm,
)

ITEM_FORMS = {
    "powerlifter": (HomePowerlifter, HomePowerlifterForm),
    "trainer": (HomeTrainer, HomeTrainerForm),
    "training_service": (HomeTrainingService, HomeTrainingServiceForm),
    "schedule_slot": (HomeScheduleSlot, HomeScheduleSlotForm),
    "pricing_plan": (HomePricingPlan, HomePricingPlanForm),
    "pricing_tier": (HomePricingTier, HomePricingTierForm),
    "gallery_image": (HomeGalleryImage, HomeGalleryImageForm),
    "testimonial": (HomeTestimonial, HomeTestimonialForm),
    "client": (HomeClientSpotlight, HomeClientSpotlightForm),
}


def _save_singleton_form(request, form, success_message, redirect_name):
    if form.is_valid():
        form.save()
        messages.success(request, success_message)
    else:
        messages.error(request, form.errors.as_text())
    return redirect(redirect_name)


def _handle_item_save(request, item_type, redirect_name):
    model, form_class = ITEM_FORMS[item_type]
    item_id = request.POST.get("item_id")
    instance = get_object_or_404(model, pk=item_id) if item_id else None
    form = form_class(request.POST, request.FILES, instance=instance)
    if form.is_valid():
        form.save()
        verb = "updated" if item_id else "added"
        messages.success(request, f"Item {verb} successfully.")
    else:
        messages.error(request, form.errors.as_text())
    return redirect(redirect_name)


def _handle_item_delete(request, item_type, redirect_name):
    model, _ = ITEM_FORMS[item_type]
    item = get_object_or_404(model, pk=request.POST.get("item_id"))
    item.delete()
    messages.success(request, "Item removed.")
    return redirect(redirect_name)


@staff_required
def home_page_settings(request):
    settings = HomePageSettings.load()
    redirect_name = "admin_portal:home_page_settings"

    if request.method == "POST":
        action = request.POST.get("action")

        singleton_handlers = {
            "hero": (
                HomeHeroForm,
                request.POST,
                request.FILES,
                settings,
                "Hero section updated.",
            ),
            "powerlifters_section": (
                HomePowerliftersSectionForm,
                request.POST,
                None,
                settings,
                "Powerlifters section updated.",
            ),
            "welcome": (
                HomeWelcomeForm,
                request.POST,
                None,
                settings,
                "Welcome section updated.",
            ),
            "training": (
                HomeTrainingForm,
                request.POST,
                None,
                settings,
                "Training section updated.",
            ),
            "schedule_section": (
                HomeScheduleSectionForm,
                request.POST,
                request.FILES,
                settings,
                "Schedule photo updated.",
            ),
            "pricing_image": (
                HomePricingImageForm,
                request.POST,
                request.FILES,
                settings,
                "Pricing image updated.",
            ),
            "sections": (
                HomeSectionsForm,
                request.POST,
                None,
                settings,
                "Section headings updated.",
            ),
            "footer": (
                HomeFooterForm,
                request.POST,
                None,
                settings,
                "Footer and contact updated.",
            ),
        }

        if action in singleton_handlers:
            form_class, data, files, instance, msg = singleton_handlers[action]
            form = form_class(data, files, instance=instance)
            return _save_singleton_form(request, form, msg, redirect_name)

        if action == "save_item":
            item_type = request.POST.get("item_type")
            if item_type in ITEM_FORMS:
                return _handle_item_save(request, item_type, redirect_name)
            messages.error(request, "Unknown item type.")
            return redirect(redirect_name)

        if action == "delete_item":
            item_type = request.POST.get("item_type")
            if item_type in ITEM_FORMS:
                return _handle_item_delete(request, item_type, redirect_name)
            messages.error(request, "Unknown item type.")
            return redirect(redirect_name)

    pricing_plans = HomePricingPlan.objects.prefetch_related("tiers").order_by("sort_order", "pk")

    return render(
        request,
        "admin_portal/home_page_settings.html",
        {
            "hp": settings,
            "hero_form": HomeHeroForm(instance=settings),
            "powerlifters_section_form": HomePowerliftersSectionForm(instance=settings),
            "welcome_form": HomeWelcomeForm(instance=settings),
            "training_form": HomeTrainingForm(instance=settings),
            "schedule_section_form": HomeScheduleSectionForm(instance=settings),
            "pricing_image_form": HomePricingImageForm(instance=settings),
            "sections_form": HomeSectionsForm(instance=settings),
            "footer_form": HomeFooterForm(instance=settings),
            "powerlifter_form": HomePowerlifterForm(),
            "trainer_form": HomeTrainerForm(),
            "training_service_form": HomeTrainingServiceForm(),
            "schedule_slot_form": HomeScheduleSlotForm(),
            "pricing_plan_form": HomePricingPlanForm(),
            "pricing_tier_form": HomePricingTierForm(),
            "gallery_form": HomeGalleryImageForm(),
            "testimonial_form": HomeTestimonialForm(),
            "client_form": HomeClientSpotlightForm(),
            "powerlifters": HomePowerlifter.objects.order_by("sort_order", "pk"),
            "trainers": HomeTrainer.objects.order_by("sort_order", "pk"),
            "training_services": HomeTrainingService.objects.order_by("sort_order", "pk"),
            "schedule_slots": HomeScheduleSlot.objects.order_by("sort_order", "pk"),
            "pricing_plans": pricing_plans,
            "gallery_images": HomeGalleryImage.objects.order_by("sort_order", "pk"),
            "testimonials": HomeTestimonial.objects.order_by("sort_order", "pk"),
            "clients": HomeClientSpotlight.objects.order_by("row", "sort_order", "pk"),
            "item_forms": {
                "powerlifter": HomePowerlifterForm,
                "trainer": HomeTrainerForm,
                "training_service": HomeTrainingServiceForm,
                "schedule_slot": HomeScheduleSlotForm,
                "pricing_plan": HomePricingPlanForm,
                "pricing_tier": HomePricingTierForm,
                "gallery_image": HomeGalleryImageForm,
                "testimonial": HomeTestimonialForm,
                "client": HomeClientSpotlightForm,
            },
        },
    )
