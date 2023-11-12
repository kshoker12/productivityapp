from django.shortcuts import render, redirect
from . import restapis
from django.contrib.auth import login, logout, authenticate
from . import models
import pdfplumber
import re
from decimal import Decimal

def get_coordinators(request):
    if request.method == "GET":
        context = {"coordinators": models.Coordinator.objects.all()}
        return render(request, "index.html", context)

def login_request(request):
    context = {}
    if request.method == "GET":
        return render(request, "login.html", context)
    if request.method == "POST":
            # Get username and password from request.POST dictionary
        username = request.POST['username']
        password = request.POST['psw']
        # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)
        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)
            # return redirect('djangoapp:index')
            return redirect("index")
        else:
            # If not, return to login page again
            return render(request, 'login.html', context)

def add_pdf(request):
    context = {}
    if request.user.is_authenticated:
        if request.method == "GET":
            return render(request, "pdf.html", context)
        if request.method == "POST":
            file = request.FILES.get("file")
            if file != None:
                data = extract_data(file)
                updateModels(data)
            return redirect("index")
    else:
        return redirect("login")

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    # Redirect user back to course list view
    return redirect('login')

def updateModels(data):
    coordinators = models.Coordinator.objects.all()
    for coordinator in coordinators:
        if coordinator.name in data["name"]:
            coordinator.lines_completed += data["lines"]
            coordinator.orders_completed += 1
            coordinator.total_cost += data["sales"]
            coordinator.save()
    
def extract_data(my_pdf):
    with pdfplumber.open(my_pdf) as pdf:
        page = pdf.pages[0]
        text = page.extract_text()
        sales_amount = Decimal(re.sub(r',',"",text.split('SalesAmount:')[1].split()[0]))
        name = text.split('Page1of1')[1].split()[0]
        lined_text = text.split("\n")
        lines = []
        lines.extend(lined_text)
        start = obtainStartIndex(lines)
        end = obtainEndIndex(lines)
        table = lines[start:end]
        number_of_lines = obtainLines(table)
        return {"name": name, "sales": sales_amount, "lines": number_of_lines}

def obtainLines(table):
    current_string = table[0].split()[0]
    start = int(current_string)
    lines = 0
    for line in table:
        if current_string in line:
            start += 10
            lines += 1
            current_string = str(start)
    
    return lines

def obtainEndIndex(lines):
    end = 0
    for line in lines:
        if "SalesAmount:" in line:
            return end
        else:
            end += 1

def obtainStartIndex(lines):
    start = 0
    for line in lines:
        if "QTY" in line:
            start += 1
            return start
        else:
            start += 1