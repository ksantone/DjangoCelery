from django.db import models

class Pipeline(models.Model):
	title = models.CharField(max_length=20)
	inputs = models.CharField(default="", max_length=150)
	outputs = models.CharField(default="", max_length=150)
	algorithms = models.CharField(default="", max_length=200)
