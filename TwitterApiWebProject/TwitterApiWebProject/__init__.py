"""
The flask application package.
"""

from flask import Flask
app = Flask(__name__)
#app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')
# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
import TwitterApiWebProject.views