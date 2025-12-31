

from app_factory import create_app

app = create_app()

# http://127.0.0.1:5001/console/api/swagger-ui.html

# flask db migrate -m "change some fields"
# flask db upgrade

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=True)