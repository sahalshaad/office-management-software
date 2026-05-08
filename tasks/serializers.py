from rest_framework import serializers

from tasks.models import Task, TaskAttachment, TaskComment


class TaskAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskAttachment
        fields = ["id", "task", "uploaded_by", "file", "label", "created_at"]
        read_only_fields = ["task", "uploaded_by", "created_at"]


class TaskCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.full_name", read_only=True)

    class Meta:
        model = TaskComment
        fields = ["id", "task", "author", "author_name", "comment", "attachment", "created_at"]
        read_only_fields = ["task", "author", "created_at"]


class TaskSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source="assigned_to.full_name", read_only=True)
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    comments = TaskCommentSerializer(many=True, read_only=True)
    attachments = TaskAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "created_by",
            "created_by_name",
            "assigned_to",
            "assigned_to_name",
            "priority",
            "status",
            "due_date",
            "progress",
            "completed_at",
            "is_overdue",
            "comments",
            "attachments",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_by", "completed_at", "created_at", "updated_at"]

    def validate_progress(self, value):
        if value > 100:
            raise serializers.ValidationError("Progress cannot exceed 100.")
        return value


class TaskProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["status", "progress"]

    def validate_progress(self, value):
        if value > 100:
            raise serializers.ValidationError("Progress cannot exceed 100.")
        return value
