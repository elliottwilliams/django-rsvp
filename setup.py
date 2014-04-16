import os
from setuptools import setup

setup(
  name = "django-rsvp",
  version = "1.1",
  author = "Daniel Lindsley",
  description = "A simple RSVP app",
  keywords = "rsvp invite django event",
  packages = ['rsvp'],
  install_requires = [
    'django',
  ]
  )