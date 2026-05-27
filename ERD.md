# Entity Relationship Diagram — workforce_nt

## Custom App Models (training)

```
+-------------------------------+          +-------------------------------+
|           Region              |          |           Category            |
+-------------------------------+          +-------------------------------+
| PK  id          AutoField     |          | PK  id          AutoField     |
|     name        CharField(100)|          |     name        CharField(20) |
|     slug        SlugField     |          |                 choices:      |
|     description TextField     |          |                 construction  |
+-------------------------------+          |                 care          |
              |                            |                 land_management|
              | 1                          |                 tourism        |
              |                            |                 unique=True    |
              |                            |     description TextField     |
              |                            +-------------------------------+
              |                                          |
              | 1                                        | 1
              |                                          |
              +---------> TrainingProgram <--------------+
                               ∞ (many)

+-----------------------------------------------+
|              TrainingProgram                  |
+-----------------------------------------------+
| PK  id             AutoField                  |
|     title          CharField(200)             |
|     slug           SlugField(unique=True)     |
|     description    TextField                  |
|     duration_weeks PositiveIntegerField       |
|     eligibility    TextField                  |
| FK  region_id      → Region.id    CASCADE     |
| FK  category_id    → Category.id  CASCADE     |
|     is_active      BooleanField(default=True) |
|     created_at     DateTimeField(auto_now_add)|
|     updated_at     DateTimeField(auto_now)    |
+-----------------------------------------------+
```

## Django Built-in Auth Model (django.contrib.auth)

Used by the `accounts` app for signup and login. No custom user model is defined — the project uses Django's default `User` directly.

```
+-----------------------------------------------+
|                 auth.User                     |
+-----------------------------------------------+
| PK  id               AutoField               |
|     username         CharField(150, unique)   |
|     first_name       CharField(150)           |
|     last_name        CharField(150)           |
|     email            EmailField               |
|     password         CharField(128)           |
|     is_staff         BooleanField             |
|     is_active        BooleanField             |
|     is_superuser     BooleanField             |
|     date_joined      DateTimeField            |
|     last_login       DateTimeField(null=True) |
| M2M groups           → auth.Group            |
| M2M user_permissions → auth.Permission       |
+-----------------------------------------------+
```

---

## Relationships Summary

| From            | Relationship | To              | On Delete | related_name |
|-----------------|-------------|-----------------|-----------|--------------|
| TrainingProgram | Many-to-One | Region          | CASCADE   | programs     |
| TrainingProgram | Many-to-One | Category        | CASCADE   | programs     |
| auth.User       | Many-to-Many| auth.Group      | —         | user_set     |
| auth.User       | Many-to-Many| auth.Permission | —         | user_set     |

---

## Relationship Diagram (Crow's Foot Notation)

```
Region ──────────────────────────────────────────┐
  |  (PK: id)                                    |
  |                                              |
  | 1                                            ∞
  └──────────────────────── TrainingProgram ─────┘
                                    ∞
  ┌──────────────────────────────────┘
  | 1
Category ────────────────────────────────────────┘
  |  (PK: id)


auth.User ───── M2M ───── auth.Group
auth.User ───── M2M ───── auth.Permission
```

**Cardinality:**
- One `Region` → Many `TrainingProgram` (required FK, CASCADE delete)
- One `Category` → Many `TrainingProgram` (required FK, CASCADE delete)
- One `TrainingProgram` → One `Region` (many-to-one)
- One `TrainingProgram` → One `Category` (many-to-one)

---

## Field-Type Reference

| Django Field Type      | SQL Equivalent              | Notes                              |
|------------------------|-----------------------------|------------------------------------|
| `AutoField`            | INTEGER PRIMARY KEY         | Implicit on every model            |
| `CharField(max)`       | VARCHAR(max)                | Requires max_length                |
| `SlugField`            | VARCHAR(50)                 | URL-safe identifier, auto-generated|
| `TextField`            | TEXT                        | Unbounded string                   |
| `PositiveIntegerField` | INTEGER UNSIGNED            | Must be ≥ 0                        |
| `BooleanField`         | BOOLEAN / TINYINT(1)        |                                    |
| `DateTimeField`        | DATETIME                    | auto_now_add / auto_now available  |
| `ForeignKey`           | INTEGER + FK constraint     | Stored as `<field>_id` column      |
| `EmailField`           | VARCHAR(254)                | Validates email format             |
| `ManyToManyField`      | Junction table              | No direct column on model          |
