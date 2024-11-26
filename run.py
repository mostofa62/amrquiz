from app import app
import os

from questions import *
from students import *
from questions_doctors import *
from doctors import *
from home import *

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5002))
    app.run(debug=True, host='0.0.0.0', port=port)


