import json
from typing import Optional
from pydantic import BaseModel


class SettingModel(BaseModel):
    document_path: Optional[str] = None


class Settings:
    def __init__(self) -> None:
        try:
            with open("settings.json", "r") as f:
                self._settings = SettingModel(**json.load(f))
        except json.decoder.JSONDecodeError as e:
            print(f"Error On Settings Init: {e}")
            self._settings = SettingModel()

    @property
    def settings(self) -> SettingModel:
        return self._settings

    def set_settings(self, settings: dict):
        for key, value in settings.items():
            setattr(self._settings, key, value)
        with open("settings.json", "w") as f:
            json.dump(self._settings.model_dump(), f)

    def update_document_path(self, document_path: str):
        self.set_settings({"document_path": document_path})
