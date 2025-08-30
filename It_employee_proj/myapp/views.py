from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate,login
from django.contrib.auth.models import auth
from django.contrib import messages
import os,re,datetime
from django.utils.timezone import now
from django.db.models import Q
import random
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.db.models import OuterRef, Subquery
from django.utils.dateparse import parse_date
from datetime import datetime, timedelta
from django.utils import timezone


# Create your views here.
def home1(request):
    return render(request,'home1.html')

def about(request):
    return render(request,'about.html')

def loginpage(request):
    return render(request,'loginpage.html')

def login_fun(request):
    if request.method=='POST':
        usname=request.POST['username']
        passw=request.POST['password']
        user=authenticate(username=usname,password=passw)
        if user is not None:
            if user.user_type == 1:
                login(request,user)
                return redirect('admin_home')
            elif user.user_type == 2:
                auth.login(request,user)
                return redirect('tl_home')
            elif user.user_type == 3:
                auth.login(request,user)
                return redirect('devp_home')
        else:
            messages.info(request,"Invalid username or password...")
            return redirect('loginpage')
def log_out(request):
    auth.logout(request)
    return redirect('home1')


def signuppage(request):
    d=Department.objects.all()
    return render(request,'signuppage.html',{'department':d})

def signup_fun(request):
    if request.method=='POST':
        fname=request.POST['fname']
        lname=request.POST['lname']
        uname=request.POST['uname']
        phone=request.POST['phone']
        email=request.POST['email']
        image=request.FILES.get('img')
        address=request.POST['address']
        course=request.POST['course']
        certificate=request.FILES.get('certification')
        dept=request.POST['department']
        us=request.POST['devp']
        d1=Department.objects.get(id=dept)
        if CustomUser.objects.filter(username=uname).exists():
            messages.error(request,'Username already exist')
            return redirect('signuppage')
        

        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if CustomUser.objects.filter(email=email).exists():
             messages.error(request,'email already exists')
             return redirect('signuppage')
        if not re.match(email_pattern, email):
            messages.error(request, 'Invalid email format.')
            return redirect('signuppage') 
        
        phone_pattern = r'^\d{10}$'
        if not re.match(phone_pattern, phone):
            messages.error(request, 'Phone number must be a 10-digit number.')
            return redirect('signuppage')

        else:
            user=CustomUser.objects.create_user(first_name=fname,last_name=lname,username=uname,email=email,user_type=us)
            user.save()
            reg=Registration(phone=phone,profile_image=image,address=address,course=course,certificate=certificate,department=d1,user=user)
            reg.save()
            subject='Regsitration confirmation'
            message='Registration is success ,please wait for admin approval...'
            send_mail(subject,"Hello "+uname+' '+message,settings.EMAIL_HOST_USER,{email})
            messages.success(request,'User registration success.Please wait for admin approval..')
            return redirect('signuppage')

@login_required(login_url='loginpage')
def devp_home(request):
    # Fetch notifications for the logged-in user
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')

    # Count unread notifications
    unread_count = notifications.filter(is_read=False).count()
    return render(request,'devp_home.html',{'unread_count':unread_count})

def devp_profile(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to edit your profile.")
        return redirect('loginpage')
    reg=Registration.objects.get(user=request.user)
    return render(request,'devp_profile.html',{'reg':reg})

def devp_profile_edit(request):
    if request.method == 'POST':
        user = request.user
        reg = Registration.objects.get(user=user)

        # Fetch form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('u_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        address = request.POST.get('address')
        course = request.POST.get('course')
        new_image=request.FILES.get('img')

        # Validation for username
        if username != user.username and CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Please choose another.")
            return redirect('devp_profile')  # Reload profile page with error message
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if CustomUser.objects.filter(email=email).exclude(id=user.id).exists():
            messages.error(request, "Email is already registered. Please use another.")
            return redirect('devp_profile')
        if not re.match(email_pattern, email):
            messages.error(request, 'Invalid email format.')
            return redirect('devp_profile')
        
        phone_pattern = r'^\d{10}$'
        if not re.match(phone_pattern, phone):
            messages.error(request, 'Phone number must be a 10-digit number.')
            return redirect('devp_profile')
        
        if new_image:
            if reg.profile_image:
                os.remove(reg.profile_image.path)
            reg.profile_image=new_image
        
        # Save user details
        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.email = email
        user.save()

        # Save additional registration details
        reg.phone = phone
        reg.address = address
        reg.course = course
        reg.save()

        messages.success(request, "Profile updated successfully!")
        return redirect('devp_profile')  # Redirect to profile page on successful update

    return render(request, 'devp_profile.html')

def devp_resetpswd(request):
    return render(request,'devp_resetpswd.html')

def devp_reset_pswd_fun(request):
    if request.method == 'POST':
        current_password = request.POST['currentpass']
        pas = request.POST['newpass']
        cpas = request.POST['confirmpass']

        if not request.user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
            return redirect('devp_resetpswd')
        
        if pas == cpas:
            if len(pas) < 8 or not any(char.isupper() for char in pas) \
                or not any(char.isdigit() for char in pas) \
                or not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?/~' for char in pas):
                messages.error(request, 'Password must be at least 8 characters long and contain at least one uppercase letter, one digit, and one special character.')
                return redirect('devp_resetpswd')
            else:
                usr = request.user.id
                tsr = CustomUser.objects.get(id=usr)
                tsr.set_password(pas)  
                tsr.save()
                messages.success(request, 'Password reset successfully.')
                return redirect('devp_home')
        else:
            messages.error(request, 'Passwords do not match.')
            return redirect('devp_resetpswd')

@login_required(login_url='loginpage')
def devp_notification(request):
    """
    Display notifications for the currently logged-in developer.
    Mark notifications as read when accessed.
    """
    # Fetch all notifications for the logged-in user and order them
    notifications_queryset = Notification.objects.filter(user=request.user).order_by('-created_at')

    # Count unread notifications
    unread_count = notifications_queryset.filter(is_read=False).count()

    # Mark all unread notifications as read
    notifications_queryset.filter(is_read=False).update(is_read=True)

    # Fetch the latest 7 notifications
    notifications = notifications_queryset[:7]

    # Pass notifications and unread_count to the template
    return render(request, 'devp_notification.html', {'notifications': notifications, 'unread_count': unread_count})


@login_required(login_url='loginpage')
def update_task(request, task_id):
    # Get the task object by ID or return a 404 if not found
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        # Log the existing task state
        previous_status = task.status
        previous_progress = task.progress_update
        previous_attachment = task.attachments

        # Update the task fields
        task.status = request.POST.get('status', task.status)
        task.progress_update = request.POST.get('progress_update', task.progress_update)

        # If a file is uploaded, save it as the new attachment
        if request.FILES.get('attachments'):
            task.attachments = request.FILES['attachments']

        # Save the updated task
        task.save()

        # Log the update
        TaskUpdate.objects.create(
            task=task,
            updated_by=request.user if request.user.is_authenticated else None,
            status=task.status,
            progress_update=task.progress_update,
            attachments=task.attachments if previous_attachment != task.attachments else None,
        )

        # Redirect to the task detail page or a confirmation page
        return redirect('devp_task')

    # Render the template with the current task object
    return render(request, 'update_task.html', {'task': task})

def devp_progress(request):
    # Get the logged-in user (developer)
    developer = request.user

    # Fetch all projects assigned to this developer
    assigned_projects = Project.objects.filter(task__user=developer).distinct()

    # Get the project_name and updated_at parameters from the request
    project_name = request.GET.get('project_name', None)
    updated_at_str = request.GET.get('updated_at', None)

    # Parse the updated_at date if provided
    if updated_at_str:
        try:
            updated_at_date = datetime.strptime(updated_at_str, '%Y-%m-%d').date()
        except ValueError:
            updated_at_date = None
    else:
        # Default to today's date if no date is provided
        updated_at_date = datetime.today().date()

    # Fetch all task updates and filter by the selected project and updated_at date
    updates = (
        TaskUpdate.objects
        .select_related('task', 'task__project')
        .filter(task__project__in=assigned_projects)  # Filter by assigned projects
        .order_by('task__project', '-updated_at')  # Sort by project and update time
    )

    if project_name:
        updates = updates.filter(task__project__project_name=project_name)

    if updated_at_date:
        # Filter by updated_at date range (start of the day to end of the day)
        start_of_day = datetime.combine(updated_at_date, datetime.min.time())  # Start of the date
        end_of_day = start_of_day + timedelta(days=1)  # End of the date
        
        updates = updates.filter(updated_at__gte=start_of_day, updated_at__lt=end_of_day)

    # Group updates by project and then by updated_at
    progress_history = {}
    for update in updates:
        project = update.task.project
        if project not in progress_history:
            progress_history[project] = {}

        update_date = update.updated_at
        if update_date not in progress_history[project]:
            progress_history[project][update_date] = []

        progress_history[project][update_date].append(update)

    # Render the daily progress history page
    return render(request, 'devp_progress.html', {
        'progress_history': progress_history,
        'projects': assigned_projects,  # Pass assigned projects for the dropdown
        'selected_project_name': project_name,  # To preselect in the dropdown
        'selected_updated_at': updated_at_str or updated_at_date.strftime('%Y-%m-%d'),  # Pre-select today's date if no date provided
    })
    

def devp_task(request):
    try:
        # Ensure the logged-in user is a developer
        if request.user.user_type != 3:  # Assuming 3 is the user type for developers
            messages.error(request, "You are not authorized to access this page.")
            return redirect('home1')  # Redirect to a safe page

        # Fetch all tasks assigned to the developer
        tasks = Task.objects.filter(user=request.user).select_related('project', 'module')

        # Get all projects associated with the developer's tasks for the dropdown
        all_projects = tasks.values_list('project', flat=True).distinct()
        project_list = Project.objects.filter(id__in=all_projects)

        # Get the selected project from GET request
        selected_project_id = request.GET.get('project', '').strip()

        if selected_project_id and selected_project_id != 'all':
            tasks = tasks.filter(project_id=selected_project_id)

        # Debugging: Check if tasks are being fetched
        if not tasks.exists():
            messages.info(request, "No tasks have been assigned to you yet.")
        else:
            # Debugging: Log fetched tasks (only for development/debugging purposes)
            for task in tasks:
                print(f"Task ID: {task.id}, Project: {task.project.project_name}, Module: {task.module.module_name}")

        # Render the tasks in the developer panel
        return render(request, 'devp_task.html', {
            'tasks': tasks,
            'projects': project_list,  # For dropdown
            'selected_project_id': selected_project_id  # Keep the selected project
        })

    except Exception as e:
        # Handle exceptions and log errors
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('devp_home')


   

@login_required(login_url='loginpage')
def tl_home(request):
    # Fetch notifications for the logged-in user
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')

    # Count unread notifications
    unread_count = notifications.filter(is_read=False).count()
    return render(request,'tl_home.html',{'unread_count':unread_count})


def tl_projectdetails(request):
    try:
        # Ensure the logged-in user is a Team Leader
        if request.user.user_type != 2:
            messages.error(request, "You are not authorized to access this page.")
            return redirect('home1')

        # Fetch the Registration object for the logged-in user
        team_leader = Registration.objects.filter(user=request.user).first()
        if not team_leader:
            messages.error(request, "You do not have a valid registration record.")
            return redirect('home1')

        # Fetch projects assigned to the Team Leader
        projects = Project.objects.filter(team_leader=team_leader)

        # Get the project name filter value from GET request
        selected_project = request.GET.get('project_name', '').strip()
        if selected_project and selected_project != 'all':
            projects = projects.filter(project_name=selected_project)

        # Fetch tasks for each project assigned to the logged-in user
        tasks = Task.objects.filter(project__in=projects, user=request.user)

        return render(
            request, 
            'tl_projectdetails.html', 
            {
                'projects': projects,
                'tasks': tasks,
                'all_projects': Project.objects.filter(team_leader=team_leader),  # For dropdown options
                'selected_project': selected_project
            }
        )

    except Exception as e:
        messages.error(request, f"An error occurred: {e}")
        return redirect('home1')

def tl_updated_details(request):
    try:
        # Ensure the user is a team leader
        if request.user.user_type != 2:
            messages.error(request, "You are not authorized to access this page.")
            return redirect('home1')

        # Fetch the Registration object for the logged-in team leader
        team_leader = Registration.objects.filter(user=request.user).first()
        if not team_leader:
            messages.error(request, "You do not have a valid registration record.")
            return redirect('home1')

        # Fetch the projects assigned to the logged-in team leader
        all_projects = Project.objects.filter(team_leader=team_leader)

        # Get filters
        daily_filter = request.GET.get('daily', 'all')
        project_filter = request.GET.get('project', 'all')
        today = datetime.today().date()  # Correctly use datetime

        # Filter projects by daily updates if required
        projects = all_projects
        if daily_filter == 'today':
            projects = projects.filter(updates__update_date=today).distinct()

        # Filter by specific project if selected
        if project_filter != 'all':
            projects = projects.filter(id=project_filter)

        # Pass the data to the template
        return render(request, 'tl_updated_details.html', {
            'projects': projects,
            'daily_filter': daily_filter,
            'project_filter': project_filter,
            'all_projects': all_projects,
        })

    except Exception as e:
        messages.error(request, f"An error occurred: {e}")
        return redirect('home1')

    
def tl_daily_progress(request, project_id):
    try:
        # Ensure the user is a team leader
        if request.user.user_type != 2:
            messages.error(request, "You are not authorized to access this page.")
            return redirect('home1')

        # Fetch the Registration object for the logged-in team leader
        team_leader = Registration.objects.filter(user=request.user).first()
        if not team_leader:
            messages.error(request, "You do not have a valid registration record.")
            return redirect('home1')

        # Fetch the project using the project_id and check if it belongs to the logged-in team leader
        project = Project.objects.filter(id=project_id, team_leader=team_leader).first()
        if not project:
            messages.error(request, "You are not authorized to view this project.")
            return redirect('home1')

        # Get the daily filter from the GET request; default to 'today'
        daily_filter = request.GET.get('daily', 'today')
        today = datetime.today().date()  # Get today's date

        # Filter updates based on the daily selection
        if daily_filter == 'today':
            # Filter updates for today
            updates = ProjectUpdate.objects.filter(project=project, update_date=today).order_by('-update_date')
        elif daily_filter == 'custom_date':
            # If a custom date is provided, filter for that date
            date_filter = request.GET.get('date', '')
            if date_filter:
                try:
                    date_obj = datetime.strptime(date_filter, '%Y-%m-%d').date()
                    updates = ProjectUpdate.objects.filter(project=project, update_date=date_obj).order_by('-update_date')
                except ValueError:
                    messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
                    return redirect('tl_daily_progress', project_id=project.id)
            else:
                updates = ProjectUpdate.objects.none()  # No updates if no valid date is provided
        else:
            updates = ProjectUpdate.objects.none()  # No updates for invalid filters

        # Pass the data to the template
        return render(request, 'tl_daily_progress.html', {
            'project': project,
            'updates': updates,
            'daily_filter': daily_filter,
            'today': today
        })

    except Exception as e:
        messages.error(request, f"An error occurred: {e}")
        return redirect('home1')


def tl_updates(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        # Get data from the request
        status = request.POST.get('status')
        comments = request.POST.get('comments')
        attachment = request.FILES.get('attachment')  # Get the file from the POST request

        # Ensure the status is valid
        if status not in dict(ProjectUpdate.STATUS_CHOICES).keys():
            messages.error(request, "Invalid status.")
            return redirect('update_project', project_id=project_id)

        # Create and save the ProjectUpdate object
        project_update = ProjectUpdate(
            project=project,
            team_leader=request.user if request.user.is_authenticated else None,  # Assuming the logged-in user is the team leader
            status=status,
            comments=comments,
            attachment=attachment
        )
        project_update.save()

        messages.success(request, "Project update saved successfully!")
        return redirect('tl_updated_details')

    # If GET request, display the update form
    return render(request, 'tl_updates.html', {'project': project})
    

def tl_dailyupdates(request, task_id):
    task = Task.objects.get(id=task_id)

    # Get the updated_at filter parameter from the GET request
    updated_at_str = request.GET.get('updated_at', None)

    # If no date filter is applied, default to today's date
    if not updated_at_str:
        today = datetime.now().date()
        updated_at_date = today
    else:
        # Convert the provided date string to a date object
        try:
            updated_at_date = datetime.strptime(updated_at_str, '%Y-%m-%d').date()
        except ValueError:
            updated_at_date = None

    # Fetch task updates and order them by latest first
    task_updates = TaskUpdate.objects.filter(task=task).order_by('-updated_at')

    # If a date filter or default (today's date) is applied, filter by that date
    if updated_at_date:
        # Get the start and end of the selected date
        start_of_day = datetime.combine(updated_at_date, datetime.min.time())
        end_of_day = start_of_day + timedelta(days=1)

        # Filter updates to only include those that fall within the selected date range
        task_updates = task_updates.filter(updated_at__gte=start_of_day, updated_at__lt=end_of_day)

    # Group updates by date
    updates_by_date = {}
    for update in task_updates:
        date_str = update.updated_at.strftime('%Y-%m-%d')  # Extract the date part (no time)
        if date_str not in updates_by_date:
            updates_by_date[date_str] = []
        updates_by_date[date_str].append(update)

    # Sort the dates in descending order
    updates_by_date = dict(sorted(updates_by_date.items(), key=lambda item: item[0], reverse=True))

    # Debugging: Print filtered updates and selected date
    print(f"Filtered updates: {updates_by_date}, Selected date: {updated_at_date}")

    return render(request, 'tl_dailyupdates.html', {
        'task': task,
        'updates_by_date': updates_by_date,
        'selected_updated_at': updated_at_date.strftime('%Y-%m-%d') if updated_at_date else None,
    })


def tl_notification(request):
    user = request.user
    print(f"Logged-in user: {user.id}, user_type: {user.user_type}")

    # Fetch all notifications for the logged-in user and order them
    notifications_queryset = Notification.objects.filter(user=user).order_by('-created_at')

    # Count unread notifications
    unread_count = notifications_queryset.filter(is_read=False).count()

    # Mark all unread notifications as read
    notifications_queryset.filter(is_read=False).update(is_read=True)

    # Fetch the latest 7 notifications
    notifications = notifications_queryset[:7]

    print(f"Unread Notifications for user: {list(notifications_queryset.values('id', 'message', 'is_read', 'created_at')[:7])}")

    # Pass both the unread count and the latest 7 notifications to the template
    return render(request, 'tl_notification.html', {
        'notifications': notifications,
        'unread_count': unread_count,
    })




def tl_taskassign(request):
    # Ensure the logged-in user is a team leader
    if not request.user.is_authenticated or request.user.user_type != 2:
        messages.error(request, "You are not authorized to assign tasks.")
        return redirect('home')  # Or any appropriate redirection

    # Fetch the team leader object for the logged-in user
    team_leader = get_object_or_404(Registration, user=request.user)

    if request.method == 'POST':
        # Get data from the form
        project_id = request.POST.get('project_id')  # Selected project
        developer_id = request.POST.get('developer_id')  # Selected developer
        module_name = request.POST.get('module_name')  # Manually entered module name
        module_description = request.POST.get('module_description')  # Manually entered module description

        # Validate and process the data
        try:
            # Fetch the selected project
            project = get_object_or_404(Project, id=project_id, team_leader=team_leader)

            # Ensure that the developer belongs to the current team leader
            developer = get_object_or_404(Registration, id=developer_id, team_leader=team_leader)

            # Create a module for the selected project
            module = Module.objects.create(
                module_name=module_name,
                description=module_description,
                project=project
            )

            # Assign the module to the developer as a task
            task = Task.objects.create(
                user=developer.user,
                project=project,
                module=module,
                status='Assigned'
            )

            # Create a notification for the developer
            Notification.objects.create(
                user=developer.user,
                message=f"You have been assigned to module '{module.module_name}' of project '{project.project_name}'."
            )

            # Success message
            messages.success(
                request,
                f"Module '{module.module_name}' has been successfully assigned to {developer.user.first_name} {developer.user.last_name}."
            )

        except Exception as e:
            # Handle any unexpected errors
            messages.error(request, f"An error occurred: {str(e)}")

        # Redirect back to the team leader's task assignment page
        return redirect('tl_taskassign')

    # Fetch projects associated with the team leader
    projects = Project.objects.filter(team_leader=team_leader)

    # Fetch developers under the current team leader
    developers = Registration.objects.filter(team_leader=team_leader, user__user_type=3)

    # Render the task assignment page
    return render(request, 'tl_taskassign.html', {'projects': projects, 'developers': developers})

def tl_status(request):
    # Ensure the logged-in user is a Team Leader
    if request.user.user_type != 2:  # Assuming 2 is the user type for Team Leaders
        messages.error(request, "You are not authorized to access this page.")
        return redirect('home1')  # Redirect to a safe page

    # Fetch the Team Leader's registration record
    team_leader = Registration.objects.filter(user=request.user).first()
    if not team_leader:
        messages.error(request, "You do not have a valid registration record.")
        return redirect('home1')

    # Fetch projects assigned to the Team Leader
    projects = Project.objects.filter(team_leader=team_leader)

    # Get all tasks related to the projects assigned to the Team Leader
    project_ids = projects.values_list('id', flat=True)
    tasks = Task.objects.filter(project_id__in=project_ids).select_related('user', 'project', 'module')

    # Get unique developers assigned to the Team Leader's projects
    developers = tasks.values('user__id', 'user__first_name', 'user__last_name').distinct()

    # Filtering logic
    project_filter = request.GET.get('project', '')
    developer_filter = request.GET.get('developer', '')

    if project_filter:
        tasks = tasks.filter(project__project_name__icontains=project_filter)
    if developer_filter.isdigit():  # Ensure developer_filter is numeric before applying
        tasks = tasks.filter(user__id=developer_filter)

    # Render the tasks in the template
    return render(request, 'tl_status.html', {
        'tasks': tasks,
        'projects': projects,
        'developers': developers,
        'project_filter': project_filter,
        'developer_filter': developer_filter,
    })


def tl_profile(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to edit your profile.")
        return redirect('loginpage')
    reg=Registration.objects.get(user=request.user)
    return render(request,'tl_profile.html',{'reg':reg})

def edit_profile(request):
    if request.method == 'POST':
        user = request.user
        reg = Registration.objects.get(user=user)

        # Fetch form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('u_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        address = request.POST.get('address')
        course = request.POST.get('course')
        new_image=request.FILES.get('img')

        # Validation for username
        if username != user.username and CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Please choose another.")
            return redirect('tl_profile')  # Reload profile page with error message
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if CustomUser.objects.filter(email=email).exclude(id=user.id).exists():
            messages.error(request, "Email is already registered. Please use another.")
            return redirect('tl_profile')
        if not re.match(email_pattern, email):
            messages.error(request, 'Invalid email format.')
            return redirect('tl_profile')
        
        phone_pattern = r'^\d{10}$'
        if not re.match(phone_pattern, phone):
            messages.error(request, 'Phone number must be a 10-digit number.')
            return redirect('tl_profile')
        
        if new_image:
            if reg.profile_image:
                os.remove(reg.profile_image.path)
            reg.profile_image=new_image
        # Save user details
        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.email = email
        user.save()

        # Save additional registration details
        reg.phone = phone
        reg.address = address
        reg.course = course
        reg.save()

        messages.success(request, "Profile updated successfully!")
        return redirect('tl_profile')  # Redirect to profile page on successful update

    return render(request, 'tl_profile.html')

def reset_pswd(request):
    return render(request,'reset_pswd.html')

def reset_pswd_fun(request):
    if request.method == 'POST':
        current_password = request.POST['currentpass']
        pas = request.POST['newpass']
        cpas = request.POST['confirmpass']

        if not request.user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
            return redirect('reset_pswd')
        
        if pas == cpas:
            if len(pas) < 8 or not any(char.isupper() for char in pas) \
                or not any(char.isdigit() for char in pas) \
                or not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?/~' for char in pas):
                messages.error(request, 'Password must be at least 8 characters long and contain at least one uppercase letter, one digit, and one special character.')
                return redirect('reset_pswd')
            else:
                usr = request.user.id
                tsr = CustomUser.objects.get(id=usr)
                tsr.set_password(pas)  
                tsr.save()
                messages.success(request, 'Password reset successfully.')
                return redirect('tl_profile')
        else:
            messages.error(request, 'Passwords do not match.')
            return redirect('reset_pswd')

@login_required(login_url='loginpage')
def admin_home(request):
    a=CustomUser.objects.filter(status='0').count()
    pending=a-1
    return render(request,'admin_home.html',{'pend':pending})

def admin_tltask_status(request):
    # Get all team leaders for the filter dropdown
    team_leaders = Registration.objects.filter(user__user_type=2)

    # Get all projects for the filter dropdown
    projects = Project.objects.all()

    # Get filters from request GET
    team_leader_id = request.GET.get('team_leader', None)
    project_id = request.GET.get('project', None)

    # Apply filters based on the selected team leader and project
    team_leader_status = []

    # Filter by team leader if available
    if team_leader_id:
        team_leaders = team_leaders.filter(id=team_leader_id)
        projects = projects.filter(team_leader__id=team_leader_id)  # Only show projects for the selected team leader

    # Filter projects by the selected project_id if available
    if project_id:
        projects = projects.filter(id=project_id)
        # If a specific project is selected, only show its team leader
        team_leaders = team_leaders.filter(id__in=projects.values_list('team_leader', flat=True))

    # Loop through each team leader and get their assigned projects
    for leader in team_leaders:
        # Filter projects assigned to the team leader
        projects_assigned = projects.filter(team_leader=leader)
        project_details = []

        for project in projects_assigned:
            # Get the latest project update
            last_update = project.updates.last()  # Get the latest update for the project
            
            

            project_details.append({
                'project_name': project.project_name,
                'description': project.description,
                'status': last_update.status if last_update else "No Updates",
                'last_updated': last_update.update_date if last_update else "Never",
                'latest_attachment': last_update.attachment if last_update else "no updates",  # Store the latest attachment
                'id': project.id
            })

        team_leader_status.append({
            'team_leader': leader,
            'projects': project_details,
        })

    return render(request, 'admin_tltask_status.html', {
        'team_leader_status': team_leader_status,
        'team_leaders': team_leaders,    
        'projects': projects,
        'selected_team_leader': team_leader_id,
        'selected_project': project_id,
    })



def admintl_daily_progress(request, project_id):
    try:
        # Ensure the user is an admin
        if request.user.user_type != 1:  # Assuming user_type 1 represents admin
            messages.error(request, "You are not authorized to access this page.")
            return redirect('home1')

        # Fetch the project using the project_id
        project = get_object_or_404(Project, id=project_id)
        
        # Get the daily filter from the GET request
        daily_filter = request.GET.get('daily', 'today')  # Default to "today"
        today = datetime.today().date()

        # Filter updates based on the selected filter
        if daily_filter == 'custom_date':
            # If a custom date is provided, filter for that date
            date_filter = request.GET.get('date', '')
            if date_filter:
                try:
                    date_obj = datetime.strptime(date_filter, '%Y-%m-%d').date()
                    updates = ProjectUpdate.objects.filter(project=project, update_date=date_obj).order_by('-update_date')
                except ValueError:
                    messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
                    return redirect('admintl_daily_progress', project_id=project.id)
            else:
                # messages.error(request, "Please provide a valid date.")
                updates = ProjectUpdate.objects.none()  # No updates
        else:  # Default to today's updates
            updates = ProjectUpdate.objects.filter(project=project, update_date=today).order_by('-update_date')

        # Pass the data to the template
        return render(request, 'admintl_daily_progress.html', {
            'project': project,
            'updates': updates,
            'daily_filter': daily_filter,
            'selected_date': today if daily_filter == 'today' else '',  # Pass selected date for custom date
        })

    except Exception as e:
        messages.error(request, f"An error occurred: {e}")
        return redirect('home1')


def admin_devptask_status(request):
    selected_team_leader_id = request.GET.get('team_leader', None)
    selected_project_id = request.GET.get('project', None)
    selected_developer_id = request.GET.get('developer', None)
    tasks_by_team_leader = {}

    # Fetch all team leaders, projects, and developers for filters
    team_leaders = Registration.objects.filter(user__user_type=2)
    projects = Project.objects.all()
    developers = CustomUser.objects.filter(user_type=3)

    # Base task queryset
    tasks = Task.objects.select_related('user', 'project', 'module')

    if selected_team_leader_id:
        try:
            team_leader = CustomUser.objects.get(id=selected_team_leader_id, user_type=2)
            team_leader_registration = Registration.objects.get(user=team_leader)
            tasks = tasks.filter(user__in=team_leader_registration.developers.values_list('user', flat=True))
        except (ValueError, CustomUser.DoesNotExist, Registration.DoesNotExist):
            raise Http404("Invalid team leader selected.")

    if selected_project_id:
        try:
            selected_project = Project.objects.get(id=selected_project_id)
            tasks = tasks.filter(project=selected_project)
        except Project.DoesNotExist:
            raise Http404("Invalid project selected.")

    if selected_developer_id:
        try:
            selected_developer = CustomUser.objects.get(id=selected_developer_id, user_type=3)
            tasks = tasks.filter(user=selected_developer)
        except CustomUser.DoesNotExist:
            raise Http404("Invalid developer selected.")

    # Group tasks by team leader
    for team_leader in team_leaders:
        team_tasks = tasks.filter(
            user__in=team_leader.developers.values_list('user', flat=True)
        )
        if team_tasks.exists():
            tasks_by_team_leader[team_leader.user.username] = {
                'developers': [task for task in team_tasks if task.user.user_type == 3],
            }

    return render(request, 'admin_devptask_status.html', {
        'tasks_by_team_leader': tasks_by_team_leader,
        'team_leaders': team_leaders,
        'projects': projects,
        'developers': developers,
        'selected_team_leader_id': selected_team_leader_id,
        'selected_project_id': selected_project_id,
        'selected_developer_id': selected_developer_id,
    })



def admindevp_daily_progress(request, developer_id, project_id):
    # Get the developer (CustomUser)
    developer = get_object_or_404(CustomUser, id=developer_id)

    # Get the specific project
    project = get_object_or_404(Project, id=project_id)

    # Get the specific date to filter updates by (defaults to today if not provided)
    filter_date_str = request.GET.get('date', None)
    if filter_date_str:
        try:
            filter_date = datetime.strptime(filter_date_str, '%Y-%m-%d').date()
        except ValueError:
            filter_date = None  # Invalid date format; will skip filtering
    else:
        filter_date = datetime.today().date()  # Default to today's date if no date filter is provided

    # Fetch tasks assigned to this developer for the specific project
    tasks = Task.objects.filter(user=developer, project=project)

    # Initialize task_updates dictionary to store updates for each task
    task_updates = {}

    # Populate the task_updates dictionary with updates for each task
    for task in tasks:
        updates = TaskUpdate.objects.filter(task=task).order_by('-updated_at')

        # Filter updates by the selected date (if applicable)
        if filter_date:
            start_of_day = datetime.combine(filter_date, datetime.min.time())  # Start of the selected date
            end_of_day = datetime.combine(filter_date, datetime.max.time())  # End of the selected date
            updates = updates.filter(updated_at__gte=start_of_day, updated_at__lte=end_of_day)

        if updates.exists():
            task_updates[task] = {
                'project': project,  # Pass the project along with the task
                'updates': updates,
            }

    return render(request, 'admindevp_daily_progress.html', {
        'developer': developer,
        'project': project,
        'task_updates': task_updates,
        'filter_date': filter_date  # Pass the selected filter date to the template
    })

    

@login_required(login_url='loginpage')
def admin_department(request):
    return render(request,'admin_department.html')

@login_required(login_url='loginpage')
def dept_add(request):
    if request.method=='POST':
        department_name=request.POST['department']
        dept=Department(dept_name=department_name)
        dept.save()
        messages.info(request,'Department Added Successfully')
        return redirect('admin_department')

@login_required(login_url='loginpage')
def admin_add_proj(request):
    return render(request,'admin_add_proj.html')
def add_project(request):
    if request.method == "POST":
        client_name = request.POST.get("client_name")
        client_email = request.POST.get("client_email")
        project_name=request.POST.get("project_name")
        project_description = request.POST.get("description")
        requirements = request.POST.get("requirements")
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        attachments = request.FILES.get("attachments")

        # Save the project to the database
        Project.objects.create(client_name=client_name,client_email=client_email,project_name=project_name,description=project_description,
                                   requirements=requirements,start_date=start_date,end_date=end_date, attachments=attachments)

        messages.success(request, "Project added successfully.")
        return redirect("admin_add_proj")

    return render(request, "admin_add_proj.html")

@login_required(login_url='loginpage')
def project_details(request):
    projects = Project.objects.all()  # Fetch all projects
    return render(request, 'project_details.html', {'projects': projects})

def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == "POST":
        project.client_name = request.POST.get("client_name")
        project.client_email = request.POST.get("client_email")
        project.project_name = request.POST.get("projectname")
        project.description = request.POST.get("description")
        project.requirements = request.POST.get("requirements")
        project.start_date = request.POST.get("start_date")
        project.end_date = request.POST.get("end_date")
        project.attachments = request.FILES.get("attachments", project.attachments)
        project.save()
        return redirect("project_details")  # Redirect to the project list or desired page.

    return render(request, "edit_project.html", {"project": project})

def delete_project(request,id):
    proj=Project.objects.get(id=id)
    proj.delete()
    return redirect('project_details')

@login_required(login_url='loginpage')
def admin_taskassign(request):
    if request.method == 'POST':
        project_id = request.POST.get('project')
        team_leader_id = request.POST.get('team_lead')

        try:
            project = Project.objects.get(id=project_id)
            team_leader = Registration.objects.get(id=team_leader_id)

            project.team_leader = team_leader
            project.save()

            # Send notification
            Notification.objects.create(
                user=team_leader.user,  # Ensure this references a CustomUser instance
                message=f"You have been assigned to the project: {project.project_name}"
            )

            print(f"Notification created for user ID: {team_leader.user.id}")
            messages.success(request, 'Task assigned and notification sent.')
            return redirect('admin_taskassign')
        except Project.DoesNotExist:
            messages.error(request, 'Project not found.')
        except Registration.DoesNotExist:
            messages.error(request, 'Team leader not found.')
        except Exception as e:
            print(f"Error: {e}")
            messages.error(request, f"Unexpected error: {str(e)}")

    projects = Project.objects.all()
    team_leads = Registration.objects.filter(user__user_type=2)  # Filter team leaders
    return render(request, 'admin_taskassign.html', {'projects': projects, 'team_leads': team_leads})



@login_required(login_url='loginpage')
def admin_approval(request):
    user=Registration.objects.filter(~Q(user__user_type=1))
    
    return render(request,'admin_approval.html',{'usr':user})

def approve(request,k):
    usr=CustomUser.objects.get(id=k)
    if usr.user_type == 3:
        usr.status='1'
        usr.save()
        passw=CustomUser.objects.get(id=k)
        reg=Registration.objects.get(user=k)
        rpas=str(random.randint(100000,999999))
        passw.set_password(rpas)
        passw.save()
        ru=reg.user.username
        re=reg.user.email
        subject='Admin approval: Developer Account Created'
        message=(
            f"Dear {reg.user.first_name } {reg.user.last_name},\n\n"
            f"Your account has been successfully created and approved by the admin. \n\n"
            f"Login Details:\n"
            f"username:{reg.user.username}\n"
            f"password:{ rpas }\n"
            f"Please log in and change your password immediately.\n\n"
            f"Thank You"
        )
        send_mail(subject,message,settings.EMAIL_HOST_USER,{usr.email})
        messages.info(request,'User approved')
        return redirect('admin_approval')
    
def disapprove(request, k):
    try:
        usr = CustomUser.objects.get(id=k)
    except CustomUser.DoesNotExist:
        messages.error(request, 'User does not exist.')
        return redirect('admin_approval')

    if usr.user_type == 3:
        usr.status = '2'
        usr.save()
        try:
            reg = Registration.objects.get(user=k)
            reg.delete()
        except Registration.DoesNotExist:
            messages.warning(request, 'Registration record not found for the user.')

        try:
            passw = CustomUser.objects.get(id=k)
            passw.delete()
        except CustomUser.DoesNotExist:
            messages.error(request, 'User already deleted.')

        subject = 'Admin Disapproval : Account Disapproved'
        message = (
            f"Dear {usr.first_name} {usr.last_name},\n\n"
            f"We regret to inform you that your account has been disapproved by the Admin.\n"
            f"Thank you!"
        )
        send_mail(subject, message, settings.EMAIL_HOST_USER, [usr.email])
        messages.info(request, 'User Disapproved')
    
    return redirect('admin_approval')

@login_required(login_url='loginpage')
def admintl_details(request):
    # Fetch all users initially
    usr = Registration.objects.all()
    team_leaders = Registration.objects.filter(user__user_type=2)  # Fetch all team leaders

    # Fetch all departments
    departments = Department.objects.all()  # Assuming you have a Department model

    # Apply role-based filtering
    user_type = request.GET.get('user_type')
    if user_type:
        usr = usr.filter(user__user_type=user_type)

    # Apply team leader-based filtering
    team_leader_id = request.GET.get('team_leader')
    if team_leader_id:
        usr = usr.filter(team_leader_id=team_leader_id)

    # Apply department-based filtering
    department_id = request.GET.get('department')
    if department_id:
        usr = usr.filter(department_id=department_id)

    return render(request, 'admintl_details.html', {
        'usr': usr,
        'team_leaders': team_leaders,
        'departments': departments,  # Pass departments to the template
    })


def admindevp_details(request):
    # Fetch all users initially
    usr = Registration.objects.all()
    team_leaders = Registration.objects.filter(user__user_type=2)  # Fetch all team leaders

    # Fetch all departments
    departments = Department.objects.all()  # Assuming you have a Department model

    # Apply role-based filtering
    user_type = request.GET.get('user_type')
    if user_type:
        usr = usr.filter(user__user_type=user_type)

    # Apply team leader-based filtering
    team_leader_id = request.GET.get('team_leader')
    if team_leader_id:
        usr = usr.filter(team_leader_id=team_leader_id)

    # Apply department-based filtering
    department_id = request.GET.get('department')
    if department_id:
        usr = usr.filter(department_id=department_id)

    return render(request, 'admindevp_details.html', {
        'usr': usr,
        'team_leaders': team_leaders,
        'departments': departments,
    })

def admin_prev_team(request):
    usr = Registration.objects.all()
    return render(request,'admin_prev_team.html', {'usr':usr})


def admin_add_devp(request):
    d=Department.objects.all()
    return render(request,'admin_add_devp.html',{'department':d})
def admin_signup_fun(request):
    if request.method == 'POST':
        fname = request.POST['fname']
        lname = request.POST['lname']
        uname = request.POST['uname']
        phone = request.POST['phone']
        email = request.POST['email']
        address = request.POST['address']
        course = request.POST['course']
        certificate = request.FILES.get('certification')
        dept = request.POST['department']
        us = request.POST['devp']
        sts=request.POST['status']

        # Validate Department
        try:
            d1 = Department.objects.get(id=dept)
        except Department.DoesNotExist:
            messages.error(request, 'Invalid department selected.')
            return redirect('admin_add_devp')

        # Check for existing username
        if CustomUser.objects.filter(username=uname).exists():
            messages.error(request, 'Username already exists.')
            return redirect('admin_add_devp')

        # Validate Email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('admin_add_devp')

        if not re.match(email_pattern, email):
            messages.error(request, 'Invalid email format.')
            return redirect('admin_add_devp')
        
        phone_pattern = r'^\d{10}$'
        if not re.match(phone_pattern, phone):
            messages.error(request, 'Phone number must be a 10-digit number.')
            return redirect('admin_add_devp')

        # Create User
        try:
            user = CustomUser.objects.create_user(
                first_name=fname,
                last_name=lname,
                username=uname,
                email=email,
                user_type=us,
                status=sts
            )
            user.save()

            reg = Registration(
                phone=phone,
                address=address,
                course=course,
                certificate=certificate,
                department=d1,
                user=user
            )
            reg.save()
            # Generate random password
            random_password = str(random.randint(100000, 999999))
            user.set_password(random_password)
            user.save()

            # Send Email with Credentials
            subject = 'Admin Approval: Developer Account Created'
            message = (
                    f"Dear {fname} {lname},\n\n"
                    f"Your account has been successfully created and approved by the admin.\n\n"
                    f"Login Details:\n"
                    f"Username: {uname}\n"
                    f"Email: {email}\n"
                    f"Password: {random_password}\n\n"
                    f"Please log in and change your password immediately.\n\n"
                    f"Thank you!"
                )
            send_mail(subject, message, settings.EMAIL_HOST_USER, [email])

            messages.success(request, 'Developer account created and credentials sent to the email.')
            return redirect('admin_add_devp')

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('admin_add_devp')

    return render(request, 'admin_add_devp.html')

def delete_devp(request,id):
    # Retrieve the CustomUser object or return a 404 if not found
    user = get_object_or_404(CustomUser, id=id)

    # Check if the user is approved (status = 1)
    if user.status == 1:
        # Deactivate the user account (soft delete)
        user.is_active = False
        user.status = 2  # Assuming 2 represents deactivated status
        user.save()
    return redirect('admindevp_details')

#admin promote to teamleader
@login_required(login_url='loginpage')
def admindevp_profile(request,id):
    profile=Registration.objects.get(id=id)
    return render(request,'admindevp_profile.html',{'usr':profile})

@user_passes_test(lambda u: u.is_superuser)  # Restrict to admin users
def promote_to_teamleader(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        user.user_type = 2  # Assuming 4 corresponds 2 'Team Leader'
        user.save()
        return redirect('admintl_details')  # Redirect back to the developer details page
    
#admin promote back to developer   
@login_required(login_url='loginpage')
def admintl_profile(request,id):
    profile=Registration.objects.get(id=id)
    return render(request,'admintl_profile.html',{'usr':profile})

@user_passes_test(lambda u: u.is_superuser)  # Restrict to admin users
def promote_to_developer(request, id):
    user = get_object_or_404(CustomUser, id=id)
    if user.user_type != 3:  # Assuming '3' represents a developer role
        user.user_type = 3
        user.save()
    return redirect('admindevp_details')  # Replace 'team_details' with your desired redirect

def admin_assignteam(request, id):
    profile = get_object_or_404(Registration, id=id, user__user_type=3)  # Ensure it's a developer
    
    if request.method == "POST":
        # Get the selected team leader (user with user_type=2)
        team_leader_id = request.POST.get('team_leader')
        if team_leader_id:
            # Fetch the team leader by ID and ensure the user_type is 2 (team leader)
            team_leader = Registration.objects.filter(id=team_leader_id, user__user_type=2).first()
            if team_leader:
                # Assign the developer to the selected team leader
                profile.team_leader = team_leader  # Assuming a team_leader field in Registration
                profile.save()
                messages.success(request, f"Developer {profile.user.username} assigned to Team Leader {team_leader.user.username}.")
                return redirect('admindevp_profile', id=id)  # Redirect back to developer profile page
            else:
                messages.error(request, "Invalid team leader selection.")
        else:
            messages.error(request, "Please select a team leader.")

    # Fetch available team leaders (user_type=2 for team leaders)
    team_leaders = Registration.objects.filter(user__user_type=2)

    return render(request, 'admin_assignteam.html', {
        'usr': profile,
        'team_leaders': team_leaders,
    })