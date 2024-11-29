from django import forms
from .models import Post, AddComment, Profile, Comment


class PostForm(forms.ModelForm):
    CATEGORY_CHOICES = [
        ('tag1', 'study'),
        ('tag2', 'game'),
        ('tag3', 'other'),
    ]
    category = forms.ChoiceField(choices=CATEGORY_CHOICES)
    class Meta:
        model = Post
        fields = ['title', 'content', 'category']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['post', 'content']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar']

class SearchForm(forms.Form):
    query = forms.CharField(label='検索', max_length=255, required=False)

class ContactForm(forms.Form):
    subject = forms.CharField(max_length=50, label='件名')
    message = forms.CharField(widget=forms.Textarea, label='メッセージ')