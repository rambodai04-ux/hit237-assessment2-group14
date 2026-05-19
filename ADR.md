# Architectural Decision Records (ADR)
## NT Workforce Training Pathways — HIT237 Assessment 2 — Group 14

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

**Status:** Accepted

**Context:**
Business logic needed to live somewhere. Putting it in views would make them hard to test and reuse.

**Alternatives Considered:**
- Logic in views — works but creates bloated views that are hard to test
- Service layer — more complex, overkill for this project size

**Decision:**
Implement Fat Models pattern. All business logic lives as class methods on the `TrainingProgram` model: `get_active_programs()`, `get_programs_by_region()`, `get_programs_by_category()`, and `get_summary()`. Views only handle HTTP concerns.

**Code Reference:** `training/models.py:52-80`, `training/views.py:8-20`

**Consequences:**
Logic is reusable from management commands, shell, or tests. Views remain clean and focused on HTTP handling.

---

## ADR-003: Class-Based Views (CBVs)

**Status:** Accepted

**Context:**
Views needed to list programs, show detail pages, list regions and categories. These are standard patterns that repeat across the app.

**Alternatives Considered:**
- Function-based views — more explicit but requires writing repetitive boilerplate for each view
- CBVs — less code, built-in pagination, inheritance support

**Decision:**
Use Django's generic CBVs — `ListView` and `DetailView`. `ProgramListView` extends `ListView` with custom `get_queryset()` for filtering and `get_context_data()` for passing regions and categories to the template.

**Code Reference:** `training/views.py`

**Consequences:**
Less code, built-in pagination, consistent patterns across all views. Slightly harder to debug due to inherited behaviour.

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

**Status:** Accepted

**Context:**
All pages need consistent navbar, footer and CSS. Repeating this in every template violates DRY.

**Alternatives Considered:**
- Copy/paste navbar and footer into every template — violates DRY, hard to maintain
- JavaScript-based components — unnecessary complexity for a server-rendered app

**Decision:**
Create `templates/base.html` with shared navbar, footer and CSS link. All page templates extend base using `{% extends "base.html" %}` and `{% block content %}`. The homepage also uses `{% block hero %}` for the hero section.

**Code Reference:** `templates/base.html`, `training/templates/training/`

**Consequences:**
Single source of truth for layout. Changing navbar or footer only requires editing one file.

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
Store images as static files in `training/static/training/images/`. Use Django's `{% load static %}` and `{% static %}` template tag. Images are mapped to categories in templates using conditional logic.

**Code Reference:** `training/static/training/images/`, `training/templates/training/program_list.html`

**Consequences:**
Simple and reliable. Images served directly by Django dev server. For production, a CDN or media server would be recommended.

---

## ADR-007: URL Design — Loose Coupling

**Status:** Accepted

**Context:**
URL patterns needed to be scalable and maintainable across the project.

**Alternatives Considered:**
- Single urls.py — works but becomes hard to maintain as app grows
- App-level urls.py included in root — follows Django best practices

**Decision:**
Use two-level URL configuration. Root `workforce_nt/urls.py` includes `training/urls.py` under the `programs/` prefix with namespace `training`. Named URLs used throughout templates with `{% url 'training:program_list' %}`.

**Code Reference:** `workforce_nt/urls.py`, `training/urls.py`

**Consequences:**
Training app URLs are self-contained. App can be reused in other projects. Named URLs prevent hardcoding.

---

## AI Tool Usage Disclosure

This project used Claude (Anthropic) as an AI coding assistant throughout development. All AI-generated code was reviewed, understood, and modified by the development team. Architecture decisions, model design, and documentation reflect genuine understanding of Django design philosophies. Chat history with dates is available as evidence of responsible AI usage.