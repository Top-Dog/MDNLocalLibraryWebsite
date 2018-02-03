import datetime
from django.utils import timezone
#from django.core.urlresolvers import reverse
from django.urls import reverse
from django.contrib.auth.models import User, Permission #Required to assign User as a borrower
from django.test import TestCase
from catalog.models import Author, BookInstance, Book, Genre


class AuthorListViewTest(TestCase):
	"""
	HTTP response codes:
	200		OK
	3xx		Redirection
	302		Page Found
	4xx		Client Messed Up
	404		Page Not Found
	5xx		Server Messed Up
	"""

	@classmethod
	def setUpTestData(cls):
		# Client works like a dummy web browser, handling POST and GET requests.
		# Create 13 authors for pagination tests
		number_of_authors = 13
		for author_num in range(number_of_authors):
			Author.objects.create(first_name='Christian %s' % author_num, last_name = 'Surname %s' % author_num,)

	def test_view_url_exists_at_desired_location(self):
		# Test using absolute url
		resp = self.client.get('/catalog/authors/') 
		self.assertEqual(resp.status_code, 200)  
		   
	def test_view_url_accessible_by_name(self):
		# Test using reverse url (lookup)
		resp = self.client.get(reverse('authors'))
		self.assertEqual(resp.status_code, 200)
		
	def test_view_uses_correct_template(self):
		resp = self.client.get(reverse('authors'))
		self.assertEqual(resp.status_code, 200)

		self.assertTemplateUsed(resp, 'catalog/author_list.html')
		
	def test_pagination_is_ten(self):
		#Get first page and confirm it has (exactly) 10 items
		resp = self.client.get(reverse('authors'))
		self.assertEqual(resp.status_code, 200)
		self.assertTrue('is_paginated' in resp.context)
		self.assertTrue(resp.context['is_paginated'] == True)
		self.assertTrue( len(resp.context['author_list']) == 10)

	def test_lists_all_authors(self):
		#Get second page and confirm it has (exactly) remaining 3 items
		resp = self.client.get(reverse('authors')+'?page=2')
		self.assertEqual(resp.status_code, 200)
		self.assertTrue('is_paginated' in resp.context)
		self.assertTrue(resp.context['is_paginated'] == True)
		self.assertTrue( len(resp.context['author_list']) == 3)


class AuthorCreateViewTest(TestCase):

	def setUp(self):
		#Create a user
		test_user1 = User.objects.create_user(username='testuser1', password='12345')
		test_user1.save()

		test_user2 = User.objects.create_user(username='testuser2', password='12345')
		test_user2.save()
		permission = Permission.objects.get(name='Create, modify, or delete authors')
		test_user2.user_permissions.add(permission)
		test_user2.save()

		#Create a book
		self.test_author = Author.objects.create(first_name='John', last_name='Smith')
		test_genre = Genre.objects.create(name='Fantasy')
		#test_language = Language.objects.create(name='English')
		test_book = Book.objects.create(title='Book Title', summary = 'My book summary', isbn='ABCDEFG', author=self.test_author) #language=test_language,
		# Create genre as a post-step
		genre_objects_for_book = Genre.objects.all()
		test_book.genre.set(genre_objects_for_book)
		test_book.save()

		#Create a BookInstance object for test_user1
		return_date= datetime.date.today() + datetime.timedelta(days=5)
		self.test_bookinstance1=BookInstance.objects.create(book=test_book,imprint='Unlikely Imprint, 2016', due_back=return_date, borrower=test_user1, status='o')

		#Create a BookInstance object for test_user2
		return_date= datetime.date.today() + datetime.timedelta(days=5)
		self.test_bookinstance2=BookInstance.objects.create(book=test_book,imprint='Unlikely Imprint, 2016', due_back=return_date, borrower=test_user2, status='o')

	def test_redirect_if_not_logged_in(self):
		resp = self.client.get(reverse('author_create'))
		#Manually check redirect (Can't use assertRedirect, because the redirect URL is unpredictable)
		self.assertEqual( resp.status_code,302)
		self.assertTrue( resp.url.startswith('/accounts/login/') )

	def test_redirect_if_logged_in_but_not_correct_permission(self):
		login = self.client.login(username='testuser1', password='12345')
		resp = self.client.get(reverse('author_create'))		
		#Manually check redirect (Can't use assertRedirect, because the redirect URL is unpredictable)
		self.assertEqual( resp.status_code,302)
		self.assertTrue( resp.url.startswith('/accounts/login/') )

	def test_logged_in_with_permission_create_author(self):
		login = self.client.login(username='testuser2', password='12345')
		resp = self.client.get(reverse('author_create'))		
		#Check that it lets us login - this is our book and we have the right permissions.
		self.assertEqual( resp.status_code,200)
		
	def test_uses_correct_template(self):
		login = self.client.login(username='testuser2', password='12345')
		resp = self.client.get(reverse('author_create'))
		self.assertEqual( resp.status_code,200)
		#Check we used correct template
		self.assertTemplateUsed(resp, 'catalog/author_form.html')

	def test_form_initial_date_of_death_is_this_year(self):
		login = self.client.login(username='testuser2', password='12345')
		resp = self.client.get(reverse('author_create'))
		self.assertEqual(resp.status_code,200)
		# Check the date
		this_year = datetime.date.today().year
		self.assertTrue(str(this_year) in resp.context['form'].initial['date_of_death'])

	def test_redirects_to_author_list_on_success(self):
		login = self.client.login(username='testuser2', password='12345')
		first_name = 'Bob'
		last_name = 'Kissinger'
		date_of_birth = datetime.date(1963, 7, 3)
		date_of_death = datetime.date(2009, 4, 13)
		resp = self.client.post(reverse('author_create'), 
						  {'first_name':first_name,
							'last_name':last_name,
							'date_of_birth':date_of_birth,
							'date_of_death':date_of_death} )
		self.assertEqual(resp.status_code, 302)
		self.assertRedirects(resp, reverse('author-detail', kwargs={'pk':self.test_author.pk+1,}) )

	def test_form_invalid_date_of_death_future(self):
		login = self.client.login(username='testuser2', password='12345')
		first_name = 'Bob'
		last_name = 'Kissinger'
		date_of_birth = datetime.date(1963, 7, 3)
		date_of_death = datetime.date.today() + datetime.timedelta(days=1)
		resp = self.client.post(reverse('author_create'), 
						  {'first_name':first_name,
							'last_name':last_name,
							'date_of_birth':date_of_birth,
							'date_of_death':date_of_death} )
		self.assertEqual(resp.status_code, 200)
		self.assertFormError(resp, 'form', 'date_of_death', 'Invalid date - date of death in the future')

	def test_form_invalid_date_of_birth_future(self):
		login = self.client.login(username='testuser2', password='12345')
		first_name = 'Bob'
		last_name = 'Kissinger'
		date_of_birth = datetime.date.today() + datetime.timedelta(days=1)
		date_of_death = datetime.date(1963, 7, 3)
		resp = self.client.post(reverse('author_create'), 
						  {'first_name':first_name,
							'last_name':last_name,
							'date_of_birth':date_of_birth,
							'date_of_death':date_of_death} )
		self.assertEqual(resp.status_code, 200)
		self.assertFormError(resp, 'form', 'date_of_birth', 'Invalid date - date of birth in the future')

	def test_form_invalid_date_of_death_before_date_of_birth(self):
		login = self.client.login(username='testuser2', password='12345')
		first_name = 'Bob'
		last_name = 'Kissinger'
		date_of_birth = datetime.date(1945, 6, 18) + datetime.timedelta(days=1)
		date_of_death = datetime.date(1945, 6, 18) - datetime.timedelta(days=1)
		resp = self.client.post(reverse('author_create'), 
						  {'first_name':first_name,
							'last_name':last_name,
							'date_of_birth':date_of_birth,
							'date_of_death':date_of_death} )
		self.assertEqual(resp.status_code, 200)
		self.assertFormError(resp, 'form', None, 'Invalid date - date of death before date of birth')


class LoanedBookInstancesByUserListViewTest(TestCase):

	def setUp(self):
		# SetUp() [per test method data] used rather than setUpTestData() [class shared data] 
		# because we'll be modifying some of these objects in the test methods.
		
		# Create two users
		test_user1 = User.objects.create_user(username='testuser1', password='12345') 
		test_user1.save()
		test_user2 = User.objects.create_user(username='testuser2', password='12345') 
		test_user2.save()
		
		#Create a book
		test_author = Author.objects.create(first_name='John', last_name='Smith')
		test_genre = Genre.objects.create(name='Fantasy')
		#test_language = Language.objects.create(name='English')
		test_book = Book.objects.create(title='Book Title', summary='My book summary', isbn='ABCDEFG', author=test_author) #language=test_language
		# Create genre as a post-step
		genre_objects_for_book = Genre.objects.all()
		test_book.genre.set(genre_objects_for_book)
		test_book.save()

		#Create 30 BookInstance objects
		number_of_book_copies = 30
		for book_copy in range(number_of_book_copies):
			return_date= timezone.now() + datetime.timedelta(days=book_copy%5)
			if book_copy % 2:
				the_borrower=test_user1
			else:
				the_borrower=test_user2
			status = 'm' # Maintenance
			BookInstance.objects.create(book=test_book, imprint='Unlikely Imprint, 2016', due_back=return_date, borrower=the_borrower, status=status)
		
	def test_redirect_if_not_logged_in(self):
		resp = self.client.get(reverse('my-borrowed'))
		self.assertRedirects(resp, '/accounts/login/?next=/catalog/mybooks/')

	def test_logged_in_uses_correct_template(self):
		login = self.client.login(username='testuser1', password='12345')
		resp = self.client.get(reverse('my-borrowed'))
		
		#Check our user is logged in
		self.assertEqual(str(resp.context['user']), 'testuser1')
		#Check that we got a response "success"
		self.assertEqual(resp.status_code, 200)

		#Check we used correct template
		self.assertTemplateUsed(resp, 'catalog/bookinstance_list_borrowed_user.html')

	def test_only_borrowed_books_in_list(self):
		login = self.client.login(username='testuser1', password='12345')
		resp = self.client.get(reverse('my-borrowed'))
		
		#Check our user is logged in
		self.assertEqual(str(resp.context['user']), 'testuser1')
		#Check that we got a response "success"
		self.assertEqual(resp.status_code, 200)
		
		#Check that initially we don't have any books in list (none on loan)
		self.assertTrue('bookinstance_list' in resp.context)
		self.assertEqual( len(resp.context['bookinstance_list']),0)
		
		#Now change all books to be on loan 
		get_ten_books = BookInstance.objects.all()[:10]

		for copy in get_ten_books:
			copy.status='o'
			copy.save()
		
		#Check that now we have borrowed books in the list
		resp = self.client.get(reverse('my-borrowed'))
		#Check our user is logged in
		self.assertEqual(str(resp.context['user']), 'testuser1')
		#Check that we got a response "success"
		self.assertEqual(resp.status_code, 200)
		
		self.assertTrue('bookinstance_list' in resp.context)
		
		#Confirm all books belong to testuser1 and are on loan
		for bookitem in resp.context['bookinstance_list']:
			self.assertEqual(resp.context['user'], bookitem.borrower)
			self.assertEqual('o', bookitem.status)

	def test_pages_ordered_by_due_date(self):
	
		#Change all books to be on loan
		for copy in BookInstance.objects.all():
			copy.status='o'
			copy.save()
			
		login = self.client.login(username='testuser1', password='12345')
		resp = self.client.get(reverse('my-borrowed'))
		
		#Check our user is logged in
		self.assertEqual(str(resp.context['user']), 'testuser1')
		#Check that we got a response "success"
		self.assertEqual(resp.status_code, 200)
				
		#Confirm that of the items, only 10 are displayed due to pagination.
		self.assertEqual( len(resp.context['bookinstance_list']),10)
		
		last_date=0
		for copy in resp.context['bookinstance_list']:
			if last_date==0:
				last_date=copy.due_back
			else:
				self.assertTrue(last_date <= copy.due_back)


class RenewBookInstancesViewTest(TestCase):

	def setUp(self):
		#Create a user
		test_user1 = User.objects.create_user(username='testuser1', password='12345')
		test_user1.save()

		test_user2 = User.objects.create_user(username='testuser2', password='12345')
		test_user2.save()
		permission = Permission.objects.get(name='Set book as returned')
		test_user2.user_permissions.add(permission) # Needed for the redirect 'all-borrowed-books' url
		permission = Permission.objects.get(name='Renew the book for an extended lease')
		test_user2.user_permissions.add(permission)
		test_user2.save()

		#Create a book
		test_author = Author.objects.create(first_name='John', last_name='Smith')
		test_genre = Genre.objects.create(name='Fantasy')
		#test_language = Language.objects.create(name='English')
		test_book = Book.objects.create(title='Book Title', summary = 'My book summary', isbn='ABCDEFG', author=test_author) #language=test_language,
		# Create genre as a post-step
		genre_objects_for_book = Genre.objects.all()
		test_book.genre.set(genre_objects_for_book)
		test_book.save()

		#Create a BookInstance object for test_user1
		return_date= datetime.date.today() + datetime.timedelta(days=5)
		self.test_bookinstance1=BookInstance.objects.create(book=test_book,imprint='Unlikely Imprint, 2016', due_back=return_date, borrower=test_user1, status='o')

		#Create a BookInstance object for test_user2
		return_date= datetime.date.today() + datetime.timedelta(days=5)
		self.test_bookinstance2=BookInstance.objects.create(book=test_book,imprint='Unlikely Imprint, 2016', due_back=return_date, borrower=test_user2, status='o')

	def test_redirect_if_not_logged_in(self):
		resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk,}) )
		#Manually check redirect (Can't use assertRedirect, because the redirect URL is unpredictable)
		self.assertEqual( resp.status_code,302)
		self.assertTrue( resp.url.startswith('/accounts/login/') )
		
	def test_redirect_if_logged_in_but_not_correct_permission(self):
		login = self.client.login(username='testuser1', password='12345')
		resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk,}) )
		
		#Manually check redirect (Can't use assertRedirect, because the redirect URL is unpredictable)
		self.assertEqual( resp.status_code,302)
		self.assertTrue( resp.url.startswith('/accounts/login/') )

	def test_logged_in_with_permission_borrowed_book(self):
		login = self.client.login(username='testuser2', password='12345')
		resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance2.pk,}) )
		
		#Check that it lets us login - this is our book and we have the right permissions.
		self.assertEqual( resp.status_code,200)

	def test_logged_in_with_permission_another_users_borrowed_book(self):
		login = self.client.login(username='testuser2', password='12345')
		resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk,}) )
		
		#Check that it lets us login. We're a librarian, so we can view any users book
		self.assertEqual( resp.status_code,200)

	def test_HTTP404_for_invalid_book_if_logged_in(self):
		import uuid 
		test_uid = uuid.uuid4() #unlikely UID to match our bookinstance!
		login = self.client.login(username='testuser2', password='12345')
		resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk':test_uid,}) )
		self.assertEqual( resp.status_code,404)
		
	def test_uses_correct_template(self):
		login = self.client.login(username='testuser2', password='12345')
		resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk,}) )
		self.assertEqual( resp.status_code,200)

		#Check we used correct template
		self.assertTemplateUsed(resp, 'catalog/book_renew_librarian.html')

	def test_form_renewal_date_initially_has_date_three_weeks_in_future(self):
		login = self.client.login(username='testuser2', password='12345')
		resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk,}) )
		self.assertEqual( resp.status_code,200)
		
		date_3_weeks_in_future = datetime.date.today() + datetime.timedelta(weeks=3)
		self.assertEqual(resp.context['form'].initial['renewal_date'], date_3_weeks_in_future )

	def test_redirects_to_all_borrowed_book_list_on_success(self):
		login = self.client.login(username='testuser2', password='12345')
		valid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=2)
		resp = self.client.post(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk,}), {'renewal_date':valid_date_in_future} )
		self.assertRedirects(resp, reverse('all-borrowed') )

	def test_form_invalid_renewal_date_past(self):
		login = self.client.login(username='testuser2', password='12345')       
		date_in_past = datetime.date.today() - datetime.timedelta(weeks=1)
		resp = self.client.post(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk,}), {'renewal_date':date_in_past} )
		self.assertEqual( resp.status_code,200)
		self.assertFormError(resp, 'form', 'renewal_date', 'Invalid date - renewal in past')
		
	def test_form_invalid_renewal_date_future(self):
		login = self.client.login(username='testuser2', password='12345')
		invalid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=5)
		resp = self.client.post(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk,}), {'renewal_date':invalid_date_in_future} )
		self.assertEqual( resp.status_code,200)
		self.assertFormError(resp, 'form', 'renewal_date', 'Invalid date - renewal more than 4 weeks ahead')