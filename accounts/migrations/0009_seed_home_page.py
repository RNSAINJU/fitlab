from django.db import migrations


def seed_home_page(apps, schema_editor):
    HomePageSettings = apps.get_model("accounts", "HomePageSettings")
    HomePowerlifter = apps.get_model("accounts", "HomePowerlifter")
    HomeTrainer = apps.get_model("accounts", "HomeTrainer")
    HomeTrainingService = apps.get_model("accounts", "HomeTrainingService")
    HomeScheduleSlot = apps.get_model("accounts", "HomeScheduleSlot")
    HomePricingPlan = apps.get_model("accounts", "HomePricingPlan")
    HomePricingTier = apps.get_model("accounts", "HomePricingTier")
    HomeGalleryImage = apps.get_model("accounts", "HomeGalleryImage")
    HomeTestimonial = apps.get_model("accounts", "HomeTestimonial")
    HomeClientSpotlight = apps.get_model("accounts", "HomeClientSpotlight")

    hp, _ = HomePageSettings.objects.get_or_create(pk=1)
    hp.hero_headline = "Ready to start?"
    hp.hero_cta_text = "Enquire Now"
    hp.hero_image_url = "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=1920&q=80"
    hp.welcome_tagline = "A Private Gym in Kathmandu"
    hp.welcome_paragraph_1 = (
        "At The Fit lab, we believe that fitness is not a one-size-fits-all approach. "
        "We are a private gym in Kathmandu, dedicated to providing a personalized fitness experience "
        "tailored to your unique goals and needs."
    )
    hp.welcome_paragraph_2 = (
        "The concept of a private gym is fairly new in Nepal. To simply explain, in our gym, the "
        "equipment and the trainer will be solely dedicated to you during your session. In a way, "
        "The Fit lab will be your private gym during your session."
    )
    hp.welcome_paragraph_3 = (
        "Step into one of the best fitness centers in Kathmandu, where you'll find a dynamic and "
        "motivating environment designed to inspire and empower you on your fitness journey. Our "
        "cutting-edge equipment, spacious workout areas, and expert trainers ensure that every visit "
        "is an opportunity to push your limits and achieve remarkable results."
    )
    hp.training_intro = (
        "When you join The Fit lab, our trainer will take the time to understand your aspirations, "
        "assess your current fitness level, and design a customized workout program that aligns with "
        "your goals. Whether you're aiming to lose weight, build strength, improve endurance, prepare "
        "for the game, or enhance overall fitness, our trainer will create a plan that optimizes your progress."
    )
    hp.schedule_image_url = "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=600&q=80"
    hp.clients_intro = (
        "At The Fit lab, we take pride in our ability to cater to a diverse range of clients. "
        "Our personalized approach ensures that every individual receives tailored fitness programs and expert "
        "guidance. We create an inclusive and supportive environment where all clients can achieve their fitness goals."
    )
    hp.footer_blurb = (
        "Experience the power of personalized fitness at The Fit lab and discover how it can "
        "transform your body, mind, and overall well-being."
    )
    hp.save()

    powerlifters = [
        ("Jenish Bhujel", "https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?w=600&q=80"),
        ("Powerlifter", "https://images.unsplash.com/photo-1567013127542-490d757e51fc?w=400&q=80"),
        ("Powerlifter", "https://images.unsplash.com/photo-1574680096145-d05b474e2155?w=400&q=80"),
        ("Powerlifter", "https://images.unsplash.com/photo-1594381898411-8465977c4a0a?w=400&q=80"),
        ("Powerlifter", "https://images.unsplash.com/photo-1534367507873-d2d7e24c797f?w=400&q=80"),
        ("Powerlifter", "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=400&q=80"),
        ("Powerlifter", "https://images.unsplash.com/photo-1540497077202-7c8a3999166f?w=400&q=80"),
        ("Powerlifter", "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=400&q=80"),
    ]
    for i, (name, url) in enumerate(powerlifters):
        HomePowerlifter.objects.create(name=name, image_url=url, sort_order=i)

    trainers = [
        ("Sandesh Rawol", "https://images.unsplash.com/photo-1567013127542-490d757e51fc?w=700&q=80"),
        ("Performance Coach", "https://images.unsplash.com/photo-1574680096145-d05b474e2155?w=700&q=80"),
        ("Strength Coach", "https://images.unsplash.com/photo-1594381898411-8465977c4a0a?w=700&q=80"),
    ]
    for i, (name, url) in enumerate(trainers):
        HomeTrainer.objects.create(name=name, image_url=url, sort_order=i)

    services = [
        "Weight Loss / Management",
        "Resistance Training",
        "Muscle Building",
        "Planning & Periodisation for Powerlifting Game",
        "Speed, Strength, Power Development",
        "Performance based nutrition consultation",
    ]
    for i, title in enumerate(services):
        HomeTrainingService.objects.create(title=title, sort_order=i)

    schedule = [
        ("One on One Session", "07:00 – 11:00 AM, 3:00 – 8:00 PM"),
        ("Group Session", "07:00 – 08:00 AM, 05:00 – 06:00 PM"),
        ("Couple Session", "07:00 – 11:00 AM, 03:00 – 08:00 PM"),
        ("Powerlifting Training", "05:00 – 06:00 PM"),
        ("Hypertrophy Training", "07:00 – 11:00 AM, 03:00 – 08:00 PM"),
        ("General Fitness", "07:00 – 11:00 AM, 03:00 – 08:00 PM"),
        ("Basic Endurance Training", "07:00 – 11:00 AM, 03:00 – 08:00 PM"),
        ("Online Training", "03:00 – 05:00 PM"),
        ("Bodybuilding Contest Preparation", "07:00 – 08:00 AM, 05:00 – 06:00 PM"),
    ]
    for i, (title, times) in enumerate(schedule):
        HomeScheduleSlot.objects.create(title=title, time_info=times, sort_order=i)

    plans = [
        {
            "title": "Personal Training",
            "features": ("Personal trainer", "Customized exercise plan for best result", "Performance based nutrition consultation"),
            "bg": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=800&q=80",
            "tiers": [
                ("3 Days a week – NRs. 23,000/-", "12 sessions (Valid for 40 days)"),
                ("4 Days a week – NRs. 28,000/-", "16 sessions (Valid for 40 days)"),
                ("5 Days a week – NRs. 33,000/-", "20 sessions (Valid for 40 days)"),
            ],
        },
        {
            "title": "Couple Training",
            "features": ("Personal trainer", "Customized exercise plan for best result", "Performance based nutrition consultation"),
            "bg": "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=800&q=80",
            "tiers": [
                ("3 Days a week – NRs. 33,500/-", "12 sessions (Valid for 40 days)"),
                ("4 Days a week – NRs. 40,000/-", "16 sessions (Valid for 40 days)"),
                ("5 Days a week – NRs. 48,000/-", "20 sessions (Valid for 40 days)"),
            ],
        },
        {
            "title": "Group Training",
            "features": ("Trainer", "Customized exercise plan for best result", "Performance based nutrition consultation"),
            "bg": "https://images.unsplash.com/photo-1518611012118-696072aa579a?w=800&q=80",
            "tiers": [
                ("3 Days a week – NRs. 6,000/-", "12 sessions (Valid for 35 days)"),
                ("4 Days a week – NRs. 8,000/-", "16 sessions (Valid for 35 days)"),
                ("5 Days a week – NRs. 9,000/-", "20 sessions (Valid for 35 days)"),
            ],
        },
    ]
    for i, plan_data in enumerate(plans):
        plan = HomePricingPlan.objects.create(
            title=plan_data["title"],
            feature_1=plan_data["features"][0],
            feature_2=plan_data["features"][1],
            feature_3=plan_data["features"][2],
            background_image_url=plan_data["bg"],
            sort_order=i,
        )
        for j, (price, sessions) in enumerate(plan_data["tiers"]):
            HomePricingTier.objects.create(
                plan=plan,
                price_label=price,
                sessions_label=sessions,
                sort_order=j,
            )

    gallery_urls = [
        "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=700&q=80",
        "https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?w=700&q=80",
        "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=700&q=80",
        "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=700&q=80",
    ]
    for i, url in enumerate(gallery_urls):
        HomeGalleryImage.objects.create(image_url=url, sort_order=i)

    testimonials = [
        (
            "A premium private gym experience with real personal attention. Every session feels purposeful and I'm seeing real results.",
            "Member",
        ),
        (
            "The trainers understand my goals and push me every session. Best gym experience I've had in Kathmandu.",
            "Personal Training Client",
        ),
        (
            "No crowds, no waiting — just focused training with expert coaching. Highly recommend.",
            "Couple Training Member",
        ),
    ]
    for i, (quote, author) in enumerate(testimonials):
        HomeTestimonial.objects.create(quote=quote, author=author, sort_order=i)

    clients = [
        (1, "Sarada Munikar – Civil Engineer", "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=400&q=80"),
        (1, "Riyaz Munikar – Student", "https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?w=400&q=80"),
        (1, "Shresha Munikar – Powerlifter", "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=400&q=80"),
        (2, "Sakshi Maskey – Makeup Artist", "https://images.unsplash.com/photo-1594381898411-8465977c4a0a?w=400&q=80"),
        (2, "Shilpa Maskey – Actress / Entrepreneur", "https://images.unsplash.com/photo-1567013127542-490d757e51fc?w=400&q=80"),
        (2, "Sayujya Sharma – Financial Advisor", "https://images.unsplash.com/photo-1574680096145-d05b474e2155?w=400&q=80"),
    ]
    for i, (row, caption, url) in enumerate(clients):
        HomeClientSpotlight.objects.create(row=row, caption=caption, image_url=url, sort_order=i)


def unseed_home_page(apps, schema_editor):
    for model_name in (
        "HomeClientSpotlight",
        "HomeTestimonial",
        "HomeGalleryImage",
        "HomePricingTier",
        "HomePricingPlan",
        "HomeScheduleSlot",
        "HomeTrainingService",
        "HomeTrainer",
        "HomePowerlifter",
        "HomePageSettings",
    ):
        apps.get_model("accounts", model_name).objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0008_home_page_cms"),
    ]

    operations = [
        migrations.RunPython(seed_home_page, unseed_home_page),
    ]
