from django.urls import path
from .views import dashboard,notes, password_page, journal
from .views import expense_tracker, logout

urlpatterns = [
    path('', dashboard, name="dashboard"),
    path('notes/', notes, name='notes'),
    path("passwords/",password_page, name="password_page"),
    path("journal/", journal, name="journal"),
    path('expense/', expense_tracker, name='expense_tracker'),
    path('logout/', logout, name='logout'),

]
    # path("lock/", lock_page, name="lock_page"),
    # path("logout/",logout_lock, name="logout_lock"),
