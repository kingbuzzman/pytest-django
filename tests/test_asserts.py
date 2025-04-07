"""
Tests the dynamic loading of all Django assertion cases.
"""

from __future__ import annotations

import inspect
from typing import TYPE_CHECKING

import pytest

import pytest_django
from pytest_django.asserts import __all__ as asserts_all


if TYPE_CHECKING:
    import django.test


def _get_actual_assertions_names() -> list[str]:
    """
    Returns list with names of all assertion helpers in Django.
    """
    from unittest import TestCase as DefaultTestCase

    from django import VERSION
    from django.test import TestCase as DjangoTestCase

    if VERSION >= (5, 0):
        from django.contrib.messages.test import MessagesTestMixin

        class MessagesTestCase(MessagesTestMixin, DjangoTestCase):
            pass

        obj = MessagesTestCase("run")
    else:
        obj = DjangoTestCase("run")

    def is_assert(func) -> bool:
        return func.startswith("assert") and "_" not in func

    base_methods = [
        name for name, member in inspect.getmembers(DefaultTestCase) if is_assert(name)
    ]

    return [
        name
        for name, member in inspect.getmembers(obj)
        if is_assert(name) and name not in base_methods
    ]


def test_django_asserts_available() -> None:
    django_assertions = _get_actual_assertions_names()
    expected_assertions = asserts_all
    assert set(django_assertions) == set(expected_assertions)

    for name in expected_assertions:
        assert hasattr(pytest_django.asserts, name)


@pytest.mark.django_db
def test_sanity() -> None:
    from django.http import HttpResponse

    from pytest_django.asserts import assertContains, assertNumQueries

    response = HttpResponse("My response")

    assertContains(response, "My response")
    with pytest.raises(AssertionError):
        assertContains(response, "Not my response")

    assertNumQueries(0, lambda: 1 + 1)
    with assertNumQueries(0):
        pass

    assert assertContains.__doc__


def test_real_assert(django_testcase: django.test.TestCase) -> None:
    django_testcase.assertEqual("a", "a")  # noqa: PT009

    with pytest.raises(AssertionError):
        django_testcase.assertXMLEqual("a" * 10_000, "a")
