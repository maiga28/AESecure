from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def dechiffrement(request):
    return render(request, 'dechiffrement.html')