from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Movie, Review

class ReviewForm(forms.ModelForm):
    rating = forms.TypedChoiceField(
        label="Оценка",
        choices=[(i, str(i)) for i in range(1, 11)],
        coerce=int,
        widget=forms.RadioSelect,
        error_messages={"required": "Выберите оценку от 1 до 10."},
    )

    class Meta:
        model = Review
        fields = ["rating", "text"]
        labels = {"text": "Обзор"}
        widgets = {
            "text": forms.Textarea(attrs={
                "rows": 5,
                "placeholder": "Что вы думаете о фильме? Можно оставить только оценку.",
                "maxlength": 5000,
            }),
        }

    def clean_text(self):
        return self.cleaned_data["text"].strip()


class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = ["title", "original_title", "year", "director", "duration",
                  "description", "poster", "poster_url", "genres"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "genres": forms.CheckboxSelectMultiple,
        }

    def clean_year(self):
        year = self.cleaned_data["year"]
        if year < 1888 or year > 2100:
            raise forms.ValidationError("Укажите год между 1888 и 2100.")
        return year

    def clean_poster(self):
        poster = self.cleaned_data.get("poster")
        if poster and hasattr(poster, "size") and poster.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Файл больше 5 МБ.")
        return poster


class RegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["username"]
