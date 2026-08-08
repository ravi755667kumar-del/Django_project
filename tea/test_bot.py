import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tea.settings')
django.setup()

from shop.chat import ask_bot

try:
    print("Calling ask_bot...")
    answer = ask_bot("hi", "test_user_id", "Ravi")
    print("Answer:")
    print(answer)
except Exception as e:
    import traceback
    traceback.print_exc()
