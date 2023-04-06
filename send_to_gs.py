# отправляет данные в подключенную GS
def send_to_gs(sh_name, df, json_path, sheet_id):
    import gspread  # для работы с GS
    from gspread_dataframe import set_with_dataframe  # функция отправки таблицы в GS
    from google.oauth2.credentials import Credentials  # для авторизации в Google
    
    #-# авторизация и подключение к листу (создание его, при отсутствии)
    gc = gspread.oauth(credentials_filename=json_path)  # местоположение ключа oauth2
    sh = gc.open_by_key(sheet_id)  # id таблицы

    # sh_name = название листа, на который будут записаны данные 
    # df = данные, которые нужно отправить
    # если указанного листа нет, то он будет создан
    try:
        worksheet = sh.worksheet(sh_name)
    except:
        worksheet = sh.add_worksheet(title=sh_name,
                                     rows="10",
                                     cols="100")

    # очистка листа
    worksheet.clear()

    # запись на лист
    set_with_dataframe(worksheet=worksheet,
                       dataframe=df,
                       include_index=False,
                       include_column_header=True,
                       resize=True)
