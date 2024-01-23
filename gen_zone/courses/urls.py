from django.urls import path
from .views import CourseListCreateView, ModuleCreateView, ModuleDetailView, LessonCreateView, LessonDetailView, StepCreateView, StepDetailView, CourseViewSet

urlpatterns = [
    path('courses/', CourseListCreateView.as_view(), name='course-list'),
    path('course/<int:id>/', CourseViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='course-detail'),
    path('course/<int:id>/module/', ModuleCreateView.as_view(), name='module-create'),
    path('course/<int:id>/module/<int:module_num>/', ModuleDetailView.as_view(), name='module-detail'),
    path('course/<int:id>/module/<int:module_num>/lesson/', LessonCreateView.as_view(), name='lesson-create'),
    path('course/<int:id>/module/<int:module_num>/lesson/<int:lesson_num>/', LessonDetailView.as_view(), name='lesson-detail'),
    path('course/<int:id>/module/<int:module_num>/lesson/<int:lesson_num>/step/', StepCreateView.as_view(), name='step-create'),
    path('course/<int:id>/module/<int:module_num>/lesson/<int:lesson_num>/step/<int:step_num>/', StepDetailView.as_view(), name='step-detail'),

    # Using DRF ViewSet for add/remove course actions
    path('course/<int:id>/add_course/', CourseViewSet.as_view({'get': 'add_course'}), name='add-course'),
    path('course/<int:id>/remove_course/', CourseViewSet.as_view({'get': 'remove_course'}), name='remove-course'),
    path('course/<int:id>/add_favorite_course/', CourseViewSet.as_view({'get': 'add_favorite_course'}), name='add-favorite-course'),
    path('course/<int:id>/remove_favorite_course/', CourseViewSet.as_view({'get': 'remove_favorite_course'}),   name='remove-favorite-course'),
    path('course/<int:id>/add_in_progress_course/', CourseViewSet.as_view({'get': 'add_course_in_progress'}), name='add-favorite-course'),
    path('course/<int:id>/remove_in_progress_course/', CourseViewSet.as_view({'get': 'remove_course_in_progress'}),   name='remove-favorite-course'),
]
