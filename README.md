# Архиватор DEFLATE
Версия 1.2  
Автор: Халиков Идрис (idrishal277@gmail.com)

# Описание
Приложение архивирует файлы используя алгоритм сжатия «DEFLATE».

# Список команд
- ``pygzip.py -c <filename>`` - архивирует файл.
- ``pygzip.py -d <filename>`` - деархивириует файл
- ``pygzip.py help`` - краткая справка.

# Краткое описание работы алгоритма
Алгоритм разбивает входные данные на блоки, каждый из которых преобразуется одним из трех способов:
- ``BLOCK TYPE 00`` - Данные не изменяются.
- ``BLOCK TYPE 01`` - Данные сжимаются с помощью алгоритма LZ77(LZSS), затем полученный поток байт сохраняется с использованием фиксированных префиксных кодов.
- ``BLOCK TYPE 10`` - Анологичен предыдущему типу, за тем исключением, что перфиксные коды не фиксированные, а создаются на основе входных данных


