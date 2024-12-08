from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import Department, Employee

class DepartmentListView(LoginRequiredMixin, ListView):
    model = Department
    template_name = 'organization/department_list.html'
    context_object_name = 'departments'

class DepartmentDetailView(LoginRequiredMixin, DetailView):
    model = Department
    template_name = 'organization/department_detail.html'
    context_object_name = 'department'

class EmployeeListView(LoginRequiredMixin, ListView):
    model = Employee
    template_name = 'organization/employee_list.html'
    context_object_name = 'employees'

    def get_queryset(self):
        queryset = super().get_queryset()
        department_id = self.request.GET.get('department')
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        return queryset

class EmployeeDetailView(LoginRequiredMixin, DetailView):
    model = Employee
    template_name = 'organization/employee_detail.html'
    context_object_name = 'employee'