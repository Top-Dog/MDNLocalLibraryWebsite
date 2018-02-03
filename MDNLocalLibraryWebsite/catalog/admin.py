from django.contrib import admin
from .models import Author, Genre, Book, BookInstance

# Register your models here (in the order they will appear in the admin view).
admin.site.register(Genre)

class BooksInline(admin.TabularInline):
	# Display book items in the author detail view
	model = Book
	extra = 0

class AuthorAdmin(admin.ModelAdmin):
		list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')
		fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]
		inlines = [BooksInline]
admin.site.register(Author, AuthorAdmin)


class BooksInstanceInline(admin.TabularInline):
	# Display book instance items in the books detail view
	model = BookInstance
	extra = 0

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
	list_display = ('title', 'author', 'display_genre')

	# View all the book instances associated with this book in the detail view
	inlines = [BooksInstanceInline]
#admin.site.register(Book, BookAdmin)

@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
	list_display = ('book', 'id', 'status', 'due_back', 'borrower', 'lang')
	list_filter = ('status', 'due_back', 'lang')
	
	# Sort the admin view into (two) sections
	fieldsets = (
		(None, {'fields' : ('book', 'imprint', 'id')}),
		('Availability', {'fields' : ('status', 'due_back', 'borrower')}))
#admin.site.register(BookInstance, BookInstanceAdmin)