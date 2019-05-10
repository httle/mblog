from django import forms
from ckeditor.widgets import CKEditorWidget

class PostForm(forms.Form):
	title = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'标题'}),error_messages={'required':'评论内容不能为空'})
	text = forms.CharField(widget=CKEditorWidget(config_name='comment_ckeditor'),error_messages={'required':'发帖内容不能为空'})

	def __init__(self,*args,**kwargs):
		if 'user' in kwargs:
			self.user = kwargs.pop('user')
		super(PostForm,self).__init__(*args,**kwargs)

	def clean(self):
		# 判断用户是否登录
		if self.user.is_authenticated:
			self.cleaned_data['user'] = self.user
		else:
			raise forms.ValidationError("用户尚未登录！")
		return self.cleaned_data
	