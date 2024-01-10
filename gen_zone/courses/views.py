from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny, IsAuthenticated
from django.http import Http404
from django.shortcuts import get_object_or_404
from .models import Course, Module, Lesson, Step, Content
from .serializers import CourseSerializer, LessonSerializer, ModuleSerializer, StepSerializer, ContentSerializer
from .permissions import IsOwnerOrReadOnly, HasCourse
from rest_framework.pagination import PageNumberPagination
        

class CourseListCreateView(generics.ListCreateAPIView):
    """
    Список всех курсов и создание нового курса:
    для создания курса нужно быть авторизованным
    Ответ:
    - id: Идентификатор курса.
    - title: Название курса.
    - description: Описание курса.
    - owner: Владелец курса.
    - modules: модули -> уроки 
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request):
        """
        Описание: Получает список всех курсов и позволяет создать новый курс.
        Параметры для создания:
        - title (обязательный): Название курса.
        - description (обязательный): Описание курса.
        - owner (автоматически): Владелец курса (текущий аутентифицированный пользователь).
        """
        if request.user.is_authenticated:
            serializer = CourseSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(owner=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Только зарегистрированные пользователи могут создавать курсы"}, status=status.HTTP_401_UNAUTHORIZED)

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    lookup_field = 'id'

    @action(detail=True, methods=['get'])
    def add_course(self, request, id=None):
        course = self.get_object()
        user = request.user

        if course not in user.courses.all():
            user.courses.add(course)
            return Response({"success": f"Course {course.title} added to user {user.email}"},
                            status=status.HTTP_200_OK)
        else:
            return Response({"error": f"User {user.email} already has access to course {course.title}"},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def remove_course(self, request, id=None):
        course = self.get_object()
        user = request.user

        if course in user.courses.all():
            user.courses.remove(course)
            return Response({"success": f"Course {course.title} removed from user {user.email}"},
                            status=status.HTTP_200_OK)
        else:
            return Response({"error": f"User {user.email} does not have access to course {course.title}"},
                            status=status.HTTP_400_BAD_REQUEST)

    def get_course(self, id):
        return get_object_or_404(Course, id=id)

    def get(self, request, id):
        course = self.get_course(id)
        serializer = self.get_serializer(course)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, id):
        course = self.get_course(id)
        self.check_object_permissions(request, course)

        serializer = self.get_serializer(course, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, id):
        course = self.get_course(id)
        self.check_object_permissions(request, course)

        course.delete()

        return Response({"success": "Course successfully deleted"}, status=status.HTTP_204_NO_CONTENT)

class ModuleCreateView(generics.CreateAPIView):
    """
    Создание модуля:

    Описание: Создает новый модуль для указанного курса.
    Параметры:
    - id (в URL): Идентификатор курса.
    - module_title (обязательный): Название модуля.
    - module_description (обязательный): Описание модуля.
    - module_num (автоматически): Номер модуля (автоматически определяется в порядке создания).

    Ответ:
    - id: Идентификатор модуля.
    - module_title: Название модуля.
    - module_description: Описание модуля.
    - module_num: Номер модуля.
    """
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    lookup_url_kwarg = 'id'

    def get_course(self, id):
        try:
            course = Course.objects.get(id=id)
            return course
        except Course.DoesNotExist:
            return None


    def post(self, request, id):
        course = self.get_course(id)

        if course is not None:
            serializer = ModuleSerializer(data=request.data)
            if serializer.is_valid():
                serializer.validated_data['course'] = course
                self.perform_create(serializer)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({"error": "Курс не найден"}, status=status.HTTP_404_NOT_FOUND)


class ModuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Получение, редактирование и удаление модуля:

    Описание: Получает данные, редактирует и удаляет модуль.
    Параметры:
    - id (в URL): Идентификатор курса.
    - module_num (в URL): Номер модуля внутри курса.

    Ответ:
    - id: Идентификатор модуля.
    - module_title: Название модуля.
    - module_description: Описание модуля.
    - module_num: Номер модуля.
    """
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    lookup_url_kwarg = 'id'


    def get_object(self):
        id = self.kwargs.get('id')
        module_num = self.kwargs.get('module_num')
        course = get_object_or_404(Course, id=id)

        module = get_object_or_404(Module, course=course, module_num=module_num)
        self.check_object_permissions(self.request, module)
        return module
        

    def get(self, request, *args, **kwargs):
        module = self.get_object()
        serializer = ModuleSerializer(module)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """
        Параметры:
        - module_title (необязательный): Название модуля.
        - module_description (необязательный): Описание модуля.
        """
        module = self.get_object()
        module_title = request.data.get('module_title', module.module_title)
        module_description = request.data.get('module_description', module.module_description)

        module.module_title = module_title
        module.module_description = module_description
        module.save()

        serializer = ModuleSerializer(module)
        return Response(serializer.data, status=status.HTTP_200_OK)
        

    def destroy(self, request, *args, **kwargs):
        module = self.get_object()
        module_num = kwargs.get('module_num')
        course = get_object_or_404(Course, id=module.course.id)

        module.delete()
        #атомарные транзакции ACID
        modules_to_update = course.modules.filter(module_num__gt=module_num)
        for mod in modules_to_update:
            mod.module_num -= 1
            mod.save()

        return Response({"success": "Модуль успешно удален"}, status=status.HTTP_204_NO_CONTENT)


class LessonCreateView(generics.CreateAPIView):
    """
    Создание урока:

    Описание: Создает новый урок для указанного курса и модуля.
    Параметры:
    - id (в URL): Идентификатор курса.
    - module_num (в URL): Номер модуля.
    - lesson_title (обязательный): Название урока.
    - lesson_description (обязательный): Описание урока.
    - lesson_num (автоматически): Номер урока (автоматически определяется в порядке создания).

    Ответ:
    - id: Идентификатор урока.
    - lesson_title: Название урока.
    - lesson_description: Описание урока.
    - lesson_num: Номер урока.
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    lookup_url_kwarg = 'id'

    def get_course(self, id):
        try:
            course = Course.objects.get(id=id)
            return course
        except Course.DoesNotExist:
            return None
        


    def post(self, request, *args, **kwargs):
        id = kwargs.get('id')
        module_num = kwargs.get('module_num')
        
        try:
            module = Module.objects.get(course__id=id, module_num=module_num)
        except Module.DoesNotExist:
            return Response({"error": "Модуль не найден"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = LessonSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['module'] = module
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LessonDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Получение, редактирование и удаление урока:

    Описание: Получает данные, редактирует и удаляет урок.
    Параметры:
    - id (в URL): Идентификатор курса.
    - module_num (в URL): Номер модуля.
    - lesson_num (в URL): Номер урока.

    Ответ:
    - id: Идентификатор урока.
    - lesson_title: Название урока.
    - lesson_description: Описание урока.
    - lesson_num: Номер урока.
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    lookup_url_kwarg = 'id'


    class StepPagination(PageNumberPagination):
        page_size = 1
        page_size_query_param = 'page_size'
        max_page_size = 1000

    pagination_class = StepPagination

    def get_object(self):
        id = self.kwargs.get('id')
        lesson_num = self.kwargs.get('lesson_num')
        module_num = self.kwargs.get('module_num')

        lesson = get_object_or_404(Lesson, module__course__id=id, module__module_num=module_num, lesson_num=lesson_num)
        return lesson

    def get(self, request, *args, **kwargs):
        lesson = self.get_object()

        # Получаем номер страницы из параметра запроса
        page = self.paginate_queryset(lesson.steps.all())
        serializer = self.get_serializer(lesson)

        # Если номер страницы указан, возвращаем только соответствующий шаг
        if page:
            serialized_data = serializer.data
            serialized_data['steps'] = StepSerializer(page, many=True).data
            return self.get_paginated_response(serialized_data)

        return Response(serializer.data)
    

    def update(self, request, *args, **kwargs):
        lesson = self.get_object()
        self.check_object_permissions(request, lesson)

        lesson_title = request.data.get('lesson_title', lesson.lesson_title)
        lesson_description = request.data.get('lesson_description', lesson.lesson_description)

        lesson.lesson_title = lesson_title
        lesson.lesson_description = lesson_description
        lesson.save()

        serializer = LessonSerializer(lesson)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        try:
            
            lesson = self.get_object()
            module = lesson.module
            lesson.delete()

            lesson_num = kwargs.get('lesson_num')
            lessons_to_update = module.lessons.filter(lesson_num__gt=lesson_num)
            for les in lessons_to_update:
                les.lesson_num -= 1
                les.save()

            return Response({"success": "Урок успешно удален"}, status=status.HTTP_204_NO_CONTENT)

        except Lesson.DoesNotExist:
            return Response({"error": "Урок не найден"}, status=status.HTTP_404_NOT_FOUND)
    

class StepCreateView(generics.CreateAPIView):
    """
    Создание шага:

    Описание: Создает новый шаг для указанного курса, модуля и урока.
    Параметры:
    - id (в URL): Идентификатор курса.
    - module_num (в URL): Номер модуля.
    - lesson_num (в URL): Номер урока.
    - step_title (обязательный): Название шага.
    - step_content (обязательный): Содержание шага.
    - step_num (автоматически): Номер шага (автоматически определяется в порядке создания).

    Ответ:
    - id: Идентификатор шага.
    - step_title: Название шага.
    - step_content: Содержание шага.
    - step_num: Номер шага.
    """
    serializer_class = StepSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def post(self, request, *args, **kwargs):
        id = self.kwargs.get('id')
        module_num = self.kwargs.get('module_num')
        lesson_num = self.kwargs.get('lesson_num')

        lesson = get_object_or_404(Lesson, module__course__id = id, module__module_num=module_num, lesson_num=lesson_num)
        self.check_object_permissions(request, lesson)
        serializer = StepSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['lesson'] = lesson
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class StepDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Получение, редактирование и удаление шага:

    Описание: Получает данные, редактирует и удаляет шаг.
    Параметры:
    - id (в URL): Идентификатор курса.
    - module_num (в URL): Номер модуля.
    - lesson_num (в URL): Номер урока.
    - step_num (в URL): Номер шага.

    Ответ:
    - id: Идентификатор шага.
    - step_title: Название шага.
    - step_content: Содержание шага.
    - step_num: Номер шага.
    """
    serializer_class = StepSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_object(self, request, *args, **kwargs):
        id = self.kwargs.get('id')
        module_num = self.kwargs.get('module_num')
        lesson_num = self.kwargs.get('lesson_num')
        step_num = self.kwargs.get('step_num')

        step = get_object_or_404(Step, lesson__module__course__id = id,
                                 lesson__module__module_num = module_num,
                                 lesson__lesson_num = lesson_num,
                                 step_num=step_num,)
        return step

    def get(self, request, *args, **kwargs):
        step = self.get_object(self, request, *args, **kwargs)
        self.check_object_permissions(request, step)
        serializer = StepSerializer(step)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        step = self.get_object(request, *args, **kwargs)
        self.check_object_permissions(request, step)

        serializer = StepSerializer(step, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


