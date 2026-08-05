import pytest
from django.core.management import call_command
from core.models import Ingredient


@pytest.mark.django_db
def test_seed_demo_is_idempotent():
    
    call_command("seed_demo", 3,3,3)
    count_after_first_run =  Ingredient.objects.count()
    call_command("seed_demo",3,3,3)
    count_after_second_run =  Ingredient.objects.count()

    assert count_after_first_run == count_after_second_run
