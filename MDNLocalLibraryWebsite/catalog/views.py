import datetime
from django.views.generic.edit import CreateView, UpdateView, DeleteView # Django Generic Editing Views
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.views import generic
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _ # Django translation function
#from django.core.urlresolvers import reverse # Old Django V1.11 import (changed to django.urls in 2.0)
from django.urls import reverse
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin # Only an authenicated user can access the view
from .models import Book, Author, BookInstance, Genre
from .forms import RenewBookForm
from django.core.exceptions import ValidationError

# Views proccess HTTP requests, request data from the database,
# generate HTML pages by rendering templates, and return HTML in
# HTTP response to be displayed.

def index(request):
	"""
	View function for home page of site.
	"""
	# Generate counts of some of the main objects
	num_books = Book.objects.all().count()
	num_instances = BookInstance.objects.all().count()
	# Available books (status = 'a')
	num_instances_available = BookInstance.objects.filter(status__exact='a').count()
	num_authors = Author.objects.count()  # The 'all()' is implied by default.
	num_genres = Genre.objects.distinct().count()
	filter_word = "Nac"
	num_books_word = Book.objects.filter(title__icontains=filter_word).count()

	# Number of visits to this view, as counted in the session variable.
	num_visits = request.session.get('num_visits', 0)
	request.session['num_visits'] = num_visits + 1
	
	# Render the HTML template index.html with the data in the context variable
	return render(request, 'catalog/index.html',
		context={'num_books':num_books,
				 'num_instances':num_instances,
				 'num_instances_available':num_instances_available,
				 'num_authors':num_authors,
				 'num_genres':num_genres,
				 'filter_word':filter_word,
				 'num_books_word':num_books_word,
				 'num_visits':num_visits},
	)

class BookListView(generic.ListView):
	"""
	Class view for all the books in the library.
	"""
	model = Book
	paginate_by = 10
	# To reference the model objects in the template view as: 'book_list' or 'object_list'
	#context_object_name = 'my_book_list'   # your own name for the list as a template variable
	#queryset = Book.objects.filter(title__icontains='war')[:5] # Get 5 books containing the title war
	#template_name = 'books/my_arbitrary_template_name_list.html'  # Specify your own template name/location
	
	def get_queryset(self):
		"""
		Overwrites the generic.ListView method. Gets the first 5 books with 'war' in
		their title.
		"""
		return Book.objects.filter(title__icontains='')[:5] # Get 5 books containing the title war

	def get_context_data(self, **kwargs):
		"""
		Overwrites the generic.ListView method. Allows additional arguments
		to be passed to the template.
		"""
		# Call the base implementation first to get a context
		context = super(BookListView, self).get_context_data(**kwargs)
		# Get the blog from id and add it to the context
		context['some_data'] = 'This is just some data'
		return context
	
class BookDetailView(generic.DetailView):
	"""
	Class view for an particular (title) book. Displays all book instances.
	"""
	model = Book

def book_detail_view(request,pk):
	try:
		book_id=Book.objects.get(pk=pk)
	except Book.DoesNotExist:
		raise Http404("Book does not exist")

	#book_id=get_object_or_404(Book, pk=pk)
	
	return render(
		request,
		'catalog/book_detail.html',
		context={'book':book_id,}
	)


class AuthorListView(generic.ListView):
	paginate_by = 10
	model = Author

class AuthorDetailView(generic.DetailView):
	model = Author

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
	"""
	Generic class-based view listing books on loan to current user. 
	"""
	model = BookInstance
	template_name ='catalog/bookinstance_list_borrowed_user.html'
	paginate_by = 10
	
	def get_queryset(self):
		return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

class AllLoanedBooksByUserListView(PermissionRequiredMixin, generic.ListView):
	"""
	Generic class-based view listing books on loan in the library.
	Only visible to librarians. 
	"""
	permission_required = 'catalog.can_mark_returned'
	model = BookInstance
	template_name ='catalog/bookinstance_list_borrowed_all.html'
	paginate_by = 10

	def get_queryset(self):
		"""
		Only return books that are on loan.
		"""
		return BookInstance.objects.filter(status__exact='o').order_by('due_back')

# An alternative to the class RenewBookForm defined forms.py 
# Class based forms are good for complex forms, or forms using fields from different models.
class RenewBookModelForm(ModelForm):
	def clean_due_back(self):
		data = self.cleaned_data['due_back']
		
		#Check date is not in past.
		if data < datetime.date.today():
			raise ValidationError(_('Invalid date: %(date)s - renewal in past'), code='dateinvalid01', params={'date':str(datetime.date.today())})

		#Check date is in range librarian allowed to change (+4 weeks)
		if data > datetime.date.today() + datetime.timedelta(weeks=4):
			raise ValidationError(_('Invalid date: %(date)s - renewal more than 4 weeks ahead'), code='dateinvalid02', params={'date':str(datetime.datetime.now())})
		
		# Remember to always return the cleaned data.
		return data

	class Meta:
		model = BookInstance
		fields = ['due_back',]
		labels = { 'due_back': _('Renewal date'), }
		help_texts = { 'due_back': _('Enter a date between now and 4 weeks (default 3).'), }


class AuthorModelForm(ModelForm):
	class Meta:
		model = Author
		fields = '__all__'

	def clean_date_of_death(self):
		data = self.cleaned_data['date_of_death']
		if data > datetime.date.today():
			raise ValidationError(_('Invalid date - date of death in the future'))
		return data

	def clean_date_of_birth(self):
		data = self.cleaned_data['date_of_birth']
		if data > datetime.date.today():
			raise ValidationError(_('Invalid date - date of birth in the future'))
		return data

	def clean(self):
		cleaned_data = super(AuthorModelForm, self).clean()
		DOB = cleaned_data.get('date_of_birth')
		DOD = cleaned_data.get('date_of_death')
		if DOB is not None and DOD is not None:
			if DOB > DOD:
				self.add_error(None, ValidationError('Invalid date - date of death before date of birth'))
		return cleaned_data

# Use generic views to create, edit, and delete Author records from the library db.
class AuthorCreate(PermissionRequiredMixin, CreateView):
	permission_required = 'catalog.can_modify_author'
	model = Author
	form_class = AuthorModelForm
	#fields = '__all__'
	initial = {'date_of_death':datetime.date.today().strftime("%d/%m/%Y"),}
	#template_name_suffix = '_form' # Default template name. The same for Update and Create.

	# Need to implement a date validator - added with the class "AuthorModelForm"

class AuthorUpdate(PermissionRequiredMixin, UpdateView):
	permission_required = 'catalog.can_modify_author'
	model = Author
	fields = ['first_name','last_name','date_of_birth','date_of_death']

class AuthorDelete(PermissionRequiredMixin, DeleteView):
	permission_required = 'catalog.can_modify_author'
	model = Author
	success_url = reverse_lazy('authors')
	#template_name_suffix = '_confirm_delete' # Default template name.


# Use generic views to create, edit, and delete Book records from the library db.
class BookCreate(PermissionRequiredMixin, CreateView):
	permission_required = 'catalog.can_modify_book'
	model = Book
	fields = '__all__'
	initial={'summary':'Please write a blurb here...',}
	#template_name_suffix = '_form' # Default template name. The smae for Update and Create.

class BookUpdate(PermissionRequiredMixin, UpdateView):
	permission_required = 'catalog.can_modify_book'
	model = Book
	fields = ['title','author','summary','isbn', 'genre']

class BookDelete(PermissionRequiredMixin, DeleteView):
	permission_required = 'catalog.can_modify_book'
	model = Book
	success_url = reverse_lazy('books')
	#template_name_suffix = '_confirm_delete' # Default template name.


from django.contrib.auth.decorators import permission_required
@permission_required('catalog.can_renew')
def renew_book_librarian(request, pk):
	"""
	Allow librarians to renew leased books (identfied
	using the book instnace id (pk).
	"""
	book_inst = get_object_or_404(BookInstance, pk=pk)

	# If this is a POST request then process the Form data (user submitted the form)
	if request.method == 'POST':

		# Create a form instance and populate it with data from the request (binding):
		form = RenewBookForm(request.POST)

		# Check if the form is valid:
		if form.is_valid():
			# process the data in form.cleaned_data as required (here we just write it to the model due_back field)
			book_inst.due_back = form.cleaned_data['renewal_date']
			book_inst.save()

			# redirect to a new URL:
			return HttpResponseRedirect(reverse('all-borrowed') )

	# If this is a GET (or any other method) create the default form.
	else:
		proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
		form = RenewBookForm(initial={'renewal_date': proposed_renewal_date,})

	return render(request, 'catalog/book_renew_librarian.html', {'form': form, 'bookinst':book_inst})