from . import views
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from django.conf.urls import handler404

handler404 = 'login.views.custom_404'

urlpatterns = [
    path('', views.login, name="login"),
    path('homepage/', views.homepage, name= "homepage"),
    path('accounts/', include('allauth.urls')),
    path('logout/', views.logout, name='account_logout'),
    path('view_reports/', views.view_reports, name='view_reports'),
    path('submit_report/', views.submit_report, name='submit_report'),
    path('delete_report/<int:report_id>/', views.delete_report, name='delete_report'),
    path('change_report_status/<int:report_id>/', views.change_report_status, name='change_report_status'),
    path('manage_users/', views.manage_users, name='manage_users'),
    path("start", views.start, name="start"),
    path("play", views.play, name="play"),
    path("leaderboard", views.leaderboard, name="leaderboard"),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/delete/', views.delete_notifications, name='delete_notifications'),
    path("add_categories", views.add_cat, name="add_category"),
    path("add_questions", views.add_question, name = "add_questions"),
    path('end_screen', views.end_screen, name = 'end_screen'),
    path('submit_question_idea/', views.submit_question_idea, name='submit_question_idea'),
    path('change_question_status/<int:question_id>/', views.change_question_status, name='change_question_status'),
    path('delete_q/<int:question_id>/', views.delete_q, name='delete_q'),
    path('delete_c/<int:category_id>/', views.delete_c, name='delete_c'),
    path('manage_q_c', views.manage_q_and_c, name = "manage_q_c"),
    path('game_settings', views.game_settings, name = "game_settings")
]
