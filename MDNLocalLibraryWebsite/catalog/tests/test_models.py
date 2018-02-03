from django.test import TestCase
from catalog.models import Author, Genre, Book

class AuthorModelTest(TestCase):

	@classmethod
	def setUpTestData(cls):
		# Set up non-modified objects used by all test methods
		# Runs once when the class is instantiated
		Author.objects.create(first_name='Big', last_name='Bob')

	def test_first_name_label(self):
		author=Author.objects.get(id=1)
		field_label = author._meta.get_field('first_name').verbose_name
		# author.first_name only gets the name 'Big' as a string (not an object handle)
		self.assertEquals(field_label,'first name')

	def test_last_name_label(self):
		author=Author.objects.get(id=1)
		field_label = author._meta.get_field('last_name').verbose_name
		self.assertEqual(field_label, 'last name')

	def test_date_of_birth_label(self):
		author=Author.objects.get(id=1)
		field_label = author._meta.get_field('date_of_birth').verbose_name
		self.assertEquals(field_label,'date of birth')

	def test_date_of_death_label(self):
		author=Author.objects.get(id=1)
		field_label = author._meta.get_field('date_of_death').verbose_name
		self.assertEquals(field_label,'died')

	def test_first_name_max_length(self):
		author=Author.objects.get(id=1)
		max_length = author._meta.get_field('first_name').max_length
		self.assertEquals(max_length,100)

	def test_last_name_max_length(self):
		author=Author.objects.get(id=1)
		max_length = author._meta.get_field('last_name').max_length
		self.assertEquals(max_length,100)

	def test_object_name_is_last_name_comma_first_name(self):
		# Tests the str() method
		author=Author.objects.get(id=1)
		expected_object_name = '%s, %s' % (author.last_name, author.first_name)
		self.assertEquals(expected_object_name,str(author))

	def test_get_absolute_url(self):
		author=Author.objects.get(id=1)
		#This will also fail if the urlconf is not defined.
		self.assertEquals(author.get_absolute_url(),'/catalog/author/1')

class GenreModelTest(TestCase):

	@classmethod
	def setUpTestData(cls):
		# Set up non-modified objects used by all test methods
		# Runs once when the class is instantiated
		Genre.objects.create(name='Adventure')
		Genre.objects.create(name='Thriller')

	def test_name_label(self):
		genre=Genre.objects.get(id=1)
		field_label = genre._meta.get_field('name').verbose_name
		self.assertEquals(field_label,'name')

	def test_name_max_length(self):
		genre=Genre.objects.get(id=1)
		max_length = genre._meta.get_field('name').max_length
		self.assertEquals(max_length,200)

	def test_object_genre_is_name(self):
		# Tests the str() method
		genre=Genre.objects.get(id=1)
		expected_object_name = '%s' % (genre.name,)
		self.assertEquals(expected_object_name,str(genre))


class BookModelTest(TestCase):

	@classmethod
	def setUpTestData(cls):
		# Set up non-modified objects used by all test methods
		# Runs once when the class is instantiated
		Book.objects.create(title='A Short History of Everything',
					  summary='A very cool book!', isbn=1234567891011)

	def test_title_label(self):
		book=Book.objects.get(id=1)
		field_label = book._meta.get_field('title').verbose_name
		self.assertEquals(field_label,'title')

	def test_title_max_length(self):
		book=Book.objects.get(id=1)
		max_length = book._meta.get_field('title').max_length
		self.assertEquals(max_length,200)

	def test_add_new_genre(self):
		book=Book.objects.get(id=1)
		book.genre.add(Genre.objects.create(name='Thriller'),
							Genre.objects.create(name='Adventure'))
		self.assertEquals(len(book.genre.all()), 2)

	def test_object_name_is_title(self):
		# Tests the str() method
		book=Book.objects.get(id=1)
		expected_object_name = '%s' % (book.title,)
		self.assertEquals(expected_object_name,str(book))

	def test_get_absolute_url(self):
		book=Book.objects.get(id=1)
		#This will also fail if the urlconf is not defined.
		self.assertEquals(book.get_absolute_url(),'/catalog/book/1')