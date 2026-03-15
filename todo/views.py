from django.shortcuts import render, redirect, get_object_or_404
from datetime import date, timedelta
from .models import Habit, HabitLog
from .models import Note, Journal
from .models import Password
from .models import Expense
from django.db.models import Sum
from django.db.models import Count
from django.db.models import Q
import json


from datetime import date, timedelta
from django.shortcuts import render, redirect
from django.db.models import Count
import json
from .models import Habit, HabitLog

def dashboard(request):
    today = date.today()
    habits = Habit.objects.all()
    total_today = habits.count()

    # ADD HABIT
    if request.method == "POST" and "add" in request.POST:
        name = request.POST.get("name")
        if name:
            Habit.objects.create(name=name)
        return redirect("dashboard")

    # DELETE HABIT
    if request.method == "POST" and "delete" in request.POST:
        Habit.objects.get(id=request.POST.get("id")).delete()
        return redirect("dashboard")

    # EDIT HABIT
    if request.method == "POST" and "edit" in request.POST:
        habit = Habit.objects.get(id=request.POST.get("id"))
        habit.name = request.POST.get("name")
        habit.save()
        return redirect("dashboard")

    # TOGGLE COMPLETE
    if request.method == "POST" and "toggle" in request.POST:
        habit_id = request.POST.get("id")
        log, created = HabitLog.objects.get_or_create(
            habit_id=habit_id,
            date=today
        )
        log.completed = not log.completed
        log.save()
        return redirect("dashboard")

    # COMPLETED TODAY
    completed_today = HabitLog.objects.filter(date=today, completed=True).count()

    # INCOMPLETE TODAY
    incomplete_today = total_today - completed_today

    # PRODUCTIVITY SCORE
    productivity_score = int((completed_today / total_today) * 100) if total_today > 0 else 0

    # MOTIVATION MESSAGE
    if productivity_score == 100:
        message = "🔥 Perfect day! You're unstoppable!"
    elif productivity_score >= 70:
        message = "💪 Great job! Keep pushing forward!"
    elif productivity_score >= 40:
        message = "⚡ Good progress! Stay consistent!"
    elif productivity_score > 0:
        message = "🌱 Small steps matter. Keep going!"
    else:
        message = "🚀 Start your habits and build momentum!"

    # LAST 15 DAYS COMPLETED
    start_date = today - timedelta(days=14)
    completed_days = 0
    for i in range(15):
        day = start_date + timedelta(days=i)
        completed = HabitLog.objects.filter(date=day, completed=True).count()
        if completed == total_today and total_today > 0:
            completed_days += 1

    # 15 DAY MOTIVATION
    if completed_days >= 13:
        motivation15 = "🏆 Incredible consistency! You're unstoppable!"
    elif completed_days >= 10:
        motivation15 = "🔥 Amazing discipline! Keep the streak going!"
    elif completed_days >= 7:
        motivation15 = "💪 You're building a powerful habit!"
    elif completed_days >= 4:
        motivation15 = "⚡ Good effort! Stay consistent!"
    else:
        motivation15 = "🌱 Start small. Every habit counts!"

    # WEEKLY DATA (Completed + Incomplete)
    weekly_completed = HabitLog.objects.filter(completed=True).values('date').annotate(completed=Count('id')).order_by('date')[:7]
    weekly_data = []
    for entry in weekly_completed:
        day = entry['date']
        completed_count = entry['completed']
        # Incomplete = total habits - completed that day
        incomplete_count = total_today - completed_count
        weekly_data.append({
            "date": str(day),
            "completed": completed_count,
            "incomplete": incomplete_count
        })

    # MONTHLY DATA (Completed + Incomplete)
    monthly_completed = HabitLog.objects.filter(completed=True).values('date').annotate(completed=Count('id')).order_by('date')[:30]
    monthly_data = []
    for entry in monthly_completed:
        day = entry['date']
        completed_count = entry['completed']
        incomplete_count = total_today - completed_count
        monthly_data.append({
            "date": str(day),
            "completed": completed_count,
            "incomplete": incomplete_count
        })

    context = {
        "habits": habits,
        "today": today,
        "completed_today": completed_today,
        "incomplete_today": incomplete_today,
        "total_today": total_today,
        "productivity_score": productivity_score,
        "motivation15": motivation15,
        "weekly": json.dumps(weekly_data),
        "monthly": json.dumps(monthly_data),
    }

    return render(request, "index.html", context)

from django.shortcuts import render, redirect, get_object_or_404
from .models import Note
from django.db.models import Q

def notes(request):

    query = request.GET.get("search")

    if request.method == "POST":

        action = request.POST.get("action")

        if action == "add":
            Note.objects.create(
                title=request.POST.get("title"),
                content=request.POST.get("content"),
                category=request.POST("category")
            )

        elif action == "edit":
            note = get_object_or_404(Note,id=request.POST.get("id"))
            note.title = request.POST.get("title")
            note.content = request.POST.get("content")
            note.save()

        elif action == "delete":
            note = get_object_or_404(Note,id=request.POST.get("id"))
            note.delete()

        elif action == "pin":
            note = get_object_or_404(Note,id=request.POST.get("id"))
            note.pinned = not note.pinned
            note.save()

        return redirect("notes")

    notes = Note.objects.all()

    if query:
        notes = notes.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query)
        )

    notes = notes.order_by("-pinned","-created")

    return render(request,"home.html",{"notes":notes})


MASTER_PASSWORD = "1234"

def password_page(request):

    # unlock state
    unlocked = request.session.get("unlocked", False)

    if request.method == "POST":

        action = request.POST.get("action")

        # UNLOCK
        if action == "unlock":
            if request.POST.get("master") == MASTER_PASSWORD:
                request.session["unlocked"] = True
                unlocked = True
            else:
                return render(request, "pass.html", {"unlocked": False, "error": "Incorrect password"})

        # LOCK
        elif action == "lock":
            request.session["unlocked"] = False
            unlocked = False

        # ADD PASSWORD
        elif action == "add" and unlocked:
            Password.objects.create(
                website=request.POST.get("website"),
                username=request.POST.get("username"),
                password=request.POST.get("password")
            )

        # DELETE PASSWORD
        elif action == "delete" and unlocked:
            p = get_object_or_404(Password, id=request.POST.get("id"))
            p.delete()

        # EDIT PASSWORD
        elif action == "edit" and unlocked:
            p = get_object_or_404(Password, id=request.POST.get("id"))
            p.website = request.POST.get("website")
            p.username = request.POST.get("username")
            p.password = request.POST.get("password")
            p.save()

        return redirect("password_page")

    passwords = Password.objects.all()

    return render(request, "pass.html", {
        "passwords": passwords,
        "unlocked": unlocked
    })

    
def journal(request):

    if request.method == "POST":

        action = request.POST.get("action")

        if action == "add":
            Journal.objects.create(
                title=request.POST["title"],
                content=request.POST["content"],
                motivation=request.POST["motivation"]
            )

        if action == "delete":
            Journal.objects.filter(id=request.POST["id"]).delete()

        if action == "edit":
            j = Journal.objects.get(id=request.POST["id"])
            j.title = request.POST["title"]
            j.content = request.POST["content"]
            j.motivation = request.POST["motivation"]
            j.save()

    journals = Journal.objects.all()

    # -------- STATS --------

    journal_count = journals.count()

    high_motivation = journals.filter(motivation="High").count()

    productivity = int((high_motivation / journal_count)*100) if journal_count else 0

    streak = high_motivation   # simple streak logic

    context = {
        "journals": journals,
        "journal_count": journal_count,
        "high_motivation": high_motivation,
        "productivity": productivity,
        "streak": streak
    }

    return render(request,"lock.html",context)

   # expenses/views.py

# Set your password here
PAGE_PASSWORD = "1234"  # change to your own password

def expense_tracker(request):
    # PASSWORD CHECK
    if not request.session.get('authenticated'):
        if request.method == 'POST' and 'page_password' in request.POST:
            entered_password = request.POST.get('page_password')
            if entered_password == PAGE_PASSWORD:
                request.session['authenticated'] = True
                return redirect('expense_tracker')
            else:
                return render(request, 'expense.html', {'error': 'Incorrect password', 'show_password': True})
        return render(request, 'expense.html', {'show_password': True})

    # ADD / EDIT / DELETE EXPENSES
    if request.method == 'POST':
        if 'add_expense' in request.POST:
            title = request.POST.get('title')
            amount = request.POST.get('amount')
            category = request.POST.get('category')
            if title and amount:
                Expense.objects.create(title=title, amount=float(amount), category=category)
        elif 'edit_expense' in request.POST:
            expense_id = request.POST.get('expense_id')
            expense = get_object_or_404(Expense, pk=expense_id)
            expense.title = request.POST.get('title')
            expense.amount = float(request.POST.get('amount'))
            expense.category = request.POST.get('category')
            expense.save()
        elif 'delete_expense' in request.POST:
            expense_id = request.POST.get('expense_id')
            expense = get_object_or_404(Expense, pk=expense_id)
            expense.delete()
        return redirect('expense_tracker')

    # GET EXPENSES
    expenses = Expense.objects.all().order_by('-date')
    total = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    return render(request, 'expense.html', {'expenses': expenses, 'total': total, 'show_password': False})

def logout(request):
    """Clear session to require password again"""
    request.session.flush()
    return redirect('expense_tracker')