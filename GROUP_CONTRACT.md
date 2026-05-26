# HIT237 — Group 14 — Project Contract & Plan
## NT Workforce Training Pathways
### Updated for Assessment 4

---

## Project Theme
**Economic Strategy and Workforce Management System**
A web application for the Northern Territory's job seekers connecting them with training programs in Construction, Care Services, Land Management and Tourism sectors, in line with the NT Government's Economic Strategy 2025.

---

## Section 1: Terms and Conditions of Group Work

### Group Allocation
Everyone in the group should do their part in the project. Marks are allocated based on the individual's contribution which is reflected in what they commit to the GitHub repository, their attendance at meetings and completion of tasks. Members, who do not contribute fairly, might get lower marks, as agreed by the team.

### Communication
WhatsApp is the preferred communication tool for the team. Everyone is expected to reply in 24 hours. Progress is reviewed and tasks/resolutions are discussed at weekly meetings. Tasks and discussions about development are tracked on GitHub Issues.

### Task Ownership
Tasks are assigned with GitHub Projects and well documented. The members have to perform the tasks they are allocated on time. If a member cannot do a task, they should announce this at an early stage of the task so that support can be given or the task can be redistributed.

### Diverse Working Styles
The team recognizes that each member's schedule and/or commitments may differ. Work is fairly distributed and collaborative deadlines are set to allow for flexibility and productivity.

### Conflict Resolution
First any conflicts will be discussed in a respectful manner within the group. Where resolution is not possible, the issue will be raised with the lecturer/tutor.

### Academic Integrity
All work should be in accordance with university academic integrity policies. AI-generated code/content should be reviewed/reviewed/understood and acknowledged in the ADR. Everyone in the group should be aware of the final submission and able to explain the part they played in the final code in the live code walk-through and viva.
---

## Section 2: Task Breakdown by Member

| Member | Assessment 2 Role | Assessment 3 Role | Assessment 4 Role |
|---|---|---|---|
| **Irab Baral** | Frontend Development (UI/UX, templates, CSS) | Template updates (auth pages, navbar auth links, messages display) | Authentication templates refinement, updated ERD and class diagrams reflecting auth and service layers |
| **Manjil Bolakhe** | Backend Development (views, URLs, forms) | Service layer (`training/services.py`), exception handling, REST API | Service layer maturity (additional services for the SavedProgram feature), expanded exception handling |
| **Karan Thapa** | Database Design (models, migrations, ORM queries) | Authentication app (`accounts/`), `LoginRequiredMixin`, ADR updates | Continued accounts app development, permission mixins, ADR ownership and superseded-entry tracking |
| **Anang Suave Yume** | Testing, Documentation, Quality Assurance | Test suite expansion (38 tests), updated supplementary materials (ERD, class diagrams) | Test suite expansion to 53 tests across 10 classes (including REST API coverage), REST API implementation (`training/api.py`, ADR-012) |

**Note on task evolution from A3 to A4.** Two tasks were shifted between assessments to evenly distribute the workload. The REST API was relocated from Manjil to Anang — Anang already had the rest of the API under his control, and the tests for Anang's code were already in place in A3, so having the API code and tests under one person made both the testing strategy, and the linkage of the ADR-012 / ADR-013 simple. The ERD, class diagrams were removed from Anang and placed in Irab to free up Anang for REST API work and Irab already had the authentication template work related to the new diagrams.

---

## Section 3: Milestone History and Assessment 4 Progress

### Assessment 1 Milestones (Completed)
- Week 3: Finalised project scope and system requirements
- Week 5: Completed system design (architecture, database, UI planning)

### Assessment 2 Milestones (Completed)
- Week 7: Delivered working Django application with models, views, templates, ORM queries
- Week 9: System testing, debugging, and ADR documentation (ADR-001 to ADR-007)
- Week 11: Final integration — 6 CBVs, fat model pattern, slug-based URLs, admin customisation

### Assessment 3 Milestones (Completed)
- Authentication system — `accounts` app with login, logout, signup; `LoginRequiredMixin` on all 6 views
- Service layer — `accounts/services.py` (`create_account`), `training/services.py` (`get_program_detail`)
- Custom exceptions — `ProgramNotFound`, `ProgramInactive` in `training/exceptions.py`
- REST API — `TrainingProgramListAPIView` at `/api/programs/` using Django REST Framework
- Test suite — 38 tests across models, services, views, permission boundaries, signup flow
- Updated ADR — ADR-008 through ADR-013 added; ADR-002 status updated

### Assessment 4 Milestones
- SavedProgram feature — `SavedProgram` model, `save_program()` / `unsave_program()` services, user-scoped dashboard view demonstrating authenticated workflow with permission boundary
- Test suite expansion from 38 → 53 tests across 10 classes, including new `TrainingProgramAPITest` covering the REST API auth boundary (anonymous 403), queryset reuse (inactive programs excluded), and serialiser surface (field set, computed fields)
- ADR evolution — ADR-013 amended to document the SavedProgram test additions; AI tool usage reflection paragraph documenting iterative refinement of AI-generated tests away from trivial status-code assertions toward meaningful permission and behavioural verification
- Updated ERD and class diagrams reflecting the authentication model and service layer
- Supplementary materials including DRF browsable API screenshots (authenticated 200 response, unauthenticated 403)
- Continuous commit history demonstrating individual contributions traceable to ADR entries

---

## Section 4: Internal Checkpoints

| Checkpoint | Method | Status |
|---|---|---|
| Weekly progress | Teams meeting | Ongoing |
| Mid-Assessment 4 review | Teams call + GitHub PR review | Completed |
| Test suite + ADR peer review | GitHub PR — all members review before merge | Completed |
| Final internal review | Teams meeting before submission deadline | Pending |

---

## Section 5: Integration Points

- Weekly code merging through GitHub branches → `main`
- All new features require review by at least one other member before merge
- `python manage.py test training accounts` must pass with 0 failures before any merge to `main`
- Final system integration and manual smoke test before submission

---

## Section 6: Contribution Agreement

All members will take an active role, communicate effectively and complete assigned tasks in a responsible manner. They are currently tracking contributions using GitHub's commit tracking and team discussions on Microsoft Teams. The commit history should show ongoing development throughout the four assessments with individual contributions identified in the commit history and entries on the ADR.

---

## Group Members

- Irab Baral
- Manjil Bolakhe
- Karan Thapa
- Anang Suave Yume
