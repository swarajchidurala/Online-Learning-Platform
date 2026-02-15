from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('mainpage/', views.mainpage, name='mainpage'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('stdpage/', views.stdpage, name='stdpage'),
    path('parentpage/', views.parentpage, name='parentpage'),
    path('tchrpage/', views.tchrpage, name='tchrpage'),
    path('hrpage/', views.hrpage, name='hrpage'),
    path('chat_api/', views.chat_api, name='chat_api'),
    path('upload_content/', views.upload_content, name='upload_content'),
    path('send_message/', views.send_message, name='send_message'),
    path('take_test/<int:course_id>/', views.take_test, name='take_test'),
    path('submit_test/<int:course_id>/', views.submit_test, name='submit_test'),
    path('record_activity_api/', views.record_activity_api, name='record_activity_api'),
    path('api/get_messages/', views.get_messages_api, name='get_messages_api'),
    path('api/send_message/', views.send_message_api, name='send_message_api'),
    path('api/delete_message/', views.delete_message_api, name='delete_message_api'),
    path('logout/', views.logout_view, name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)