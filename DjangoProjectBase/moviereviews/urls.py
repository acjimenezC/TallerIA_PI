
from django.contrib import admin
from django.urls import path, include
from movie import views as movieViews
from movie import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', movieViews.home, name='home'),
    path('about/', movieViews.about, name='about'),
    path('news/', include('news.urls')),
    path('statistics/', movieViews.statistics_view, name='statistics'),
    path('signup/', movieViews.signup, name='signup'),
    path('recommend/', views.recommend_movie, name='recommend_movie'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)