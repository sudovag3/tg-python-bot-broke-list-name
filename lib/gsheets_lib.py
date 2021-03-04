import pygsheets

class GSheets:

    def __init__(self,service_file,filename='',file_url=''):
        if service_file:
            gc = pygsheets.authorize(service_file=service_file)
        else:
            gc = pygsheets.authorize()
        if filename!='':
            sh = gc.open(filename)
        elif file_url!='':
            sh = gc.open_by_url(file_url)
        else:
            #logger.info('name and url is empty')
            return False

        self.service_file = service_file
        self.filename = filename
        self.gc = gc
        self.sh = sh
        pass
    # сохранение данных в таблицу
    def set_df_to_sheets(self, sheetname, df):
        wks = self.sh.worksheet_by_title(sheetname)
        wks.clear()
        wks.set_dataframe(df, (1, 1),fit=True,nan='')
        #logger.info(f'Save: {sheetname}')
        return df
    # получение данных и таблицы
    def get_df_to_sheets(self, sheetname):
        wks = self.sh.worksheet_by_title(sheetname)

        df= wks.get_as_df()
        #logger.info(f'Load: {sheetname}')
        return df
    # добавление данных в таблицу
    def add_df_to_sheets(self, sheetname, df):
        wks = self.sh.worksheet_by_title(sheetname)
        #wks.clear()
        wks.insert_rows(1, number=len(df), values=None, inherit=False)
        wks.set_dataframe(df, (2, 1),nan='',copy_head=False)
        #logger.info(f'Add: {sheetname}')
        return df