from django.contrib.auth.models import User
from random import randint
from django.shortcuts import render, redirect, get_object_or_404
from .models import (
    Report,
    UserScore,
    GameInstance,
    Category,
    Question,
    Notification,
    QuestionSuggestion,
)
from .forms import (
    QuestionSuggestionForm,
    ReportForm,
    ScoreForm,
    GameForm,
    QuestionForm,
    CategoryForm,
)
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
import datetime
from datetime import datetime, timedelta
from django.utils import timezone
from django.http import HttpResponse
from django.contrib import messages


def index(request):
    is_google_auth = request.user.socialaccount_set.filter(provider="google").exists()
    return render(request, "login/index.html", {"is_google_auth": is_google_auth})


def login(request):
    return render(request, "login/homepage_test.html")


def homepage(request):
    if request.user.is_authenticated:
        has_admin_permission = request.user.has_perm("admin.is_admin")
        print(f"User '{request.user.username}' has 'Is Admin' permission: {has_admin_permission}")
        print(request.user.user_permissions.all())
        if has_admin_permission:
            return render(request, "login/admin_dashboard.html")
        else:
            return render(request, "login/user_dashboard.html")
    else:
        return redirect('/')


@login_required
def view_reports(request):
    if request.user.has_perm("admin.is_admin"):
        reports = Report.objects.all().order_by("-submitted_at")
        questions = QuestionSuggestion.objects.all()
        context = {"reports": reports, "questions": questions}
        return render(request, "reports/reports.html", context)
    else:
        return render(request, "login/homepage_test.html")


@login_required
def submit_report(request):
    categories = Category.objects.all()
    if request.method == "POST":
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.submitted_by = request.user
            report.save()
            messages.success(request, "Your report has been submitted. It will appear in the Notifications page after being reviewed by an admin")
            return redirect("homepage")
    else:
        form = ReportForm()
    context = {"form": form, "categories": categories}
    return render(request, "reports/submit_report.html", context)


@login_required
def delete_report(request, report_id):
    if request.user.has_perm("admin.is_admin"):
        report = get_object_or_404(Report, id=report_id)
        report.delete()
        messages.success(request, "Report deleted successfully.")
        return redirect("view_reports")
    else:
        return render(request, "login/homepage_test.html")


@login_required
def manage_users(request):
    if request.user.has_perm("admin.is_admin"):
        if request.method == "POST":
            user_id = request.POST.get("update")
            selected_role = request.POST.get(f"role_{user_id}")
            is_superuser = "superuser_" + user_id in request.POST
            user = User.objects.get(id=user_id)
            user.is_staff = selected_role == "admin"
            user.is_superuser = is_superuser
            user.save()
            messages.success(request, "User role updated succesfully.")
            return redirect("manage_users")

        users = User.objects.all()
        return render(request, "users/users.html", {"users": users})
    else:
        return render(request, "login/homepage_test.html")


# Create your views here.
@login_required
def start(request):
    user = request.user
    if GameInstance.objects.filter(user=user).exists():
        return redirect("play")

    # create game instance
    categories = Category.objects.filter(question__isnull=False).distinct()
    if request.method == "POST":
        # get cat
        cat = request.POST["cat"]

        if Category.objects.filter(category_text=cat).exists():
            game_cat = Category.objects.get(category_text=cat)
            # game = form.save(commit=False)
            game_time_start = datetime.now()
            game_time_end = datetime.now() + timedelta(minutes=+1)
            game_user = request.user
            # q_set = Question.objects.filter(category = game_cat).order_by('?').first()
            # get random question
            game_current_question = (
                Question.objects.filter(category=game_cat).order_by("?").first()
            )

            game = GameInstance.objects.create(
                user=game_user,
                category=game_cat.category_text,
                t_start=game_time_start,
                t_end=game_time_end,
                current_question=game_current_question,
                guesses_used=0,
                has_won=False,
            )
            game.save()

            return redirect("play")

    return render(request, "game/start.html", {"categories": categories})


@login_required
def play(request):
    # get info from button
    # TODO complex implenetation with correct/inncorrect answers
    user = request.user
    if GameInstance.objects.filter(user=user).exists():
        game = GameInstance.objects.get(user=user)
        # print(game.current_question.question_text)

        # if time is over - delete and send back to another page
        # REFERENCES
        # Title: 'Can't compare naive and aware datetime.now() <= challenge.datetime_end'
        # Author: ePi272314
        # Date: Oct 3, 2015
        # URL: https://stackoverflow.com/questions/15307623/cant-compare-naive-and-aware-datetime-now-challenge-datetime-end
        # if datetime.now(game.t_end.tzinfo) >= game.t_end:
        #     #end sourced code
        #     game.delete()
        #     return redirect('start')

        if game.has_won:
            return redirect("end_screen")

        time_remaining = game.t_end - timezone.now()
        # second = time_remaining)
        # time_second = time_remaining
        if time_remaining < timedelta(0, 0, 0):
            request.session["point_mul"] = 0
            return redirect("end_screen")

        # source: https://stackoverflow.com/questions/538666/format-timedelta-to-string
        str_min = str(time_remaining).split(":")[1]
        int_min = int(str_min) * 60
        str_sec = str(time_remaining).split(":")[2]
        int_sec = float(str_sec)

        # second = int(int_min + int_sec)
        second = time_remaining.seconds

        # second = int(str_time)
        # textContent.split(':')[2])

        # basic function: Add one to score every time the button is pressed
        if request.method == "POST":
            if not game.hint_provided:
                game.hint_provided = (
                    request.POST.get("hint_provided", "false") == "true"
                )
            time_out = request.POST.get("time_out", "false") == "true"

            # source for session variables: https://docs.djangoproject.com/en/4.2/topics/http/sessions/
            if time_out:
                request.session["point_mul"] = 0
                return redirect("end_screen")

            game.guesses_used = game.guesses_used + 1

            str_lat = request.POST.get("lat")
            str_long = request.POST.get("long")
            user = request.user.username
            question = game.current_question

            lat = float(str_lat)
            long = float(str_long)

            # actions if correct
            if guess_in_range(
                question.min_lat,
                question.max_lat,
                question.min_long,
                question.max_long,
                lat,
                long,
            ):
                # answer is correct

                # point multiplier
                point_mul = 1
                if not game.hint_provided:
                    if time_remaining >= timedelta(seconds=30):
                        point_mul = 3
                    elif time_remaining >= timedelta(seconds=15):
                        point_mul = 2
                request.session["point_mul"] = point_mul

                # if UserScore.objects.filter(info_for=user).exists():
                #     # already exists, update scor
                #     s_user = UserScore.objects.get(info_for=user)
                #     # s_user.save(commit=False)
                #     s_user.score += 1 * point_mul
                #     s_user.save()
                # else:
                #     # create it
                #     s_user = UserScore(info_for=user, score=(1 * point_mul))
                #     s_user.save()

                game.has_won = True
                game.save()
                return redirect("end_screen")

            # actions if incorrect
            # check for how many guesses
            if game.guesses_used >= 3:
                request.session['point_mul'] = 0
                return redirect('end_screen')
            
            messages.add_message(request, messages.INFO, "Sorry, that is")
            messages.add_message(request, messages.WARNING, "INCORRECT")
            if game.guesses_used == 2:
                guess_left_message = "you have " + str(3-game.guesses_used) + " guess remaining"
                messages.add_message(request, messages.INFO, guess_left_message)
            else:
                guess_left_message = "you have " + str(3-game.guesses_used) + " guesses remaining"
                messages.add_message(request, messages.INFO, guess_left_message)

            # save game so it can be refreshed
            game.save()


        return render(request, "game/play.html", {"game": game, "second": second})
    else:
        # game instance not created
        return redirect("start")
        # return render(request, 'game/start.html')


def guess_in_range(min_lat, max_lat, min_long, max_long, guess_lat, guess_long):
    for_lat = False
    for_long = False

    if min_lat > 0:
        if max_lat >= guess_lat and min_lat <= guess_lat:
            for_lat = True
    elif max_lat <= guess_lat and min_lat >= guess_lat:
        for_lat = True

    if min_long > 0:
        if max_long >= guess_long and min_long <= guess_long:
            for_long = True
    elif max_long <= guess_long and min_long >= guess_long:
        for_long = True

    return for_lat and for_long


@login_required
def leaderboard(request):
    scores = UserScore.objects.all().order_by("-score")
    return render(request, "users/leaderboard.html", {"scores": scores})


def logout(request):
    auth_logout(request)
    return redirect("login")


@login_required
def notifications(request):
    user_notifications = Notification.objects.filter(user=request.user).order_by(
        "-timestamp"
    )
    return render(
        request, "reports/notifications.html", {"notifications": user_notifications}
    )


@login_required
def change_report_status(request, report_id):
    if request.method == "POST":
        action = request.POST.get("action")
        admin_message = request.POST.get("admin_message")

        report = get_object_or_404(Report, id=report_id)

        if action == "approve":
            notification_message = (
                f"Your report '{report.report_name}' has been approved."
            )
        else:
            notification_message = (
                f"Your report '{report.report_name}' has been disapproved. "
                f"Admin message: {admin_message}"
            )
        Notification.objects.create(
            user=report.submitted_by, report=report, message=notification_message
        )
        report.delete()
        messages.success(request, "Report status successfully sent to user.")
        return redirect("view_reports")
    else:
        return HttpResponse("Invalid request", status=400)


@login_required
def delete_notifications(request):
    notification_ids = request.POST.getlist("notification_ids")
    # Assuming Notification is your model and it has a 'delete()' method
    for notification_id in notification_ids:
        Notification.objects.get(id=notification_id).delete()
    messages.success(request, "Your notification has been deleted.")

    return redirect("notifications")


@login_required
def add_cat(request):
    has_admin_permission = request.user.has_perm("admin.is_admin")
    print(
        f"User '{request.user.username}' has 'Is Admin' permission: {has_admin_permission}"
    )

    print(request.user.user_permissions.all())
    if request.user.has_perm("admin.is_admin"):
        if request.method == "POST":
            form_c = CategoryForm(request.POST, instance=Category())
            if form_c.is_valid():
                new_cat = form_c.save()
                messages.success(request, "New category successfully created.")
                return redirect("homepage")
            else:
                messages.error(request, "Category creation was unsuccessful. Enter all the necessary information.")
        else:
            form_c = CategoryForm(instance=Category())

        return render(request, "game/add_categories.html", {"cat_form": form_c})

    else:
        # not an admin send to homepage
        return render(request, "login/homepage_test.html")


@login_required
def add_question(request):
    has_admin_permission = request.user.has_perm("admin.is_admin")
    print(
        f"User '{request.user.username}' has 'Is Admin' permission: {has_admin_permission}"
    )

    print(request.user.user_permissions.all())
    if request.user.has_perm("admin.is_admin"):
        categories = Category.objects.all()
        if request.method == "POST":
            cat = request.POST["cat"]

            if Category.objects.filter(category_text=cat).exists():
                q_category = Category.objects.get(category_text=cat)
                form_q = QuestionForm(request.POST, instance=Question())

                if form_q.is_valid():
                    new_q = form_q.save(commit=False)
                    new_q.category = q_category
                    new_q.save()
                    messages.success(request, "Your question successfully created.")
                    return redirect("homepage")
            else:
                form_q = QuestionForm(instance=Question())
                messages.error(request, "Your question creation was unsuccessful. Don't forget to select a category")
        else:
            form_q = QuestionForm(instance=Question())

        return render(
            request,
            "game/add_questions.html",
            {"categories": categories, "q_form": form_q},
        )

    else:
        # not an admin send to homepage
        return render(request, "login/homepage_test.html")


@login_required
def end_screen(request):
    user = request.user
    
    if 'point_mul' not in request.session and GameInstance.objects.filter(user=user).exists:
        game = GameInstance.objects.get(user=user)
        game.delete()
        return redirect("start")
    
    if UserScore.objects.filter(info_for=user).exists() and GameInstance.objects.filter(user=user).exists():
        if GameInstance.objects.filter(user=user).exists():
            point_mul = request.session["point_mul"]
            # already exists, update scor
            s_user = UserScore.objects.get(info_for=user)
            # s_user.save(commit=False)
            s_user.score += 1 * point_mul
            s_user.save()
    elif GameInstance.objects.filter(user=user).exists():
        point_mul = request.session["point_mul"]
        # create it
        s_user = UserScore(info_for=user, score=(1 * point_mul))
        s_user.save()

    if GameInstance.objects.filter(user=user).exists():
        game = GameInstance.objects.get(user=user)
        message = ""
        question = game.current_question
        answer = question.answer_text
        s_user = UserScore.objects.get(info_for=user)
        total_points = s_user.score

        # points earned -- get point_mul from play view
        point_mul = request.session["point_mul"]
        points_earned = 1 * point_mul

        if game.has_won:
            # display winning message
            message = "You have won!"
            won = True
        else:
            # display lose message
            message = "You have lost"
            won = False
        game.delete()

        return render(
            request,
            "game/end_screen.html",
            {
                "message": message,
                "answer": answer,
                "points_earned": points_earned,
                "total_points": total_points,
                "won": won,
            },
        )

    else:
        # game instance not created
        return redirect("start")


@login_required
def submit_question_idea(request):
    if request.method == "POST":
        form = QuestionSuggestionForm(request.POST)
        print(request.POST)

        cat = request.POST.get("category", None)
        try:
            category = Category.objects.get(category_text=cat)
        except Category.DoesNotExist:
            messages.error(request, "Invalid category selected.")
            return render(request, "reports/submit_report.html", {"form": form})

        question = QuestionSuggestion(
            category=category,
            question_text=request.POST.get("question_text", ""),
            answer_text=request.POST.get("answer_text", ""),
            max_lat=request.POST.get("max_lat", 0),
            min_lat=request.POST.get("min_lat", 0),
            max_long=request.POST.get("max_long", 0),
            min_long=request.POST.get("min_long", 0),
            hint=request.POST.get("hint", ""),
            submitted_by=request.user,
        )

        question.save()
        messages.success(request, "Your question suggestion has been submitted. It will appear in the Notifications page after being reviewed by an admin")
        return redirect("homepage")
    else:
        form = QuestionSuggestionForm()

    return render(request, "reports/submit_report.html", {"form": form})


@login_required
def change_question_status(request, question_id):
    if request.method == "POST":
        action = request.POST.get("action")
        admin_message = request.POST.get("admin_message")

        question_suggestion = get_object_or_404(QuestionSuggestion, id=question_id)

        if action == "approve":
            # Create a new question from the suggestion
            new_question = Question(
                category=question_suggestion.category,
                question_text=question_suggestion.question_text,
                answer_text=question_suggestion.answer_text,
                max_lat=question_suggestion.max_lat,
                min_lat=question_suggestion.min_lat,
                max_long=question_suggestion.max_long,
                min_long=question_suggestion.min_long,
                hint=question_suggestion.hint,
            )
            new_question.save()
            notification_message = f"Your question suggestion '{question_suggestion.question_text}' has been approved."
        else:
            # Handle disapproval
            notification_message = f"Your question suggestion '{question_suggestion.question_text}' has been disapproved. Admin message: {admin_message}"

        # Create a notification for the user who submitted the suggestion
        Notification.objects.create(
            user=question_suggestion.submitted_by, message=notification_message
        )

        # Delete the question suggestion or handle it accordingly
        question_suggestion.delete()
        messages.success(request, "Question status successfully sent to user.")
        return redirect("view_reports")
    else:
        return HttpResponse("Invalid request", status=400)


@login_required
def delete_q(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    question.delete()
    messages.success(request, "Question deleted successfully.")
    return redirect("manage_q_c")


@login_required
def delete_c(request, category_id):
    question = get_object_or_404(Category, pk=category_id)
    question.delete()
    messages.success(request, "Category deleted successfully.")
    return redirect("manage_q_c")


@login_required
def manage_q_and_c(request):
    # check if admin
    has_admin_permission = request.user.has_perm("admin.is_admin")
    print(
        f"User '{request.user.username}' has 'Is Admin' permission: {has_admin_permission}"
    )

    print(request.user.user_permissions.all())
    if request.user.has_perm("admin.is_admin"):
        categories = Category.objects.all()
        questions = Question.objects.all()

        return render(
            request,
            "game/manage_q_and_c.html",
            {"categories": categories, "questions": questions},
        )

    else:
        # not an admin send to homepage
        return render(request, "login/homepage_test.html")


@login_required
def custom_404(request, exception):
    return render(request, "404.html", status=404)


@login_required
def game_settings(request):
    if request.user.has_perm("admin.is_admin"):
        return render(request, "game/game_settings.html")
    else:
        return render(request, "login/homepage_test.html")
