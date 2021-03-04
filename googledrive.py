
import dropbox

dbx = dropbox.Dropbox('V1Lt6QGymxYAAAAAAAAAAewFSct5TfwVqOsn1MJwYgkmO___22SBHlWRL_pQJrZO')  # наш access token

with open(r'C:\Users\Andrey\PycharmProjects\tgOpros\tgOprosAdmin\photos\profile_363083919_answer_3_.jpg', 'rb') as file:  # открываем файл в режиме чтение побайтово
    response = dbx.files_upload(file.read(),
                                '/myfile.png')  # загружаем файл: первый аргумент (file.read()) - какой файл; второй - название, которое будет присвоено файлу уже на дропбоксе.
    print(response)  # выводим результат загрузки

print(dbx.sharing_create_shared_link('/myfile.png'))