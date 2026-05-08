from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from core.mixins import AdminRequiredMixin
from notifications.models import Notification
from notifications.services import send_notification
from tasks.forms import TaskCommentForm, TaskForm, TaskProgressForm
from tasks.models import Task


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = "tasks/task_list.html"
    context_object_name = "tasks"
    paginate_by = 20

    def get_queryset(self):
        qs = Task.objects.select_related("assigned_to", "created_by")
        if not self.request.user.is_admin_role:
            qs = qs.filter(Q(assigned_to=self.request.user) | Q(created_by=self.request.user))
        status = self.request.GET.get("status")
        priority = self.request.GET.get("priority")
        if status:
            qs = qs.filter(status=status)
        if priority:
            qs = qs.filter(priority=priority)
        return qs


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = "tasks/task_detail.html"
    context_object_name = "task"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comment_form"] = TaskCommentForm()
        return context

    def post(self, request, *args, **kwargs):
        task = self.get_object()
        form = TaskCommentForm(request.POST, request.FILES)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.author = request.user
            comment.save()
            messages.success(request, "Comment added.")
        return redirect("tasks:detail", pk=task.pk)


class TaskCreateView(AdminRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"
    success_url = reverse_lazy("tasks:list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "Task assigned.")
        response = super().form_valid(form)
        send_notification(
            "New task assigned",
            self.object.title,
            Notification.Type.TASK,
            created_by=self.request.user,
            recipients=[self.object.assigned_to],
        )
        return response


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"
    success_url = reverse_lazy("tasks:list")

    def get_queryset(self):
        qs = Task.objects.all()
        if not self.request.user.is_admin_role:
            qs = qs.filter(assigned_to=self.request.user)
        return qs

    def get_form_class(self):
        if self.request.user.is_admin_role:
            return TaskForm
        return TaskProgressForm
