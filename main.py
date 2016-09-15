import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Blog(db.Model):
    title = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class FrontPage(Handler):
    def render_front(self, title="", content="", error=""):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5")

        self.render("front.html", title=title, content=content, error=error, blogs=blogs)
    def get(self):
        self.render_front()


class NewPost(Handler):
    def render_front(self, title="", content="", error=""):
        self.render("new-post.html", title=title, content=content, error=error)
    def get(self):
        self.render("new-post.html")

    def post(self):
        title = self.request.get("title")
        content = self.request.get("content")

        if title and content:
            a = Blog(title = title, content = content)
            a.put()
            post = a.key().id()

            self.redirect("/blog/%s" % str(post))
        else:
            error = "we need both a title and some content!"
            self.render_front(title=title, content=content, error=error)

class ViewPostHandler(Handler):
    def get(self, id):
        posts = Blog.get_by_id(int(id))

        if posts:
            self.render("front.html", posts = posts)

        else:
            self.redirect('/notfound')

class Home(Handler):
    def get(self):
        self.redirect('/blog')

class ArchivePage(Handler):
    def render_front(self, title="", content="", error=""):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created ASC")

        self.render("front.html", title=title, content=content, error=error, blogs=blogs)
    def get(self):
        self.render_front()




app = webapp2.WSGIApplication([
    ('/blog', FrontPage),
    ('/newpost', NewPost),
    ('/', Home),
    ('/archives', ArchivePage),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
