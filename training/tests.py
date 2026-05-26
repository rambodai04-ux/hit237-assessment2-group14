from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from .exceptions import ProgramNotFound, ProgramInactive
from .models import Category, Region, TrainingProgram
from .services import get_program_detail


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_region(name="Darwin"):
    return Region.objects.create(name=name)

def make_category(name=Category.CONSTRUCTION):
    return Category.objects.create(name=name, description="Test category")

def make_program(region=None, category=None, title="Test Program",
                 duration_weeks=8, is_active=True):
    if region is None:
        region = make_region()
    if category is None:
        category = make_category()
    return TrainingProgram.objects.create(
        title=title,
        description="A test training program.",
        duration_weeks=duration_weeks,
        eligibility="Open to all NT residents.",
        region=region,
        category=category,
        is_active=is_active,
    )


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------

class TrainingProgramModelTest(TestCase):

    def setUp(self):
        self.region = make_region("Alice Springs")
        self.category = make_category(Category.CARE)
        self.program = make_program(
            region=self.region,
            category=self.category,
            title="Cert III in Individual Support",
            duration_weeks=10,
        )

    def test_slug_auto_generated_on_save(self):
        self.assertEqual(self.program.slug, "cert-iii-in-individual-support")

    def test_str_returns_title(self):
        self.assertEqual(str(self.program), "Cert III in Individual Support")

    def test_is_long_program_property_true_above_8_weeks(self):
        self.program.duration_weeks = 9
        self.assertTrue(self.program.is_long_program)

    def test_is_long_program_property_false_at_8_weeks(self):
        self.program.duration_weeks = 8
        self.assertFalse(self.program.is_long_program)

    def test_duration_display_singular(self):
        self.program.duration_weeks = 1
        self.assertEqual(self.program.duration_display, "1 week")

    def test_duration_display_plural(self):
        self.program.duration_weeks = 10
        self.assertEqual(self.program.duration_display, "10 weeks")

    def test_get_summary_contains_title_and_region(self):
        summary = self.program.get_summary()
        self.assertIn("Cert III in Individual Support", summary)
        self.assertIn("Alice Springs", summary)

    def test_get_active_programs_excludes_inactive(self):
        make_program(region=self.region, category=self.category,
                     title="Inactive Program", is_active=False)
        active = list(TrainingProgram.get_active_programs())
        titles = [p.title for p in active]
        self.assertIn("Cert III in Individual Support", titles)
        self.assertNotIn("Inactive Program", titles)

    def test_get_programs_by_region_filters_correctly(self):
        other_region = make_region("Katherine")
        make_program(region=other_region, category=self.category,
                     title="Katherine Program")
        result = TrainingProgram.get_programs_by_region(self.region.pk)
        self.assertTrue(all(p.region_id == self.region.pk for p in result))

    def test_get_long_programs_respects_min_weeks(self):
        make_program(region=self.region, category=self.category,
                     title="Short Program", duration_weeks=4)
        long = list(TrainingProgram.get_long_programs(min_weeks=8))
        titles = [p.title for p in long]
        self.assertIn("Cert III in Individual Support", titles)  # 10 weeks
        self.assertNotIn("Short Program", titles)


class RegionModelTest(TestCase):

    def test_slug_auto_generated_on_save(self):
        region = Region.objects.create(name="Top End")
        self.assertEqual(region.slug, "top-end")

    def test_str_returns_name(self):
        region = Region.objects.create(name="Darwin")
        self.assertEqual(str(region), "Darwin")

    def test_with_program_counts_annotates_correctly(self):
        region = make_region("Darwin")
        category = make_category()
        make_program(region=region, category=category, title="Region Active Program", is_active=True)
        make_program(region=region, category=category, title="Region Inactive Program", is_active=False)
        regions = list(Region.with_program_counts())
        darwin = next(r for r in regions if r.name == "Darwin")
        self.assertEqual(darwin.program_count, 2)
        self.assertEqual(darwin.active_program_count, 1)


class CategoryModelTest(TestCase):

    def test_str_returns_display_name(self):
        category = make_category(Category.TOURISM)
        self.assertEqual(str(category), "Tourism")

    def test_with_program_counts_annotates_correctly(self):
        region = make_region()
        category = make_category(Category.CONSTRUCTION)
        make_program(region=region, category=category, title="Cat Active Program One", is_active=True)
        make_program(region=region, category=category, title="Cat Active Program Two", is_active=True)
        make_program(region=region, category=category, title="Cat Inactive Program", is_active=False)
        categories = list(Category.with_program_counts())
        construction = next(c for c in categories if c.name == Category.CONSTRUCTION)
        self.assertEqual(construction.program_count, 3)
        self.assertEqual(construction.active_program_count, 2)


# ---------------------------------------------------------------------------
# Service tests
# ---------------------------------------------------------------------------

class GetProgramDetailServiceTest(TestCase):

    def setUp(self):
        self.region = make_region()
        self.category = make_category()
        self.program = make_program(
            region=self.region,
            category=self.category,
            title="Cert III in Construction",
            duration_weeks=12,
        )

    def test_returns_program_for_valid_slug(self):
        result = get_program_detail(self.program.slug)
        self.assertEqual(result.pk, self.program.pk)

    def test_raises_program_not_found_for_bad_slug(self):
        with self.assertRaises(ProgramNotFound):
            get_program_detail("does-not-exist")

    def test_raises_program_inactive_for_inactive_program(self):
        self.program.is_active = False
        self.program.save()
        with self.assertRaises(ProgramInactive):
            get_program_detail(self.program.slug)

    def test_select_related_avoids_extra_queries(self):
        """Service should pre-fetch region and category in a single query."""
        result = get_program_detail(self.program.slug)
        with self.assertNumQueries(0):
            _ = result.region.name
            _ = result.category.get_name_display()

    def test_returns_correct_title(self):
        result = get_program_detail(self.program.slug)
        self.assertEqual(result.title, "Cert III in Construction")


# ---------------------------------------------------------------------------
# View / permission boundary tests
# ---------------------------------------------------------------------------

class AuthenticationRedirectTest(TestCase):
    """Unauthenticated requests to protected views must redirect to login."""

    def setUp(self):
        self.client = Client()
        self.region = make_region()
        self.category = make_category()
        self.program = make_program(region=self.region, category=self.category)

    def test_program_list_redirects_when_logged_out(self):
        response = self.client.get(reverse("training:program_list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])

    def test_program_detail_redirects_when_logged_out(self):
        url = reverse("training:program_detail", kwargs={"slug": self.program.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])

    def test_region_list_redirects_when_logged_out(self):
        response = self.client.get(reverse("training:region_list"))
        self.assertEqual(response.status_code, 302)

    def test_category_list_redirects_when_logged_out(self):
        response = self.client.get(reverse("training:category_list"))
        self.assertEqual(response.status_code, 302)

    def test_redirect_preserves_next_parameter(self):
        """After login the user should be returned to the originally requested page."""
        response = self.client.get(reverse("training:program_list"))
        self.assertIn("next=", response["Location"])


class AuthenticatedViewTest(TestCase):
    """Authenticated users must be able to access all protected views."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.client = Client()
        self.client.login(username="testuser", password="testpass123")
        self.region = make_region()
        self.category = make_category()
        self.program = make_program(region=self.region, category=self.category)

    def test_program_list_accessible_when_logged_in(self):
        response = self.client.get(reverse("training:program_list"))
        self.assertEqual(response.status_code, 200)

    def test_program_detail_accessible_when_logged_in(self):
        url = reverse("training:program_detail", kwargs={"slug": self.program.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_region_list_accessible_when_logged_in(self):
        response = self.client.get(reverse("training:region_list"))
        self.assertEqual(response.status_code, 200)

    def test_region_detail_accessible_when_logged_in(self):
        url = reverse("training:region_detail", kwargs={"slug": self.region.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_category_list_accessible_when_logged_in(self):
        response = self.client.get(reverse("training:category_list"))
        self.assertEqual(response.status_code, 200)

    def test_category_detail_accessible_when_logged_in(self):
        url = reverse("training:category_detail", kwargs={"name": self.category.name})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_program_list_context_contains_regions(self):
        response = self.client.get(reverse("training:program_list"))
        self.assertIn("regions", response.context)

    def test_program_list_context_contains_categories(self):
        response = self.client.get(reverse("training:program_list"))
        self.assertIn("categories", response.context)

    def test_program_list_search_filters_results(self):
        make_program(region=self.region, category=self.category, title="Unique Searchable Title")
        response = self.client.get(
            reverse("training:program_list") + "?q=Unique+Searchable"
        )
        programs = list(response.context["programs"])
        self.assertTrue(all("Unique Searchable" in p.title for p in programs))

    def test_inactive_programs_excluded_from_list(self):
        make_program(region=self.region, category=self.category,
                     title="Hidden Inactive", is_active=False)
        response = self.client.get(reverse("training:program_list"))
        titles = [p.title for p in response.context["programs"]]
        self.assertNotIn("Hidden Inactive", titles)


class AccountSignupTest(TestCase):
    """Signup flow creates a new User and redirects to login."""

    def test_signup_creates_user(self):
        self.client.post(reverse("accounts:signup"), {
            "username": "newuser",
            "email": "new@example.com",
            "first_name": "New",
            "last_name": "User",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        })
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_signup_redirects_to_login(self):
        response = self.client.post(reverse("accounts:signup"), {
            "username": "newuser2",
            "email": "new2@example.com",
            "first_name": "New",
            "last_name": "User",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        })
        self.assertRedirects(response, reverse("accounts:login"))

    def test_signup_with_mismatched_passwords_fails(self):
        self.client.post(reverse("accounts:signup"), {
            "username": "baduser",
            "password1": "StrongPass123!",
            "password2": "WrongPassword!",
        })
        self.assertFalse(User.objects.filter(username="baduser").exists())


# ---------------------------------------------------------------------------
# Dashboard / SavedProgram tests
# ---------------------------------------------------------------------------

class SavedProgramServiceTest(TestCase):
    """Tests for save_program and unsave_program service functions."""

    def setUp(self):
        self.user = User.objects.create_user(username="saveuser", password="pass1234")
        self.region = make_region("Darwin")
        self.category = make_category()
        self.program = make_program(
            region=self.region, category=self.category,
            title="Save Test Program"
        )

    def test_save_program_creates_saved_record(self):
        from .services import save_program
        from .models import SavedProgram
        save_program(self.user, self.program.slug)
        self.assertTrue(
            SavedProgram.objects.filter(user=self.user, program=self.program).exists()
        )

    def test_save_program_raises_not_found_for_bad_slug(self):
        from .services import save_program
        with self.assertRaises(ProgramNotFound):
            save_program(self.user, "bad-slug")

    def test_save_program_raises_inactive_for_inactive(self):
        from .services import save_program
        self.program.is_active = False
        self.program.save()
        with self.assertRaises(ProgramInactive):
            save_program(self.user, self.program.slug)

    def test_unsave_program_removes_record(self):
        from .services import save_program, unsave_program
        from .models import SavedProgram
        save_program(self.user, self.program.slug)
        unsave_program(self.user, self.program.slug)
        self.assertFalse(
            SavedProgram.objects.filter(user=self.user, program=self.program).exists()
        )

    def test_unsave_returns_false_if_not_saved(self):
        from .services import unsave_program
        result = unsave_program(self.user, self.program.slug)
        self.assertFalse(result)


class DashboardViewTest(TestCase):
    """Tests for user-specific dashboard."""

    def setUp(self):
        self.user = User.objects.create_user(username="dashuser", password="pass1234")
        self.client = Client()
        self.client.login(username="dashuser", password="pass1234")
        self.region = make_region()
        self.category = make_category()
        self.program = make_program(
            region=self.region, category=self.category,
            title="Dashboard Test Program"
        )

    def test_dashboard_accessible_when_logged_in(self):
        response = self.client.get(reverse("training:dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_redirects_when_logged_out(self):
        self.client.logout()
        response = self.client.get(reverse("training:dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])

    def test_dashboard_shows_only_users_saved_programs(self):
        from .services import save_program
        save_program(self.user, self.program.slug)
        other_user = User.objects.create_user(username="other", password="pass1234")
        other_program = make_program(
            region=self.region, category=self.category,
            title="Other Users Program"
        )
        save_program(other_user, other_program.slug)
        response = self.client.get(reverse("training:dashboard"))
        saved = list(response.context["saved_programs"])
        self.assertEqual(len(saved), 1)
        self.assertEqual(saved[0].program.title, "Dashboard Test Program")

    def test_dashboard_empty_for_user_with_no_saved_programs(self):
        response = self.client.get(reverse("training:dashboard"))
        self.assertEqual(response.context["saved_count"], 0)

# ---------------------------------------------------------------------------
# REST API tests
# ---------------------------------------------------------------------------

class TrainingProgramAPITest(TestCase):
    """Tests for /api/programs/ — verifies the IsAuthenticated boundary,
    that the queryset reuses get_active_programs() (no inactive leakage),
    and that the serialiser surface matches the declared field list.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="apiuser", password="apipass123"
        )
        self.region = make_region("Darwin")
        self.category = make_category(Category.CONSTRUCTION)
        self.active_program = make_program(
            region=self.region,
            category=self.category,
            title="Active API Program",
            duration_weeks=12,
            is_active=True,
        )
        self.inactive_program = make_program(
            region=self.region,
            category=self.category,
            title="Hidden Inactive Program",
            duration_weeks=6,
            is_active=False,
        )
        self.url = reverse("training:api_program_list")

    def test_unauthenticated_request_is_rejected(self):
        """The API must enforce IsAuthenticated; anonymous GET returns 403.
        Mirrors AuthenticationRedirectTest on the HTML side — same security
        property, different protocol surface."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_authenticated_request_returns_200(self):
        self.client.login(username="apiuser", password="apipass123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_response_is_json(self):
        self.client.login(username="apiuser", password="apipass123")
        response = self.client.get(self.url)
        self.assertIn("application/json", response["Content-Type"])

    def test_inactive_programs_excluded_from_api_response(self):
        """Verifies the queryset reuses get_active_programs(); an inactive
        program must not leak through the API just because it exists in the
        database. Guards against a regression where the queryset is
        'simplified' to TrainingProgram.objects.all()."""
        self.client.login(username="apiuser", password="apipass123")
        response = self.client.get(self.url)
        titles = [item["title"] for item in response.json()]
        self.assertIn("Active API Program", titles)
        self.assertNotIn("Hidden Inactive Program", titles)

    def test_serialised_fields_match_meta_definition(self):
        """The payload must contain exactly the fields declared in
        TrainingProgramSerializer.Meta. Guards against two failure modes:
        accidental field leakage (e.g. someone changes fields to '__all__'
        and exposes internal columns) and accidental removal (breaking
        downstream clients)."""
        self.client.login(username="apiuser", password="apipass123")
        response = self.client.get(self.url)
        expected_fields = {
            "id", "title", "slug", "description", "duration_weeks",
            "duration_display", "eligibility", "is_active",
            "region_name", "category_name",
        }
        self.assertEqual(set(response.json()[0].keys()), expected_fields)

    def test_computed_fields_resolve_to_related_values(self):
        """region_name, category_name, and duration_display are read-only
        computed fields. They must resolve to the related object's display
        value (not raw FK ids), and duration_display must use the model's
        pluralisation logic. This is where the serialiser does work beyond
        mirroring the model, so it is where bugs are most likely."""
        self.client.login(username="apiuser", password="apipass123")
        response = self.client.get(self.url)
        item = next(p for p in response.json() if p["title"] == "Active API Program")
        self.assertEqual(item["region_name"], "Darwin")
        self.assertEqual(item["category_name"], "Construction")
        self.assertEqual(item["duration_display"], "12 weeks") 