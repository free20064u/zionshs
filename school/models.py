from django.db import models

class Facility(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='facilities/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Facilities"

class NewsItem(models.Model):
    title = models.CharField(max_length=200)
    summary = models.TextField()
    pub_date = models.DateField()
    image = models.ImageField(upload_to='news/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-pub_date', '-created_at'] # Order by newest first
        verbose_name_plural = "News Items"

class Subject(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Programme(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    subjects = models.ManyToManyField(Subject, related_name='programmes')
    order = models.PositiveIntegerField(default=0, help_text="Order in which this programme appears on the website.")

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['order', 'title']