# coding=utf-8
"""Export JSON from Parler archives feature tests."""

from pytest_bdd import (
    given,
    scenario,
)


@scenario('features/export-json.feature', 'Basic Export')
def test_basic_export():
    """Basic Export."""


@given('Generate a collection of valid JSON containing data from the posts')
def generate_a_collection_of_valid_json_containing_data_from_the_posts():
    """Generate a collection of valid JSON containing data from the posts."""
#    raise NotImplementedError


@given('an archive of posts')
def an_archive_of_posts():
    """an archive of posts."""
#    raise NotImplementedError
