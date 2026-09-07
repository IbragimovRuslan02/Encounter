"""
Encounter — платформа психологических тестов.

Запуск:
    cd Encounter
    pip install -r requirements.txt
    python run.py
"""
from app import create_app
from app.seed import init_db

app = create_app()


if __name__ == "__main__":
    with app.app_context():
        init_db()
    print("\n🚀 Encounter запущен: http://127.0.0.1:5000")
    print("👤 Админ: admin / admin123\n")
    app.run(host="0.0.0.0", port=5000, debug=True)
