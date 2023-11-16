from django.shortcuts import render, redirect
from . import restapis
from django.contrib.auth import login, logout, authenticate
from . import models
import pdfplumber
import re
import os
from decimal import Decimal
from matplotlib import pyplot as plt
from matplotlib import cm
import numpy as np
from django.conf import settings

def get_coordinators(request):
    if request.method == "GET":
        activeWeek = models.CurrentWeek.objects.filter(selected = True)[0]
        context = {"weeks": models.Week.objects.filter(week = activeWeek.week), "currentWeeks": models.CurrentWeek.objects.all(), "activeWeek": activeWeek}
        return render(request, "index.html", context)
    if request.method == "POST":
        dropdown_value = request.POST.get('dropdown')
        activeWeek = models.CurrentWeek.objects.get(week = dropdown_value)
        context = {"weeks": models.Week.objects.filter(week = activeWeek.week), "currentWeeks": models.CurrentWeek.objects.all(), "activeWeek": activeWeek}
        return render(request, "index.html", context)

def tables(request):
    if request.method == "GET":
        fig, lx = plt.subplots()
        fig1, ox = plt.subplots()
        fig2, cx = plt.subplots()
        lx_max = 0
        ox_max = 0
        cx_max = 0.00
        colors = cm.viridis(np.linspace(0, 1, len(models.Coordinator.objects.all())))
        i = 0
        for cd in models.Coordinator.objects.all():
            weeksObject = models.Week.objects.filter(coordinator__name = cd.name)
            weeks = normalizeArray(weeksObject.values_list("week"))
            lines = normalizeArray(weeksObject.values_list("lines_completed"))
            cost = normalizeArray(weeksObject.values_list("total_cost"))
            orders = normalizeArray(weeksObject.values_list("orders_completed"))
            lx.scatter(weeks, lines, color = colors[i], label = weeksObject[0].coordinator.name)
            ox.scatter(weeks, orders, color = colors[i], label = weeksObject[0].coordinator.name)
            cx.scatter(weeks, cost, color = colors[i], label = weeksObject[0].coordinator.name)
            lx.plot(weeks, lines, color = colors[i])
            ox.plot(weeks, orders, color = colors[i])
            cx.plot(weeks, cost, color = colors[i])
            lx_max = calculateMax(lines, lx_max)
            ox_max = calculateMax(orders, ox_max)
            cx_max = calculateMax(cost, cx_max)
            i+= 1

        lx.set_xlabel('Weeks')
        lx.set_ylabel('Lines Completed')
        lx.set_title('Lines Completed per Week')
        lx.set_xticks(range(1, len(models.CurrentWeek.objects.all()) + 1, 1))
        lx.set_yticks(range(0, lx_max, 1))

        # Add legend
        lx.legend()
        file_path = settings.BASE_DIR
        file_path_0 = os.path.join(file_path, "ProductivityApp/templates/static/images/lines_table.png")
        fig.savefig(file_path_0)

        ox.set_xlabel('Weeks')
        ox.set_ylabel('Orders Completed')
        ox.set_title('Orders Completed per Week')
        ox.set_xticks(range(1, len(models.CurrentWeek.objects.all()) + 1, 1))
        ox.set_yticks(range(0, ox_max, 1))

        # Add legend
        ox.legend()
        file_path_1 = os.path.join(file_path, "ProductivityApp/templates/static/images/orders_table.png")
        fig1.savefig(file_path_1)

        cx.set_xlabel('Weeks')
        cx.set_ylabel('Orders Completed')
        cx.set_title('Orders Completed per Week')
        cx.set_xticks(range(1, len(models.CurrentWeek.objects.all()) + 1, 1))
        cx.set_yticks(range(0, ox_max, 1))

        # Add legend
        cx.legend()
        file_path_2 = os.path.join(file_path, "ProductivityApp/templates/static/images/cost_table.png")
        fig2.savefig(file_path_2)
    return render(request, "tables.html", {})

def reset(request):
    if request.user.is_authenticated and request.user.username == "dennis":
        if request.method == "GET":
            activeWeek = models.CurrentWeek.objects.filter(selected = True)[0]
            activeWeek.selected = False
            activeWeek.save()
            for cd in models.Coordinator.objects.all():
                weekObject = models.Week(coordinator = cd, week = len(models.CurrentWeek.objects.all()) + 1, lines_completed = 0, orders_completed = 0, total_cost = 0)
                weekObject.save()
            newWeek = models.CurrentWeek(week = len(models.CurrentWeek.objects.all()) + 1, selected = True)
            newWeek.save()
    return redirect("index")


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
    activeWeek = models.CurrentWeek.objects.filter(selected = True)[0]
    weeks = models.Week.objects.filter(week = activeWeek.week)
    for week in weeks:
        if week.coordinator.name in data["name"]:
            week.lines_completed += data["lines"]
            week.orders_completed += 1
            week.total_cost += data["sales"]
            week.save()
    
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

def calculateMax(arr, max_value):
    arr_max = max_value
    for a in arr:
        if (a > max_value):
            arr_max = a
    return arr_max 

def normalizeArray(arr):
    new_arr = []
    for a in arr:
        val = list(a)
        new_arr.append(val[0])
    return new_arr
