# Architectural Decision Records (ADR)
## NT Workforce Training Pathways — HIT237 Assessment 2 & 3 — Group 14

---

## ADR-001: Django MVT Architecture

**Status:** Accepted

**Context:**
We needed to build a web application for NT job seekers to browse training pathways. The application required a clean separation between data, logic, and presentation layers.

**Alternatives Considered:**
- Flask — lightweight but requires assembling components manually, lacks built-in ORM and admin
- Pure HTML/CSS/JS — no database support, not scalable

**Decision:**
Use Django's MVT (Model-View-Template) architecture. Django acts as the controller, handling URL routing automatically while we focus on Models, Views and Templates.

**Code Reference:** `workforce_nt/settings.py`, `workforce_nt/urls.py`

**Consequences:**
Clean separation of concerns. Django handles routing, security (CSRF, XSS), and admin automatically.

---

## ADR-002: Fat Models, Skinny Views Pattern

**Status:** Partially superseded by ADR-008 — see below

**Context:**
Business logic needed to live somewhere. Putting it in views would make them hard to test and reuse.

**Alternatives Considered:**
- Logic in views — works but creates bloated views that are hard to test
- Service layer — more complex, considered overkill at Assessment 2 project size

**Decision:**
Implement Fat Models pattern. All business logic lives as class methods on the `TrainingProgram` model: `get_active_programs()`, `get_programs_by_region()`, `get_programs_by_category()`, and `get_summary()`. Views only handle HTTP concerns.

**Code Reference:** `training/models.py:52-80`, `training/views.py:8-20`

**Consequences:**
Logic is reusable from management commands, shell, or tests. Views remain clean and focused on HTTP handling.

**Assessment 3 Update:**
This decision held for pure query logic. However, cross-cutting workflows introduced in Assessment 3 (user registration, program detail orchestration) required service functions. ADR-008 extends this decision: fat model classmethods remain for single-model reads; service functions handle multi-step or multi-model operations.

---

## ADR-003: Class-Based Views (CBVs)

**Status:** Accepted — extended in Assessment 3

**Context:**
Views needed to list programs, show detail pages, list regions and categories. These are standard patterns that repeat across the app.

**Alternatives Considered:**
- Function-based views — more explicit but requires writing repetitive boilerplate for each view
- CBVs — less code, built-in pagination, inheritance support

**Decision:**
Use Django's generic CBVs — `ListView` and `DetailView`. `ProgramListView` extends `ListView` with custom `get_queryset()` for filtering and `get_context_data()` for passing regions and categories to the template.

**Code Reference:** `training/views.py`

**Consequences:**
Less code, built-in pagination, consistent patterns across all views. Slightly harder to debug due to inherited behaviour. In Assessment 3, mixins (`LoginRequiredMixin`, `StaffRequiredMixin`) were composed with CBVs using Django's MRO — this pattern works cleanly with class-based views and would have been awkward with function-based views.

---

## ADR-004: Model Relationships — ForeignKey Design

**Status:** Accepted

**Context:**
Training programs need to be associated with regions and categories. We needed to decide how to model these relationships.

**Alternatives Considered:**
- CharField with choices on TrainingProgram — simpler but not extensible, no separate admin management
- ManyToMany — overkill, a program belongs to one region and one category
- ForeignKey — clean 1:N relationship, allows regions/categories to have many programs

**Decision:**
Use `ForeignKey` from `TrainingProgram` to both `Region` and `Category` with `related_name="programs"` enabling reverse lookups like `region.programs.all()`.

**Code Reference:** `training/models.py:35-45`

**Consequences:**
Clean relational design. Regions and categories can be managed independently. Reverse lookups work naturally in templates.

---

## ADR-005: Django Template Inheritance (DRY Philosophy)

**Status:** Accepted — extended in Assessment 3

**Context:**
All pages need consistent navbar, footer and CSS. Repeating this in every template violates DRY.

**Alternatives Considered:**
- Copy/paste navbar and footer into every template — violates DRY, hard to maintain
- JavaScript-based components — unnecessary complexity for a server-rendered app

**Decision:**
Create `base.html` with shared navbar, footer and CSS link. All page templates extend base using `{% extends %}` and `{% block content %}`.

**Code Reference:** `training/templates/training/base.html`

**Consequences:**
Single source of truth for layout. In Assessment 3, the navbar was extended to include conditional login/logout links using `{% if user.is_authenticated %}` and flash message display, both requiring only a single edit to `base.html`.

---

## ADR-006: Static Files and Image Management

**Status:** Accepted

**Context:**
The application needed images for visual appeal and to represent each training category.

**Alternatives Considered:**
- External image URLs — dependent on third-party availability
- Django ImageField with media uploads — requires Pillow and media server configuration
- Static files — simple, reliable for development

**Decision:**
Store images as static files in `training/static/training/images/`. Use Django's `{% load static %}` and `{% static %}` template tag.

**Code Reference:** `training/static/training/images/`, `training/templates/training/program_list.html`

**Consequences:**
Simple and reliable for development. For production, a CDN or object storage would be recommended.

---

## ADR-007: URL Design — Loose Coupling

**Status:** Accepted — extended in Assessment 3

**Context:**
URL patterns needed to be scalable and maintainable across the project.

**Alternatives Considered:**
- Single `urls.py` — works but becomes hard to maintain as app grows
- App-level `urls.py` included in root — follows Django best practices

**Decision:**
Two-level URL configuration. Root `workforce_nt/urls.py` includes app-level URL files. Named URLs used throughout with `{% url 'training:program_list' %}`.

**Code Reference:** `workforce_nt/urls.py`, `training/urls.py`

**Consequences:**
In Assessment 3, `accounts/urls.py` was added and included at `accounts/` prefix with zero changes required to `training/urls.py`. The loose coupling justified itself immediately when adding the new app.

---

## ADR-008: Selective Service Layer for Cross-Cutting Workflows

**Status:** Accepted (extends ADR-002)

**Context:**
Assessment 3 added user registration (creating a `User`) and exposed a need to call the same orchestration logic from views, tests, and potentially management commands. `SignupView.form_valid()` was the first place cross-model or multi-step writes appeared. The original Fat Models approach is still correct for read-only query classmethods that touch only one model. The service layer is introduced only where that boundary is crossed.

**Alternatives Considered:**
- Keep all logic in views — fast to write but untestable in isolation; view tests require HTTP machinery even to test a password-hash call
- Full HackSoft-style services + selectors — correctly separates reads from writes but adds a `selectors.py` module that is unnecessary overhead given the current query volume
- Targeted services file per app — one `services.py` per Django app containing only functions that coordinate multiple models or enforce cross-model business rules

**Decision:**
Introduce `accounts/services.py` with `create_account()` and `training/services.py` with `get_program_detail()`. Fat model classmethods (`get_active_programs()`, `get_programs_by_region()`, etc.) remain on the model because they only read from a single model's data. The rule: if the function needs to write to more than one model, or if it needs to be callable outside an HTTP context, it becomes a service function.

**Code Reference:** `accounts/services.py`, `training/services.py`, `accounts/views.py`

**Consequences:**
`SignupView.form_valid` is now three lines. Services are called directly in unit tests without a test client. The distinction between "model method" and "service function" is documented here and must be enforced in code review to prevent drift.

---

## ADR-009: User Authentication with Django's Built-in Auth

**Status:** Accepted

**Context:**
The application was publicly accessible with no login requirement. Assessment 3 required that all training content views be protected and that users be able to register, log in, and log out.

**Alternatives Considered:**
- `django-allauth` — full social login support, but adds a large dependency and template complexity not needed here
- JWT-based authentication — appropriate for a headless API but adds complexity when the app is primarily server-rendered HTML
- Django's built-in `LoginView`, `LogoutView`, `LoginRequiredMixin` — ships with Django, zero additional dependencies, integrates with the session framework already in use

**Decision:**
Use Django's built-in authentication system. A new `accounts` app contains `urls.py`, `forms.py` (`CustomUserCreationForm` extending `UserCreationForm`), `views.py` (`SignupView`), and `services.py` (`create_account()`). `LOGIN_URL`, `LOGIN_REDIRECT_URL`, and `LOGOUT_REDIRECT_URL` are configured in `settings.py`. `LoginRequiredMixin` is added to all six training views.

**Code Reference:** `accounts/`, `training/views.py`, `workforce_nt/settings.py`

**Consequences:**
All training content is now behind a login wall. Django handles session management, password hashing (PBKDF2 by default), and CSRF automatically. The `next` parameter is preserved on redirect so users land on their originally requested page after login. No new dependencies introduced.

---

## ADR-010: StaffRequiredMixin for Write Operations

**Status:** Accepted

**Context:**
`LoginRequiredMixin` ensures only authenticated users access the application. However, create/edit/delete operations should be restricted to staff. Django's built-in `PermissionRequiredMixin` couples views to Django's permission table, adding management overhead for a project of this size.

**Alternatives Considered:**
- `PermissionRequiredMixin` with named permissions — correct for large apps, requires permission setup via `manage.py`
- Decorator `@staff_member_required` — function-based only, not composable with CBVs
- Custom `StaffRequiredMixin` overriding `dispatch()` — one class, checked before `get()` or `post()`, returns `HttpResponseForbidden` (403) directly

**Decision:**
`StaffRequiredMixin` is defined in `training/views.py`. It overrides `dispatch()`, checks `request.user.is_staff`, and returns a 403 if the check fails. It is listed second in the MRO after `LoginRequiredMixin` so unauthenticated users hit the login redirect before the staff check.

**Code Reference:** `training/views.py:StaffRequiredMixin`

**Consequences:**
Separation between authenticated and staff access is enforced at the dispatch layer, before any view logic runs. Staff status is managed via Django admin. The 403 response is plain text — a styled error page would be the natural next step.

---

## ADR-011: Custom Exception Classes for Service Layer

**Status:** Accepted

**Context:**
`training/services.py:get_program_detail()` needed to signal two distinct failure modes: program not found, and program exists but is inactive. Using `Http404` would couple the service to HTTP. Using `ValidationError` merges two different failure semantics under one type.

**Alternatives Considered:**
- `Http404` — raises a 404 directly, but services must be callable from management commands or background tasks where there is no HTTP context
- `ValidationError` — Django's exception for invalid data, but "program is inactive" is a business rule violation, not a validation error
- Custom exceptions inheriting from `Exception` — explicit, typed, testable with `assertRaises`, decoupled from HTTP

**Decision:**
`training/exceptions.py` defines `ProgramNotFound(Exception)` and `ProgramInactive(Exception)`. Services raise these. Views catch them and convert to user-facing messages. Tests use `assertRaises` to verify the correct type is raised under each condition.

**Code Reference:** `training/exceptions.py`, `training/services.py`, `training/views.py`

**Consequences:**
Services are testable in isolation. The exception type carries semantic meaning. Future endpoints can catch each exception independently and respond differently (e.g. 404 vs 410 Gone).

---

## ADR-012: REST API with Django REST Framework

**Status:** Accepted

**Context:**
Training program data may need to be consumed by external clients (mobile apps, front-end frameworks). The existing views serve HTML only.

**Alternatives Considered:**
- Hand-rolled JSON views using `JsonResponse` — requires manual serialisation, pagination, and auth for every endpoint
- GraphQL (`strawberry-graphql`) — powerful but heavy; the data model is flat enough that REST is sufficient
- Django REST Framework — the de-facto standard, ships generic views mirroring Django's CBVs, handles serialisation and authentication integration

**Decision:**
Install `djangorestframework` and add to `INSTALLED_APPS`. `training/api.py` defines `TrainingProgramSerializer` and `TrainingProgramListAPIView` using `ListAPIView` with `IsAuthenticated` permission. The same `get_active_programs()` queryset used by the HTML view is reused — no duplication of query logic.

**Code Reference:** `training/api.py`, `training/urls.py`

**Consequences:**
`/api/programs/` returns JSON for authenticated requests; 403 for unauthenticated. DRF's browsable API is available in development (screenshots in supplementary materials). The serialiser is currently read-only and list-only — write endpoints would require a separate ADR entry.

---

## ADR-013: Testing Strategy

**Status:** Accepted

**Context:**
Assessment 3 required a meaningful test suite. What to test, what not to test, and why must be justified. Tests that only assert trivial conditions or mirror implementation details without verifying meaningful behaviour were explicitly excluded.

**Decision:**
The test suite is organised into five layers covering 38 tests:

1. **Model tests** (`TrainingProgramModelTest`, `RegionModelTest`, `CategoryModelTest`) — verify slug auto-generation, `__str__` output, property logic (`is_long_program`, `duration_display`), and fat model classmethods (`get_active_programs`, `get_programs_by_region`, `get_long_programs`, `with_program_counts`). Pure unit tests with no HTTP machinery.

2. **Service tests** (`GetProgramDetailServiceTest`) — verify `get_program_detail()` raises `ProgramNotFound` for a missing slug, raises `ProgramInactive` for an inactive program, and that `select_related` avoids N+1 queries (`assertNumQueries(0)` after fetching). The query count assertion verifies an ORM design decision, not just a return value.

3. **Permission boundary tests** (`AuthenticationRedirectTest`) — verify all six protected views return 302 to `/accounts/login/` when accessed without a session, and that the `next` parameter is preserved. These tests verify the boundary between public and private, which is the most critical correctness property of the authentication feature.

4. **Authenticated view tests** (`AuthenticatedViewTest`) — verify 200 responses, correct context keys, search filtering behaviour, and inactive program exclusion for a logged-in user.

5. **Signup tests** (`AccountSignupTest`) — verify the full registration flow: user created in DB, redirect to login on success, and password mismatch correctly prevented.

**What is not tested and why:**
- Django's own `LoginView` and `LogoutView` — Django's own test suite covers these; testing them here tests the framework, not our code.
- Template rendering details (exact HTML output) — brittle and low value; functional correctness verified by status codes and context variables instead.
- REST API serialiser field values — the serialiser is a thin wrapper over already-tested model properties; a serialiser integration test is the natural next addition.

**Code Reference:** `training/tests.py`

**Consequences:**
38 tests covering models, services, views, permission boundaries, and signup. Running `python manage.py test training accounts -v 2` produces no failures on a fresh database. Test isolation is guaranteed by Django's `TestCase` (each test runs in a transaction that is rolled back after completion).

---

## AI Tool Usage Disclosure

**Assessment 2:**
This project used Claude (Anthropic) as an AI coding assistant throughout development. All AI-generated code was reviewed, understood, and modified by the development team. Architecture decisions, model design, and documentation reflect genuine understanding of Django design philosophies.

**Assessment 3 Update:**
AI coding assistants continued to be used for scaffolding the auth app, generating initial test cases, and drafting ADR entries. All generated code was reviewed against Django documentation and modified to reflect actual project decisions. The testing strategy (ADR-013) was critically evaluated — initial AI-generated tests that only checked `response.status_code == 200` without testing permission boundaries were replaced with tests verifying meaningful invariants (query counts, redirect targets, context contents). ADR entries were written to explain *why* each decision was made, not just *what* was decided. Chat history with dates is available as evidence of responsible AI usage.

---

## ADR-014: User Dashboard and SavedProgram Feature

**Status:** Accepted

**Context:**
The rubric for Feature Maturity required at least two substantive new features requiring authenticated workflows and evidence of a coherent user journey. The application previously had authentication but no user-specific content — every logged-in user saw the same pages. A personalisation feature was needed to demonstrate role-dependent workflows.

**Alternatives Considered:**
- Enrolment/application tracking — more complex, requires status management and admin review flow
- Favourites list (read-only bookmarks) — simple, directly addresses "user-specific dashboard" criterion
- Program history (view count) — passive, not user-driven

**Decision:**
Add a `SavedProgram` model linking `User` to `TrainingProgram` with a `unique_together` constraint preventing duplicates. Add `save_program()` and `unsave_program()` service functions in `training/services.py`. Add `DashboardView`, `SaveProgramView`, and `UnsaveProgramView` to `training/views.py`. The dashboard becomes the `LOGIN_REDIRECT_URL` so users land on their personalised page after login.

**Code Reference:** `training/models.py:SavedProgram`, `training/services.py:save_program,unsave_program`, `training/views.py:DashboardView`, `training/templates/training/dashboard.html`, `training/migrations/0003_savedprogram.py`

**Consequences:**
The application now has a coherent user journey: browse programs → save to dashboard → manage saved programs. The `unique_together` constraint enforces data integrity at the database level. Save/unsave goes through the service layer so both operations raise typed domain exceptions (`ProgramNotFound`, `ProgramInactive`) caught by the view layer. The dashboard is user-isolated: `SavedProgram.objects.filter(user=request.user)` ensures users only see their own saved programs.

---

## ADR-013 (Updated): Testing Strategy

**Status:** Accepted — updated to reflect SavedProgram tests

The test suite now covers 51 tests across 7 test classes. The SavedProgram feature added two new test classes:

- `SavedProgramServiceTest` — verifies `save_program()` creates a DB record, raises `ProgramNotFound` for a bad slug, raises `ProgramInactive` for an inactive program, and that `unsave_program()` deletes the record and returns `False` when nothing was saved.
- `DashboardViewTest` — verifies the dashboard returns 200 for authenticated users, redirects to login for unauthenticated users, shows only the current user's saved programs (not other users'), and shows 0 count for a user with no saved programs. The user-isolation test is the most important: it verifies that the `filter(user=request.user)` in `DashboardView` correctly scopes results, which is the security property of the feature.

**Code Reference:** `training/tests.py:SavedProgramServiceTest,DashboardViewTest`
