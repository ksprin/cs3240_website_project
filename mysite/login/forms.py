from django import forms
from .models import Report, UserScore, GameInstance, Question, Category, QuestionSuggestion

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['report_name', 'report_description', 'image']
        exclude = ['submitted_by']

class ScoreForm(forms.ModelForm):
    class Meta:
        model = UserScore
        fields = ['score']
        exclude = ['info_for']

class GameForm(forms.ModelForm):
    class Meta:
        model = GameInstance
        fields = ['category']
        exclude = ['t_start', 't_end', 'current_question', 'user', 'hint_provided', 'guesses_used', 'has_won']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_text', 'description']
        exclude = []
    def clean_category_text(self):
        category_text = self.cleaned_data['category_text']
        if Category.objects.filter(category_text__iexact=category_text).exists():
            raise forms.ValidationError("A category with this name already exists.")
        return category_text

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'answer_text', 'max_lat', 'min_lat', 'max_long', 'min_long', 'hint']
        exclude = ['category']

class QuestionSuggestionForm(forms.ModelForm):
    class Meta:
        model = QuestionSuggestion
        fields = ['category', 'question_text', 'answer_text', 'max_lat', 'min_lat', 'max_long', 'min_long', 'hint']
        exclude = ['submitted_by']
