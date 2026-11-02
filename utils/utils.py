#utils.py
import json
import logging


class TokenUsageWatcher:

    _logger = logging.getLogger(__file__)

    def __init__(self, tokens_json):
        self.json_file = tokens_json
        self.limits = {}
        

    def get_limits(self):
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                self.limits = json.load(f)
        except Exception as error:
            self._logger.error('Failed to read tokens_json file: %s', error)
        return self.limits


    def _save_token_usage(self):
        try:
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(self.limits, f, ensure_ascii=False, indent=4)
                return True
        except Exception as error:
                self._logger.error('Failed to write token usage in file: %s', error)
                return False


    def update_usage(self, current_model, token_usage):
        try:
            self.get_limits()
            self.limits[current_model] -= token_usage
            if self._save_token_usage():
                return self.limits[current_model]
        except Exception as error:
                self._logger.error('Failed to update token usage in file: %s', error)
                return self.limits[current_model]