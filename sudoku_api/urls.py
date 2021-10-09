from django.urls import path, include

urlpatterns = [
    path('api/', include("account.urls"), name="sudoku_api"),
]
