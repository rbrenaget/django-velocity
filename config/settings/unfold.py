"""
Django Unfold Admin Configuration.
https://unfoldadmin.com/docs/
"""

from django.templatetags.static import static
from django.urls import reverse_lazy

UNFOLD = {
    "SITE_TITLE": "Django Velocity",
    "SITE_HEADER": "Django Velocity",
    "SITE_SUBHEADER": "Administration",
    # "SITE_ICON": lambda request: static("icon.svg"),
    "SITE_LOGO": {
        "light": lambda request: static("logo-light.svg"),
        "dark": lambda request: static("logo-dark.svg"),
    },
    "SITE_SYMBOL": "speed",  # Material Symbols icon
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    # Theme colors (using Tailwind CSS color names)
    "COLORS": {
        "primary": {
            "50": "250 245 255",
            "100": "243 232 255",
            "200": "233 213 255",
            "300": "216 180 254",
            "400": "192 132 252",
            "500": "168 85 247",
            "600": "147 51 234",
            "700": "126 34 206",
            "800": "107 33 168",
            "900": "88 28 135",
            "950": "59 7 100",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Authentication & Users",
                "separator": True,
                "items": [
                    {
                        "title": "Users",
                        "icon": "person",
                        "link": reverse_lazy("admin:users_user_changelist"),
                    },
                    {
                        "title": "Groups",
                        "icon": "group",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                    },
                ],
            },
        ],
    },
}
