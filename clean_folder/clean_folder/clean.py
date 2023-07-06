from pathlib import Path
import shutil
import re
# известние файли для сортировки
FILE_EXTENSIONS = {
    'images': {'.jpeg', '.png', '.jpg', '.svg'},
    'video': {'.avi', '.mp4', '.mov', '.mkv'},
    'documents': {'.doc', '.docx', '.txt', '.pdf', '.xlsx', '.pptx'},
    'audio': {'.mp3', '.ogg', '.wav', '.amr'},
    'archives': {'.zip', '.gz', '.tar'}
}
my_extens = set() # сет для записи всех имеющихся расширений в папке
# константи для переименования файлов
CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g")
TRANS = {}
for c,t in zip(CYRILLIC_SYMBOLS,TRANSLATION):

    TRANS[ord(c)] = t
    TRANS[ord(c.upper())] = t.upper()



def normalize(name : str) -> str :
    """
    транлитерация кирилици
    замена всего кроме латинского алфавита и чисел на _
    """
    t_name = name.translate(TRANS)
    t_name = re.sub(r'\W', '_', t_name)  
    return t_name  

def new_path_name(ex: Path) -> Path:
    """
    переименование по транслиту + "_"
    возврат нового пути(../файл.суф)
    """
    new_name = normalize(ex.stem) + ex.suffix # новое имя + суфикс
    new_ex = ex.rename(ex.parent / new_name) # переименование файлов + присваеваем новий путь
    return new_ex

def get_new_folder_name(ex: Path) -> str:
    """
    получаем имя для новой папки(по расширению файла) 
    соответствующей файловой группе 
    """
    name_dir = "" 
    for key,val in FILE_EXTENSIONS.items():
        if ex.suffix in val : 
            name_dir = key
            break
    if not name_dir: # если нет совпадений по константе
        name_dir = "others"  

    return name_dir     

def replace_file_new_dir(ex: Path, name_dir: str) :
    """
    сознаем новую папку если такой нет
    перенос файла -> возврат нового пути 
    """
    new_dir_path = main_path / name_dir # путь к новой папке для ее создание и переноса файлов
    new_dir_path.mkdir(exist_ok=True) # создаем новую папку если такой нет 
    new_ex_path = ex.replace(new_dir_path / ex.name) # перенос файлов в папки по категориям
    return new_ex_path

def  extract_archive(archive_path: Path, del_archive=True) :
    """
    разархивируем архив в папку с именем архива
    с флагом на удаление архива + ловим ошибку
    """
    target_dir = archive_path.parent / archive_path.stem # путь для созданием папки с именем архива
    target_dir.mkdir(exist_ok=True) # создаем папку для архива
    try:
        shutil.unpack_archive(archive_path, target_dir) # распаковка
        if del_archive: # удаляем архив по флагу после распаковки
            archive_path.unlink()
    except ValueError:
        print(f"Не удалось разпаковать архив : {archive_path.name}")
    except shutil.ReadError:
        print(f"Архив - {archive_path.stem} не распакован\tнеизвестное расширение({archive_path.suffix})")
  

def input_path()-> Path:
    """
    инпут пути к папке 
    проверка на валидность(существует+папка)
    """
    while True:
        path = Path(input("Введите полний путь к папке которую хотите отсортировать:\n"))
        if path.exists() and path.is_dir():
            return path
        else:
            print("введений вами путь не существует или не является папкой\n")            



def directory_tree (path: Path,  my_dict_files=None) :
    """
    основной рекурсивний проход 
    всех папок и файлов
    """
    for item in path.iterdir() :
        if item.is_file():
            
            item = new_path_name(item) # переименование файла

            name_dir = get_new_folder_name(item) # имя для новой папки

            item = replace_file_new_dir(item, name_dir) # создание папок + перемещение файлов

            if name_dir == "archives": # если категория ахиви(файл можно разпаковать TODO list from shatil) 
                extract_archive(item) # разпаковка + по умолчанию флаг на удаление 

            
            # get_data: set of ex +  my_dict_files-> категория : [файли] TODO отдельная функция?
            my_extens.add(item.suffix)  # заполнение сета расширений 
            if  my_dict_files is None :  my_dict_files = {} #создаем словарь на первом заходе 
            if name_dir not in my_dict_files : # если нет ключа создаем ключ:спиок
                my_dict_files[name_dir] = [item.stem]
            else:
                my_dict_files[name_dir].append(item.stem)         


        elif item.is_dir() and (item.name not in FILE_EXTENSIONS) : # проверка на папку и она не из наших ключей

            my_dict_files = directory_tree(path / item.name, my_dict_files) # рекурсивний заход + my_dict_files-> категория : [файли]
            
            if not any(item.iterdir()): # проверка на пустую папку
                item.rmdir()            # удаляем папку(пустую)

    return  my_dict_files

def main():
    path = input_path()
    global main_path # TODO найти другой способ
    main_path =  path # путь к нашей папке для создания нових
    
    # получаем сет всех известих(скрипту) расширений из константного словаря
    all_extens = set()
    for ext in FILE_EXTENSIONS.values():
        all_extens.update(ext)

    # my_dict_files = {} # словарь для записи -  категория : [файли]
    my_dict_files = directory_tree(path) # визов рекурсивного прохода
    
    print("\nсписок файлов в сортированной дериктории  по категориям :\n")
    for key, val in my_dict_files.items() :
        val_str = ", ".join(val)
        print("{:<10}: {}".format(key,val_str))
    
    print("\nПеречень всех известних расширений в сортированной директории :\n")
    know_extens = all_extens.intersection(my_extens)
    print("\t".join(know_extens))

    print("\nПеречень всех расширений не известних данному скрипту :\n")
    n_know_extens = my_extens.difference(know_extens)
    print("\t".join(n_know_extens))


if __name__ == "__main__" :
    main()