from django.urls import path
from .import views

urlpatterns = [
    path('',views.home1,name='home1'),
    path('about',views.about,name='about'),
    path('loginpage',views.loginpage,name='loginpage'),
    path('login_fun',views.login_fun,name='login_fun'),
    path('log_out',views.log_out,name='log_out'),
    path('signuppage',views.signuppage,name='signuppage'),
    path('signup_fun',views.signup_fun,name='signup_fun'),


    #developerside
    path('devp_home',views.devp_home,name='devp_home'),
    path('devp_notification',views.devp_notification,name='devp_notification'),
    path('devp_profile',views.devp_profile,name='devp_profile'),
    path('devp_profile_edit',views.devp_profile_edit,name='devp_profile_edit'),
    path('devp_resetpswd',views.devp_resetpswd,name='devp_resetpswd'),
    path('devp_reset_pswd_fun',views.devp_reset_pswd_fun,name='devp_reset_pswd_fun'),
    path('update_task/<int:task_id>/',views.update_task,name='update_task'),
    path('devp_progress',views.devp_progress,name='devp_progress'),
    path('devp_task',views.devp_task,name='devp_task'),


    #teamleaderside
    path('tl_home',views.tl_home,name='tl_home'),
    path('tl_projectdetails',views.tl_projectdetails,name='tl_projectdetails'),
    path('tl_updated_details',views.tl_updated_details,name='tl_updated_details'),
    path('tl_updates/<int:project_id>/', views.tl_updates, name='tl_updates'),
    path('tl_daily_progress/<int:project_id>',views.tl_daily_progress,name='tl_daily_progress'),
    path('tl_dailyupdates/<int:task_id>/', views.tl_dailyupdates, name='tl_dailyupdates'),
    # path('tl_updates_func/<int:task_id>/', views.tl_updates_func, name='tl_updates_func'),
    path('tl_notification',views.tl_notification,name='tl_notification'),
    path('tl_taskassign',views.tl_taskassign,name='tl_taskassign'),
    path('tl_status',views.tl_status,name='tl_status'),
    path('tl_profile',views.tl_profile,name='tl_profile'),
    path('edit-profile', views.edit_profile, name='edit_profile'),
    path('reset_pswd',views.reset_pswd,name='reset_pswd'),
    path('reset_pswd_fun',views.reset_pswd_fun,name='reset_pswd_fun'),



    #adminside
    path('admin_home',views.admin_home,name='admin_home'),
    path('admin_tltask_status',views.admin_tltask_status,name='admin_tltask_status'),
    path('admintl_daily_progress/<int:project_id>', views.admintl_daily_progress, name='admintl_daily_progress'),
    path('admin_devptask_status',views.admin_devptask_status,name='admin_devptask_status'),
    path('admindevp_daily-progress/<int:developer_id>/<int:project_id>/', views.admindevp_daily_progress, name='admindevp_daily_progress'),
    path('admin_department',views.admin_department,name='admin_department'),
    path('dept_add',views.dept_add,name='dept_add'),
    path('admin_add_proj',views.admin_add_proj,name='admin_add_proj'),
    path('add_project',views.add_project,name='add_project'),
    path('project_details',views.project_details,name='project_details'),
    path('edit_project/<int:project_id>/',views.edit_project, name='edit_project'),
    path('delete_project/<int:id>',views.delete_project,name='delete_project'),
    path('admin_taskassign',views.admin_taskassign,name='admin_taskassign'),
    path('admin_approval',views.admin_approval,name='admin_approval'),
    path('approve/<int:k>',views.approve,name='approve'),
    path('disapprove/<int:k>',views.disapprove,name='disapprove'),
    path('admintl_details',views.admintl_details,name='admintl_details'),
    path('admindevp_details',views.admindevp_details,name='admindevp_details'),
    path('admin_prev_team',views.admin_prev_team,name='admin_prev_team'),
    path('admin_add_devp',views.admin_add_devp,name='admin_add_devp'),
    path('admin_signup_fun',views.admin_signup_fun,name='admin_signup_fun'),
    path('delete_devp/<int:id>',views.delete_devp,name='delete_devp'),
    path('admindevp_profile/<int:id>',views.admindevp_profile,name='admindevp_profile'),
    path('promote_to_teamleader/<int:user_id>/', views.promote_to_teamleader, name='promote_to_teamleader'),
    path('admintl_profile/<int:id>',views.admintl_profile,name='admintl_profile'),
    path('promote_to_developer/<int:id>/', views.promote_to_developer, name='promote_to_developer'),
    path('admin_assignteam/<int:id>/', views.admin_assignteam, name='admin_assignteam'),
]