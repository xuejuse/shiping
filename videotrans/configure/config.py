# -*- coding: utf-8 -*-
import datetime
import json
import os
import locale
import logging
import re
import sys
from queue import Queue
from pathlib import Path


def get_executable_path():
    # 这个函数会返回可执行文件所在的目录
    if getattr(sys, 'frozen', False):
        # 如果程序是被“冻结”打包的，使用这个路径
        return os.path.dirname(sys.executable).replace('\\', '/')
    else:
        return str(Path.cwd()).replace('\\', '/')


# root dir
rootdir = get_executable_path()
root_path = Path(rootdir)

# cache tmp
temp_path = root_path / "tmp"
temp_path.mkdir(parents=True, exist_ok=True)
TEMP_DIR = temp_path.as_posix()

# home 
homepath = Path.home() / 'Videos/pyvideotrans'
homepath.mkdir(parents=True, exist_ok=True)
homedir = homepath.as_posix()

# home tmp
TEMP_HOME = homedir + "/tmp"
Path(TEMP_HOME).mkdir(parents=True, exist_ok=True)

# logs 

logs_path = root_path / "logs"
logs_path.mkdir(parents=True, exist_ok=True)
LOGS_DIR = logs_path.as_posix()

logger = logging.getLogger('VideoTrans')

## 

# 配置日志格式
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# 创建日志记录器
# logger = logging.getLogger('MyLogger')
logger.setLevel(logging.INFO)  # 设置日志级别

# 创建文件处理器，并设置级别为DEBUG
file_handler = logging.FileHandler(f'{rootdir}/logs/video-{datetime.datetime.now().strftime("%Y%m%d")}.log',
                                   encoding='utf-8')
file_handler.setLevel(logging.INFO)  # 只记录ERROR及以上级别的日志

# 创建控制台处理器，并设置级别为DEBUG
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

# 设置日志格式
formatter = logging.Formatter(log_format)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# 添加处理器到日志记录器
logger.addHandler(file_handler)
logger.addHandler(console_handler)


# 捕获所有未处理的异常
def log_uncaught_exceptions(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        # 允许键盘中断（Ctrl+C）退出
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


# 安装自定义异常钩子
sys.excepthook = log_uncaught_exceptions

# ffmpeg
if sys.platform == 'win32':
    PWD = rootdir.replace('/', '\\')
    os.environ['PATH'] = PWD + f';{PWD}\\ffmpeg;' + os.environ['PATH']
else:
    os.environ['PATH'] = rootdir + f':{rootdir}/ffmpeg:' + os.environ['PATH']

os.environ['QT_API'] = 'pyside6'
os.environ['SOFT_NAME'] = 'pyvideotrans'
# spwin主窗口
queue_logs = Queue(1000)
# box窗口
queuebox_logs = Queue(1000)
# 开始按钮状态
current_status = "stop"
# video toolbox 状态
box_status = "stop"

# 存放一次性多选的视频
queue_mp4 = []

# 存放视频分离为无声视频进度，noextname为key，用于判断某个视频是否是否已预先创建好 novice_mp4, “ing”=需等待，end=成功完成，error=出错了
queue_novice = {}

# 倒计时
task_countdown = 0
# 获取的视频信息 全局缓存
video_cache = {}

# youtube是否取消了下载
canceldown = False
# 工具箱翻译进行状态,ing进行中，其他停止
box_trans = "stop"
# 工具箱tts状态
box_tts = "stop"
# 工具箱识别状态
box_recogn = 'stop'
# 中断win背景分离
separate_status = 'stop'
# 最后一次打开的目录
# 软件退出
exit_soft = False

# 翻译队列
trans_queue = []
# 配音队列
dubb_queue = []
# 识别队列
regcon_queue = []
# 合成队列
compose_queue = []
# 全局任务id列表
unidlist = []
# 全局错误
errorlist = {}

# 当前可用编码 libx264 h264_qsv h264_nvenc 等
video_codec = None

# 视频慢速时最小间隔毫秒，默认50ms，小于这个值的视频片段将舍弃，避免出错
video_min_ms = 50

openaiTTS_rolelist = "alloy,echo,fable,onyx,nova,shimmer"
# 识别-翻译-配音-合并 线程启动标志
task_thread = False
# 存放 edget-tts 角色列表
edgeTTS_rolelist = None
AzureTTS_rolelist = None

# 语言
try:
    defaulelang = locale.getdefaultlocale()[0][:2].lower()
except Exception:
    defaulelang = "zh"


def parse_init():
    default = {
        "ai302_models": "gpt-4o-mini,gpt-4o,gpt-4,gpt-4-turbo-preview,ernie-4.0-8k,qwen-max,glm-4,moonshot-v1-8k,yi-large,deepseek-chat,doubao-pro-128k,generalv3.5,gemini-1.5-pro,baichuan2-53b,sensechat-5,llama3-70b-8192,qwen2-72b-instruct",
        "ai302tts_models": "tts-1,tts-1-hd,azure",
        "lang": "",
        "crf": 13,
        "cuda_qp": False,
        "preset": "slow",
        "ffmpeg_cmd": "",
        "video_codec": 264,
        "chatgpt_model": "gpt-4o-mini,gpt-4o,gpt-4,gpt-4-turbo,gpt-4-turbo-preview,qwen,moonshot-v1-8k,deepseek-chat",
        "azure_model": "gpt-4o,gpt-4,gpt-35-turbo",
        "localllm_model": "qwen:7b,qwen:1.8b-chat-v1.5-q2_k,moonshot-v1-8k,deepseek-chat",
        "zijiehuoshan_model": "",
        "model_list": "tiny,tiny.en,base,base.en,small,small.en,medium,medium.en,large-v1,large-v2,large-v3,distil-whisper-small.en,distil-whisper-medium.en,distil-whisper-large-v2,distil-whisper-large-v3",
        "audio_rate": 3,
        "video_rate": 20,
        "remove_silence": False,
        "remove_srt_silence": False,
        "remove_white_ms": 0,
        "force_edit_srt": True,
        "vad": True,
        "overall_silence": 250,
        "overall_maxsecs": 6,
        "overall_threshold": 0.5,
        "overall_speech_pad_ms": 100,
        "voice_silence": 250,
        "interval_split": 10,
        "trans_thread": 15,
        "retries": 2,
        "translation_wait": 0.1,
        "dubbing_thread": 5,
        "countdown_sec": 15,
        "backaudio_volume": 0.8,
        "separate_sec": 600,
        "loop_backaudio": True,
        "cuda_com_type": "float32",
        "initial_prompt_zh": "add punctuation after end of each line. 就比如说，我要先去吃饭。segment at end of each  sentence.",
        "whisper_threads": 4,
        "whisper_worker": 1,
        "beam_size": 5,
        "best_of": 5,
        "temperature": 0,
        "condition_on_previous_text": False,
        "fontsize": 16,
        "fontname": "黑体",
        "fontcolor": "&hffffff",
        "fontbordercolor": "&h000000",
        "subtitle_bottom": 10,
        "cjk_len": 20,
        "other_len": 54,
        "gemini_model": "gemini-1.5-pro,gemini-pro,gemini-1.5-flash",
        "zh_hant_s": True,
        "azure_lines": 150,
        "chattts_voice": "11,12,16,2222,4444,6653,7869,9999,5,13,14,1111,3333,4099,5099,5555,8888,6666,7777"
    }
    if not os.path.exists(rootdir + "/videotrans/cfg.json"):
        json.dump(default, open(rootdir + '/videotrans/cfg.json', 'w', encoding='utf-8'), ensure_ascii=False)
        return default
    try:
        tmpjson = json.load(open(rootdir + "/videotrans/cfg.json", 'r', encoding='utf-8'))
    except Exception as e:
        raise Exception('videotrans/cfg.json not found  or  error'+str(e))
    else:
        settings = {}
        for key, val in tmpjson.items():
            value = str(val).strip()
            if value.isdigit():
                settings[key] = int(value)
            elif re.match(r'^\d*\.\d+$', value):
                settings[key] = float(value)
            elif value.lower() == 'true':
                settings[key] = True
            elif value.lower() == 'false':
                settings[key] = False
            else:
                settings[key] = value.lower() if value else ""
        default.update(settings)
        if default['ai302tts_models'].find('azure') == -1:
            default["ai302tts_models"] = "tts-1,tts-1-hd,azure"
        if default['gemini_model'].find('gemini') == -1:
            default["gemini_model"] = "gemini-pro,gemini-1.5-pro,gemini-1.5-flash"
        json.dump(default, open(rootdir + '/videotrans/cfg.json', 'w', encoding='utf-8'), ensure_ascii=False)
        return default


# 初始化一个字典变量
settings = parse_init()
# default language 如果 ini中设置了，则直接使用，否则自动判断
if settings['lang']:
    defaulelang = settings['lang'].lower()
# 语言代码文件是否存在
lang_path = root_path / f'videotrans/language/{defaulelang}.json'
if not lang_path.exists():
    defaulelang = "en"
    lang_path = root_path / f'videotrans/language/{defaulelang}.json'

obj = json.load(lang_path.open('r', encoding='utf-8'))
# 交互语言代码
transobj = obj["translate_language"]
# 软件界面
uilanglist = obj["ui_lang"]
# 语言代码:语言显示名称
langlist: dict = obj["language_code_list"]
# 语言显示名称：语言代码
rev_langlist = {code_alias: code for code, code_alias in langlist.items()}
# 语言显示名称 list
langnamelist = list(langlist.values())
# 工具箱语言
box_lang = obj['toolbox_lang']

# openai  faster-whisper 识别模型
model_list = re.split('\,|，', settings['model_list'])

ChatTTS_voicelist = re.split('\,|，', settings['chattts_voice'])
chatgpt_model_list = [it.strip() for it in settings['chatgpt_model'].split(',') if it.strip()]
azure_model_list = [it.strip() for it in settings['azure_model'].split(',') if it.strip()]
localllm_model_list = [it.strip() for it in settings['localllm_model'].split(',') if it.strip()]
zijiehuoshan_model_list = [it.strip() for it in settings['zijiehuoshan_model'].split(',') if it.strip()]
if len(chatgpt_model_list) < 1:
    chatgpt_model_list = ['']
if len(localllm_model_list) < 1:
    localllm_model_list = ['']
if len(zijiehuoshan_model_list) < 1:
    zijiehuoshan_model_list = ['']


# 设置或获取 config.params
def getset_params(obj=None):
    if obj is not None:
        with open(rootdir + "/videotrans/params.json", 'w', encoding='utf-8') as f:
            f.write(json.dumps(obj, ensure_ascii=False))
        return None
    default = {
        "last_opendir": homedir,
        "cuda": False,

        "only_video": False,
        "is_separate": False,

        "target_dir": "",

        "source_language": "en",
        "target_language": "zh-cn",
        "subtitle_language": "chi",
        "translate_type": "Google",
        "subtitle_type": 0,  # embed soft

        "listen_text_zh-cn": "你好啊，我亲爱的朋友，希望你的每一天都是美好愉快的！",
        "listen_text_zh-tw": "你好啊，我親愛的朋友，希望你的每一天都是美好愉快的！",
        "listen_text_en": "Hello, my dear friend. I hope your every day is beautiful and enjoyable!",
        "listen_text_fr": "Bonjour mon cher ami. J'espère que votre quotidien est beau et agréable !",
        "listen_text_de": "Hallo mein lieber Freund. Ich hoffe, dass Ihr Tag schön und angenehm ist!",
        "listen_text_ja": "こんにちは私の親愛なる友人。 あなたの毎日が美しく楽しいものでありますように！",
        "listen_text_ko": "안녕, 내 사랑하는 친구. 당신의 매일이 아름답고 즐겁기를 바랍니다!",
        "listen_text_ru": "Привет, мой дорогой друг. Желаю, чтобы каждый твой день был прекрасен и приятен!",
        "listen_text_es": "Hola mi querido amigo. ¡Espero que cada día sea hermoso y agradable!",
        "listen_text_th": "สวัสดีเพื่อนรัก. ฉันหวังว่าทุกวันของคุณจะสวยงามและสนุกสนาน!",
        "listen_text_it": "Ciao caro amico mio. Spero che ogni tuo giorno sia bello e divertente!",
        "listen_text_pt": "Olá meu querido amigo. Espero que todos os seus dias sejam lindos e agradáveis!",
        "listen_text_vi": "Xin chào người bạn thân yêu của tôi. Tôi hy vọng mỗi ngày của bạn đều đẹp và thú vị!",
        "listen_text_ar": "مرحبا صديقي العزيز. أتمنى أن يكون كل يوم جميلاً وممتعًا!",
        "listen_text_tr": "Merhaba sevgili arkadaşım. Umarım her gününüz güzel ve keyifli geçer!",
        "listen_text_hi": "नमस्ते मेरे प्यारे दोस्त। मुझे आशा है कि आपका हर दिन सुंदर और आनंददायक हो!!",
        "listen_text_hu": "Helló kedves barátom. Remélem minden napod szép és kellemes!",
        "listen_text_uk": "Привіт, мій дорогий друже, сподіваюся, ти щодня прекрасна!",
        "listen_text_id": "Halo, temanku, semoga kamu cantik setiap hari!",
        "listen_text_ms": "Helo, sahabat saya, saya harap anda cantik setiap hari!",
        "listen_text_kk": "Сәлеметсіз бе, менің қымбатты досым, сендер күн сайын әдемісің деп үміттенемін!",
        "listen_text_cs": "Ahoj, můj drahý příteli, doufám, že jsi každý den krásná!",
        "listen_text_pl": "Witam, mój drogi przyjacielu, mam nadzieję, że jesteś piękna każdego dnia!",
        "listen_text_nl": "Hallo mijn lieve vriend, ik hoop dat elke dag goed en fijn voor je is!!",

        "tts_type": "edgeTTS",  # 所选的tts==edge-tts:openaiTTS|coquiTTS|elevenlabsTTS
        "tts_type_list": ["edgeTTS", 'CosyVoice', "ChatTTS", "302.ai", "FishTTS", "AzureTTS", "GPT-SoVITS",
                          "clone-voice",
                          "openaiTTS", "elevenlabsTTS", "gtts", "TTS-API"],

        "whisper_type": "all",
        "whisper_model": "tiny",
        "model_type": "faster",

        "voice_autorate": False,
        "voice_role": "No",
        "voice_rate": "0",
        "video_autorate": False,
        "append_video": True,

        "deepl_authkey": "",
        "deepl_api": "",
        "deeplx_address": "",

        "ott_address": "",

        "tencent_SecretId": "",
        "tencent_SecretKey": "",

        "baidu_appid": "",
        "baidu_miyue": "",

        "chatgpt_api": "",
        "chatgpt_key": "",
        "chatgpt_model": chatgpt_model_list[0],
        "chatgpt_template": """请将<source>中的原文内容按字面意思翻译到{lang}，然后只输出译文，不要添加任何说明或引导词。

**格式要求：**
- 按行翻译原文，并生成该行对应的译文，确保原文行和译文行中的每个单词相互对应。
- 有几行原文，必须生成几行译文。

**内容要求：**
- 翻译必须精简短小，避免长句。
- 如果原文无法翻译，请返回空行，不得添加“无意义语句或不可翻译”等任何提示语。
- 只输出译文即可，禁止输出任何原文。

**执行细节：**
- 如果某行原文很短，在翻译后也仍然要保留该行，不得与上一行或下一行合并。
- 原文换行处字符相对应的译文字符也必须换行。
- 严格按照字面意思翻译，不要解释或回答原文内容。

**最终目标：**
- 提供格式与原文完全一致的高质量翻译结果。

<source>[TEXT]</source>

译文:""" if defaulelang == 'zh' else """""",

        "azure_api": "",
        "azure_key": "",
        "azure_version":"2024-06-01",
        "azure_model": azure_model_list[0],
        "azure_template": """请将<source>中的原文内容按字面意思翻译到{lang}，然后只输出译文，不要添加任何说明或引导词。

**格式要求：**
- 按行翻译原文，并生成该行对应的译文，确保原文行和译文行中的每个单词相互对应。
- 有几行原文，必须生成几行译文。

**内容要求：**
- 翻译必须精简短小，避免长句。
- 如果原文无法翻译，请返回空行，不得添加“无意义语句或不可翻译”等任何提示语。
- 只输出译文即可，禁止输出任何原文。

**执行细节：**
- 如果某行原文很短，在翻译后也仍然要保留该行，不得与上一行或下一行合并。
- 原文换行处字符相对应的译文字符也必须换行。
- 严格按照字面意思翻译，不要解释或回答原文内容。

**最终目标：**
- 提供格式与原文完全一致的高质量翻译结果。

<source>[TEXT]</source>

译文:""" if defaulelang == 'zh' else """Please translate the original text in <source> literally to {lang}, and then output only the translated text without adding any notes or leading words.

**Format Requirements:**
- Translate the original text line by line and generate the translation corresponding to that line, making sure that each word in the original line and the translated line corresponds to each other.
- If there are several lines of original text, several lines of translation must be generated.

**Content requirements:**
- Translations must be concise and short, avoiding long sentences.
- If the original text cannot be translated, please return to an empty line, and do not add any hints such as "meaningless statement or untranslatable", etc. Only the translated text can be output, and it is forbidden to output the translated text.
- Only the translation can be output, and it is forbidden to output any original text.

**Execution details:**
- If a line is very short in the original text, it should be retained after translation, and should not be merged with the previous or next line.
- The characters corresponding to the characters in the translation at the line breaks in the original text must also be line breaks.
- Translate strictly literally, without interpreting or answering the content of the original text.

**End goal:**
- Provide high-quality translations that are formatted exactly like the original.

<source>[TEXT]</source>

Translation:""",

        "gemini_key": "",
        "gemini_model": "gemini-1.5-pro",
        "gemini_template": """请将<source>中的原文内容按字面意思翻译到{lang}，然后只输出译文，不要添加任何说明或引导词。

**格式要求：**
- 按行翻译原文，并生成该行对应的译文，确保原文行和译文行中的每个单词相互对应。
- 有几行原文，必须生成几行译文。

**内容要求：**
- 翻译必须精简短小，避免长句。
- 如果原文无法翻译，请返回空行，不得添加“无意义语句或不可翻译”等任何提示语。
- 只输出译文即可，禁止输出任何原文。

**执行细节：**
- 如果某行原文很短，在翻译后也仍然要保留该行，不得与上一行或下一行合并。
- 原文换行处字符相对应的译文字符也必须换行。
- 严格按照字面意思翻译，不要解释或回答原文内容。

**最终目标：**
- 提供格式与原文完全一致的高质量翻译结果。

<source>[TEXT]</source>

译文:""" if defaulelang == 'zh' else """Please translate the original text in <source> literally to {lang}, and then output only the translated text without adding any notes or leading words.

**Format Requirements:**
- Translate the original text line by line and generate the translation corresponding to that line, making sure that each word in the original line and the translated line corresponds to each other.
- If there are several lines of original text, several lines of translation must be generated.

**Content requirements:**
- Translations must be concise and short, avoiding long sentences.
- If the original text cannot be translated, please return to an empty line, and do not add any hints such as "meaningless statement or untranslatable", etc. Only the translated text can be output, and it is forbidden to output the translated text.
- Only the translation can be output, and it is forbidden to output any original text.

**Execution details:**
- If a line is very short in the original text, it should be retained after translation, and should not be merged with the previous or next line.
- The characters corresponding to the characters in the translation at the line breaks in the original text must also be line breaks.
- Translate strictly literally, without interpreting or answering the content of the original text.

**End goal:**
- Provide high-quality translations that are formatted exactly like the original.

<source>[TEXT]</source>

Translation:""",

        "localllm_api": "",
        "localllm_key": "",
        "localllm_model": localllm_model_list[0],
        "localllm_template": """""" if defaulelang == 'zh' else """Please translate the original text in <source> literally to {lang}, and then output only the translated text without adding any notes or leading words.

**Format Requirements:**
- Translate the original text line by line and generate the translation corresponding to that line, making sure that each word in the original line and the translated line corresponds to each other.
- If there are several lines of original text, several lines of translation must be generated.

**Content requirements:**
- Translations must be concise and short, avoiding long sentences.
- If the original text cannot be translated, please return to an empty line, and do not add any hints such as "meaningless statement or untranslatable", etc. Only the translated text can be output, and it is forbidden to output the translated text.
- Only the translation can be output, and it is forbidden to output any original text.

**Execution details:**
- If a line is very short in the original text, it should be retained after translation, and should not be merged with the previous or next line.
- The characters corresponding to the characters in the translation at the line breaks in the original text must also be line breaks.
- Translate strictly literally, without interpreting or answering the content of the original text.

**End goal:**
- Provide high-quality translations that are formatted exactly like the original.

<source>[TEXT]</source>

Translation:""",

        "zijiehuoshan_key": "",
        "zijiehuoshan_model": zijiehuoshan_model_list[0],
        "zijiehuoshan_template": """请将<source>中的原文内容按字面意思翻译到{lang}，然后只输出译文，不要添加任何说明或引导词。

**格式要求：**
- 按行翻译原文，并生成该行对应的译文，确保原文行和译文行中的每个单词相互对应。
- 有几行原文，必须生成几行译文。

**内容要求：**
- 翻译必须精简短小，避免长句。
- 如果原文无法翻译，请返回空行，不得添加“无意义语句或不可翻译”等任何提示语。
- 只输出译文即可，禁止输出任何原文。

**执行细节：**
- 如果某行原文很短，在翻译后也仍然要保留该行，不得与上一行或下一行合并。
- 原文换行处字符相对应的译文字符也必须换行。
- 严格按照字面意思翻译，不要解释或回答原文内容。

**最终目标：**
- 提供格式与原文完全一致的高质量翻译结果。

<source>[TEXT]</source>

译文:""",

        "ai302_key": "",
        "ai302_model": "",
        "ai302_template": """请将<source>中的原文内容按字面意思翻译到{lang}，然后只输出译文，不要添加任何说明或引导词。

**格式要求：**
- 按行翻译原文，并生成该行对应的译文，确保原文行和译文行中的每个单词相互对应。
- 有几行原文，必须生成几行译文。

**内容要求：**
- 翻译必须精简短小，避免长句。
- 如果原文无法翻译，请原样返回，不得添加“无意义语句或不可翻译”等任何提示语。
- 只输出译文即可，不要输出原文。

**执行细节：**
- 如果某行原文很短，在翻译后也仍然要保留该行，不得与上一行或下一行合并。
- 原文换行处字符相对应的译文字符也必须换行。
- 严格按照字面意思翻译，不要解释或回答原文内容。

**最终目标：**
- 提供格式与原文完全一致的高质量翻译结果。

<source>[TEXT]</source>

译文:
""",

        "trans_api_url": "",
        "trans_secret": "",

        "coquitts_role": "",
        "coquitts_key": "",

        "elevenlabstts_role": [],
        "elevenlabstts_key": "",

        "openaitts_role": openaiTTS_rolelist,

        "clone_api": "",
        "clone_voicelist": ["clone"],

        "zh_recogn_api": "",

        "ttsapi_url": "",
        "ttsapi_voice_role": "",
        "ttsapi_extra": "pyvideotrans",

        "ai302tts_key": "",
        "ai302tts_model": "",
        "ai302tts_role": openaiTTS_rolelist,

        "azure_speech_region": "",
        "azure_speech_key": "",

        "gptsovits_url": "",
        "gptsovits_role": "",
        "gptsovits_extra": "pyvideotrans",

        "cosyvoice_url": "",
        "cosyvoice_role": "",

        "fishtts_url": "",
        "fishtts_role": "",

        "doubao_appid":"",
        "doubao_access":"",

        "chattts_api":"",


        "app_mode": "biaozhun",

        "proxy": ""
    }

    try:
        if os.path.exists(rootdir + "/videotrans/params.json"):
            default.update(json.load(open(rootdir + "/videotrans/params.json", 'r', encoding='utf-8')))

        chatgpt_path = root_path / f'videotrans/chatgpt{"" if defaulelang == "zh" else "-en"}.txt'
        if chatgpt_path.exists():
            default['chatgpt_template'] = chatgpt_path.read_text(encoding='utf-8').strip() + "\n"
        else:
            chatgpt_path.write_text(default['chatgpt_template'])

        azure_path = root_path / f'videotrans/azure{"" if defaulelang == "zh" else "-en"}.txt'
        if azure_path.exists():
            default['azure_template'] = azure_path.read_text(encoding='utf-8').strip() + "\n"
        else:
            azure_path.write_text(default['azure_template'])

        gemini_path = root_path / f'videotrans/gemini{"" if defaulelang == "zh" else "-en"}.txt'
        if gemini_path.exists():
            default['gemini_template'] = gemini_path.read_text(encoding='utf-8').strip() + "\n"
        else:
            gemini_path.write_text(default['gemini_template'])

        localllm_path = root_path / f'videotrans/localllm{"" if defaulelang == "zh" else "-en"}.txt'
        if localllm_path.exists():
            default['localllm_template'] = localllm_path.read_text(encoding='utf-8').strip() + "\n"
        else:
            localllm_path.write_text(default['localllm_template'])

        zijiehuoshan_path = root_path / f'videotrans/zijie.txt'
        if zijiehuoshan_path.exists():
            default['zijiehuoshan_template'] = zijiehuoshan_path.read_text(encoding='utf-8').strip() + "\n"
        else:
            zijiehuoshan_path.write_text(default['zijiehuoshan_template'])

        ai302_path = root_path / f'videotrans/302ai.txt'
        if ai302_path.exists():
            default['ai302_template'] = ai302_path.read_text(encoding='utf-8').strip() + "\n"
        else:
            ai302_path.write_text(default['ai302_template'])
    except Exception:
        pass
    if not os.path.exists(rootdir + "/videotrans/params.json"):
        json.dump(default,open(rootdir + "/videotrans/params.json",'w', encoding='utf-8'),ensure_ascii=False)
    return default


params = getset_params()


