from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    """Sitemap for the public marketing pages.

    Everything else in the app (dashboard, admin-portal, activity, rewards,
    referrals) sits behind login and has no SEO value, so it's deliberately
    left out.
    """

    priority = 1.0
    changefreq = "weekly"

    def items(self):
        return ["accounts:home"]

    def location(self, item):
        return reverse(item)
