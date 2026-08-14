from django.apps import AppConfig


class ShopConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shop'

    def ready(self):
        # Preload the RAG model in a background thread when the server starts
        # so the very first chatbot message doesn't have a 5-second delay.
        try:
            import threading
            from shop.rag import _get_retriever
            threading.Thread(target=_get_retriever, daemon=True).start()
        except Exception as e:
            print(f"Error preloading RAG model: {e}")
