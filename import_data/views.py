from .models import DataFrame
from django.views.generic import ListView, DetailView

class PublishedPostsMixin(object):
	def get_queryset(self):
		return self.model.objects.live()
    	# Should remove 2 lines since we're using a model manager,  keeping it for reference
	    #queryset = super(PublishedPostsMixin, self).get_queryset()
        #return queryset.filter(published=True)

class PostListView(PublishedPostsMixin, ListView):
	model = Post

class PostDetailView(PublishedPostsMixin, DetailView):
	model = Post




# Should remove these but leaving them for reference		
def blog_list(request, *args, **kwargs):
	post_list = Post.objects.filter(published=True)
	template_name = "post_list.html"
	context = {
		"post_list": post_list
	}
	return render(request, template_name, context)

def blog_detail(request, pk, *args, **kwargs):
	post = Post.objects.get(pk=pk, published=True)
	template_name = "blog/post_detail.html"
	context = {
		"post": post
	}
	return render(request, template_name, context)