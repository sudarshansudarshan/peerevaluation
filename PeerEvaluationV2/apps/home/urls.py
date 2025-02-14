
from django.urls import path, re_path
from apps.home import views


urlpatterns = [
    path('', views.index, name='home'),
    path('add_course', views.course, name='add_course'),
    path('add_batch', views.batch, name='add_batch'),
    path('download_csv', views.download_answer_sheets, name='download_csv'),
    path('enrollment', views.enrollment, name='enrollment'),
    path('ta_hub/', views.ta_hub, name='ta_hub'),
    path('examination/', views.examination, name='examination'),
    path('student_eval', views.student_eval, name='student_eval'),
    path('peer_eval/', views.peer_evaluation, name='peer_eval'), # Send students for peer evaluation
    path('upload-evaluation/', views.upload_evaluation, name="upload_evaluation"),
    path('download_csv/<int:exam_id>', views.export_evaluations_to_csv, name='download_csv'),
    path('associateTopic/', views.topic, name='associateTopic'),
    path('llm_answer/', views.llm_answer, name='llm_answer'),
    path('documentation', views.documentation, name='llm_eval'),
    path('change-password/', views.change_password, name='change_password'),
    path('remove-ta/', views.remove_ta, name='remove_ta'),
    path('download_online_eval/', views.download_online_eval, name='download_online_eval'),
    path('bulk_register_users/', views.bulk_register_users, name='bulk_register_users'),
    re_path(r'^.*\.*', views.pages, name='pages'),
]
