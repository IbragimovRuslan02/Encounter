"""
Encounter — маркетплейс + психологические тесты.

Запуск:
    pip install -r requirements.txt
    python run.py
"""
from app import create_app
from app.seed import init_db

app = create_app()


if __name__ == "__main__":
    with app.app_context():
        init_db()
    print("\nEncounter running at http://127.0.0.1:5000")
    print("\nDemo accounts:")
    print("  admin  / admin123  -- administrator")
    print("  shop1  / seller123 -- approved seller (TechnoSila)")
    print("  shop2  / seller123 -- approved seller (Uyutny Dom)")
    print("  shop3  / seller123 -- pending seller application")
    print("  buyer1 / buyer123  -- customer")
    print("  buyer2 / buyer123  -- customer\n")
    app.run(host="0.0.0.0", port=5000, debug=True)
