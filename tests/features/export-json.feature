@parlex @exporter
Feature: Export JSON from Parler archives
  As a data scientist,
  I want to export the contents of archived social media posts as a series of JSON records,
  So I can do deeper research into the social media datasets.
  
  Scenario: Basic Export
    Given an archive of posts
    Generate a collection of valid JSON containing data from the posts
