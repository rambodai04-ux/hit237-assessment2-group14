from django.db import transaction

from .exceptions import ProgramNotFound, ProgramInactive
from .models import TrainingProgram


def get_program_detail(slug):
    """
    Fetches a single active training program by slug.
    Raises ProgramNotFound if it doesn't exist.
    Raises ProgramInactive if it exists but is not active.
    Returns the TrainingProgram instance on success.
    """
    try:
        program = TrainingProgram.objects.select_related(
            "region", "category"
        ).get(slug=slug)
    except TrainingProgram.DoesNotExist:
        raise ProgramNotFound(f"No training program found for slug '{slug}'.")

    if not program.is_active:
        raise ProgramInactive(f"'{program.title}' is no longer active.")

    return program


def save_program(user, program_slug):
    """
    Bookmarks a training program for the given user.
    Raises ProgramNotFound if slug does not exist.
    Raises ProgramInactive if program is not active.
    Returns the SavedProgram instance on success, or None if already saved.
    """
    from .models import SavedProgram
    program = get_program_detail(program_slug)
    saved, created = SavedProgram.objects.get_or_create(user=user, program=program)
    return saved if created else None


def unsave_program(user, program_slug):
    """
    Removes a bookmarked program for the given user.
    Raises ProgramNotFound if slug does not exist.
    Returns True if deleted, False if it was not saved.
    """
    from .models import SavedProgram
    try:
        program = TrainingProgram.objects.get(slug=program_slug)
    except TrainingProgram.DoesNotExist:
        raise ProgramNotFound(f"No program found for slug '{program_slug}'.")
    deleted, _ = SavedProgram.objects.filter(user=user, program=program).delete()
    return deleted > 0
