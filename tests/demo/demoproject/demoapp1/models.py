# -*- coding: utf-8 -*-

from django.db import models


class Monitored1(models.Model):
    sender = models.CharField(max_length=200)


class Monitored2(models.Model):
    sender = models.CharField(max_length=200)


class Monitored3(models.Model):
    sender = models.CharField(max_length=200)
