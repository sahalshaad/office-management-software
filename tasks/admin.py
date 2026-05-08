from django.contrib import admin

from tasks.models import Task, TaskAttachment, TaskComment


class TaskAttachmentInline(admin.TabularInline):
    model = TaskAttachment
    extra = 0


class TaskCommentInline(admin.TabularInline):
    model = TaskComment
    extra = 0
    readonly_fields = ("created_at",)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "assigned_to", "priority", "status", "progress", "due_date", "created_by")
    list_filter = ("priority", "status", "due_date")
    search_fields = ("title", "description", "assigned_to__email", "assigned_to__employee_id")
    inlines = [TaskAttachmentInline, TaskCommentInline]
    date_hierarchy = "due_date"


@admin.register(TaskAttachment)
class TaskAttachmentAdmin(admin.ModelAdmin):
    list_display = ("task", "uploaded_by", "label", "created_at")
    search_fields = ("task__title", "label")


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ("task", "author", "created_at")
    search_fields = ("task__title", "comment", "author__email")
