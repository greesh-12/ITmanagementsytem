from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.utils.timezone import now



# Create your models here.
class CustomUser(AbstractUser):
    user_type=models.IntegerField(default=1,null=True)
    status=models.IntegerField(default=0,null=True)

class Department(models.Model):
    dept_name = models.CharField(max_length=100, unique=True)  # Department name
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True)

    def __str__(self):
        return self.name
    
class Registration(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True)
    address=models.CharField(max_length=255)
    course=models.CharField(max_length=200)
    phone=models.CharField(max_length=20,null=True,blank=True)
    profile_image = models.ImageField(upload_to='image/',null=True,blank=True)
    certificate=models.FileField(upload_to='certifications/',validators=[FileExtensionValidator(['pdf','jpg','png'])], null=True)
    department=models.ForeignKey(Department,on_delete=models.CASCADE,null=True)
    team_leader = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='developers', limit_choices_to={'user__user_type': 2})


class Project(models.Model):
    client_name = models.CharField(max_length=200)
    client_email = models.EmailField()
    project_name=models.CharField(max_length=200)
    description=models.TextField(null=True, blank=True)
    requirements=models.TextField(null=True, blank=True)
    start_date=models.DateField(null=True)
    end_date=models.DateField(null=True)
    attachments = models.FileField(upload_to='attachments/', blank=True, null=True)
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True, blank=True)
    team_leader = models.ForeignKey('Registration', on_delete=models.SET_NULL, null=True, blank=True, related_name='led_projects',  limit_choices_to={'user__user_type': 2})
    developers = models.ManyToManyField('Registration',related_name='projects_developed', limit_choices_to={'user__user_type': 3})

    def __str__(self):
        return self.project_name

class ProjectUpdate(models.Model):
    # Defining possible status choices
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
        ('canceled', 'Canceled'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="updates")
    team_leader = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)  # Status for a particular day
    comments = models.TextField()  # Comments for the status update
    update_date = models.DateField(auto_now_add=True)  # The date of the update
    attachment = models.FileField(upload_to='project_updates/', blank=True, null=True)  # File upload for update

    def __str__(self):
        return f"Update for {self.project.project_name} on {self.update_date}"


class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:20]}"
    
class Module(models.Model):
    module_name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="modules")


class Task(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    project = models.ForeignKey(Project,on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[('Assigned', 'Assigned'), ('In Progress', 'In Progress'), ('Completed', 'Completed')])
    assigned_at = models.DateTimeField(auto_now_add=True)
    attachments = models.FileField(upload_to='attachments/', null=True, blank=True)  # Add this field
    progress_update = models.TextField(null=True, blank=True)  # Field to store daily work progress
    updated_at = models.DateTimeField(auto_now=True)
    team_leader_status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'),('In Progress', 'In Progress'),('Completed', 'Completed'),('On Hold', 'On Hold'),],
        default='Pending',
    )  # Team leader's status
    team_leader_comments = models.TextField(null=True, blank=True)  # Optional comments by the team leader

    def __str__(self):
        return f"Task {self.id} - {self.module.module_name}"
    
class TaskProgressHistory(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='progress_history')
    progress_update = models.TextField()  # Detailed work progress
    updated_at = models.DateTimeField(auto_now_add=True)  # Timestamp for this update

    def __str__(self):
        return f"Progress for Task {self.task.id} on {self.updated_at.date()}"
    
class TaskUpdate(models.Model):
    task = models.ForeignKey(Task, related_name='updates', on_delete=models.CASCADE)
    updated_by=models.ForeignKey(CustomUser,on_delete=models.SET_NULL,null=True,blank=True)
    status = models.CharField(max_length=50)
    progress_update = models.TextField(blank=True,null=True)
    attachments = models.FileField(upload_to='task_updates/', blank=True, null=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self):
        return f"Update for {self.task.id} on {self.updated_at.strftime('%Y-%m-%d')}"

   