from rest_framework import serializers
from .models import Course, Module, Lesson, Step, Content
#from users.serializers import UserSerializer


# for sidebar
class SBLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['lesson_num', 'lesson_title', 'lesson_description']

class SBModuleSerializer(serializers.ModelSerializer):
    lessons = SBLessonSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = ['module_num','module_title' ,'module_description', 'lessons']

# class SBCourseSerializer(serializers.ModelSerializer):
#     modules = SBModuleSerializer(many=True, read_only=True)
#     owner = UserSerializer(read_only=True)
#
#     class Meta:
#         model = Course
#         fields = [
#             'id',
#             'title',
#             'description',
#             'rating',
#             'preview',
#             'price',
#             'modules'
#         ]
#     def get_preview_url(self, obj):
#         # Здесь создайте URL для изображения, используя его относительный путь
#         if obj.preview:
#             return self.context['request'].build_absolute_uri(obj.preview.url)
#         return None
#

#usual
class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = ['content_num', 'content_type', 'text', 'image', 'width', 'height']

class StepSerializer(serializers.ModelSerializer):
    contents = ContentSerializer(many=True, required=False)

    class Meta:
        model = Step
        fields = ['step_num','contents']
        read_only_fields = ['step_num']

    def create(self, validated_data):
        lesson = validated_data['lesson']
        
        # Auto-increment step_num
        step_num = lesson.steps.count() + 1

        # Create new step
        step = Step.objects.create(lesson=lesson, step_num=step_num)


        return step

    def update(self, instance, validated_data):
        contents_data = validated_data.get('contents', [])

        # Delete contents not present in the update data
        instance.contents.exclude(content_num__in=[content_data['content_num'] for content_data in contents_data]).delete()

        # Update existing or create new contents
        for content_data in contents_data:
            content_num = content_data.get('content_num')
            content, created = Content.objects.get_or_create(step=instance, content_num=content_num, defaults=content_data)
            if not created:
                for key, value in content_data.items():
                    setattr(content, key, value)
                content.save()

        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Сортировка contents по content_num
        sorted_contents = sorted(representation['contents'], key=lambda x: x.get('content_num', 0))
        representation['contents'] = sorted_contents
        return representation

class LessonSerializer(serializers.ModelSerializer):
    steps = StepSerializer(many=True, read_only=True)

    class Meta:
        model = Lesson
        fields = ['lesson_num', 'lesson_title', 'lesson_description', 'steps']
        read_only_fields = ['lesson_num']
    
    def create(self, validated_data):
        # course = validated_data['course']
        module = validated_data['module']
        lesson_title = validated_data['lesson_title']
        lesson_description = validated_data['lesson_description']

        lesson_num = module.lessons.count() + 1

        lesson = Lesson.objects.create(
            module=module,
            lesson_num=lesson_num,
            lesson_title=lesson_title,
            lesson_description=lesson_description
        )

        return lesson

class ModuleSerializer(serializers.ModelSerializer):
    lessons = SBLessonSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = ['module_num', 'module_title' ,'module_description', 'lessons']
        read_only_fields = ['module_num']
        depth = 1
    
    def create(self, validated_data):
        course = validated_data['course']
        module_title = validated_data['module_title']
        module_description = validated_data['module_description']

        module_num = course.modules.count() + 1

        module = Module.objects.create(
            course=course,
            module_num=module_num,
            module_title=module_title,
            module_description=module_description
        )

        return module

class CourseSerializer(serializers.ModelSerializer):
    #   owner = UserSerializer(read_only=True)
    modules = SBModuleSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'owner', 'rating', 'preview', 'price', 'modules']
        read_only_fields = ['rating', 'id', 'modules', 'owner']
        extra_kwargs = {'preview': {'required': True}}
        depth = 1
    
