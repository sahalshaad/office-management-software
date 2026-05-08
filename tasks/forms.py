from django import forms

from tasks.models import Task, TaskComment


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "assigned_to", "priority", "status", "due_date", "progress"]
        widgets = {"due_date": forms.DateTimeInput(attrs={"type": "datetime-local"})}


class TaskCommentForm(forms.ModelForm):
    class Meta:
        model = TaskComment
        fields = ["comment", "attachment"]


class TaskProgressForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["status", "progress"]
