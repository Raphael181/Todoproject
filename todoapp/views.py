from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy

#imports for user login and regsitration purposes
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login


from .models import Task

#Login and register views 
class Login(LoginView):
  template_name = 'todoapp/login.html'
  fields = '__all__'
  redirect_authenticated_user = True

  def get_success_url(self):
    return reverse_lazy('tasks')

class Register(FormView):
  template_name = 'todoapp/register.html'
  form_class = UserCreationForm
  #redirects the existing user 
  redirect_authenticated_user = True
  #after succesful registration, takes you to the home page
  success_url = reverse_lazy('tasks')

  def form_valid(self, form):
    user  = form.save()
    if user is not None:
      login(self.request, user)
    return super(Register, self).form_valid(form)


  #if user is logged in/ registered, do not allow them to go to the login or register pages by typing it into the webbrowser
  def get(self, *args , **kwargs):
    if self.request.user.is_authenticated:
      return redirect('tasks')
    return super(Register, self).get(*args, **kwargs)

#List views for creating, updating and Deleting items on the list
#The "LoginRequiredMixin" view is used to make sure that the users are authenticated to make changes to their list
class TaskList(LoginRequiredMixin, ListView):
  model = Task
  #customising
  context_object_name = "tasks"

  def get_context_data(self ,**kwargs):
    context = super().get_context_data(**kwargs)
    context['tasks']  = context['tasks'].filter(user = self.request.user)
    context['count']  = context['tasks'].filter(complete = False).count()

    #search functionality
    search_input = self.request.GET.get('search-area') or ''
    if search_input:
      context['tasks'] = context['tasks'].filter(title__startswith = search_input)

    context['search_input'] = search_input
    return context

class TaskDetail(LoginRequiredMixin, DetailView):
  model = Task
  context_object_name = "task"
  template_name = 'todoapp/task.html'

class TaskCreate(LoginRequiredMixin, CreateView):
  #By default looks for a template "task_form.html." This can be changed later
  model = Task
  fields = ['title', 'description', 'complete']
  success_url = reverse_lazy('tasks')

  def form_valid(self, form):
    form.instance.user = self.request.user
    return super(TaskCreate , self).form_valid(form)

class TaskUpdate(LoginRequiredMixin, UpdateView):
  model  = Task
  #if the user is logged in, there is no need to make a drop down list of users
  fields =['title', 'description', 'complete']
  success_url = reverse_lazy('tasks')

class TaskDelete(LoginRequiredMixin, DeleteView):
  model  = Task
  context_object_name = 'task'
  success_url = reverse_lazy('tasks')