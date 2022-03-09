import os
from app import app

if __name__ == '__main__':
    port = os.environ.get('PORT')
    app.run(debug=True, host='0.0.0.0', port=port)
