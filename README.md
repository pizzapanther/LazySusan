Lazy Susan
==========

Lazy Susan: any similar structure, as a shelf or tabletop, designed to revolve so
that whatever it holds can be seen or reached easily.

Lazy Susan is a Django admin application written for the Google App Engine ORM.
While Django NonRel is a great way to use Django on Google App Engine, it
reduces you to using the Django ORM which abstracts away a lot of the advantages
of using Google App Engine's Datastore.  In my opinion, if your going to use
Google App Engine, then you should use the full power of Big Table.

If you agree with this premise, you can use Django to still to develop your App
Engine web app, but you lose one of the best things going for Django over other
web frameworks, the built-in Admin interface.

Lazy Susan, brings that back for you.  Lazy Susan brings you an App Engine
admin interface that follows Django's admin conventions.  Lazy Susan does
deviate in some respects due to immaturity and to provide a more relevant
interface.
