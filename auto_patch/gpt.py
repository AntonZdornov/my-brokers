import site
import pathlib

p = pathlib.Path(site.getsitepackages()[0]) / "ChatTTS/model/gpt.py"
print("Файл для патча:", p)

s = p.read_text()

old = "attention_mask = attention_mask.narrow(1, -max_cache_length, max_cache_length)"
new = (
    "max_cache_length = min(max_cache_length, attention_mask.size(1))\n"
    "start = max(attention_mask.size(1) - max_cache_length, 0)\n"
    "attention_mask = attention_mask.narrow(1, start, max_cache_length)"
)

if old in s:
    s = s.replace(old, new)
    p.write_text(s)
    print("✅ Patched успешно:", p)
else:
    print("⚠️ Строка не найдена — возможно, файл уже был пропатчен")

# запустило модель
# # гарантируем корректные границы
# L = attention_mask.size(1)

# # если max_cache_length где-то стал кривым, зажмём его в [1, L]
# if not isinstance(max_cache_length, int):
#     max_cache_length = int(max_cache_length) if max_cache_length is not None else L

# max_cache_length = max(1, min(max_cache_length, L))  # длина минимум 1, максимум L
# start = max(L - max_cache_length, 0)                  # старт не ниже 0

# attention_mask = attention_mask.narrow(1, start, max_cache_length)
