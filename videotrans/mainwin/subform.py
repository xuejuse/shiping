import json
import os
import re
import webbrowser

from PySide6 import QtWidgets
from PySide6.QtCore import QThread, Signal, QUrl
from PySide6.QtGui import Qt, QDesktopServices
from PySide6.QtWidgets import QMessageBox, QFileDialog, QLineEdit, QPushButton

from videotrans.configure import config
from videotrans.task.separate_worker import SeparateWorker
from videotrans.util import tools


class Subform():
    def __init__(self, main=None):
        self.main = main

    def set_auzuretts_key(self):
        class TestTTS(QThread):
            uito = Signal(str)

            def __init__(self, *, parent=None, text=None, role=None, language=None):
                super().__init__(parent=parent)
                self.text = text
                self.role = role
                self.language = language

            def run(self):
                from videotrans.tts.azuretts import get_voice
                try:
                    get_voice(text=self.text, role=self.role, rate="+0%", language=self.language, set_p=False,
                              filename=config.homedir + "/test.mp3")

                    self.uito.emit("ok")
                except Exception as e:
                    self.uito.emit(str(e))

        def feed(d):
            if d == "ok":
                tools.pygameaudio(config.homedir + "/test.mp3")
                QtWidgets.QMessageBox.information(self.main.aztw, "ok", "Test Ok")
            else:
                QtWidgets.QMessageBox.critical(self.main.aztw, config.transobj['anerror'], d)
            self.main.aztw.test.setText('测试' if config.defaulelang == 'zh' else 'Test')

        def test():
            key = self.main.aztw.speech_key.text().strip()
            if not key:
                QtWidgets.QMessageBox.critical(self.main.aztw, config.transobj['anerror'], '填写Azure speech key ')
                return
            region = self.main.aztw.speech_region.text().strip()
            if not region or not region.startswith('https:'):
                region = self.main.aztw.azuretts_area.currentText()

            config.params['azure_speech_key'] = key
            config.params['azure_speech_region'] = region

            task = TestTTS(parent=self.main.aztw,
                           text="你好啊我的朋友" if config.defaulelang == 'zh' else 'hello,my friend',
                           role="zh-CN-YunjianNeural" if config.defaulelang == 'zh' else 'en-US-AvaNeural',
                           language="zh-CN" if config.defaulelang == 'zh' else 'en-US'
                           )
            self.main.aztw.test.setText('测试中请稍等...' if config.defaulelang == 'zh' else 'Testing...')
            task.uito.connect(feed)
            task.start()

        def save():
            key = self.main.aztw.speech_key.text()
            region = self.main.aztw.speech_region.text().strip()
            if not region or not region.startswith('https:'):
                region = self.main.aztw.azuretts_area.currentText()

            config.params['azure_speech_key'] = key
            config.params['azure_speech_region'] = region
            config.getset_params(config.params)
            self.main.aztw.close()

        from videotrans.component import AzurettsForm
        self.main.aztw = AzurettsForm()
        if config.params['azure_speech_region'] and config.params['azure_speech_region'].startswith('http'):
            self.main.aztw.speech_region.setText(config.params['azure_speech_region'])
        else:
            self.main.aztw.azuretts_area.setCurrentText(config.params['azure_speech_region'])
        if config.params['azure_speech_key']:
            self.main.aztw.speech_key.setText(config.params['azure_speech_key'])
        self.main.aztw.save.clicked.connect(save)
        self.main.aztw.test.clicked.connect(test)
        self.main.aztw.show()

    def set_elevenlabs_key(self):
        def save():
            key = self.main.ew.elevenlabstts_key.text()
            config.params['elevenlabstts_key'] = key
            config.getset_params(config.params)
            self.main.ew.close()

        from videotrans.component import ElevenlabsForm
        self.main.ew = ElevenlabsForm()
        if config.params['elevenlabstts_key']:
            self.main.ew.elevenlabstts_key.setText(config.params['elevenlabstts_key'])
        self.main.ew.set.clicked.connect(save)
        self.main.ew.show()

    def set_clone_address(self):
        class TestTTS(QThread):
            uito = Signal(str)

            def __init__(self, *, parent=None, text=None, language=None, role=None):
                super().__init__(parent=parent)
                self.text = text
                self.language = language
                self.role = role

            def run(self):
                from videotrans.tts.clone import get_voice
                try:
                    tools.get_clone_role(True)
                    if len(config.params["clone_voicelist"]) < 2:
                        raise Exception('没有可供测试的声音')
                    get_voice(text=self.text, language=self.language, role=config.params["clone_voicelist"][1],
                              set_p=False,
                              filename=config.homedir + "/test.mp3")

                    self.uito.emit("ok")
                except Exception as e:
                    self.uito.emit(str(e))

        def feed(d):
            if d == "ok":
                tools.pygameaudio(config.homedir + "/test.mp3")
                QtWidgets.QMessageBox.information(self.main.clonw, "ok", "Test Ok")
            else:
                QtWidgets.QMessageBox.critical(self.main.clonw, config.transobj['anerror'], d)
            self.main.clonw.test.setText('测试' if config.defaulelang == 'zh' else 'Test')

        def test():
            if not self.main.clonw.clone_address.text().strip():
                QtWidgets.QMessageBox.critical(self.main.clonw, config.transobj['anerror'], '必须填写http地址')
                return
            config.params['clone_api'] = self.main.clonw.clone_address.text().strip()
            task = TestTTS(parent=self.main.clonw,
                           text="你好啊我的朋友" if config.defaulelang == 'zh' else 'hello,my friend'
                           , language="zh-cn" if config.defaulelang == 'zh' else 'en')
            self.main.clonw.test.setText('测试中请稍等...' if config.defaulelang == 'zh' else 'Testing...')
            task.uito.connect(feed)
            task.start()

        def save():
            key = self.main.clonw.clone_address.text().strip()
            key = key.rstrip('/')
            key = 'http://' + key.replace('http://', '')
            config.params["clone_api"] = key
            config.getset_params(config.params)
            self.main.clonw.close()

        from videotrans.component import CloneForm
        self.main.clonw = CloneForm()
        if config.params["clone_api"]:
            self.main.clonw.clone_address.setText(config.params["clone_api"])
        self.main.clonw.set_clone.clicked.connect(save)
        self.main.clonw.test.clicked.connect(test)
        self.main.clonw.show()

    def set_chattts_address(self):
        class TestTTS(QThread):
            uito = Signal(str)

            def __init__(self, *, parent=None, text=None):
                super().__init__(parent=parent)
                self.text = text

            def run(self):
                from videotrans.tts.chattts import get_voice
                try:
                    get_voice(text=self.text, role="boy1", set_p=False, filename=config.homedir + "/test.mp3")

                    self.uito.emit("ok")
                except Exception as e:
                    self.uito.emit(str(e))

        def feed(d):
            if d == "ok":
                tools.pygameaudio(config.homedir + "/test.mp3")
                QtWidgets.QMessageBox.information(self.main.chatttsw, "ok", "Test Ok")
            else:
                QtWidgets.QMessageBox.critical(self.main.chatttsw, config.transobj['anerror'], d)
            self.main.chatttsw.test.setText('测试' if config.defaulelang == 'zh' else 'Test')

        def test():
            if not self.main.chatttsw.chattts_address.text().strip():
                QtWidgets.QMessageBox.critical(self.main.chatttsw, config.transobj['anerror'], '必须填写http地址')
                return
            apiurl = self.main.chatttsw.chattts_address.text().strip()
            if not apiurl:
                return QtWidgets.QMessageBox.critical(self.main.llmw, config.transobj['anerror'],
                                                      '必须填写api地址' if config.defaulelang == 'zh' else 'Please input ChatTTS API url')

            config.params['chattts_api'] = apiurl
            task = TestTTS(parent=self.main.chatttsw,
                           text="你好啊我的朋友" if config.defaulelang == 'zh' else 'hello,my friend'
                           )
            self.main.chatttsw.test.setText('测试中请稍等...' if config.defaulelang == 'zh' else 'Testing...')
            task.uito.connect(feed)
            task.start()

        def save():
            key = self.main.chatttsw.chattts_address.text().strip()
            voice = self.main.chatttsw.chattts_voice.text().strip()
            key = key.rstrip('/')
            key = 'http://' + key.replace('http://', '').replace('/tts', '')
            config.params["chattts_api"] = key
            config.getset_params(config.params)
            config.settings['chattts_voice']=voice
            json.dump(config.settings, open(config.rootdir + "/videotrans/cfg.json", 'w', encoding='utf-8'),ensure_ascii=False)
            
            self.main.chatttsw.close()

        from videotrans.component import ChatttsForm
        self.main.chatttsw = ChatttsForm()
        if config.params["chattts_api"]:
            self.main.chatttsw.chattts_address.setText(config.params["chattts_api"])
        if config.settings["chattts_voice"]:
            self.main.chatttsw.chattts_voice.setText(config.settings["chattts_voice"])
        self.main.chatttsw.set_chattts.clicked.connect(save)
        self.main.chatttsw.test.clicked.connect(test)
        self.main.chatttsw.show()

    def set_ai302tts_address(self):
        class TestTTS(QThread):
            uito = Signal(str)

            def __init__(self, *, parent=None, text=None):
                super().__init__(parent=parent)
                self.text = text

            def run(self):
                from videotrans.tts.ai302tts import get_voice
                try:
                    get_voice(
                        text="你好啊我的朋友" if config.defaulelang == 'zh' else 'hello,my friend',
                        role="zh-CN-YunjianNeural" if config.defaulelang == 'zh' else 'en-US-AvaNeural',
                        language="zh-CN" if config.defaulelang == 'zh' else 'en-US',
                        rate='+0%',
                        set_p=False, filename=config.homedir + "/test.mp3")
                    self.uito.emit("ok")
                except Exception as e:
                    self.uito.emit(str(e))

        def feed(d):
            if d == "ok":
                tools.pygameaudio(config.homedir + "/test.mp3")
                QtWidgets.QMessageBox.information(self.main.ai302ttsw, "ok", "Test Ok")
            else:
                QtWidgets.QMessageBox.critical(self.main.ai302ttsw, config.transobj['anerror'], d)
            self.main.ai302ttsw.test_ai302tts.setText('测试')

        def test():
            key = self.main.ai302ttsw.ai302tts_key.text().strip()
            model = self.main.ai302ttsw.ai302tts_model.currentText()
            if not key or not model:
                return QtWidgets.QMessageBox.critical(self.main.ai302ttsw, config.transobj['anerror'],
                                                      '必须填写 302.ai 的API KEY 和 model')
            config.params["ai302tts_key"] = key
            config.params["ai302tts_model"] = model
            task = TestTTS(parent=self.main.ai302ttsw, text="你好啊我的朋友")
            self.main.ai302ttsw.test_ai302tts.setText('测试中请稍等...')
            task.uito.connect(feed)
            task.start()

        def save():
            key = self.main.ai302ttsw.ai302tts_key.text().strip()
            model = self.main.ai302ttsw.ai302tts_model.currentText()
            config.params["ai302tts_key"] = key
            config.params["ai302tts_model"] = model
            config.getset_params(config.params)
            self.main.ai302ttsw.close()

        def setallmodels():
            t = self.main.ai302ttsw.edit_allmodels.toPlainText().strip().replace('，', ',').rstrip(',')
            current_text = self.main.ai302ttsw.ai302tts_model.currentText()
            self.main.ai302ttsw.ai302tts_model.clear()
            self.main.ai302ttsw.ai302tts_model.addItems([x for x in t.split(',') if x.strip()])
            if current_text:
                self.main.ai302ttsw.ai302tts_model.setCurrentText(current_text)
            config.settings['ai302tts_models'] = t
            json.dump(config.settings, open(config.rootdir + '/videotrans/cfg.json', 'w', encoding='utf-8'),
                      ensure_ascii=False)

        from videotrans.component import AI302TTSForm
        self.main.ai302ttsw = AI302TTSForm()

        allmodels_str = config.settings['ai302tts_models']
        allmodels = config.settings['ai302tts_models'].split(',')
        self.main.ai302ttsw.ai302tts_model.clear()
        self.main.ai302ttsw.ai302tts_model.addItems(allmodels)
        self.main.ai302ttsw.edit_allmodels.setPlainText(allmodels_str)
        if config.params["ai302tts_model"] and config.params["ai302tts_model"] in allmodels:
            self.main.ai302ttsw.ai302tts_model.setCurrentText(config.params["ai302tts_model"])
        if config.params["ai302tts_key"]:
            self.main.ai302ttsw.ai302tts_key.setText(config.params["ai302tts_key"])
        self.main.ai302ttsw.edit_allmodels.textChanged.connect(setallmodels)
        self.main.ai302ttsw.set_ai302tts.clicked.connect(save)
        self.main.ai302ttsw.test_ai302tts.clicked.connect(test)
        self.main.ai302ttsw.show()

    def set_doubao(self):

        def save():
            appid = self.main.doubaow.doubao_appid.text()

            access = self.main.doubaow.doubao_access.text()
            config.params["doubao_appid"] = appid
            config.params["doubao_access"] = access
            config.getset_params(config.params)

            self.main.doubaow.close()

        from videotrans.component import DoubaoForm
        self.main.doubaow = DoubaoForm()
        if config.params["doubao_appid"]:
            self.main.doubaow.doubao_appid.setText(config.params["doubao_appid"])
        if config.params["doubao_access"]:
            self.main.doubaow.doubao_access.setText(config.params["doubao_access"])

        self.main.doubaow.set_save.clicked.connect(save)
        self.main.doubaow.show()

    def set_ttsapi(self):
        class TestTTS(QThread):
            uito = Signal(str)

            def __init__(self, *, parent=None, text=None, language=None, rate="+0%", role=None):
                super().__init__(parent=parent)
                self.text = text
                self.language = language
                self.rate = rate
                self.role = role

            def run(self):

                from videotrans.tts.ttsapi import get_voice
                try:

                    get_voice(text=self.text, language=self.language, rate=self.rate, role=self.role, set_p=False,
                              filename=config.homedir + "/test.mp3")

                    self.uito.emit("ok")
                except Exception as e:
                    self.uito.emit(str(e))

        def feed(d):
            if d == "ok":
                tools.pygameaudio(config.homedir + "/test.mp3")
                QtWidgets.QMessageBox.information(self.main.ttsapiw, "ok", "Test Ok")
            else:
                QtWidgets.QMessageBox.critical(self.main.ttsapiw, config.transobj['anerror'], d)
            self.main.ttsapiw.test.setText('测试api' if config.defaulelang == 'zh' else 'Test api')

        def test():
            url = self.main.ttsapiw.api_url.text()
            extra = self.main.ttsapiw.extra.text()
            role = self.main.ttsapiw.voice_role.text().strip()

            config.params["ttsapi_url"] = url
            config.params["ttsapi_extra"] = extra
            config.params["ttsapi_voice_role"] = role

            task = TestTTS(parent=self.main.ttsapiw,
                           text="你好啊我的朋友" if config.defaulelang == 'zh' else 'hello,my friend',
                           role=self.main.ttsapiw.voice_role.text().strip().split(',')[0],
                           language="zh-cn" if config.defaulelang == 'zh' else 'en')
            self.main.ttsapiw.test.setText('测试中请稍等...' if config.defaulelang == 'zh' else 'Testing...')
            task.uito.connect(feed)
            task.start()

        def save():
            url = self.main.ttsapiw.api_url.text()
            extra = self.main.ttsapiw.extra.text()
            role = self.main.ttsapiw.voice_role.text().strip()

            config.params["ttsapi_url"] = url
            config.params["ttsapi_extra"] = extra
            config.params["ttsapi_voice_role"] = role
            config.getset_params(config.params)
            self.main.ttsapiw.close()

        from videotrans.component import TtsapiForm
        self.main.ttsapiw = TtsapiForm()
        if config.params["ttsapi_url"]:
            self.main.ttsapiw.api_url.setText(config.params["ttsapi_url"])
        if config.params["ttsapi_voice_role"]:
            self.main.ttsapiw.voice_role.setText(config.params["ttsapi_voice_role"])
        if config.params["ttsapi_extra"]:
            self.main.ttsapiw.extra.setText(config.params["ttsapi_extra"])

        self.main.ttsapiw.save.clicked.connect(save)
        self.main.ttsapiw.test.clicked.connect(test)
        self.main.ttsapiw.otherlink.clicked.connect(lambda: self.main.util.open_url('openvoice'))
        self.main.ttsapiw.otherlink.setCursor(Qt.PointingHandCursor)
        self.main.ttsapiw.show()

    def set_gptsovits(self):
        class TestTTS(QThread):
            uito = Signal(str)

            def __init__(self, *, parent=None, text=None, language=None, role=None):
                super().__init__(parent=parent)
                self.text = text
                self.language = language
                self.role = role

            def run(self):
                from videotrans.tts.gptsovits import get_voice
                try:
                    get_voice(text=self.text, language=self.language, set_p=False, role=self.role,
                              filename=config.homedir + "/test.wav")
                    self.uito.emit("ok")
                except Exception as e:
                    self.uito.emit(str(e))

        def feed(d):
            if d == "ok":
                tools.pygameaudio(config.homedir + "/test.wav")
                QtWidgets.QMessageBox.information(self.main.gptsovitsw, "ok", "Test Ok")
            else:
                QtWidgets.QMessageBox.critical(self.main.gptsovitsw, config.transobj['anerror'], d)
            self.main.gptsovitsw.test.setText('测试api')

        def test():
            url = self.main.gptsovitsw.api_url.text()
            config.params["gptsovits_url"] = url
            task = TestTTS(parent=self.main.gptsovitsw,
                           text="你好啊我的朋友",
                           role=getrole(),
                           language="zh")
            self.main.gptsovitsw.test.setText('测试中请稍等...')
            task.uito.connect(feed)
            task.start()

        def getrole():
            tmp = self.main.gptsovitsw.role.toPlainText().strip()
            role = None
            if not tmp:
                return role

            for it in tmp.split("\n"):
                s = it.strip().split('#')
                if len(s) != 3:
                    QtWidgets.QMessageBox.critical(self.main.gptsovitsw, config.transobj['anerror'],
                                                   "每行都必须以#分割为三部分，格式为   音频名称.wav#音频文字内容#音频语言代码")
                    return
                if not s[0].endswith(".wav"):
                    QtWidgets.QMessageBox.critical(self.main.gptsovitsw, config.transobj['anerror'],
                                                   "每行都必须以#分割为三部分，格式为  音频名称.wav#音频文字内容#音频语言代码 ,并且第一部分为.wav结尾的音频名称")
                    return
                if s[2] not in ['zh', 'ja', 'en']:
                    QtWidgets.QMessageBox.critical(self.main.gptsovitsw, config.transobj['anerror'],
                                                   "每行必须以#分割为三部分，格式为 音频名称.wav#音频文字内容#音频语言代码 ,并且第三部分语言代码只能是 zh或en或ja")
                    return
                role = s[0]
            config.params['gptsovits_role'] = tmp
            return role

        def save():
            url = self.main.gptsovitsw.api_url.text()
            extra = self.main.gptsovitsw.extra.text()
            role = self.main.gptsovitsw.role.toPlainText().strip()

            config.params["gptsovits_url"] = url
            config.params["gptsovits_extra"] = extra
            config.params["gptsovits_role"] = role
            config.getset_params(config.params)

            self.main.gptsovitsw.close()

        from videotrans.component import GPTSoVITSForm
        self.main.gptsovitsw = GPTSoVITSForm()
        if config.params["gptsovits_url"]:
            self.main.gptsovitsw.api_url.setText(config.params["gptsovits_url"])
        if config.params["gptsovits_extra"]:
            self.main.gptsovitsw.extra.setText(config.params["gptsovits_extra"])
        if config.params["gptsovits_role"]:
            self.main.gptsovitsw.role.setPlainText(config.params["gptsovits_role"])

        self.main.gptsovitsw.save.clicked.connect(save)
        self.main.gptsovitsw.test.clicked.connect(test)
        self.main.gptsovitsw.show()

    def set_cosyvoice(self):
        class TestTTS(QThread):
            uito = Signal(str)

            def __init__(self, *, parent=None, text=None, role=None):
                super().__init__(parent=parent)
                self.text = text
                self.role = role

            def run(self):
                from videotrans.tts.cosyvoice import get_voice
                try:
                    get_voice(text=self.text, set_p=False, role=self.role, language='zh',
                              filename=config.homedir + "/test.wav")
                    self.uito.emit("ok")
                except Exception as e:
                    self.uito.emit(str(e))

        def feed(d):
            if d == "ok":
                tools.pygameaudio(config.homedir + "/test.wav")
                QtWidgets.QMessageBox.information(self.main.cosyvoicew, "ok", "Test Ok")
            else:
                QtWidgets.QMessageBox.critical(self.main.cosyvoicew, config.transobj['anerror'], d)
            self.main.cosyvoicew.test.setText('测试api')

        def test():
            url = self.main.cosyvoicew.api_url.text()
            config.params["cosyvoice_url"] = url
            task = TestTTS(parent=self.main.cosyvoicew,
                           text="你好啊我的朋友",
                           role=getrole())
            self.main.cosyvoicew.test.setText('测试中请稍等...')
            task.uito.connect(feed)
            task.start()

        def getrole():
            tmp = self.main.cosyvoicew.role.toPlainText().strip()
            role = None
            if not tmp:
                return role

            for it in tmp.split("\n"):
                s = it.strip().split('#')
                if len(s) != 2:
                    QtWidgets.QMessageBox.critical(self.main.cosyvoicew, config.transobj['anerror'],
                                                   "每行都必须以#分割为2部分，格式为  音频名称.wav#音频文字内容,并且第一部分为.wav结尾的音频名称")
                    return

                role = s[0]
            config.params['cosyvoice_role'] = tmp
            return role

        def save():
            url = self.main.cosyvoicew.api_url.text()

            role = self.main.cosyvoicew.role.toPlainText().strip()

            config.params["cosyvoice_url"] = url

            config.params["cosyvoice_role"] = role
            config.getset_params(config.params)

            self.main.cosyvoicew.close()

        from videotrans.component import CosyVoiceForm
        self.main.cosyvoicew = CosyVoiceForm()
        if config.params["cosyvoice_url"]:
            self.main.cosyvoicew.api_url.setText(config.params["cosyvoice_url"])
        if config.params["cosyvoice_role"]:
            self.main.cosyvoicew.role.setPlainText(config.params["cosyvoice_role"])

        self.main.cosyvoicew.save.clicked.connect(save)
        self.main.cosyvoicew.test.clicked.connect(test)
        self.main.cosyvoicew.show()

    def set_fishtts(self):
        class TestTTS(QThread):
            uito = Signal(str)

            def __init__(self, *, parent=None, text=None, role=None):
                super().__init__(parent=parent)
                self.text = text
                self.role = role

            def run(self):
                from videotrans.tts.fishtts import get_voice
                try:
                    get_voice(text=self.text, set_p=False, role=self.role,
                              filename=config.homedir + "/test.wav")
                    self.uito.emit("ok")
                except Exception as e:
                    self.uito.emit(str(e))

        def feed(d):
            if d == "ok":
                tools.pygameaudio(config.homedir + "/test.wav")
                QtWidgets.QMessageBox.information(self.main.fishttsw, "ok", "Test Ok")
            else:
                QtWidgets.QMessageBox.critical(self.main.fishttsw, config.transobj['anerror'], d)
            self.main.fishttsw.test.setText('测试api')

        def test():
            url = self.main.fishttsw.api_url.text()
            config.params["fishtts_url"] = url
            task = TestTTS(parent=self.main.fishttsw,
                           text="你好啊我的朋友",
                           role=getrole())
            self.main.fishttsw.test.setText('测试中请稍等...')
            task.uito.connect(feed)
            task.start()

        def getrole():
            tmp = self.main.fishttsw.role.toPlainText().strip()
            role = None
            if not tmp:
                return role

            for it in tmp.split("\n"):
                s = it.strip().split('#')
                if len(s) != 2:
                    QtWidgets.QMessageBox.critical(self.main.fishttsw, config.transobj['anerror'],
                                                   "每行都必须以#分割为2部分，格式为   音频名称.wav#音频文字内容")
                    return
                if not s[0].endswith(".wav"):
                    QtWidgets.QMessageBox.critical(self.main.fishttsw, config.transobj['anerror'],
                                                   "每行都必须以#分割为2部分，格式为  音频名称.wav#音频文字内容")
                    return
                role = s[0]
            config.params['fishtts_role'] = tmp
            return role

        def save():
            url = self.main.fishttsw.api_url.text()
            role = self.main.fishttsw.role.toPlainText().strip()

            config.params["fishtts_url"] = url
            config.params["fishtts_role"] = role

            config.getset_params(config.params)
            self.main.fishttsw.close()

        from videotrans.component import FishTTSForm
        self.main.fishttsw = FishTTSForm()
        if config.params["fishtts_url"]:
            self.main.fishttsw.api_url.setText(config.params["fishtts_url"])
        if config.params["fishtts_role"]:
            self.main.fishttsw.role.setPlainText(config.params["fishtts_role"])

        self.main.fishttsw.save.clicked.connect(save)
        self.main.fishttsw.test.clicked.connect(test)
        self.main.fishttsw.show()

    # 识别

    def set_zh_recogn(self):
        class Test(QThread):
            uito = Signal(str)

            def __init__(self, *, parent=None, text=None, language=None, role=None):
                super().__init__(parent=parent)

            def run(self):
                try:
                    import requests
                    res = requests.get(config.params['zh_recogn_api'])
                    self.uito.emit("ok")
                except Exception as e:
                    self.uito.emit(str(e))

        def feed(d):
            if d == "ok":
                QtWidgets.QMessageBox.information(self.main.zhrecognw, "ok", "Test Ok")
            else:
                QtWidgets.QMessageBox.critical(self.main.zhrecognw, config.transobj['anerror'], d)
            self.main.zhrecognw.test.setText('测试' if config.defaulelang == 'zh' else 'Test')

        def test():
            if not self.main.zhrecognw.zhrecogn_address.text().strip():
                QtWidgets.QMessageBox.critical(self.main.zhrecognw, config.transobj['anerror'], '必须填写http地址')
                return
            config.params['zh_recogn_api'] = self.main.zhrecognw.zhrecogn_address.text().strip()
            task = Test(parent=self.main.zhrecognw)
            self.main.zhrecognw.test.setText('测试中请稍等...' if config.defaulelang == 'zh' else 'Testing...')
            task.uito.connect(feed)
            task.start()

        def save():
            key = self.main.zhrecognw.zhrecogn_address.text().strip()
            key = key.rstrip('/')
            key = 'http://' + key.replace('http://', '')
            config.params["zh_recogn_api"] = key
            config.getset_params(config.params)
            self.main.zhrecognw.close()

        from videotrans.component import ZhrecognForm
        self.main.zhrecognw = ZhrecognForm()
        if config.params["zh_recogn_api"]:
            self.main.zhrecognw.zhrecogn_address.setText(config.params["zh_recogn_api"])
        self.main.zhrecognw.set.clicked.connect(save)
        self.main.zhrecognw.test.clicked.connect(test)
        self.main.zhrecognw.show()

    # 分离背景音

    def open_separate(self):
        def get_file():
            fname, _ = QFileDialog.getOpenFileName(self.main.sepw, "Select audio or video",
                                                   config.params['last_opendir'],
                                                   "files(*.wav *.mp3 *.aac *.m4a *.flac *.mp4 *.mov *.mkv)")
            if fname:
                self.main.sepw.fromfile.setText(fname.replace('file:///', '').replace('\\', '/'))

        def update(d):
            # 更新
            if d == 'succeed':
                self.main.sepw.set.setText(config.transobj['Separate End/Restart'])
                self.main.sepw.fromfile.setText('')
            elif d == 'end':
                self.main.sepw.set.setText(config.transobj['Start Separate'])
            else:
                QMessageBox.critical(self.main.sepw, config.transobj['anerror'], d)

        def start():
            if config.separate_status == 'ing':
                config.separate_status = 'stop'
                self.main.sepw.set.setText(config.transobj['Start Separate'])
                return
            # 开始处理分离，判断是否选择了源文件
            file = self.main.sepw.fromfile.text()
            if not file or not os.path.exists(file):
                QMessageBox.critical(self.main.sepw, config.transobj['anerror'],
                                     config.transobj['must select audio or video file'])
                return
            self.main.sepw.set.setText(config.transobj['Start Separate...'])
            basename = os.path.basename(file)
            # 判断名称是否正常
            rs, newfile, base = tools.rename_move(file, is_dir=False)
            if rs:
                file = newfile
                basename = base
            # 创建文件夹
            out = os.path.join(outdir, basename).replace('\\', '/')
            os.makedirs(out, exist_ok=True)
            self.main.sepw.url.setText(out)
            # 开始分离
            config.separate_status = 'ing'
            self.main.sepw.task = SeparateWorker(parent=self.main.sepw, out=out, file=file, basename=basename)
            self.main.sepw.task.finish_event.connect(update)
            self.main.sepw.task.start()

        from videotrans.component import SeparateForm
        try:
            if self.main.sepw is not None:
                self.main.sepw.show()
                return
            self.main.sepw = SeparateForm()
            self.main.sepw.set.setText(config.transobj['Start Separate'])
            outdir = os.path.join(config.homedir, 'separate').replace('\\', '/')
            if not os.path.exists(outdir):
                os.makedirs(outdir, exist_ok=True)
            # 创建事件过滤器实例并将其安装到 lineEdit 上
            self.main.sepw.url.setText(outdir)

            self.main.sepw.selectfile.clicked.connect(get_file)

            self.main.sepw.set.clicked.connect(start)
            self.main.sepw.show()
        except Exception:
            pass

    # 合并2个srt
    def open_hebingsrt(self):
        class CompThread(QThread):
            uito = Signal(str)

            def __init__(self, *, parent=None, file1=None, file2=None):
                super().__init__(parent=parent)
                self.file1 = file1
                self.file2 = file2
                self.result_dir = config.homedir + "/Mergersrt"
                os.makedirs(self.result_dir, exist_ok=True)
                self.result_file = self.result_dir + "/" + os.path.splitext(os.path.basename(file1))[0] + '-plus-' + \
                                   os.path.splitext(os.path.basename(file2))[0] + '.srt'

            def run(self):
                try:
                    text = ""
                    srt1_list = tools.get_subtitle_from_srt(self.file1)
                    srt2_list = tools.get_subtitle_from_srt(self.file2)
                    srt2_len = len(srt2_list)
                    for i, it in enumerate(srt1_list):
                        text += f"{it['line']}\n{it['time']}\n{it['text'].strip()}"
                        if i < srt2_len:
                            text += f"\n{srt2_list[i]['text'].strip()}"
                        text += "\n\n"
                    with open(self.result_file, 'w', encoding="utf-8", errors="ignore") as f:
                        f.write(text.strip())

                    self.uito.emit(self.result_file)
                except Exception as e:
                    self.uito.emit('error:' + str(e))

        def feed(d):
            if d.startswith("error:"):
                QtWidgets.QMessageBox.critical(self.main.hew, config.transobj['anerror'], d)
            else:
                self.main.hew.startbtn.setText('开始执行合并' if config.defaulelang == 'zh' else 'commencement of execution')
                self.main.hew.startbtn.setDisabled(False)
                self.main.hew.resultlabel.setText(d)
                self.main.hew.resultbtn.setDisabled(False)
                with open(self.main.hew.resultlabel.text(), 'r', encoding='utf-8') as f:
                    self.main.hew.resultinput.setPlainText(f.read())

        def get_file(inputname):
            fname, _ = QFileDialog.getOpenFileName(self.main.hew, "Select subtitles srt", config.params['last_opendir'],
                                                   "files(*.srt)")
            if fname:
                if inputname == 1:
                    self.main.hew.srtinput1.setText(fname.replace('file:///', '').replace('\\', '/'))
                else:
                    self.main.hew.srtinput2.setText(fname.replace('file:///', '').replace('\\', '/'))

        def start():
            # 开始处理分离，判断是否选择了源文件
            srt1 = self.main.hew.srtinput1.text()
            srt2 = self.main.hew.srtinput2.text()
            if not srt1 or not srt2:
                QMessageBox.critical(self.main.hew, config.transobj['anerror'],
                                     '必须选择字幕文件1和字幕文件2' if config.defaulelang == 'zh' else 'Subtitle File 1 and Subtitle File 2 must be selected')
                return

            self.main.hew.startbtn.setText('执行合并中...' if config.defaulelang == 'zh' else 'Consolidation in progress...')
            self.main.hew.startbtn.setDisabled(True)
            self.main.hew.resultbtn.setDisabled(True)
            self.main.hew.resultinput.setPlainText("")

            task = CompThread(parent=self.main.hew, file1=srt1, file2=srt2)

            task.uito.connect(feed)
            task.start()

        def opendir():
            filepath = self.main.hew.resultlabel.text()
            if not filepath:
                return QMessageBox.critical(self.main.hew, config.transobj['anerror'],
                                            '尚未生成合并字幕' if config.defaulelang == 'zh' else 'Combined subtitles not yet generated')
            QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.dirname(filepath)))

        from videotrans.component import HebingsrtForm
        try:
            if self.main.hew is not None:
                self.main.hew.show()
                return
            self.main.hew = HebingsrtForm()
            self.main.hew.srtbtn1.clicked.connect(lambda: get_file(1))
            self.main.hew.srtbtn2.clicked.connect(lambda: get_file(2))

            self.main.hew.resultbtn.clicked.connect(opendir)
            self.main.hew.startbtn.clicked.connect(start)
            self.main.hew.show()
        except Exception:
            pass

    # 设置每行角色
    def set_line_role_fun(self):
        def get_checked_boxes(widget):
            checked_boxes = []
            for child in widget.children():
                if isinstance(child, QtWidgets.QCheckBox) and child.isChecked():
                    checked_boxes.append(child.objectName())
                else:
                    checked_boxes.extend(get_checked_boxes(child))
            return checked_boxes

        def save(role):
            # 初始化一个列表，用于存放所有选中 checkbox 的名字
            checked_checkbox_names = get_checked_boxes(self.main.row)

            if len(checked_checkbox_names) < 1:
                return QtWidgets.QMessageBox.critical(self.main.row, config.transobj['anerror'],
                                                      config.transobj['zhishaoxuanzeyihang'])

            for n in checked_checkbox_names:
                _, line = n.split('_')
                # 设置labe为角色名
                ck = self.main.row.findChild(QtWidgets.QCheckBox, n)
                ck.setText(config.transobj['default'] if role in ['No', 'no', '-'] else role)
                ck.setChecked(False)
                config.params['line_roles'][line] = config.params['voice_role'] if role in ['No', 'no', '-'] else role

        from videotrans.component import SetLineRole
        self.main.row = SetLineRole()
        box = QtWidgets.QWidget()  # 创建新的 QWidget，它将承载你的 QHBoxLayouts
        box.setLayout(QtWidgets.QVBoxLayout())  # 设置 QVBoxLayout 为新的 QWidget 的layout
        if config.params['voice_role'] in ['No', '-', 'no']:
            return QtWidgets.QMessageBox.critical(self.main.row, config.transobj['anerror'],
                                                  config.transobj['xianxuanjuese'])
        if not self.main.subtitle_area.toPlainText().strip():
            return QtWidgets.QMessageBox.critical(self.main.row, config.transobj['anerror'],
                                                  config.transobj['youzimuyouset'])

        #  获取字幕
        srt_json = tools.get_subtitle_from_srt(self.main.subtitle_area.toPlainText().strip(), is_file=False)
        for it in srt_json:
            # 创建新水平布局
            h_layout = QtWidgets.QHBoxLayout()
            check = QtWidgets.QCheckBox()
            check.setText(
                config.params['line_roles'][f'{it["line"]}'] if f'{it["line"]}' in config.params['line_roles'] else
                config.transobj['default'])
            check.setObjectName(f'check_{it["line"]}')
            # 创建并配置 QLineEdit
            line_edit = QtWidgets.QLineEdit()
            line_edit.setPlaceholderText(config.transobj['shezhijueseline'])

            line_edit.setText(f'[{it["line"]}] {it["text"]}')
            line_edit.setReadOnly(True)
            # 将标签和编辑线添加到水平布局
            h_layout.addWidget(check)
            h_layout.addWidget(line_edit)
            box.layout().addLayout(h_layout)
        box.layout().setAlignment(Qt.AlignmentFlag.AlignTop)
        self.main.row.select_role.addItems(self.main.current_rolelist)
        self.main.row.set_role_label.setText(config.transobj['shezhijuese'])

        self.main.row.select_role.currentTextChanged.connect(save)
        # 创建 QScrollArea 并将 box QWidget 设置为小部件
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidget(box)
        scroll_area.setWidgetResizable(True)
        scroll_area.setAlignment(Qt.AlignmentFlag.AlignTop)

        # 将 QScrollArea 添加到主窗口的 layout
        self.main.row.layout.addWidget(scroll_area)

        self.main.row.set_ok.clicked.connect(lambda: self.main.row.close())
        self.main.row.show()

    # 下载
    def open_youtube(self):
        def download():
            proxy = self.main.youw.proxy.text().strip()
            outdir = self.main.youw.outputdir.text()
            url = self.main.youw.url.text().strip()
            vid = self.main.youw.formatname.isChecked()
            if not url or not re.match(r'^https://(www.)?(youtube.com/(watch|shorts)|youtu.be/\w)', url, re.I):
                QtWidgets.QMessageBox.critical(self.main.youw, config.transobj['anerror'],
                                               config.transobj[
                                                   'You must fill in the YouTube video playback page address'])
                return
            if proxy:
                config.params['proxy'] = proxy
            from videotrans.task.download_youtube import Download
            down = Download(proxy=proxy, url=url, out=outdir, parent=self.main, vid=vid)
            down.start()
            self.main.youw.set.setText(config.transobj["downing..."])

        def selectdir():
            dirname = QtWidgets.QFileDialog.getExistingDirectory(self.main, "Select Dir", outdir).replace('\\', '/')
            self.main.youw.outputdir.setText(dirname)

        from videotrans.component import YoutubeForm
        self.main.youw = YoutubeForm()
        self.main.youw.set.setText(config.transobj['start download'])
        self.main.youw.selectdir.setText(config.transobj['Select Out Dir'])
        outdir = config.params['youtube_outdir'] if 'youtube_outdir' in config.params else os.path.join(config.homedir,
                                                                                                        'youtube').replace(
            '\\', '/')
        if not os.path.exists(outdir):
            os.makedirs(outdir, exist_ok=True)
        # 创建事件过滤器实例并将其安装到 lineEdit 上

        self.main.youw.outputdir.setText(outdir)
        if config.params['proxy']:
            self.main.youw.proxy.setText(config.params['proxy'])
        self.main.youw.selectdir.clicked.connect(selectdir)

        self.main.youw.set.clicked.connect(download)
        self.main.youw.show()

    # 高级设置
    def open_setini(self):
        def save():
            # 创建一个空字典来存储结果
            line_edit_dict = {}

            # 使用findChildren方法查找所有QLineEdit控件
            line_edits = self.main.setiniw.findChildren(QLineEdit)
            # 遍历找到的所有QLineEdit控件
            for line_edit in line_edits:
                # 检查QLineEdit是否有objectName
                if hasattr(line_edit, 'objectName') and line_edit.objectName():
                    name = line_edit.objectName()
                    # 将objectName作为key，text作为value添加到字典中
                    line_edit_dict[name] = line_edit.text()
            try:
                json.dump(line_edit_dict, open(config.rootdir + "/videotrans/cfg.json", 'w', encoding='utf-8'),
                          ensure_ascii=False)
            except Exception as e:
                return QtWidgets.QMessageBox.critical(self.main.setiniw, config.transobj['anerror'], str(e))
            else:
                config.settings = line_edit_dict

            self.main.setiniw.close()

        def alert(btn):
            name = btn.objectName()[4:]
            QMessageBox.information(self.main.setiniw, f'Help {name}', self.main.setiniw.notices[name])

        from videotrans.component import SetINIForm
        self.main.setiniw = SetINIForm()
        for button in self.main.setiniw.findChildren(QPushButton):
            if button.objectName().startswith('btn_'):
                # 绑定clicked事件，lambda表达式传递按钮本身
                button.clicked.connect(lambda checked, btn=button: alert(btn))

        self.main.setiniw.set_ok.clicked.connect(save)
        self.main.setiniw.show()

    # 翻译

    # set deepl key
    def set_deepL_key(self):
        def save():
            key = self.main.dlw.deepl_authkey.text()
            api = self.main.dlw.deepl_api.text().strip()
            config.params['deepl_authkey'] = key
            config.params['deepl_api'] = api
            config.getset_params(config.params)
            self.main.dlw.close()

        from videotrans.component import DeepLForm
        self.main.dlw = DeepLForm()
        if config.params['deepl_authkey']:
            self.main.dlw.deepl_authkey.setText(config.params['deepl_authkey'])
        if config.params['deepl_api']:
            self.main.dlw.deepl_api.setText(config.params['deepl_api'])
        self.main.dlw.set_deepl.clicked.connect(save)
        self.main.dlw.show()

    def set_deepLX_address(self):
        def save():
            key = self.main.dexw.deeplx_address.text()
            config.params["deeplx_address"] = key
            config.getset_params(config.params)
            self.main.dexw.close()

        from videotrans.component import DeepLXForm
        self.main.dexw = DeepLXForm()
        if config.params["deeplx_address"]:
            self.main.dexw.deeplx_address.setText(config.params["deeplx_address"])
        self.main.dexw.set_deeplx.clicked.connect(save)
        self.main.dexw.show()

    def set_ott_address(self):
        def save():
            key = self.main.ow.ott_address.text()
            config.params["ott_address"] = key
            config.getset_params(config.params)
            self.main.ow.close()

        from videotrans.component import OttForm
        self.main.ow = OttForm()
        if config.params["ott_address"]:
            self.main.ow.ott_address.setText(config.params["ott_address"])
        self.main.ow.set_ott.clicked.connect(save)
        self.main.ow.show()

    # set baidu
    def set_baidu_key(self):
        def save_baidu():
            appid = self.main.baw.baidu_appid.text()
            miyue = self.main.baw.baidu_miyue.text()
            config.params["baidu_appid"] = appid
            config.params["baidu_miyue"] = miyue
            config.getset_params(config.params)
            self.main.baw.close()

        from videotrans.component import BaiduForm
        self.main.baw = BaiduForm()
        if config.params["baidu_appid"]:
            self.main.baw.baidu_appid.setText(config.params["baidu_appid"])
        if config.params["baidu_miyue"]:
            self.main.baw.baidu_miyue.setText(config.params["baidu_miyue"])
        self.main.baw.set_badiu.clicked.connect(save_baidu)
        self.main.baw.show()

    def set_tencent_key(self):
        def save():
            SecretId = self.main.tew.tencent_SecretId.text()
            SecretKey = self.main.tew.tencent_SecretKey.text()
            config.params["tencent_SecretId"] = SecretId
            config.params["tencent_SecretKey"] = SecretKey
            config.getset_params(config.params)
            self.main.tew.close()

        from videotrans.component import TencentForm
        self.main.tew = TencentForm()
        if config.params["tencent_SecretId"]:
            self.main.tew.tencent_SecretId.setText(config.params["tencent_SecretId"])
        if config.params["tencent_SecretKey"]:
            self.main.tew.tencent_SecretKey.setText(config.params["tencent_SecretKey"])
        self.main.tew.set_tencent.clicked.connect(save)
        self.main.tew.show()

    # set chatgpt
    def set_chatgpt_key(self):
        class TestChatgpt(QThread):
            uito = Signal(str)

            def __init__(self, *, parent=None):
                super().__init__(parent=parent)

            def run(self):
                try:
                    from videotrans.translator.chatgpt import trans as trans_chatgpt
                    raw = "你好啊我的朋友" if config.defaulelang != 'zh' else "hello,my friend"
                    text = trans_chatgpt(raw, "English" if config.defaulelang != 'zh' else "Chinese", set_p=False,
                                         is_test=True)
                    self.uito.emit(f"ok:{raw}\n{text}")
                except Exception as e:
                    self.uito.emit(str(e))

        def feed(d):
            if not d.startswith("ok:"):
                QtWidgets.QMessageBox.critical(self.main.w, config.transobj['anerror'], d)
            else:
                QtWidgets.QMessageBox.information(self.main.w, "OK", d[3:])
            self.main.w.test_chatgpt.setText('测试' if config.defaulelang == 'zh' else 'Test')

        def test():
            key = self.main.w.chatgpt_key.text()
            api = self.main.w.chatgpt_api.text().strip()
            api = api if api else 'https://api.openai.com/v1'
            model = self.main.w.chatgpt_model.currentText()
            template = self.main.w.chatgpt_template.toPlainText()

            os.environ['OPENAI_API_KEY'] = key
            config.params["chatgpt_key"] = key
            config.params["chatgpt_api"] = api
            config.params["chatgpt_model"] = model
            config.params["chatgpt_template"] = template

            task = TestChatgpt(parent=self.main.w)
            self.main.w.test_chatgpt.setText('测试中请稍等...' if config.defaulelang == 'zh' else 'Testing...')
            task.uito.connect(feed)
            task.start()
            self.main.w.test_chatgpt.setText('测试中请稍等...' if config.defaulelang == 'zh' else 'Testing...')

        def save_chatgpt():
            key = self.main.w.chatgpt_key.text()
            api = self.main.w.chatgpt_api.text().strip()
            api = api if api else 'https://api.openai.com/v1'
            model = self.main.w.chatgpt_model.currentText()
            template = self.main.w.chatgpt_template.toPlainText()

            with open(config.rootdir + f"/videotrans/chatgpt{'-en' if config.defaulelang != 'zh' else ''}.txt", 'w',
                      encoding='utf-8') as f:
                f.write(template)
            os.environ['OPENAI_API_KEY'] = key
            config.params["chatgpt_key"] = key
            config.params["chatgpt_api"] = api
            config.params["chatgpt_model"] = model
            config.params["chatgpt_template"] = template
            config.getset_params(config.params)
            self.main.w.close()

        def setallmodels():
            t = self.main.w.edit_allmodels.toPlainText().strip().replace('，', ',').rstrip(',')
            current_text = self.main.w.chatgpt_model.currentText()
            self.main.w.chatgpt_model.clear()
            self.main.w.chatgpt_model.addItems([x for x in t.split(',') if x.strip()])
            if current_text:
                self.main.w.chatgpt_model.setCurrentText(current_text)
            config.settings['chatgpt_model'] = t
            json.dump(config.settings, open(config.rootdir + '/videotrans/cfg.json', 'w', encoding='utf-8'),
                      ensure_ascii=False)

        from videotrans.component import ChatgptForm
        self.main.w = ChatgptForm()
        allmodels_str = config.settings['chatgpt_model']
        allmodels = config.settings['chatgpt_model'].split(',')
        self.main.w.chatgpt_model.clear()
        self.main.w.chatgpt_model.addItems(allmodels)
        self.main.w.edit_allmodels.setPlainText(allmodels_str)

        if config.params["chatgpt_key"]:
            self.main.w.chatgpt_key.setText(config.params["chatgpt_key"])
        if config.params["chatgpt_api"]:
            self.main.w.chatgpt_api.setText(config.params["chatgpt_api"])
        if config.params["chatgpt_model"] and config.params['chatgpt_model'] in allmodels:
            self.main.w.chatgpt_model.setCurrentText(config.params["chatgpt_model"])
        if config.params["chatgpt_template"]:
            self.main.w.chatgpt_template.setPlainText(config.params["chatgpt_template"])

        self.main.w.set_chatgpt.clicked.connect(save_chatgpt)
        self.main.w.test_chatgpt.clicked.connect(test)
        self.main.w.edit_allmodels.textChanged.connect(setallmodels)
        self.main.w.show()

    def set_ai302_key(self):
        class TestAI302(QThread):
            uito = Signal(str)

            def __init__(self, *, parent=None):
                super().__init__(parent=parent)

            def run(self):
                try:
                    from videotrans.translator.ai302 import trans as trans_ai302
                    raw = "你好啊我的朋友" if config.defaulelang != 'zh' else "hello,my friend"
                    text = trans_ai302(raw, "English" if config.defaulelang != 'zh' else "Chinese", set_p=False,
                                       is_test=True)
                    self.uito.emit(f"ok:{raw}\n{text}")
                except Exception as e:
                    self.uito.emit(str(e))

        def feed(d):
            if not d.startswith("ok:"):
                QtWidgets.QMessageBox.critical(self.main.ai302fyw, config.transobj['anerror'], d)
            else:
                QtWidgets.QMessageBox.information(self.main.ai302fyw, "OK", d[3:])
            self.main.ai302fyw.test_ai302.setText('测试' if config.defaulelang == 'zh' else 'Test')

        def test():
            key = self.main.ai302fyw.ai302_key.text()
            model = self.main.ai302fyw.ai302_model.currentText()
            template = self.main.ai302fyw.ai302_template.toPlainText()

            config.params["ai302_key"] = key
            config.params["ai302_model"] = model
            config.params["ai302_template"] = template

            task = TestAI302(parent=self.main.ai302fyw)
            self.main.ai302fyw.test_ai302.setText('测试中请稍等...' if config.defaulelang == 'zh' else 'Testing...')
            task.uito.connect(feed)
            task.start()
            self.main.ai302fyw.test_ai302.setText('测试中请稍等...' if config.defaulelang == 'zh' else 'Testing...')

        def save_ai302():
            key = self.main.ai302fyw.ai302_key.text()
            model = self.main.ai302fyw.ai302_model.currentText()
            template = self.main.ai302fyw.ai302_template.toPlainText()

            config.params["ai302_key"] = key
            config.params["ai302_model"] = model
            config.params["ai302_template"] = template
            with open(config.rootdir + f"/videotrans/302ai.txt", 'w', encoding='utf-8') as f:
                f.write(template)
            config.getset_params(config.params)
            self.main.ai302fyw.close()

        def setallmodels():
            t = self.main.ai302fyw.edit_allmodels.toPlainText().strip().replace('，', ',').rstrip(',')
            current_text = self.main.ai302fyw.ai302_model.currentText()
            self.main.ai302fyw.ai302_model.clear()
            self.main.ai302fyw.ai302_model.addItems([x for x in t.split(',') if x.strip()])
            if current_text:
                self.main.ai302fyw.ai302_model.setCurrentText(current_text)
            config.settings['ai302_models'] = t
            json.dump(config.settings, open(config.rootdir + '/videotrans/cfg.json', 'w', encoding='utf-8'),
                      ensure_ascii=False)

        from videotrans.component import AI302Form
        self.main.ai302fyw = AI302Form()
        allmodels_str = config.settings['ai302_models']
        allmodels = config.settings['ai302_models'].split(',')

        self.main.ai302fyw.ai302_model.clear()
        self.main.ai302fyw.ai302_model.addItems(allmodels)
        self.main.ai302fyw.edit_allmodels.setPlainText(allmodels_str)

        if config.params["ai302_key"]:
            self.main.ai302fyw.ai302_key.setText(config.params["ai302_key"])
        if config.params["ai302_model"] and config.params["ai302_model"] in allmodels:
            self.main.ai302fyw.ai302_model.setCurrentText(config.params["ai302_model"])
        if config.params["ai302_template"]:
            self.main.ai302fyw.ai302_template.setPlainText(config.params["ai302_template"])
        self.main.ai302fyw.edit_allmodels.textChanged.connect(setallmodels)
        self.main.ai302fyw.set_ai302.clicked.connect(save_ai302)
        self.main.ai302fyw.test_ai302.clicked.connect(test)
        self.main.ai302fyw.label_0.clicked.connect(lambda: webbrowser.open_new_tab("https://302.ai"))
        self.main.ai302fyw.label_01.clicked.connect(lambda: webbrowser.open_new_tab("https://pyvideotrans.com/302ai"))
        self.main.ai302fyw.show()

    def set_localllm_key(self):
        class TestLocalLLM(QThread):
            uito = Signal(str)

            def __init__(self, *, parent=None):
                super().__init__(parent=parent)

            def run(self):
                try:
                    from videotrans.translator.localllm import trans as trans_localllm
                    raw = "你好啊我的朋友" if config.defaulelang != 'zh' else "hello,my friend"
                    text = trans_localllm(raw, "English" if config.defaulelang != 'zh' else "Chinese", set_p=False,
                                          is_test=True)
                    self.uito.emit(f"ok:{raw}\n{text}")
                except Exception as e:
                    self.uito.emit(str(e))

        def feed(d):
            if not d.startswith("ok:"):
                QtWidgets.QMessageBox.critical(self.main.llmw, config.transobj['anerror'], d)
            else:
                QtWidgets.QMessageBox.information(self.main.llmw, "OK", d[3:])
            self.main.llmw.test_localllm.setText('测试' if config.defaulelang == 'zh' else 'Test')

        def test():
            key = self.main.llmw.localllm_key.text()
            api = self.main.llmw.localllm_api.text().strip()
            if not api:
                return QtWidgets.QMessageBox.critical(self.main.llmw, config.transobj['anerror'],
                                                      '必须填写api地址' if config.defaulelang == 'zh' else 'Please input LLM API url')

            model = self.main.llmw.localllm_model.currentText()
            template = self.main.llmw.localllm_template.toPlainText()

            config.params["localllm_key"] = key
            config.params["localllm_api"] = api
            config.params["localllm_model"] = model
            config.params["localllm_template"] = template

            task = TestLocalLLM(parent=self.main.llmw)
            self.main.llmw.test_localllm.setText('测试中请稍等...' if config.defaulelang == 'zh' else 'Testing...')
            task.uito.connect(feed)
            task.start()

        def save_localllm():
            key = self.main.llmw.localllm_key.text()
            api = self.main.llmw.localllm_api.text().strip()

            model = self.main.llmw.localllm_model.currentText()
            template = self.main.llmw.localllm_template.toPlainText()

            config.params["localllm_key"] = key
            config.params["localllm_api"] = api
            config.params["localllm_model"] = model
            config.params["localllm_template"] = template
            with open(config.rootdir + f"/videotrans/localllm{'-en' if config.defaulelang != 'zh' else ''}.txt", 'w',
                      encoding='utf-8') as f:
                f.write(template)
            config.getset_params(config.params)
            self.main.llmw.close()

        def setallmodels():
            t = self.main.llmw.edit_allmodels.toPlainText().strip().replace('，', ',').rstrip(',')
            current_text = self.main.llmw.localllm_model.currentText()
            self.main.llmw.localllm_model.clear()
            self.main.llmw.localllm_model.addItems([x for x in t.split(',') if x.strip()])
            if current_text:
                self.main.llmw.localllm_model.setCurrentText(current_text)
            config.settings['localllm_model'] = t
            json.dump(config.settings, open(config.rootdir + '/videotrans/cfg.json', 'w', encoding='utf-8'),
                      ensure_ascii=False)

        from videotrans.component import LocalLLMForm
        self.main.llmw = LocalLLMForm()
        allmodels_str = config.settings['localllm_model']
        allmodels = config.settings['localllm_model'].split(',')
        self.main.llmw.localllm_model.clear()
        self.main.llmw.localllm_model.addItems(allmodels)
        self.main.llmw.edit_allmodels.setPlainText(allmodels_str)
        if config.params["localllm_key"]:
            self.main.llmw.localllm_key.setText(config.params["localllm_key"])
        if config.params["localllm_api"]:
            self.main.llmw.localllm_api.setText(config.params["localllm_api"])
        if config.params["localllm_model"] and config.params["localllm_model"] in allmodels:
            self.main.llmw.localllm_model.setCurrentText(config.params["localllm_model"])
        if config.params["localllm_template"]:
            self.main.llmw.localllm_template.setPlainText(config.params["localllm_template"])
        self.main.llmw.edit_allmodels.textChanged.connect(setallmodels)
        self.main.llmw.set_localllm.clicked.connect(save_localllm)
        self.main.llmw.test_localllm.clicked.connect(test)
        self.main.llmw.show()

    def set_zijiehuoshan_key(self):
        class TestZijiehuoshan(QThread):
            uito = Signal(str)

            def __init__(self, *, parent=None):
                super().__init__(parent=parent)

            def run(self):
                try:
                    from videotrans.translator.huoshan import trans as trans_zijiehuoshan
                    raw = "你好啊我的朋友"
                    text = trans_zijiehuoshan(raw, "English", set_p=False, is_test=True)
                    self.uito.emit(f"ok:{raw}\n{text}")
                except Exception as e:
                    self.uito.emit(str(e))

        def feed(d):
            if not d.startswith("ok:"):
                QtWidgets.QMessageBox.critical(self.main.zijiew, config.transobj['anerror'], d)
            else:
                QtWidgets.QMessageBox.information(self.main.zijiew, "OK", d[3:])
            self.main.zijiew.test_zijiehuoshan.setText('测试')

        def test():
            key = self.main.zijiew.zijiehuoshan_key.text()
            model = self.main.zijiew.zijiehuoshan_model.currentText()
            if not key or not model.strip():
                return QtWidgets.QMessageBox.critical(self.main.zijiew, config.transobj['anerror'], '必须填写API key和推理接入点')

            template = self.main.zijiew.zijiehuoshan_template.toPlainText()
            config.params["zijiehuoshan_key"] = key
            config.params["zijiehuoshan_model"] = model
            config.params["zijiehuoshan_template"] = template

            task = TestZijiehuoshan(parent=self.main.zijiew)
            self.main.zijiew.test_zijiehuoshan.setText('测试中请稍等...' if config.defaulelang == 'zh' else 'Testing...')
            task.uito.connect(feed)
            task.start()

        def save_zijiehuoshan():
            key = self.main.zijiew.zijiehuoshan_key.text()

            model = self.main.zijiew.zijiehuoshan_model.currentText()
            template = self.main.zijiew.zijiehuoshan_template.toPlainText()

            config.params["zijiehuoshan_key"] = key
            config.params["zijiehuoshan_model"] = model
            config.params["zijiehuoshan_template"] = template
            with open(config.rootdir + f"/videotrans/zijie.txt", 'w', encoding='utf-8') as f:
                f.write(template)
            config.getset_params(config.params)
            self.main.zijiew.close()

        def setallmodels():
            t = self.main.zijiew.edit_allmodels.toPlainText().strip().replace('，', ',').rstrip(',')
            t_list = [x for x in t.split(',') if x.strip()]
            current_text = self.main.zijiew.zijiehuoshan_model.currentText()
            self.main.zijiew.zijiehuoshan_model.clear()
            self.main.zijiew.zijiehuoshan_model.addItems(t_list)
            if current_text:
                self.main.zijiew.zijiehuoshan_model.setCurrentText(current_text)
            config.settings['zijiehuoshan_model'] = t
            json.dump(config.settings, open(config.rootdir + '/videotrans/cfg.json', 'w', encoding='utf-8'),
                      ensure_ascii=False)

        from videotrans.component import ZijiehuoshanForm
        self.main.zijiew = ZijiehuoshanForm()
        allmodels_str = config.settings['zijiehuoshan_model']
        allmodels = config.settings['zijiehuoshan_model'].split(',')
        self.main.zijiew.zijiehuoshan_model.clear()
        self.main.zijiew.zijiehuoshan_model.addItems(allmodels)
        self.main.zijiew.edit_allmodels.setPlainText(allmodels_str)
        if config.params["zijiehuoshan_key"]:
            self.main.zijiew.zijiehuoshan_key.setText(config.params["zijiehuoshan_key"])
        if config.params["zijiehuoshan_model"] and config.params['zijiehuoshan_model'] in allmodels:
            self.main.zijiew.zijiehuoshan_model.setCurrentText(config.params["zijiehuoshan_model"])

        if config.params["zijiehuoshan_template"]:
            self.main.zijiew.zijiehuoshan_template.setPlainText(config.params["zijiehuoshan_template"])
        self.main.zijiew.edit_allmodels.textChanged.connect(setallmodels)
        self.main.zijiew.set_zijiehuoshan.clicked.connect(save_zijiehuoshan)
        self.main.zijiew.test_zijiehuoshan.clicked.connect(test)
        self.main.zijiew.show()

    def set_gemini_key(self):
        def save():
            key = self.main.gw.gemini_key.text()
            model = self.main.gw.model.currentText()
            template = self.main.gw.gemini_template.toPlainText()
            os.environ['GOOGLE_API_KEY'] = key
            config.params["gemini_model"] = model
            config.params["gemini_key"] = key
            config.params["gemini_template"] = template
            with open(config.rootdir + f"/videotrans/gemini{'-en' if config.defaulelang != 'zh' else ''}.txt", 'w',
                      encoding='utf-8') as f:
                f.write(template)
            config.getset_params(config.params)
            self.main.gw.close()

        def setallmodels():
            t = self.main.gw.edit_allmodels.toPlainText().strip().replace('，', ',').rstrip(',')
            current_text = self.main.gw.model.currentText()
            self.main.gw.model.clear()
            self.main.gw.model.addItems([x for x in t.split(',') if x.strip()])
            if current_text:
                self.main.gw.model.setCurrentText(current_text)
            config.settings['gemini_model'] = t
            json.dump(config.settings, open(config.rootdir + '/videotrans/cfg.json', 'w', encoding='utf-8'),
                      ensure_ascii=False)

        from videotrans.component import GeminiForm
        self.main.gw = GeminiForm()
        allmodels_str = config.settings['gemini_model']
        allmodels = config.settings['gemini_model'].split(',')
        self.main.gw.model.clear()
        self.main.gw.model.addItems(allmodels)
        self.main.gw.edit_allmodels.setPlainText(allmodels_str)
        if config.params["gemini_key"]:
            self.main.gw.gemini_key.setText(config.params["gemini_key"])
        if config.params["gemini_model"]:
            self.main.gw.model.setCurrentText(config.params["gemini_model"])
        if config.params["gemini_template"]:
            self.main.gw.gemini_template.setPlainText(config.params["gemini_template"])
        self.main.gw.set_gemini.clicked.connect(save)
        self.main.gw.edit_allmodels.textChanged.connect(setallmodels)
        self.main.gw.show()

    def set_azure_key(self):
        def save():
            key = self.main.azw.azure_key.text()
            api = self.main.azw.azure_api.text()
            model = self.main.azw.azure_model.currentText()
            version = self.main.azw.azure_version.currentText()
            template = self.main.azw.azure_template.toPlainText()

            config.params["azure_key"] = key
            config.params["azure_api"] = api
            config.params["azure_version"] = version
            config.params["azure_model"] = model
            config.params["azure_template"] = template
            with open(config.rootdir + f"/videotrans/azure{'-en' if config.defaulelang != 'zh' else ''}.txt", 'w',
                      encoding='utf-8') as f:
                f.write(template)
            config.getset_params(config.params)

            self.main.azw.close()

        def setallmodels():
            t = self.main.azw.edit_allmodels.toPlainText().strip().replace('，', ',').rstrip(',')
            current_text = self.main.azw.azure_model.currentText()
            self.main.azw.azure_model.clear()

            self.main.azw.azure_model.addItems([x for x in t.split(',') if x.strip()])
            if current_text:
                self.main.azw.azure_model.setCurrentText(current_text)
            config.settings['azure_model'] = t
            json.dump(config.settings, open(config.rootdir + '/videotrans/cfg.json', 'w', encoding='utf-8'),
                      ensure_ascii=False)

        from videotrans.component import AzureForm
        self.main.azw = AzureForm()
        allmodels_str = config.settings['azure_model']
        allmodels = config.settings['azure_model'].split(',')
        self.main.azw.azure_model.clear()
        self.main.azw.azure_model.addItems(allmodels)
        self.main.azw.edit_allmodels.setPlainText(allmodels_str)

        if config.params["azure_key"]:
            self.main.azw.azure_key.setText(config.params["azure_key"])
        if config.params["azure_api"]:
            self.main.azw.azure_api.setText(config.params["azure_api"])
        if config.params["azure_version"]:
            self.main.azw.azure_version.setCurrentText(config.params["azure_version"])
        if config.params["azure_model"] and config.params['azure_model'] in allmodels:
            self.main.azw.azure_model.setCurrentText(config.params["azure_model"])
        if config.params["azure_template"]:
            self.main.azw.azure_template.setPlainText(config.params["azure_template"])

        self.main.azw.edit_allmodels.textChanged.connect(setallmodels)
        self.main.azw.set_azure.clicked.connect(save)
        self.main.azw.show()

    def set_transapi(self):
        class Test(QThread):
            uito = Signal(str)

            def __init__(self, *, parent=None, text=None):
                super().__init__(parent=parent)
                self.text = text

            def run(self):
                from videotrans.translator.transapi import trans
                try:
                    t = trans(self.text, target_language="en", set_p=False, is_test=True, source_code="zh")
                    self.uito.emit(f"ok:{self.text}\n{str(t)}")
                except Exception as e:
                    self.uito.emit(str(e))

        def feed(d):
            if d.startswith("ok:"):
                QtWidgets.QMessageBox.information(self.main.transapiw, "ok", d[3:])
            else:
                QtWidgets.QMessageBox.critical(self.main.transapiw, config.transobj['anerror'], d)
            self.main.transapiw.test.setText('测试api' if config.defaulelang == 'zh' else 'Test api')

        def test():
            url = self.main.transapiw.api_url.text()
            config.params["ttsapi_url"] = url
            if not url:
                return QtWidgets.QMessageBox.critical(self.main.transapiw, config.transobj['anerror'],
                                                      "必须填写自定义翻译的url" if config.defaulelang == 'zh' else "The url of the custom translation must be filled in")
            url = self.main.transapiw.api_url.text()
            miyue = self.main.transapiw.miyue.text()
            config.params["trans_api_url"] = url
            config.params["trans_secret"] = miyue
            task = Test(parent=self.main.transapiw, text="你好啊我的朋友")
            self.main.transapiw.test.setText('测试中请稍等...' if config.defaulelang == 'zh' else 'Testing...')
            task.uito.connect(feed)
            task.start()

        def save():
            url = self.main.transapiw.api_url.text()
            miyue = self.main.transapiw.miyue.text()
            config.params["trans_api_url"] = url
            config.params["trans_secret"] = miyue
            config.getset_params(config.params)
            self.main.transapiw.close()

        from videotrans.component import TransapiForm
        self.main.transapiw = TransapiForm()
        if config.params["trans_api_url"]:
            self.main.transapiw.api_url.setText(config.params["trans_api_url"])
        if config.params["trans_secret"]:
            self.main.transapiw.miyue.setText(config.params["trans_secret"])

        self.main.transapiw.save.clicked.connect(save)
        self.main.transapiw.test.clicked.connect(test)
        self.main.transapiw.show()
