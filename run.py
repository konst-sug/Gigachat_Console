from config import logger, G_CHAT_KEY, TOKENS_FILE
from gigachat import GigaChat
from chat import ChatWorker, SettingsReader
from utils import TokenUsageWatcher


def start(models):
    "Выбор модели"
    reader = SettingsReader()
    model = reader.simple_select(models)
    return model


def chat_reply(history, context=None):

    mod = context["model"] if context else start()
    giga_client = GigaChat(credentials=G_CHAT_KEY, 
                       model=mod,
                       verify_ssl_certs=False)
    resp = giga_client.chat.stream(
    {"messages": [{"role": "system", "content": "Ты — полезный ассистент."}] + history}
)
    usage_result = None
    def generator():
        current_usage = None
        nonlocal usage_result
        for chunk in resp:
            if hasattr(chunk, 'usage') and chunk.usage is not None:
                current_usage = chunk.usage
            logger.info(chunk)
            if chunk.event:
                content = chunk.messages
                yield {"content": content, "usage": current_usage}
            
    return generator()


def main():
    tuw = TokenUsageWatcher(TOKENS_FILE)
    limits = tuw.get_limits()

    mod = start(set(limits.keys()))
    context = {"model": mod}
    ChatWorker(reply_fn=chat_reply, limits_dict=limits, context=context).run()


if __name__ == "__main__":
    main()