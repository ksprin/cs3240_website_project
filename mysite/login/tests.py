from django.test import TestCase
from django.contrib.auth.models import User, Permission
from django.urls import reverse, resolve
from .models import UserScore, Report, Notification, Category, Question, GameInstance, QuestionSuggestion
from login.views import homepage, view_reports, submit_report, delete_report, change_report_status, manage_users, start, play, leaderboard, notifications, delete_notifications, add_cat, end_screen, submit_question_idea, change_question_status, delete_q, delete_c, manage_q_and_c
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.sites.models import Site
import time



#reference: https://www.youtube.com/watch?v=0MrgsYswT1c
class URLTestCases(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='54321')

    def test_homepage(self):
        url = reverse("homepage")
        self.assertEquals(resolve(url).func, homepage)

    def test_view_reports(self):
        url = reverse("view_reports")
        self.assertEquals(resolve(url).func, view_reports)

    def test_submit_report(self):
        url = reverse("submit_report")
        self.assertEquals(resolve(url).func, submit_report)

    def test_delete_report(self):
        url = reverse("delete_report", args = [1])
        self.assertEquals(resolve(url).func, delete_report)
    
    def test_change_report_status(self):
        url = reverse("change_report_status", args = [1])
        self.assertEquals(resolve(url).func, change_report_status)
    
    def test_manage_users(self):
        url = reverse("manage_users")
        self.assertEquals(resolve(url).func, manage_users)
    
    def test_start(self):
        url = reverse("start")
        self.assertEquals(resolve(url).func, start)
    
    def test_play(self):
        url = reverse("play")
        self.assertEquals(resolve(url).func, play)
    
    def test_leaderboard(self):
        url = reverse("leaderboard")
        self.assertEquals(resolve(url).func, leaderboard)
    
    def test_notifications(self):
        url = reverse("notifications")
        self.assertEquals(resolve(url).func, notifications)
    
    def test_delete_notifications(self):
        url = reverse("delete_notifications")
        self.assertEquals(resolve(url).func, delete_notifications)

    def test_add_category(self):
        url = reverse("add_category")
        self.assertEquals(resolve(url).func, add_cat)

    def test_end_submit_question_idea(self):
        url = reverse("submit_question_idea")
        self.assertEquals(resolve(url).func, submit_question_idea)

    def test_change_question_status(self):
        url = reverse("change_question_status", args = [1])
        self.assertEquals(resolve(url).func, change_question_status)

    def test_delete_q(self):
        url = reverse("delete_q", args = [1])
        self.assertEquals(resolve(url).func, delete_q)

    def test_delete_c(self):
        url = reverse("delete_c", args = [1])
        self.assertEquals(resolve(url).func, delete_c)

    def test_delete_c(self):
        url = reverse("delete_c", args = [1])
        self.assertEquals(resolve(url).func, delete_c)

    def test_manage_q_c(self):
        url = reverse("manage_q_c")
        self.assertEquals(resolve(url).func, manage_q_and_c)

class ViewTestCases(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='54321')
        self.admin_user = User.objects.create_superuser(username='admin', password='12345')
        self.s_user = UserScore.objects.create(info_for = 'testuser', score = 1)
    def test_reg_user_to_homepage(self):
        self.client.login(username='testuser', password='54321')
        response = self.client.get(reverse('homepage')) 
        self.assertTemplateUsed(response, 'login/user_dashboard.html')
    def test_admin_user_to_admin_dashboard(self):
        self.client.login(username='admin', password='12345')
        response = self.client.get(reverse('homepage'))
        self.assertTemplateUsed(response, 'login/admin_dashboard.html')
    def test_create_report(self):
            report_data = {
                'report_name': 'New Test Report',
                'report_description': 'Description of the new test report',
                'submitted_by': self.user,
            }
            new_report = Report.objects.create(**report_data)
            self.assertTrue(Report.objects.filter(id=new_report.id).exists())
            self.assertEqual(new_report.report_name, report_data['report_name'])
            self.assertEqual(new_report.report_description, report_data['report_description'])
            self.assertEqual(new_report.submitted_by, self.user)
            self.assertFalse(new_report.is_approved)  
    def test_delete_report(self):
            report_data = {
                'report_name': 'New Test Report',
                'report_description': 'Description of the new test report',
                'submitted_by': self.user,
            }
            new_report = Report.objects.create(**report_data)
            new_report.delete()
            self.assertFalse(Report.objects.filter(id=new_report.id).exists()) 


class TestModels(TestCase):
    def setup(self):
        self.time = datetime.now()
        self.user = User.objects.create_user(username='testuser', password='54321')
    
        self.questionT = Question.objects.create(self.catT, "text", "answer", 10, 1, 10, 1, "hint")

    def test_category(self):
        self.catT = Category.objects.create(category_text = "title", description = "des")
        self.assertEquals(self.catT.category_text, "title")

    def test_question(self):
        self.catT = Category.objects.create(category_text = "title", description = "des")
        self.questionT = Question.objects.create(category = self.catT, question_text = "text", answer_text = "answer", max_lat = 10, min_lat = 1, max_long = 10, min_long = 1, hint = "hint")
        self.assertEquals(self.questionT.category, self.catT)
        

class GameViewTestCases(TestCase): #testing play
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='54321')
        logged_in = self.client.login(username='testuser', password='54321')
        self.assertTrue(logged_in, "User login failed")


        self.category = Category.objects.create(category_text="Category1", description="Description")
        self.question = Question.objects.create(
            category=self.category, question_text="Sample Question", 
            answer_text="Sample Answer", max_lat=10, min_lat=5, 
            max_long=10, min_long=5, hint="Sample Hint"
        )

        self.game_instance = GameInstance.objects.create(
            user=self.user, category=self.category.category_text, 
            current_question=self.question, guesses_used=0, has_won=False,
            t_start= timezone.now(),
            t_end=timezone.now() + timedelta(minutes=5)
        )

    def test_reg_user_to_startgame(self):
        self.game_instance.delete()
        self.client.login(username='testuser', password='54321')
        response = self.client.get(reverse('start'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/start.html')

    def test_playurl_no_instance(self):
        self.game_instance.delete()
        self.client.login(username='testuser', password='54321')
        response = self.client.get(reverse('play'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('start'))

    def test_play_view_game_exists(self):
        response = self.client.get(reverse('play'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/play.html')

    def test_play_view_post_incorrect_answer(self):
        self.client.post(reverse('play'), {
            'lat': 0,  
            'long': 0,
        })
        self.game_instance.refresh_from_db()
        self.assertFalse(self.game_instance.has_won)
        self.assertEqual(self.game_instance.guesses_used, 1)

    def test_play_all_wrong(self):
        num_guesses_to_lose = 3
        
        for i in range(num_guesses_to_lose-1):
            self.client.post(reverse('play'), {
                'lat': 0,  
                'long': 0,
            })
            self.game_instance.refresh_from_db()
        response = self.client.post(reverse('play'), {'lat':0, 'long':0}, follow=True)
        self.assertRedirects(response, reverse("end_screen"))
        self.assertFalse(response.context['won'])
    
    def test_correct_end_screen(self):
        response = self.client.post(reverse('play'), {'lat':10,'long':5}, follow=True)
        self.assertRedirects(response, reverse("end_screen"))
        self.assertTrue(response.context['won'])
    
    def test_time_end(self):
        sameTime = timezone.now()

        self.game_instance.delete()
        self.game_instance = GameInstance.objects.create(
            user=self.user, category=self.category.category_text, 
            current_question=self.question, guesses_used=0, has_won=False,
            t_start= sameTime,
            t_end=sameTime
        )
        self.game_instance.refresh_from_db()
        response = self.client.get(reverse('play'), follow=True)
        self.assertRedirects(response, reverse("end_screen"))
        self.assertFalse(response.context['won'])


        

    



        


    # def test_play_view_post_max_guesses(self): Couldn't figure out how to simulate a guess but it works on Heroku
    #     self.game_instance.guesses_used = 2 
    #     self.game_instance.save()
    #     response = self.client.post(reverse('play'), {
    #         'lat': 0,  
    #         'long': 0,
    #     })
    #     self.game_instance.refresh_from_db()
    #     self.assertEqual(self.game_instance.guesses_used, 3)
    #     self.assertFalse(self.game_instance.has_won)

    #     self.assertRedirects(response, reverse('end_screen'), status_code=302, target_status_code=200)


class QuestionStatusChangeTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(username='admin', password='12345')
        self.client.login(username='admin', password='12345')
        self.user = User.objects.create_user(username='testuser', password='54321')
        self.category = Category.objects.create(category_text="Category1", description="Sample Category")
        self.question_suggestion = QuestionSuggestion.objects.create(
            category=self.category,
            question_text="Sample Question",
            answer_text="Sample Answer",
            max_lat=40.712776,
            min_lat=40.712775,
            max_long=-74.005974,
            min_long=-74.005973,
            hint="Sample Hint",
            submitted_by=self.user
        )

    def test_approve_question_suggestion(self):
        response = self.client.post(reverse('change_question_status', args=[self.question_suggestion.id]), {
            'action': 'approve'
        })
        self.assertRedirects(response, reverse('view_reports'))
        self.assertFalse(QuestionSuggestion.objects.filter(id=self.question_suggestion.id).exists())
        self.assertTrue(Question.objects.filter(question_text="Sample Question").exists())
        self.assertTrue(Notification.objects.filter(user=self.user).exists())

    def test_disapprove_question_suggestion(self):
        response = self.client.post(reverse('change_question_status', args=[self.question_suggestion.id]), {
            'action': 'disapprove',
            'admin_message': 'Not suitable'
        })
        self.assertRedirects(response, reverse('view_reports'))
        self.assertFalse(QuestionSuggestion.objects.filter(id=self.question_suggestion.id).exists())
        self.assertTrue(Notification.objects.filter(user=self.user, message__contains='Not suitable').exists())




